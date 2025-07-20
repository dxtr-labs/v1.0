// src/app/api/user/workflows/route.ts
// User-specific workflow management API

import { NextRequest, NextResponse } from "next/server";
import { createAIWorkflow, getUserAIWorkflows } from "../../../../../lib/user-db.js";

// Get user workflows
export async function GET(req: NextRequest) {
  try {
    // TODO: Get user ID from authentication session
    const userId = parseInt(req.nextUrl.searchParams.get('userId') || '1');
    const limit = parseInt(req.nextUrl.searchParams.get('limit') || '50');

    const workflows = await getUserAIWorkflows(userId, limit);

    return NextResponse.json({
      success: true,
      data: {
        workflows,
        count: workflows.length
      }
    });
  } catch (error: any) {
    console.error('Error fetching user workflows:', error);
    return NextResponse.json(
      { success: false, error: "Failed to fetch workflows" },
      { status: 500 }
    );
  }
}

// Create new AI workflow for user
export async function POST(req: NextRequest) {
  try {
    const body = await req.json() as {
      userId: number;
      workflowName?: string;
      workflowDescription?: string;
      aiPrompt: string;
    };
    
    const { userId, workflowName, workflowDescription, aiPrompt } = body;

    if (!userId || !aiPrompt) {
      return NextResponse.json(
        { success: false, error: "User ID and AI prompt are required" },
        { status: 400 }
      );
    }

    // Generate unique request ID
    const requestId = `req_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

    const workflowData: Partial<AIWorkflow> = {
      request_id: requestId,
      workflow_name: workflowName,
      workflow_description: workflowDescription,
      ai_prompt: aiPrompt,
      workflow_status: 'pending'
    };

    const workflow = await createAIWorkflow(userId, workflowData);

    return NextResponse.json({
      success: true,
      data: {
        workflow,
        requestId: workflow.request_id
      }
    }, { status: 201 });
  } catch (error: any) {
    console.error('Error creating user workflow:', error);
    
    if (error.message.includes('Database not available')) {
      return NextResponse.json(
        { success: false, error: "Service temporarily unavailable. Please try again later." },
        { status: 503 }
      );
    }

    return NextResponse.json(
      { success: false, error: "Failed to create workflow" },
      { status: 500 }
    );
  }
}
