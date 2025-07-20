// app/api/user/n8n-logs/route.ts
// API endpoint for managing N8N workflow execution logs

import { NextRequest, NextResponse } from 'next/server';
import { validateSession } from '../../../../../lib/structured-auth.js';
import {
  getN8NWorkflowLogs,
  createN8NWorkflowLog,
  updateN8NWorkflowLog
} from '../../../../../lib/structured-db.js';

// GET - Retrieve N8N workflow logs for the user
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

    // Get logs, optionally filtered by request ID
    const logs = await getN8NWorkflowLogs(
      parseInt(user.userid), 
      requestId ? parseInt(requestId) : undefined
    );

    return NextResponse.json({
      success: true,
      logs,
      count: logs.length,
      filter: requestId ? { requestId } : null
    });

  } catch (error: any) {
    console.error('[N8N-LOGS] Error retrieving N8N logs:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to retrieve N8N logs' },
      { status: 500 }
    );
  }
}

// POST - Create a new N8N workflow log entry
export async function POST(req: NextRequest) {
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

    const { 
      request_id, 
      workflow_json, 
      nodes_used, 
      execution_status, 
      output_log, 
      repetition_count 
    } = await req.json() as {
      request_id: number;
      workflow_json?: any;
      nodes_used?: string[];
      execution_status?: 'pending' | 'success' | 'error';
      output_log?: string;
      repetition_count?: number;
    };

    if (!request_id) {
      return NextResponse.json(
        { success: false, error: 'Request ID is required' },
        { status: 400 }
      );
    }

    const log = await createN8NWorkflowLog({
      user_id: parseInt(user.userid),
      request_id,
      workflow_json,
      nodes_used,
      execution_status,
      output_log,
      repetition_count
    });

    return NextResponse.json({
      success: true,
      log,
      message: 'N8N workflow log created successfully'
    });

  } catch (error: any) {
    console.error('[N8N-LOGS] Error creating N8N log:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to create N8N log' },
      { status: 500 }
    );
  }
}

// PUT - Update an existing N8N workflow log
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

    const { 
      log_id, 
      execution_status, 
      output_log, 
      repetition_count 
    } = await req.json() as {
      log_id: number;
      execution_status?: 'pending' | 'success' | 'error';
      output_log?: string;
      repetition_count?: number;
    };

    if (!log_id) {
      return NextResponse.json(
        { success: false, error: 'Log ID is required' },
        { status: 400 }
      );
    }

    const updatedLog = await updateN8NWorkflowLog(log_id, {
      execution_status,
      output_log,
      repetition_count
    });

    if (updatedLog) {
      return NextResponse.json({
        success: true,
        log: updatedLog,
        message: 'N8N workflow log updated successfully'
      });
    } else {
      return NextResponse.json(
        { success: false, error: 'Log not found or access denied' },
        { status: 404 }
      );
    }

  } catch (error: any) {
    console.error('[N8N-LOGS] Error updating N8N log:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to update N8N log' },
      { status: 500 }
    );
  }
}
