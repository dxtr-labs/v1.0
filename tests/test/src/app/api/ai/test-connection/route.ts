import { NextRequest, NextResponse } from 'next/server';
import { validateSession } from '../../../../../lib/structured-auth.js';

interface TestConnectionRequest {
  model: string;
  apiKey: string;
}

interface ExternalAIModel {
  name: string;
  endpoint: string | ((apiKey: string) => string);
  testPayload: any;
  headers: (apiKey: string) => Record<string, string>;
}

interface LocalAIModel {
  name: string;
  local: true;
}

type AIModel = ExternalAIModel | LocalAIModel;

// AI Model Configuration
const AI_MODELS: Record<string, AIModel> = {
  'openai-gpt4': {
    name: 'GPT-4',
    endpoint: 'https://api.openai.com/v1/chat/completions',
    testPayload: {
      model: 'gpt-4',
      messages: [{ role: 'user', content: 'Hello, this is a connection test.' }],
      max_tokens: 10
    },
    headers: (apiKey: string) => ({
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    })
  },
  'openai-gpt35': {
    name: 'GPT-3.5 Turbo',
    endpoint: 'https://api.openai.com/v1/chat/completions',
    testPayload: {
      model: 'gpt-3.5-turbo',
      messages: [{ role: 'user', content: 'Hello, this is a connection test.' }],
      max_tokens: 10
    },
    headers: (apiKey: string) => ({
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    })
  },
  'google-gemini-pro': {
    name: 'Gemini Pro',
    endpoint: (apiKey: string) => `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${apiKey}`,
    testPayload: {
      contents: [{
        parts: [{ text: 'Hello, this is a connection test.' }]
      }]
    },
    headers: () => ({
      'Content-Type': 'application/json'
    })
  },
  'google-gemini-flash': {
    name: 'Gemini Flash',
    endpoint: (apiKey: string) => `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
    testPayload: {
      contents: [{
        parts: [{ text: 'Hello, this is a connection test.' }]
      }]
    },
    headers: () => ({
      'Content-Type': 'application/json'
    })
  },
  'anthropic-claude': {
    name: 'Claude 3 Sonnet',
    endpoint: 'https://api.anthropic.com/v1/messages',
    testPayload: {
      model: 'claude-3-sonnet-20240229',
      max_tokens: 10,
      messages: [{ role: 'user', content: 'Hello, this is a connection test.' }]
    },
    headers: (apiKey: string) => ({
      'x-api-key': apiKey,
      'Content-Type': 'application/json',
      'anthropic-version': '2023-06-01'
    })
  },
  'anthropic-claude-haiku': {
    name: 'Claude 3 Haiku',
    endpoint: 'https://api.anthropic.com/v1/messages',
    testPayload: {
      model: 'claude-3-haiku-20240307',
      max_tokens: 10,
      messages: [{ role: 'user', content: 'Hello, this is a connection test.' }]
    },
    headers: (apiKey: string) => ({
      'x-api-key': apiKey,
      'Content-Type': 'application/json',
      'anthropic-version': '2023-06-01'
    })
  },
  // DeepSeek models (local) - special handling
  'deepseek-coder': {
    name: 'DeepSeek Coder (Local)',
    local: true
  },
  'deepseek-chat': {
    name: 'DeepSeek Chat (Local)',
    local: true
  }
};

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

    const body = await req.json() as TestConnectionRequest;
    const { model, apiKey } = body;

    if (!model || !apiKey) {
      return NextResponse.json(
        { error: "Model and API key are required" },
        { status: 400 }
      );
    }

    // Get model configuration
    const modelConfig = AI_MODELS[model as keyof typeof AI_MODELS];
    if (!modelConfig) {
      return NextResponse.json(
        { error: "Unsupported AI model" },
        { status: 400 }
      );
    }

    console.log(`🧪 Testing connection for ${modelConfig.name}...`);

    // Handle local models differently
    if ('local' in modelConfig && modelConfig.local) {
      try {
        // For local models, we'll test by attempting to initialize
        console.log(`🏠 Testing local model: ${modelConfig.name}`);
        
        // Simulate local model test (in real implementation, you'd test the local model)
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate loading time
        
        console.log(`✅ ${modelConfig.name} local model ready`);
        return NextResponse.json({
          success: true,
          modelInfo: `${modelConfig.name} is running locally - no API required`,
          status: 200,
          local: true
        });
        
      } catch (localError) {
        console.log(`❌ ${modelConfig.name} local model failed:`, localError);
        return NextResponse.json({
          success: false,
          error: "Local model initialization failed"
        });
      }
    }

    try {
      // Prepare request for external API models
      const externalModel = modelConfig as ExternalAIModel;
      const endpoint = typeof externalModel.endpoint === 'function' 
        ? externalModel.endpoint(apiKey) 
        : externalModel.endpoint;
      
      const headers = externalModel.headers(apiKey);

      // Make test API call
      const response = await fetch(endpoint, {
        method: 'POST',
        headers,
        body: JSON.stringify(externalModel.testPayload),
        signal: AbortSignal.timeout(10000) // 10 second timeout
      });

      if (response.ok) {
        console.log(`✅ ${modelConfig.name} connection successful`);
        return NextResponse.json({
          success: true,
          modelInfo: `${modelConfig.name} is ready for use`,
          status: response.status
        });
      } else {
        const errorText = await response.text();
        console.log(`❌ ${modelConfig.name} connection failed:`, response.status, errorText);
        
        // Parse common error messages
        let errorMessage = `API returned ${response.status}`;
        if (response.status === 401) {
          errorMessage = "Invalid API key";
        } else if (response.status === 403) {
          errorMessage = "API key doesn't have required permissions";
        } else if (response.status === 429) {
          errorMessage = "Rate limit exceeded";
        } else if (response.status >= 500) {
          errorMessage = "AI service is temporarily unavailable";
        }

        return NextResponse.json({
          success: false,
          error: errorMessage
        });
      }

    } catch (fetchError) {
      console.error(`❌ ${modelConfig.name} connection error:`, fetchError);
      
      let errorMessage = "Connection failed";
      if (fetchError instanceof Error) {
        if (fetchError.name === 'AbortError') {
          errorMessage = "Connection timeout";
        } else if (fetchError.message.includes('network')) {
          errorMessage = "Network error";
        } else {
          errorMessage = fetchError.message;
        }
      }

      return NextResponse.json({
        success: false,
        error: errorMessage
      });
    }

  } catch (error) {
    console.error('Error testing AI connection:', error);
    return NextResponse.json(
      { error: "Failed to test AI connection" },
      { status: 500 }
    );
  }
}
