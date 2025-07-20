
import { Workflow, WorkflowNode } from './types';
import { nodeRegistry } from './node-registry';

export class WorkflowExecutor {
  private workflow: Workflow;

  constructor(workflow: Workflow) {
    this.workflow = workflow;
  }

  async execute() {
    console.log(`Starting execution for workflow: ${this.workflow.name}`);
    const executionOrder = this.determineExecutionOrder();
    const results: Record<string, any> = {};

    for (const nodeId of executionOrder) {
      const node = this.workflow.nodes.find(n => n.id === nodeId);
      if (!node) {
        throw new Error(`Node with id ${nodeId} not found in workflow.`);
      }

      const nodeType = nodeRegistry.get(node.type);
      if (!nodeType) {
        throw new Error(`Node type "${node.type}" is not registered.`);
      }

      // Simple dependency injection from previous node results
      const params = { ...node.data };
      const connections = this.workflow.connections.filter(c => c.target === nodeId);
      for (const conn of connections) {
        if (results[conn.source]) {
          // A simple merge, real implementation would be more sophisticated
          Object.assign(params, results[conn.source]);
        }
      }

      try {
        const result = await nodeType.execute(params);
        results[nodeId] = result;
        console.log(`Node ${node.id} (${node.type}) executed successfully.`);
      } catch (error) {
        console.error(`Error executing node ${node.id} (${node.type}):`, error);
        // Stop execution on error
        return { success: false, error: `Node ${node.id} failed.`, results };
      }
    }

    console.log(`Workflow ${this.workflow.name} finished successfully.`);
    return { success: true, results };
  }

  private determineExecutionOrder(): string[] {
    // For simplicity, we'll assume a linear workflow for now.
    // A real implementation would perform a topological sort of the graph.
    const nodesById = new Map(this.workflow.nodes.map(n => [n.id, n]));
    const connectionsBySource = new Map<string, string[]>();
    this.workflow.connections.forEach(c => {
        if (!connectionsBySource.has(c.source)) connectionsBySource.set(c.source, []);
        connectionsBySource.get(c.source)!.push(c.target);
    });

    const startNode = this.workflow.nodes.find(n => !this.workflow.connections.some(c => c.target === n.id));
    if (!startNode) {
        if (this.workflow.nodes.length > 0) {
            return [this.workflow.nodes[0].id];
        }
        return [];
    }
    
    const order = [startNode.id];
    let currentNodeId = startNode.id;

    while(connectionsBySource.has(currentNodeId) && connectionsBySource.get(currentNodeId)!.length > 0) {
        const nextNodeId = connectionsBySource.get(currentNodeId)![0]; // Assume single output for now
        if (order.includes(nextNodeId)) break; // Avoid cycles
        order.push(nextNodeId);
        currentNodeId = nextNodeId;
    }

    return order;
  }
}
