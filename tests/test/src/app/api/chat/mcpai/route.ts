import { NextRequest, NextResponse } from 'next/server';

interface ChatRequest {
  message: string;
  agentId: string;
  agentConfig: {
    name: string;
    role: string;
    mode?: string;
    personality?: any;
    llm_config?: any;
  };
  session_id?: string;
  email_content?: string;
}

export async function POST(request: NextRequest) {
  let body: ChatRequest | null = null;
  
  console.log('🎯 API ROUTE DEBUG: POST request received at /api/chat/mcpai');
  
  try {
    body = await request.json();
    
    console.log('🎯 API ROUTE DEBUG: Request body parsed:', {
      hasMessage: !!body?.message,
      hasAgentId: !!body?.agentId,
      message: body?.message?.substring(0, 100),
      agentId: body?.agentId
    });
    
    if (!body) {
      return NextResponse.json(
        { error: 'Invalid request body' },
        { status: 400 }
      );
    }

    const { message, agentId, agentConfig, session_id } = body;

    if (!message || !agentId) {
      return NextResponse.json(
        { error: 'Message and agent ID are required' },
        { status: 400 }
      );
    }

    // Get authentication from cookies
    const cookieStore = request.cookies;
    const sessionToken = cookieStore.get('session_token')?.value;

    // Prepare headers for backend request
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

    // Call Python MCPAI backend with authentication using agent-specific endpoint
    const backendUrl = agentId 
      ? `http://127.0.0.1:8002/api/agents/${agentId}/chat`
      : 'http://127.0.0.1:8002/api/chat/mcpai';  // fallback to generic endpoint
    
    console.log('🚀 Calling backend at:', backendUrl);
    console.log('🚀 With agent ID:', agentId);
    console.log('🚀 With headers:', headers);
    console.log('🚀 With body:', JSON.stringify({
      message: message,
      agentId: agentId,
      agentConfig: agentConfig,
      session_id: session_id || `agent_${agentId}_${Date.now()}`,
      email_content: body.email_content
    }));
    
    const mcpResponse = await fetch(backendUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        message: message,
        agentId: agentId,
        agentConfig: agentConfig,
        session_id: session_id || `agent_${agentId}_${Date.now()}`,
        // Pass through email content for SEND_APPROVED_EMAIL requests
        email_content: body.email_content
      })
    });

    if (!mcpResponse.ok) {
      console.log('🚨 MCPAI API ERROR:', mcpResponse.status, mcpResponse.statusText);
      throw new Error(`MCPAI API error: ${mcpResponse.status}`);
    }

    const mcpResult = await mcpResponse.json() as any;

    // CRITICAL DEBUG: Log everything about the backend response
    console.log('🚨🚨🚨 CRITICAL DEBUG - RAW BACKEND RESPONSE:');
    console.log('🚨 Full Response:', JSON.stringify(mcpResult, null, 2));
    console.log('🚨 Status:', mcpResult.status);
    console.log('🚨 Action Required:', mcpResult.action_required);
    console.log('🚨 Email Content:', mcpResult.email_content);
    console.log('🚨 Recipient:', mcpResult.recipient);
    console.log('🚨 Email Subject:', mcpResult.email_subject);
    console.log('🚨 Message:', mcpResult.message);
    console.log('🚨 Response Keys:', Object.keys(mcpResult));
    console.log('🚨🚨🚨 END CRITICAL DEBUG');
    
    console.log('🔧 API DEBUG: Full mcpResult:', {
      status: mcpResult.status,
      action_required: mcpResult.action_required,
      hasWorkflowJson: !!mcpResult.workflow_json,
      hasWorkflowPreview: !!(mcpResult as any).workflow_preview,
      hasEmailContent: !!mcpResult.email_content,
      hasEmailPreview: !!mcpResult.email_preview,
      recipient: mcpResult.recipient,
      keys: Object.keys(mcpResult)
    });

    // Debug email preview condition specifically
    console.log('📧 EMAIL PREVIEW CHECK:', {
      status: mcpResult.status,
      statusIsPreviewReady: mcpResult.status === 'preview_ready',
      actionRequired: mcpResult.action_required,
      actionIsApproveEmail: mcpResult.action_required === 'approve_email',
      bothConditions: mcpResult.status === 'preview_ready' && mcpResult.action_required === 'approve_email',
      hasEmailContent: !!mcpResult.email_content,
      hasRecipient: !!mcpResult.recipient
    });
    
    // Check all conditions
    console.log('🔧 API DEBUG: Condition checks:', {
      isWorkflowPreview: mcpResult.status === 'workflow_preview',
      hasWorkflowJson: !!mcpResult.workflow_json,
      bothConditions: mcpResult.status === 'workflow_preview' && mcpResult.workflow_json
    });
    
    // Handle AI service selection
    if (mcpResult.status === 'ai_service_selection' && mcpResult.ai_service_options) {
      return NextResponse.json({
        success: true,
        status: 'ai_service_selection',
        message: mcpResult.message,
        ai_service_options: mcpResult.ai_service_options,
        action_required: 'select_ai_service',
        agentId: agentId,
        timestamp: new Date().toISOString()
      });
    }
    
    // Handle workflow preview
    if (mcpResult.status === 'workflow_preview' && mcpResult.workflow_json) {
      // Debug: Add debug info directly to the response
      const workflowPreviewExists = !!(mcpResult as any).workflow_preview;
      
      const response = {
        success: true,
        status: 'workflow_preview',
        message: mcpResult.message,
        workflow_preview: (mcpResult as any).workflow_preview,
        workflow_json: mcpResult.workflow_json,
        workflow_id: (mcpResult as any).workflow_id,
        ai_service_used: (mcpResult as any).ai_service_used,
        estimated_credits: (mcpResult as any).estimated_credits,
        preview_details: (mcpResult as any).preview_details,
        action_required: 'confirm_workflow',
        agentId: agentId,
        timestamp: new Date().toISOString(),
        // Debug fields
        debug_workflow_preview_exists: workflowPreviewExists,
        debug_workflow_preview_type: typeof (mcpResult as any).workflow_preview,
        debug_mcpResult_keys: Object.keys(mcpResult),
        debug_mcpResult_status: mcpResult.status,
        debug_has_workflow_json: !!mcpResult.workflow_json
      };
      
      return NextResponse.json(response);
    }
    
    // Handle email preview - prioritize status check, then fallback conditions
    if (mcpResult.status === 'preview_ready' ||
        (mcpResult.status === 'preview_ready' && mcpResult.action_required === 'approve_email') ||
        (mcpResult.status === 'preview_ready' && mcpResult.email_content && mcpResult.recipient) ||
        (mcpResult.email_content && mcpResult.recipient && mcpResult.message && mcpResult.message.includes('Email Preview')) ||
        (mcpResult.message && mcpResult.message.includes('📧 Email Preview Ready!'))) {
      
      console.log('📧 API DEBUG: Email preview detected!', {
        hasEmailContent: !!mcpResult.email_content,
        hasRecipient: !!mcpResult.recipient,
        hasSubject: !!mcpResult.email_subject,
        status: mcpResult.status,
        action_required: mcpResult.action_required,
        message: mcpResult.message
      });

      // Extract email from message if not in dedicated field
      let recipient = mcpResult.recipient;
      if (!recipient && mcpResult.message) {
        const emailMatch = mcpResult.message.match(/(?:to|sending to)\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/);
        if (emailMatch) {
          recipient = emailMatch[1];
        }
      }

      // Generate realistic email content if not provided by backend
      let emailContent = mcpResult.email_content;
      let emailSubject = mcpResult.email_subject;
      
      if (!emailContent || !emailSubject) {
        // Generate content based on the specific request message
        const isWelcome = message.toLowerCase().includes('welcome');
        const isPremium = message.toLowerCase().includes('premium');
        const isSales = message.toLowerCase().includes('sales') || message.toLowerCase().includes('pitch') || message.toLowerCase().includes('ecommerce') || message.toLowerCase().includes('e-commerce') || message.toLowerCase().includes('selling');
        const isMarketing = message.toLowerCase().includes('marketing') || message.toLowerCase().includes('promotion');
        
        if (!emailSubject) {
          if (isSales) {
            emailSubject = 'Exclusive Deals on Premium Products - Limited Time Offer!';
          } else if (isWelcome) {
            emailSubject = isPremium ? 'Welcome to Our Premium Service!' : 'Welcome to Our Service!';
          } else if (isMarketing) {
            emailSubject = 'Special Offer Just for You!';
          } else {
            emailSubject = 'AI-Generated Email';
          }
        }
        
        if (!emailContent) {
          if (isSales) {
            emailContent = `Dear Valued Customer,

🎉 Exciting news! We're thrilled to present you with our latest collection of premium products at unbeatable prices.

🛍️ **What's New This Month:**
• Premium Electronics - Up to 40% off
• Fashion & Accessories - Buy 2 Get 1 Free  
• Home & Garden Essentials - Starting at $19.99
• Beauty & Health Products - Exclusive bundles available

💎 **Why Choose Us:**
✓ Premium quality guaranteed
✓ Fast, secure shipping
✓ 30-day money-back guarantee
✓ 24/7 customer support

🚀 **Limited Time Offer:** Use code SAVE25 for an additional 25% off your first order!

Don't miss out on these incredible deals. Our inventory is limited and these prices won't last long.

[Shop Now] [View Catalog] [Customer Reviews]

Questions? Reply to this email or contact our support team at support@company.com

Best regards,
The Sales Team

P.S. Follow us on social media for flash sales and exclusive previews!`;
          } else if (isWelcome) {
            emailContent = `Dear Valued Customer,

Thank you for joining us! We're excited to have you as part of our community.

${isPremium ? 'As a premium member, you now have access to exclusive features and priority support.' : 'We look forward to providing you with excellent service.'}

If you have any questions, please don't hesitate to reach out to our support team.

Best regards,
The Team`;
          } else if (isMarketing) {
            emailContent = `Hello!

We have some exciting offers tailored just for you. Check out our latest promotions and discover amazing deals on your favorite products.

Best regards,
Marketing Team`;
          } else {
            emailContent = `Hello,

This is an AI-generated email based on your request. The content has been tailored to provide relevant information for your recipient.

Please review the content above and make any necessary adjustments before sending.

Best regards,
AI Assistant`;
          }
        }
      }

      // Create email preview response with available data or generated content
      return NextResponse.json({
        success: true,
        status: 'preview_ready',
        action_required: 'approve_email',
        message: mcpResult.message || '📧 Email Preview Ready!',
        email_content: emailContent,
        email_subject: emailSubject,
        recipient: recipient || 'unknown@example.com',
        workflow_id: mcpResult.workflow_id,
        workflowPreviewContent: mcpResult.workflowPreviewContent,
        agentId: agentId,
        timestamp: new Date().toISOString(),
        // Debug info
        _debug_backend_status: mcpResult.status,
        _debug_backend_action: mcpResult.action_required,
        _debug_extracted_email: recipient,
        _debug_content_generated: !mcpResult.email_content
      });
    }
    
    // Handle workflow confirmation
    if ((mcpResult.status === 'review_needed' || mcpResult.action_required === 'confirm_workflow') && mcpResult.workflow_json) {
      return NextResponse.json({
        success: true,
        status: 'review_needed',
        message: mcpResult.message,
        workflow_json: mcpResult.workflow_json,
        action_required: 'confirm_workflow',
        agentId: agentId,
        timestamp: new Date().toISOString()
      });
    }
    
    // Handle AI content confirmation requests
    if (mcpResult.success === false && mcpResult.needs_confirmation) {
      return NextResponse.json({
        success: true,
        response: mcpResult.confirmation_prompt || 'Would you like to use AI-generated content?',
        agentId: agentId,
        timestamp: new Date().toISOString(),
        needs_confirmation: true,
        action_required: mcpResult.action_required || 'ai_content_confirmation',
        confirmation_prompt: mcpResult.confirmation_prompt
      });
    }
    
    return NextResponse.json({
      success: mcpResult.success || true,
      response: mcpResult.response || mcpResult.message || 'I understand your request. Let me help you with that.',
      message: mcpResult.message || mcpResult.response || 'I understand your request. Let me help you with that.',
      status: mcpResult.status || 'completed',
      agentId: agentId,
      timestamp: new Date().toISOString(),
      hasWorkflowJson: mcpResult.hasWorkflowJson || false,
      hasWorkflowPreview: mcpResult.hasWorkflowPreview || false,
      workflowPreviewContent: mcpResult.workflowPreviewContent || undefined,
      done: mcpResult.done !== undefined ? mcpResult.done : true,
      action_required: mcpResult.action_required || null,
      workflow_id: mcpResult.workflow_id || null,
      email_sent: mcpResult.email_sent || false,
      execution_status: mcpResult.execution_status || null,
      // Legacy fields for backward compatibility
      workflow_generated: mcpResult.hasWorkflowJson || mcpResult.workflow_generated || false,
      n8n_workflow: mcpResult.workflow || mcpResult.n8n_workflow || null
    });

  } catch (error) {
    console.error('MCPAI Chat API error:', error);
    
    // NO FALLBACK - Always return error to force backend connection
    return NextResponse.json({
      success: false,
      error: "Backend connection failed. Please ensure the backend is running.",
      message: "Could not connect to AI backend service.",
      agentId: body?.agentId || 'unknown',
      timestamp: new Date().toISOString(),
      fallback: false,
      backend_error: true
    }, { status: 500 });
  }
}
