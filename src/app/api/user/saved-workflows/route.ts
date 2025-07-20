// app/api/user/saved-workflows/route.ts
// API endpoint for managing user saved workflows

import { NextRequest, NextResponse } from 'next/server';
import { validateSession } from '../../../../../lib/structured-auth.js';
import {
  saveUserWorkflow,
  getUserSavedWorkflows,
  deleteSavedWorkflow,
  getSavedWorkflow
} from '../../../../../lib/structured-db.js';

// GET - Retrieve all saved workflows for the user
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

    const savedWorkflows = await getUserSavedWorkflows(parseInt(user.userid));

    return NextResponse.json({
      success: true,
      workflows: savedWorkflows,
      count: savedWorkflows.length
    });

  } catch (error: any) {
    console.error('[SAVED-WORKFLOWS] Error retrieving saved workflows:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to retrieve saved workflows' },
      { status: 500 }
    );
  }
}

// POST - Save a new workflow
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

    const { workflow_json, workflow_name, repetition_note } = await req.json() as {
      workflow_json: any;
      workflow_name: string;
      repetition_note?: string;
    };

    if (!workflow_json || !workflow_name) {
      return NextResponse.json(
        { success: false, error: 'Workflow JSON and name are required' },
        { status: 400 }
      );
    }

    const savedWorkflow = await saveUserWorkflow({
      user_id: parseInt(user.userid),
      workflow_json,
      workflow_name,
      repetition_note
    });

    return NextResponse.json({
      success: true,
      workflow: savedWorkflow,
      message: 'Workflow saved successfully'
    });

  } catch (error: any) {
    console.error('[SAVED-WORKFLOWS] Error saving workflow:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to save workflow' },
      { status: 500 }
    );
  }
}

// DELETE - Delete a saved workflow
export async function DELETE(req: NextRequest) {
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
    const workflowId = searchParams.get('id');

    if (!workflowId) {
      return NextResponse.json(
        { success: false, error: 'Workflow ID is required' },
        { status: 400 }
      );
    }

    const deleted = await deleteSavedWorkflow(parseInt(workflowId), parseInt(user.userid));

    if (deleted) {
      return NextResponse.json({
        success: true,
        message: 'Workflow deleted successfully'
      });
    } else {
      return NextResponse.json(
        { success: false, error: 'Workflow not found or access denied' },
        { status: 404 }
      );
    }

  } catch (error: any) {
    console.error('[SAVED-WORKFLOWS] Error deleting workflow:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to delete workflow' },
      { status: 500 }
    );
  }
}
