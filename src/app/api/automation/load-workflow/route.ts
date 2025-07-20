import { NextRequest, NextResponse } from 'next/server';

// Store workflows temporarily (in production, use Redis or database)
const workflowStore = new Map<string, any>();

interface WorkflowPayload {
  workflow: any;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json() as WorkflowPayload;
    const { workflow } = body;

    if (!workflow) {
      return NextResponse.json(
        { error: 'Workflow data is required' },
        { status: 400 }
      );
    }

    // Generate a unique ID for this workflow session
    const workflowId = `workflow_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Store the workflow data
    workflowStore.set(workflowId, {
      ...workflow,
      createdAt: new Date().toISOString(),
      expiresAt: new Date(Date.now() + 60 * 60 * 1000).toISOString() // 1 hour expiry
    });

    // Clean up expired workflows
    cleanExpiredWorkflows();

    return NextResponse.json({
      success: true,
      workflowId,
      redirectUrl: `/dashboard/automation/agent?workflowId=${workflowId}&mode=configure`
    });

  } catch (error) {
    console.error('Error in load-workflow:', error);
    return NextResponse.json(
      { error: 'Failed to process workflow data' },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const workflowId = searchParams.get('workflowId');

    if (!workflowId) {
      return NextResponse.json(
        { error: 'Workflow ID is required' },
        { status: 400 }
      );
    }

    const workflowData = workflowStore.get(workflowId);

    if (!workflowData) {
      return NextResponse.json(
        { error: 'Workflow not found or expired' },
        { status: 404 }
      );
    }

    // Check if expired
    if (new Date() > new Date(workflowData.expiresAt)) {
      workflowStore.delete(workflowId);
      return NextResponse.json(
        { error: 'Workflow session expired' },
        { status: 410 }
      );
    }

    return NextResponse.json({
      success: true,
      workflow: workflowData
    });

  } catch (error) {
    console.error('Error retrieving workflow:', error);
    return NextResponse.json(
      { error: 'Failed to retrieve workflow data' },
      { status: 500 }
    );
  }
}

function cleanExpiredWorkflows() {
  const now = new Date();
  for (const [id, data] of workflowStore.entries()) {
    if (now > new Date(data.expiresAt)) {
      workflowStore.delete(id);
    }
  }
}
