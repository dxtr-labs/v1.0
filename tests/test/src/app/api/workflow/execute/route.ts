// src/app/api/workflow/execute/route.ts
// Proper workflow execution endpoint

import { NextRequest, NextResponse } from 'next/server';
import { validateSession } from '../../../../../lib/structured-auth.js';
import { executeEmailWorkflow } from '../../../../../lib/email-executor.js';

interface WorkflowNode {
  id: string;
  type: string;
  data: any;
  parameters?: any;
}

interface Workflow {
  id?: string;
  name: string;
  description?: string;
  nodes: WorkflowNode[];
  connections?: any[];
}

export async function POST(req: NextRequest) {
  try {
    console.log('🚀 [WORKFLOW-EXECUTE] Starting workflow execution...');

    // Get session token from cookies
    const sessionToken = req.cookies.get('session_token')?.value;
    
    if (!sessionToken) {
      console.log('❌ [WORKFLOW-EXECUTE] No session token found');
      return NextResponse.json(
        { success: false, error: "Authentication required" },
        { status: 401 }
      );
    }

    // Validate session and get user
    const user = await validateSession(sessionToken);
    if (!user) {
      console.log('❌ [WORKFLOW-EXECUTE] Session validation failed');
      return NextResponse.json(
        { success: false, error: "Invalid session" },
        { status: 401 }
      );
    }

    console.log('✅ [WORKFLOW-EXECUTE] User authenticated:', user.email);

    // Get request body
    const body = await req.json() as { 
      workflow: Workflow;
      parameters?: Record<string, any>;
    };
    
    const { workflow, parameters = {} } = body;

    if (!workflow || !workflow.nodes) {
      return NextResponse.json(
        { success: false, error: "Valid workflow with nodes is required" },
        { status: 400 }
      );
    }

    console.log(`📝 [WORKFLOW-EXECUTE] Executing workflow: ${workflow.name}`);
    console.log(`📊 [WORKFLOW-EXECUTE] Workflow has ${workflow.nodes.length} nodes`);

    // Execute the workflow
    const executionResults = [];
    
    for (const node of workflow.nodes) {
      console.log(`🔧 [WORKFLOW-EXECUTE] Processing node: ${node.id} (${node.type})`);
      
      try {
        const result = await executeNode(node, parameters, user);
        executionResults.push({
          nodeId: node.id,
          nodeType: node.type,
          success: result.success,
          result: result.data,
          message: result.message,
          error: result.error
        });
        
        if (!result.success && result.critical) {
          // Stop execution on critical errors
          console.log(`❌ [WORKFLOW-EXECUTE] Critical error in node ${node.id}, stopping execution`);
          break;
        }
      } catch (error) {
        console.error(`❌ [WORKFLOW-EXECUTE] Error executing node ${node.id}:`, error);
        executionResults.push({
          nodeId: node.id,
          nodeType: node.type,
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    }

    const successfulNodes = executionResults.filter(r => r.success).length;
    const totalNodes = executionResults.length;
    
    console.log(`✅ [WORKFLOW-EXECUTE] Execution complete: ${successfulNodes}/${totalNodes} nodes successful`);

    return NextResponse.json({
      success: successfulNodes > 0,
      message: `Workflow executed: ${successfulNodes}/${totalNodes} steps completed successfully`,
      workflowName: workflow.name,
      executionResults,
      summary: {
        totalNodes,
        successfulNodes,
        failedNodes: totalNodes - successfulNodes
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ [WORKFLOW-EXECUTE] Error:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json(
      { 
        success: false, 
        error: "Workflow execution failed",
        message: errorMessage,
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}

async function executeNode(node: WorkflowNode, globalParameters: Record<string, any>, user: any): Promise<{
  success: boolean;
  data?: any;
  message?: string;
  error?: string;
  critical?: boolean;
}> {
  const nodeParams = { ...globalParameters, ...node.parameters, ...node.data };
  
  switch (node.type) {
    case 'EmailSend':
    case 'email':
    case 'send-email':
      return await executeEmailNode(node, nodeParams);
      
    case 'Delay':
    case 'delay':
    case 'wait':
      return await executeDelayNode(node, nodeParams);
      
    case 'HttpRequest':
    case 'http-request':
    case 'api-call':
      return await executeHttpNode(node, nodeParams);
      
    case 'Log':
    case 'log':
    case 'console':
      return executeLogNode(node, nodeParams);
      
    default:
      console.log(`⚠️ [WORKFLOW-EXECUTE] Unknown node type: ${node.type}, skipping`);
      return {
        success: true,
        message: `Skipped unknown node type: ${node.type}`,
        data: { skipped: true, nodeType: node.type }
      };
  }
}

async function executeEmailNode(node: WorkflowNode, params: any): Promise<any> {
  try {
    const { toEmail, subject, content } = params;
    
    if (!toEmail || !subject || !content) {
      return {
        success: false,
        error: `Missing required email parameters. Required: toEmail, subject, content. Got: ${JSON.stringify(params)}`,
        critical: true
      };
    }

    console.log(`📧 [EMAIL-NODE] Sending email to ${toEmail} with subject: ${subject}`);
    
    const result = await executeEmailWorkflow(toEmail, subject, content);
    
    if (result.success) {
      return {
        success: true,
        message: `Email sent successfully to ${toEmail}`,
        data: {
          messageId: result.messageId,
          recipient: toEmail,
          subject,
          service: 'PrivateEmail'
        }
      };
    } else {
      return {
        success: false,
        error: `Email sending failed: ${result.error}`,
        critical: true
      };
    }
  } catch (error) {
    return {
      success: false,
      error: `Email node execution failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      critical: true
    };
  }
}

async function executeDelayNode(node: WorkflowNode, params: any): Promise<any> {
  const delayMs = params.delay || params.duration || 1000;
  console.log(`⏱️ [DELAY-NODE] Waiting ${delayMs}ms`);
  
  await new Promise(resolve => setTimeout(resolve, delayMs));
  
  return {
    success: true,
    message: `Delayed execution by ${delayMs}ms`,
    data: { delayMs }
  };
}

async function executeHttpNode(node: WorkflowNode, params: any): Promise<any> {
  try {
    const { url, method = 'GET', headers = {}, body } = params;
    
    if (!url) {
      return {
        success: false,
        error: 'HTTP node requires a URL parameter',
        critical: true
      };
    }

    console.log(`🌐 [HTTP-NODE] Making ${method} request to ${url}`);
    
    const response = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined
    });

    const responseData = await response.text();
    
    return {
      success: response.ok,
      message: `HTTP ${method} to ${url} - Status: ${response.status}`,
      data: {
        status: response.status,
        statusText: response.statusText,
        response: responseData
      }
    };
  } catch (error) {
    return {
      success: false,
      error: `HTTP request failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      critical: false
    };
  }
}

function executeLogNode(node: WorkflowNode, params: any): any {
  const message = params.message || params.text || 'Log node executed';
  console.log(`📝 [LOG-NODE] ${message}`);
  
  return {
    success: true,
    message: `Logged: ${message}`,
    data: { logMessage: message }
  };
}
