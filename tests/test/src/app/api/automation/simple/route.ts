// src/app/api/automation/simple/route.ts
// Simple automation API endpoint - DEPRECATED
// Redirects to new workflow engine

import { NextRequest, NextResponse } from 'next/server';
import { validateSession } from '../../../../../lib/structured-auth.js';

export async function POST(req: NextRequest) {
  try {
    console.log('🚀 [SIMPLE-API] Starting automation request (redirecting to new workflow engine)...');

    // Get session token from cookies
    const sessionToken = req.cookies.get('session_token')?.value;
    
    if (!sessionToken) {
      console.log('❌ [SIMPLE-API] No session token found');
      return NextResponse.json(
        { success: false, error: "Authentication required" },
        { status: 401 }
      );
    }

    // Validate session and get user
    const user = await validateSession(sessionToken);
    if (!user) {
      console.log('❌ [SIMPLE-API] Session validation failed');
      return NextResponse.json(
        { success: false, error: "Invalid session" },
        { status: 401 }
      );
    }

    console.log('✅ [SIMPLE-API] User authenticated:', user.email);

    // Get request body
    const body = await req.json() as { 
      prompt: string; 
      type?: string;
      conversationId?: string;
      previousContext?: any;
      parameters?: Record<string, any>;
    };
    const { prompt } = body;

    if (!prompt || typeof prompt !== 'string') {
      return NextResponse.json(
        { success: false, error: "Prompt is required" },
        { status: 400 }
      );
    }

    console.log('📝 [SIMPLE-API] User prompt:', prompt);

    // Redirect to new workflow generation API
    const workflowResponse = await fetch(`${req.nextUrl.origin}/api/generate-workflow`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': req.headers.get('cookie') || ''
      },
      body: JSON.stringify({ prompt })
    });

    if (!workflowResponse.ok) {
      const errorData: any = await workflowResponse.json();
      throw new Error(errorData.error || 'Workflow generation failed');
    }

    const workflow: any = await workflowResponse.json();

    // Return result in the format expected by frontend
    return NextResponse.json({
      success: true,
      message: `Generated workflow with ${workflow.nodes?.length || 0} steps`,
      workflow: workflow,
      deprecated: true,
      redirected: true,
      newEndpoint: '/api/generate-workflow',
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ [SIMPLE-API] Error:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json(
      { 
        success: false, 
        error: "Internal server error",
        message: errorMessage,
        failureReason: `API error: ${errorMessage}`,
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}
