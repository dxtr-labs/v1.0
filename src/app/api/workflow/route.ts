import { NextResponse } from 'next/server';
import { v4 as uuidv4 } from 'uuid';
import { Workflow, WorkflowNode, WorkflowConnection } from '@/lib/workflow-engine/types';
import { WorkflowExecutor } from '@/lib/workflow-engine/executor';
import { dbPromise } from '@/lib/db-sqlite';

async function getDb() {
  return dbPromise;
}

export async function GET(request: Request) {
  const db = await getDb();
  const url = new URL(request.url);
  const workflowId = url.searchParams.get('id');

  if (workflowId) {
    const workflow = await db.get('SELECT * FROM workflows WHERE id = ?', [workflowId]);
    if (!workflow) {
      return NextResponse.json({ error: 'Workflow not found' }, { status: 404 });
    }
    workflow.nodes = await db.all('SELECT * FROM workflow_nodes WHERE workflowId = ?', [workflowId]);
    workflow.connections = await db.all('SELECT * FROM workflow_connections WHERE workflowId = ?', [workflowId]);
    
    // Data from DB is stringified JSON, so we need to parse it.
    workflow.nodes = workflow.nodes.map((node: any) => ({
        ...node,
        data: JSON.parse(node.data),
        position: JSON.parse(node.position),
    }));

    return NextResponse.json(workflow);
  }

  const allWorkflows = await db.all('SELECT * FROM workflows');
  return NextResponse.json(allWorkflows);
}

interface PostBody {
    name: string;
    nodes: WorkflowNode[];
    connections: WorkflowConnection[];
    creatorId: string;
}

export async function POST(request: Request) {
  const db = await getDb();
  const { name, nodes, connections, creatorId }: PostBody = await request.json();

  const newWorkflowId = uuidv4();
  
  await db.run(
    'INSERT INTO workflows (id, name, creatorId, version, createdAt, updatedAt) VALUES (?, ?, ?, ?, ?, ?)',

    [newWorkflowId, name, creatorId, 1, new Date().toISOString(), new Date().toISOString()]
  );

  for (const node of nodes) {
    await db.run(
      'INSERT INTO workflow_nodes (id, workflowId, type, data, position) VALUES (?, ?, ?, ?, ?)',
      [node.id, newWorkflowId, node.type, JSON.stringify(node.data), JSON.stringify(node.position)]
    );
  }

  for (const conn of connections) {
    await db.run(
      'INSERT INTO workflow_connections (id, workflowId, source, target, sourceHandle, targetHandle) VALUES (?, ?, ?, ?, ?, ?)',
      [uuidv4(), newWorkflowId, conn.source, conn.target, conn.sourceHandle, conn.targetHandle]
    );
  }

  const savedWorkflow = await db.get('SELECT * FROM workflows WHERE id = ?', [newWorkflowId]);

  return NextResponse.json(savedWorkflow);
}

interface PutBody {
    workflowId: string;
    action: 'execute' | 'update' | 'delete';
    payload?: any;
}

export async function PUT(request: Request) {
    const db = await getDb();
    const { workflowId, action, payload }: PutBody = await request.json();

    if (!workflowId) {
        return NextResponse.json({ error: 'Workflow ID is required' }, { status: 400 });
    }

    const workflowData = await db.get('SELECT * FROM workflows WHERE id = ?', [workflowId]);
    if (!workflowData) {
        return NextResponse.json({ error: 'Workflow not found' }, { status: 404 });
    }

    const nodes = await db.all('SELECT * FROM workflow_nodes WHERE workflowId = ?', [workflowId]);
    const connections = await db.all('SELECT * FROM workflow_connections WHERE workflowId = ?', [workflowId]);

    const workflow: Workflow = {
        ...workflowData,
        nodes: nodes.map((node: any) => ({
            ...node,
            data: JSON.parse(node.data),
            position: JSON.parse(node.position),
        })),
        connections: connections,
    };


    if (action === 'execute') {
        const executor = new WorkflowExecutor(workflow);
        const result = await executor.execute();
        return NextResponse.json(result);
    }

    return NextResponse.json({ message: 'Action not implemented' }, { status: 501 });
}
