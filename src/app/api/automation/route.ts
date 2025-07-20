// src/app/api/automation/route.ts
// Comprehensive AI-driven automation API - DEPRECATED
// Redirects to new workflow engine

import { NextRequest, NextResponse } from 'next/server';

interface AutomationRequest {
  prompt: string;
  conversationFlowId?: string;
  flowId?: string;
  userResponse?: string;
  existingFlow?: any;
  conversationFlow?: any;
}

export async function POST(request: NextRequest) {
  try {
    console.log('🤖 Comprehensive Automation API called (redirecting to new workflow engine)');
    
    const body: AutomationRequest = await request.json();
    const { prompt } = body;
    
    if (!prompt) {
      return NextResponse.json({
        success: false,
        message: 'Please tell me what you want to automate. I can help with workflows like:',
        data: {
          availableAutomations: [
            { name: 'Email Automation', category: 'Communication', description: 'Send emails automatically', example: 'Send welcome email to new users' },
            { name: 'Database Operations', category: 'Data', description: 'Manage database records', example: 'Insert user data into database' },
            { name: 'File Processing', category: 'Files', description: 'Process and manipulate files', example: 'Convert CSV to JSON' },
            { name: 'API Integration', category: 'Web', description: 'Connect to external APIs', example: 'Get weather data from API' },
            { name: 'Scheduled Tasks', category: 'Scheduling', description: 'Run tasks on schedule', example: 'Daily backup at midnight' },
            { name: 'AI Processing', category: 'AI', description: 'Use AI for data analysis', example: 'Analyze sentiment of text' }
          ],
          categories: ['Communication', 'Data', 'Files', 'Web', 'Scheduling', 'AI'],
          totalModules: 6,
          deprecated: true,
          newEndpoint: '/api/generate-workflow'
        }
      }, { status: 400 });
    }
    
    console.log('🧠 Processing new automation request (redirecting):', prompt);
    
    // Redirect to new workflow generation API
    const workflowResponse = await fetch(`${request.nextUrl.origin}/api/generate-workflow`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': request.headers.get('cookie') || ''
      },
      body: JSON.stringify({ prompt })
    });

    if (!workflowResponse.ok) {
      const errorData: any = await workflowResponse.json();
      throw new Error(errorData.error || 'Workflow generation failed');
    }

    const workflow: any = await workflowResponse.json();
    
    return NextResponse.json({
      success: true,
      message: `Generated workflow with ${workflow.nodes?.length || 0} steps`,
      workflow: workflow,
      deprecated: true,
      redirected: true,
      newEndpoint: '/api/generate-workflow'
    });
    
  } catch (error) {
    console.error('❌ Automation API error:', error);
    return NextResponse.json({
      success: false,
      message: `Automation API failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

export async function GET(request: NextRequest) {
  try {
    return NextResponse.json({
      success: true,
      message: 'Automation Engine Status - DEPRECATED',
      data: {
        totalModules: 6,
        categories: ['Communication', 'Data', 'Files', 'Web', 'Scheduling', 'AI'],
        modules: [
          { name: 'Email', category: 'Communication', description: 'Email automation', requiredParams: ['to', 'subject'], optionalParams: ['body'], examples: ['Send welcome email'] },
          { name: 'Database', category: 'Data', description: 'Database operations', requiredParams: ['operation'], optionalParams: ['table', 'data'], examples: ['Insert user record'] },
          { name: 'HTTP', category: 'Web', description: 'HTTP requests', requiredParams: ['url'], optionalParams: ['method', 'data'], examples: ['Get API data'] },
          { name: 'Scheduler', category: 'Scheduling', description: 'Scheduled tasks', requiredParams: ['schedule'], optionalParams: ['timezone'], examples: ['Daily backup'] },
          { name: 'AI', category: 'AI', description: 'AI processing', requiredParams: ['task'], optionalParams: ['model'], examples: ['Sentiment analysis'] },
          { name: 'Spreadsheet', category: 'Data', description: 'Spreadsheet operations', requiredParams: ['operation'], optionalParams: ['file'], examples: ['Export to CSV'] }
        ],
        capabilities: [
          'Workflow-driven automation flows',
          'Visual workflow designer', 
          'Email automation with nodemailer',
          'Database operations with SQLite',
          'File processing and manipulation',
          'Web API integrations',
          'Scheduled task automation',
          'AI processing integration',
          'Real-time execution monitoring'
        ],
        deprecated: true,
        newEndpoint: '/api/generate-workflow',
        migrationNote: 'This API is deprecated. Use /api/generate-workflow for new workflows.'
      }
    });
  } catch (error) {
    return NextResponse.json({
      success: false,
      message: 'Failed to get automation status',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}
