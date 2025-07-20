import { NextRequest, NextResponse } from 'next/server';
import { validateSession } from '../../../../../lib/structured-auth.js';

interface AnalyzePromptRequest {
  prompt: string;
  model?: string;
  apiKey?: string;
}

interface AnalysisResult {
  intent: string;
  confidence: number;
  parameters: Record<string, any>;
  suggestions: string[];
  workflowRecommendation?: {
    type: string;
    description: string;
    estimatedComplexity: 'simple' | 'medium' | 'complex';
  };
}

export async function POST(req: NextRequest) {
  try {
    // Get session token from cookies
    const sessionToken = req.cookies.get('session_token')?.value;
    
    if (!sessionToken) {
      return NextResponse.json(
        { error: "Authentication required" },
        { status: 401 }
      );
    }

    // Validate session and get user
    const user = await validateSession(sessionToken);
    if (!user) {
      return NextResponse.json(
        { error: "Invalid session" },
        { status: 401 }
      );
    }

    const body = await req.json() as AnalyzePromptRequest;
    const { prompt, model, apiKey } = body;

    if (!prompt || prompt.trim().length === 0) {
      return NextResponse.json(
        { error: "Prompt is required" },
        { status: 400 }
      );
    }

    console.log(`🔍 Analyzing prompt for user ${user.email}: "${prompt.substring(0, 100)}..."`);

    // For now, we'll use a simple rule-based analysis
    // In production, this would call the selected AI model
    const analysis = await analyzePromptWithRules(prompt);

    // If model and API key are provided, enhance with AI analysis
    if (model && apiKey) {
      try {
        const aiAnalysis = await analyzePromptWithAI(prompt, model, apiKey);
        // Merge AI analysis with rule-based analysis
        if (aiAnalysis.confidence !== undefined) {
          analysis.confidence = Math.max(analysis.confidence, aiAnalysis.confidence);
        }
        if (aiAnalysis.suggestions) {
          analysis.suggestions = [...analysis.suggestions, ...aiAnalysis.suggestions];
        }
        if (aiAnalysis.workflowRecommendation) {
          analysis.workflowRecommendation = aiAnalysis.workflowRecommendation;
        }
      } catch (aiError) {
        console.warn('AI analysis failed, using rule-based analysis:', aiError);
      }
    }

    return NextResponse.json({
      success: true,
      analysis,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error analyzing prompt:', error);
    return NextResponse.json(
      { error: "Failed to analyze prompt" },
      { status: 500 }
    );
  }
}

// Rule-based prompt analysis (fallback)
async function analyzePromptWithRules(prompt: string): Promise<AnalysisResult> {
  const lowerPrompt = prompt.toLowerCase();
  
  // Email automation detection
  if (lowerPrompt.includes('email') || lowerPrompt.includes('send') || lowerPrompt.includes('mail')) {
    const emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
    const emails = prompt.match(emailRegex) || [];
    
    return {
      intent: 'email_automation',
      confidence: 0.8,
      parameters: {
        recipients: emails,
        hasSchedule: lowerPrompt.includes('daily') || lowerPrompt.includes('weekly') || lowerPrompt.includes('schedule'),
        hasSubject: lowerPrompt.includes('subject:') || lowerPrompt.includes('title:'),
        hasContent: lowerPrompt.includes('content:') || lowerPrompt.includes('body:') || lowerPrompt.includes('message:')
      },
      suggestions: [
        'Consider adding a subject line for your email',
        'Specify when you want the email to be sent',
        'Add email content or template'
      ],
      workflowRecommendation: {
        type: 'email_workflow',
        description: 'Create an automated email sending workflow',
        estimatedComplexity: emails.length > 1 ? 'medium' : 'simple'
      }
    };
  }
  
  // Webhook automation detection
  if (lowerPrompt.includes('webhook') || lowerPrompt.includes('trigger') || lowerPrompt.includes('when')) {
    return {
      intent: 'webhook_automation',
      confidence: 0.7,
      parameters: {
        hasTrigger: true,
        hasConditions: lowerPrompt.includes('if') || lowerPrompt.includes('when'),
        hasActions: lowerPrompt.includes('then') || lowerPrompt.includes('send') || lowerPrompt.includes('create')
      },
      suggestions: [
        'Define the trigger conditions clearly',
        'Specify what actions should happen',
        'Consider adding error handling'
      ],
      workflowRecommendation: {
        type: 'webhook_workflow',
        description: 'Create a webhook-triggered automation workflow',
        estimatedComplexity: 'medium'
      }
    };
  }
  
  // Data processing automation
  if (lowerPrompt.includes('process') || lowerPrompt.includes('transform') || lowerPrompt.includes('data')) {
    return {
      intent: 'data_processing',
      confidence: 0.6,
      parameters: {
        hasDataSource: lowerPrompt.includes('from') || lowerPrompt.includes('input'),
        hasTransformation: lowerPrompt.includes('convert') || lowerPrompt.includes('transform'),
        hasOutput: lowerPrompt.includes('save') || lowerPrompt.includes('export')
      },
      suggestions: [
        'Specify the data source and format',
        'Define the transformation rules',
        'Choose the output destination'
      ],
      workflowRecommendation: {
        type: 'data_workflow',
        description: 'Create a data processing and transformation workflow',
        estimatedComplexity: 'complex'
      }
    };
  }
  
  // Generic automation
  return {
    intent: 'general_automation',
    confidence: 0.5,
    parameters: {
      hasActions: lowerPrompt.includes('do') || lowerPrompt.includes('create') || lowerPrompt.includes('make'),
      hasSchedule: lowerPrompt.includes('every') || lowerPrompt.includes('daily') || lowerPrompt.includes('weekly')
    },
    suggestions: [
      'Be more specific about what you want to automate',
      'Define the triggers and actions clearly',
      'Consider the frequency of automation'
    ],
    workflowRecommendation: {
      type: 'custom_workflow',
      description: 'Create a custom automation workflow',
      estimatedComplexity: 'medium'
    }
  };
}

// AI-powered prompt analysis (when API key is available)
async function analyzePromptWithAI(prompt: string, model: string, apiKey: string): Promise<Partial<AnalysisResult>> {
  // This is a placeholder for AI analysis
  // In production, you would call the selected AI model here
  
  const analysisPrompt = `
Analyze this automation request and provide insights:
"${prompt}"

Please identify:
1. The main intent (email_automation, webhook_automation, data_processing, etc.)
2. Confidence level (0-1)
3. Key parameters mentioned
4. Workflow complexity estimation
5. Helpful suggestions

Respond in JSON format.
`;

  try {
    // For now, return enhanced analysis based on rules
    // In production, implement actual AI model calls here
    return {
      confidence: 0.9,
      suggestions: [
        'AI suggests adding error handling to your workflow',
        'Consider setting up monitoring and alerts',
        'AI recommends testing with sample data first'
      ],
      workflowRecommendation: {
        type: 'ai_enhanced_workflow',
        description: 'AI-optimized automation workflow with best practices',
        estimatedComplexity: 'medium'
      }
    };
  } catch (error) {
    console.error('AI analysis failed:', error);
    throw error;
  }
}
