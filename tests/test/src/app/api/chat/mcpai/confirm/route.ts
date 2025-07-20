import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json() as {
      agentId: string;
      confirmed: boolean;
      original_message?: string;
      workflow_json?: any;
      workflow_id?: string;
      action_type?: string;
      recipient?: string;
      email_content?: string;
      email_subject?: string;
    };
    const { 
      agentId, 
      confirmed, 
      original_message, 
      workflow_json, 
      workflow_id,
      action_type,
      recipient,
      email_content,
      email_subject
    } = body;
    
    console.log('🔍 CONFIRMATION API DEBUG: Full body:', JSON.stringify(body, null, 2));
    console.log('🔍 CONFIRMATION API DEBUG: Action type:', action_type);
    console.log('🔍 CONFIRMATION API DEBUG: Email confirmation:', {
      workflow_id,
      recipient,
      has_content: !!email_content,
      subject: email_subject
    });
    
    if (!agentId) {
      return NextResponse.json({
        success: false,
        error: 'Agent ID is required'
      }, { status: 400 });
    }

    // Get authentication from cookies
    const cookieStore = request.cookies;
    const sessionToken = cookieStore.get('session_token')?.value;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Forward the session cookie to the backend
    if (sessionToken) {
      headers['Cookie'] = `session_token=${sessionToken}`;
    } else {
      return NextResponse.json(
        { error: 'Authentication required. Please log in.' },
        { status: 401 }
      );
    }
    
    // Handle email confirmation specifically
    if (action_type === 'approve_email' && confirmed) {
      console.log('📧 Processing email approval...');
      
      // Call the email send confirmation endpoint
      const emailResponse = await fetch('http://localhost:8002/api/chat/mcpai', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          message: `SEND_APPROVED_EMAIL:${workflow_id}:${recipient}:${email_subject}`,
          workflow_id: workflow_id,
          recipient: recipient,
          email_content: email_content,
          email_subject: email_subject,
          action_type: 'send_approved_email'
        })
      });

      if (!emailResponse.ok) {
        const errorText = await emailResponse.text();
        console.error('Email send failed:', errorText);
        return NextResponse.json({
          success: false,
          error: `Email send failed: ${errorText}`
        }, { status: emailResponse.status });
      }

      const emailResult = await emailResponse.json() as {
        success?: boolean;
        message?: string;
        email_sent?: boolean;
        status?: string;
      };
      console.log('📧 Email send result:', emailResult);
      
      return NextResponse.json({
        success: true,
        message: emailResult.message || 'Email sent successfully',
        email_sent: emailResult.email_sent || true,
        automation_type: 'email_sent',
        status: 'completed'
      });
    }
    
    // Handle email preview rejection
    if (action_type === 'approve_email' && !confirmed) {
      return NextResponse.json({
        success: true,
        message: 'Email preview cancelled. You can request a new email or modify your request.',
        email_sent: false,
        status: 'cancelled'
      });
    }
    
    // Forward other confirmations to the original workflow endpoint
    const mcpResponse = await fetch('http://localhost:8002/api/workflow/confirm', {
      method: 'POST',
      headers,
      body: JSON.stringify({
        workflow_json: workflow_json,
        confirmed: confirmed,
        workflow_id: workflow_id,
        action_type: action_type
      })
    });
    
    if (!mcpResponse.ok) {
      const errorText = await mcpResponse.text();
      console.error('Backend confirmation failed:', errorText);
      return NextResponse.json({
        success: false,
        error: `Backend confirmation failed: ${errorText}`
      }, { status: mcpResponse.status });
    }
    
    const mcpResult = await mcpResponse.json() as {
      success?: boolean;
      message?: string;
      execution_details?: any;
    };
    
    return NextResponse.json({
      success: mcpResult.success || true,
      response: mcpResult.message || 'Workflow confirmed and executed successfully.',
      agentId: agentId,
      timestamp: new Date().toISOString(),
      execution_details: mcpResult.execution_details || null
    });
    
  } catch (error) {
    console.error('Confirmation API error:', error);
    return NextResponse.json({
      success: false,
      error: 'Failed to process confirmation'
    }, { status: 500 });
  }
}
