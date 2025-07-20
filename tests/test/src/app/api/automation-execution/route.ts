// src/app/api/automation-execution/route.ts
// Compatibility endpoint that redirects to orchestrate-workflow

import { NextRequest, NextResponse } from 'next/server';
import { validateSession } from '../../../../lib/structured-auth.js';

// Helper function to handle user messages and extract automation intent
async function handleUserMessage(
  request: NextRequest,
  userMessage: string, 
  requestId?: string,
  providedParameters?: Record<string, any>
): Promise<NextResponse> {
  // Parse user message for automation intent
  const lowerMessage = userMessage.toLowerCase();
  
  // Detect email automation intent
  if (lowerMessage.includes('email') || lowerMessage.includes('send') || lowerMessage.includes('mail')) {
    const emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
    const emailMatches = userMessage.match(emailRegex);
    
    const extractedParams = {
      recipient: emailMatches?.[0] || providedParameters?.recipient,
      content: extractContentFromMessage(userMessage) || providedParameters?.content,
      subject: extractSubjectFromMessage(userMessage) || providedParameters?.subject,
      ...providedParameters
    };
    
    // Check for missing required parameters before proceeding
    let missingParameters: Array<{name: string, description: string, required: boolean, type: string}> = [];
    
    if (!extractedParams.recipient) {
      missingParameters.push({
        name: 'recipient',
        description: 'Email address to send to (e.g., slakshanand1105@gmail.com)',
        required: true,
        type: 'email'
      });
    }
    
    if (!extractedParams.content) {
      missingParameters.push({
        name: 'content',
        description: 'Email message content (e.g., "Good morning! Hope you have a great day!")',
        required: true,
        type: 'text'
      });
    }
    
    // Optional parameters
    if (!extractedParams.subject) {
      missingParameters.push({
        name: 'subject',
        description: 'Email subject line (e.g., "Good Morning!")',
        required: false,
        type: 'text'
      });
    }
    
    // If we have missing required parameters, ask for them directly
    const requiredMissing = missingParameters.filter(p => p.required);
    if (requiredMissing.length > 0) {
      return NextResponse.json({
        success: false,
        needsParameters: true,
        message: "To send the email, I need:",
        missingParameters,
        workflowType: 'email',
        requestId: requestId || `email_${Date.now()}`,
        helpText: generateHelpText(missingParameters, 'email automation')
      });
    }
    
    // Create orchestration request for email automation
    const orchestrationRequest = {
      message: 'send email automation',
      requestId: requestId || `msg_${Date.now()}`,
      parameters: extractedParams
    };
    
    // Forward to orchestrate-workflow endpoint
    return await forwardToOrchestration(request, orchestrationRequest);
  }
  
  // Detect schedule automation intent
  if (lowerMessage.includes('daily') || lowerMessage.includes('schedule') || lowerMessage.includes('every')) {
    const scheduleParams = {
      schedule: extractScheduleFromMessage(userMessage) || providedParameters?.schedule,
      ...providedParameters
    };
    
    const orchestrationRequest = {
      message: userMessage,
      requestId: requestId || `msg_${Date.now()}`,
      parameters: scheduleParams
    };
    
    return await forwardToOrchestration(request, orchestrationRequest);
  }
  
  // Generic automation request
  const orchestrationRequest = {
    message: userMessage,
    requestId: requestId || `msg_${Date.now()}`,
    parameters: providedParameters || {}
  };
  
  return await forwardToOrchestration(request, orchestrationRequest);
}

// Helper function to extract email content from natural language
function extractContentFromMessage(message: string): string | null {
  // Look for content patterns like "saying X" or "with message X"
  const contentPatterns = [
    /saying\s+"([^"]+)"/i,
    /with message\s+"([^"]+)"/i,
    /body\s*:\s*"([^"]+)"/i,
    /content\s*:\s*"([^"]+)"/i
  ];
  
  for (const pattern of contentPatterns) {
    const match = message.match(pattern);
    if (match) return match[1];
  }
  
  // Try to extract content after email address and common keywords
  const emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
  const cleanMessage = message.replace(emailRegex, '').trim();
  
  // Remove common email keywords to find the actual content
  const keywords = ['send', 'email', 'to', 'mail', 'message'];
  let potentialContent = cleanMessage;
  
  for (const keyword of keywords) {
    potentialContent = potentialContent.replace(new RegExp(`\\b${keyword}\\b`, 'gi'), '').trim();
  }
  
  // If we have meaningful content left, use it
  if (potentialContent.length > 2 && potentialContent !== message.trim()) {
    return potentialContent;
  }
  
  return null;
}

// Helper function to extract email subject from natural language
function extractSubjectFromMessage(message: string): string | null {
  const subjectPatterns = [
    /subject\s*:\s*"([^"]+)"/i,
    /with subject\s+"([^"]+)"/i,
    /titled\s+"([^"]+)"/i
  ];
  
  for (const pattern of subjectPatterns) {
    const match = message.match(pattern);
    if (match) return match[1];
  }
  
  return null;
}

// Helper function to extract schedule information from natural language
function extractScheduleFromMessage(message: string): string | null {
  const schedulePatterns = [
    /every day at (\d{1,2}:\d{2}\s*(?:AM|PM)?)/i,
    /daily at (\d{1,2}:\d{2}\s*(?:AM|PM)?)/i,
    /at (\d{1,2}:\d{2}\s*(?:AM|PM)?)\s*(?:every day|daily)/i
  ];
  
  for (const pattern of schedulePatterns) {
    const match = message.match(pattern);
    if (match) return `daily at ${match[1]}`;
  }
  
  return null;
}

// Helper function to generate helpful text for missing parameters
function generateHelpText(missingParameters: Array<{name: string, description: string, required: boolean, type: string}>, automationType: string): string {
  const required = missingParameters.filter(p => p.required);
  const optional = missingParameters.filter(p => !p.required);
  
  let help = "To complete your automation, I need:\n\n";
  
  if (required.length > 0) {
    help += "**Required:**\n";
    required.forEach(param => {
      help += `• **${param.name}**: ${param.description}\n`;
    });
  }
  
  if (optional.length > 0) {
    help += "\n**Optional (I can use defaults if not provided):**\n";
    optional.forEach(param => {
      help += `• **${param.name}**: ${param.description}\n`;
    });
  }
  
  help += "\nPlease provide the missing information and I'll set up your automation!";
  
  return help;
}

// Helper function to forward requests to orchestration endpoint
async function forwardToOrchestration(request: NextRequest, orchestrationRequest: any): Promise<NextResponse> {
  const orchestrationResponse = await fetch(`${request.nextUrl.origin}/api/automation/orchestrate-workflow`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Cookie': request.headers.get('cookie') || ''
    },
    body: JSON.stringify(orchestrationRequest)
  });

  if (!orchestrationResponse.ok) {
    const errorData = await orchestrationResponse.text();
    return NextResponse.json(
      { success: false, error: `Orchestration failed: ${errorData}` },
      { status: orchestrationResponse.status }
    );
  }

  const orchestrationData = await orchestrationResponse.json() as {
    success: boolean;
    message?: string;
    requestId?: string;
    workflowId?: string;
    executionResult?: any;
    matchedTemplate?: any;
  };
  
  // Transform response to match expected format
  return NextResponse.json({
    success: orchestrationData.success,
    message: orchestrationData.message,
    requestId: orchestrationData.requestId,
    workflowId: orchestrationData.workflowId,
    executionResult: orchestrationData.executionResult,
    matchedTemplate: orchestrationData.matchedTemplate
  });
}

export async function POST(request: NextRequest) {
  try {
    // Validate session first
    const sessionToken = request.cookies.get('session_token')?.value;
    if (!sessionToken) {
      return NextResponse.json(
        { success: false, error: "Authentication required" },
        { status: 401 }
      );
    }

    // Import here to avoid circular dependency issues
    const user = await validateSession(sessionToken);
    if (!user) {
      return NextResponse.json(
        { success: false, error: "Invalid session" },
        { status: 401 }
      );
    }

    // Get the request body
    const body = await request.json() as { 
      workflow?: any; 
      requestId?: string; 
      userMessage?: string;
      providedParameters?: Record<string, any>;
    };
    
    // Extract the workflow from the request
    const { workflow, requestId, userMessage, providedParameters } = body;
    
    if (!workflow && !userMessage) {
      return NextResponse.json(
        { success: false, error: "Either workflow or userMessage is required" },
        { status: 400 }
      );
    }

    // If we have a user message instead of a workflow, parse it for automation intent
    if (userMessage && !workflow) {
      return await handleUserMessage(request, userMessage, requestId, providedParameters);
    }

    // Transform the workflow into a message for orchestration
    let message = 'Execute automation workflow';
    let parameters = providedParameters || {};
    let missingParameters: Array<{name: string, description: string, required: boolean, type: string}> = [];
    
    // Try to extract meaningful information from the workflow
    if (workflow.name) {
      message = `Execute workflow: ${workflow.name}`;
    }
    
    // Extract parameters based on workflow type and detect missing ones
    let emailNodes: any[] = [];
    let scheduleNodes: any[] = [];
    
    if (workflow.nodes) {
      // Look for email nodes to extract email automation intent
      emailNodes = workflow.nodes.filter((node: any) => 
        node.type && (
          node.type.includes('email') || 
          node.type.includes('gmail') || 
          node.type.includes('smtp') ||
          node.type.includes('emailsend')
        )
      );
      
      if (emailNodes.length > 0) {
        const emailNode = emailNodes[0];
        message = 'send email automation';
        
        // Extract parameters from email node
        if (emailNode.parameters) {
          parameters = {
            recipient: emailNode.parameters.to || emailNode.parameters.toEmail || emailNode.parameters.email || parameters.recipient,
            content: emailNode.parameters.text || emailNode.parameters.html || emailNode.parameters.message || emailNode.parameters.body || parameters.content,
            subject: emailNode.parameters.subject || emailNode.parameters.title || parameters.subject,
            ...parameters
          };
        }
        
        // Check for missing required email parameters
        if (!parameters.recipient) {
          missingParameters.push({
            name: 'recipient',
            description: 'Email address to send to (e.g., slakshanand1105@gmail.com)',
            required: true,
            type: 'email'
          });
        }
        
        if (!parameters.content) {
          missingParameters.push({
            name: 'content',
            description: 'Email message content (e.g., "Good morning! Hope you have a great day!")',
            required: true,
            type: 'text'
          });
        }
        
        // Optional parameters
        if (!parameters.subject) {
          missingParameters.push({
            name: 'subject',
            description: 'Email subject line (e.g., "Good Morning!")',
            required: false,
            type: 'text'
          });
        }
      }
      
      // Look for schedule/timer nodes
      scheduleNodes = workflow.nodes.filter((node: any) => 
        node.type && (
          node.type.includes('schedule') || 
          node.type.includes('cron') || 
          node.type.includes('interval')
        )
      );
      
      if (scheduleNodes.length > 0) {
        const scheduleNode = scheduleNodes[0];
        if (scheduleNode.parameters) {
          parameters = {
            schedule: scheduleNode.parameters.rule || scheduleNode.parameters.interval || parameters.schedule,
            timezone: scheduleNode.parameters.timezone || parameters.timezone,
            ...parameters
          };
        }
        
        // Check for missing schedule parameters
        if (!parameters.schedule) {
          missingParameters.push({
            name: 'schedule',
            description: 'When to run this automation (e.g., "every day at 7:00 AM", "0 7 * * *")',
            required: true,
            type: 'schedule'
          });
        }
      }
    }

    // If we have missing required parameters, ask the user for them
    const requiredMissing = missingParameters.filter(p => p.required);
    if (requiredMissing.length > 0) {
      return NextResponse.json({
        success: false,
        needsParameters: true,
        message: "I need a few more details to set up your automation:",
        missingParameters,
        workflowType: emailNodes.length > 0 ? 'email' : scheduleNodes.length > 0 ? 'schedule' : 'general',
        requestId: requestId || `param_${Date.now()}`,
        helpText: generateHelpText(missingParameters, message)
      });
    }

    // Create orchestration request
    const orchestrationRequest = {
      message,
      requestId,
      parameters
    };

    // Forward to orchestrate-workflow endpoint
    const orchestrationResponse = await fetch(`${request.nextUrl.origin}/api/automation/orchestrate-workflow`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': request.headers.get('cookie') || ''
      },
      body: JSON.stringify(orchestrationRequest)
    });

    if (!orchestrationResponse.ok) {
      const errorData = await orchestrationResponse.text();
      return NextResponse.json(
        { success: false, error: `Orchestration failed: ${errorData}` },
        { status: orchestrationResponse.status }
      );
    }

    const orchestrationData = await orchestrationResponse.json() as {
      success: boolean;
      message?: string;
      requestId?: string;
      workflowId?: string;
      executionResult?: any;
      matchedTemplate?: any;
    };
    
    // Transform response to match expected format
    return NextResponse.json({
      success: orchestrationData.success,
      message: orchestrationData.message,
      requestId: orchestrationData.requestId,
      workflowId: orchestrationData.workflowId,
      executionResult: orchestrationData.executionResult,
      matchedTemplate: orchestrationData.matchedTemplate
    });

  } catch (error) {
    console.error('❌ [AUTOMATION-EXECUTION] Error:', error);
    return NextResponse.json(
      { success: false, error: "Automation execution failed. Please try again." },
      { status: 500 }
    );
  }
}
