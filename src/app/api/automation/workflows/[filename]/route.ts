import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET(
  request: NextRequest,
  { params }: { params: { filename: string } }
) {
  try {
    const { filename } = params;
    
    if (!filename.endsWith('.json')) {
      return NextResponse.json({ error: 'Invalid file format' }, { status: 400 });
    }
    
    const workflowsDir = path.join(process.cwd(), 'src/app/dashboard/automation/workflows');
    const filePath = path.join(workflowsDir, filename);
    
    // Check if file exists
    if (!fs.existsSync(filePath)) {
      return NextResponse.json({ error: 'Workflow file not found' }, { status: 404 });
    }

    // Read and parse the workflow file
    const fileContent = fs.readFileSync(filePath, 'utf-8');
    const workflowData = JSON.parse(fileContent);
    
    // Transform the data to match our expected format
    const transformedWorkflow = {
      id: workflowData.id || filename.replace('.json', ''),
      name: workflowData.name || filename.replace('.json', '').replace(/_/g, ' ').replace(/^\d+\s*/, ''),
      description: workflowData.meta?.description || `Automated workflow with ${workflowData.nodes?.length || 0} steps`,
      nodes: workflowData.nodes?.map((node: any, index: number) => ({
        id: node.id || `node_${index}`,
        type: node.type || 'action',
        name: node.name || node.type || `Step ${index + 1}`,
        position: node.position || { x: 100 + (index * 200), y: 100 },
        parameters: node.parameters || {},
        credentials: node.credentials || {}
      })) || [],
      connections: workflowData.connections || []
    };

    return NextResponse.json(transformedWorkflow);
    
  } catch (error) {
    console.error('Error loading workflow file:', error);
    return NextResponse.json(
      { error: 'Error parsing workflow file' }, 
      { status: 500 }
    );
  }
}
