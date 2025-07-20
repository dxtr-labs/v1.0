// src/app/api/user/logs/route.ts
// User-specific workflow logs API

import { NextRequest, NextResponse } from "next/server";
import { createUserLog, getUserLogs, getUserWorkflowLogs, logUserWorkflowExecution } from "../../../../../lib/user-db.js";

// Get user workflow logs
export async function GET(req: NextRequest) {
  try {
    // TODO: Get user ID from authentication session
    const userId = parseInt(req.nextUrl.searchParams.get('userId') || '1');
    const requestId = req.nextUrl.searchParams.get('requestId') || undefined;
    const limit = parseInt(req.nextUrl.searchParams.get('limit') || '100');

    const logs = await getUserWorkflowLogs(userId, requestId, limit);

    return NextResponse.json({
      success: true,
      data: {
        logs,
        count: logs.length,
        userId,
        requestId
      }
    });
  } catch (error: any) {
    console.error('Error fetching user logs:', error);
    return NextResponse.json(
      { success: false, error: "Failed to fetch logs" },
      { status: 500 }
    );
  }
}

// Create new workflow log entry
export async function POST(req: NextRequest) {
  try {
    const body = await req.json() as {
      userId: number;
      requestId: string;
      status: 'started' | 'running' | 'completed' | 'failed' | 'cancelled' | 'pending';
      message?: string;
      stepName?: string;
      workflowId?: number;
      aiWorkflowId?: number;
      executionId?: string;
      inputData?: any;
      outputData?: any;
      errorDetails?: string;
      executionTimeMs?: number;
    };

    const { 
      userId, requestId, status, message, stepName, workflowId, 
      aiWorkflowId, executionId, inputData, outputData, errorDetails, executionTimeMs 
    } = body;

    if (!userId || !requestId || !status) {
      return NextResponse.json(
        { success: false, error: "User ID, request ID, and status are required" },
        { status: 400 }
      );
    }

    const logData = {
      request_id: requestId,
      status,
      message,
      step_name: stepName,
      workflow_id: workflowId,
      ai_workflow_id: aiWorkflowId,
      execution_id: executionId,
      input_data: inputData,
      output_data: outputData,
      error_details: errorDetails,
      execution_time_ms: executionTimeMs
    };

    const log = await logUserWorkflowExecution(userId, logData);

    return NextResponse.json({
      success: true,
      data: {
        log,
        message: "Log entry created successfully"
      }
    }, { status: 201 });
  } catch (error: any) {
    console.error('Error creating user log:', error);
    
    if (error.message.includes('Database not available')) {
      return NextResponse.json(
        { success: false, error: "Service temporarily unavailable. Please try again later." },
        { status: 503 }
      );
    }

    return NextResponse.json(
      { success: false, error: "Failed to create log entry" },
      { status: 500 }
    );
  }
}
