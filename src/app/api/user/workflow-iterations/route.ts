// app/api/user/workflow-iterations/route.ts
// API endpoint for managing AI workflow iteration versions

import { NextRequest, NextResponse } from 'next/server';
import { validateSession } from '../../../../../lib/structured-auth.js';
import { 
  getAIIterationVersions,
  markIterationAsFinal,
  getAIWorkflowRequest
} from '../../../../../lib/structured-db.js';

// GET - Retrieve all iteration versions for a specific workflow request
export async function GET(req: NextRequest) {
  try {
    const sessionToken = req.cookies.get('session_token')?.value;
    if (!sessionToken) {
      return NextResponse.json(
        { success: false, error: 'Authentication required' },
        { status: 401 }
      );
    }

    const user = await validateSession(sessionToken);
    if (!user) {
      return NextResponse.json(
        { success: false, error: 'Invalid session' },
        { status: 401 }
      );
    }

    const { searchParams } = new URL(req.url);
    const requestId = searchParams.get('requestId');

    if (!requestId) {
      return NextResponse.json(
        { success: false, error: 'Request ID is required' },
        { status: 400 }
      );
    }

    // Verify the request belongs to the user
    const workflowRequest = await getAIWorkflowRequest(requestId);
    if (!workflowRequest || workflowRequest.userid !== user.userid) {
      return NextResponse.json(
        { success: false, error: 'Workflow request not found or access denied' },
        { status: 404 }
      );
    }

    const iterations = await getAIIterationVersions(parseInt(workflowRequest.requestid));

    return NextResponse.json({
      success: true,
      iterations,
      count: iterations.length,
      requestInfo: {
        id: workflowRequest.requestid,
        request_id: workflowRequest.requestid,
        workflow_name: workflowRequest.input_prompt, // Using input_prompt as workflow name
        status: workflowRequest.status
      }
    });

  } catch (error: any) {
    console.error('[WORKFLOW-ITERATIONS] Error retrieving iterations:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to retrieve workflow iterations' },
      { status: 500 }
    );
  }
}

// PUT - Mark a specific iteration as final
export async function PUT(req: NextRequest) {
  try {
    const sessionToken = req.cookies.get('session_token')?.value;
    if (!sessionToken) {
      return NextResponse.json(
        { success: false, error: 'Authentication required' },
        { status: 401 }
      );
    }

    const user = await validateSession(sessionToken);
    if (!user) {
      return NextResponse.json(
        { success: false, error: 'Invalid session' },
        { status: 401 }
      );
    }

    const { requestId, versionNumber } = await req.json() as {
      requestId: string;
      versionNumber: number;
    };

    if (!requestId || versionNumber === undefined) {
      return NextResponse.json(
        { success: false, error: 'Request ID and version number are required' },
        { status: 400 }
      );
    }

    // Verify the request belongs to the user
    const workflowRequest = await getAIWorkflowRequest(requestId);
    if (!workflowRequest || workflowRequest.userid !== user.userid) {
      return NextResponse.json(
        { success: false, error: 'Workflow request not found or access denied' },
        { status: 404 }
      );
    }

    await markIterationAsFinal(parseInt(workflowRequest.requestid), versionNumber);

    return NextResponse.json({
      success: true,
      message: `Version ${versionNumber} marked as final for request ${requestId}`
    });

  } catch (error: any) {
    console.error('[WORKFLOW-ITERATIONS] Error marking iteration as final:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to update iteration status' },
      { status: 500 }
    );
  }
}
