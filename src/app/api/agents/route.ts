import { NextRequest, NextResponse } from 'next/server';

interface CreateAgentRequest {
  name: string;
  role: string;
  mode?: string;
  personality?: string | {
    tone?: string;
    style?: string;
    expertise?: string[];
    responseLength?: string;
  };
  llmConfig?: {
    model?: string;
    temperature?: number;
    max_tokens?: number;
    system_prompt?: string;
  };
  description?: string;
}

const BACKEND_URL = 'http://127.0.0.1:8002';

export async function GET(request: NextRequest) {
  try {
    console.log('Frontend API: Fetching agents from backend...');
    
    // Forward cookies from the request
    const cookies = request.headers.get('cookie') || '';
    
    // Get or create a simple user session ID
    let userSessionId = 'default_user';
    const sessionCookie = request.cookies.get('user_session');
    if (sessionCookie) {
      userSessionId = sessionCookie.value;
    }
    
    console.log('Frontend API: Using user session ID:', userSessionId);
    
    const response = await fetch(`${BACKEND_URL}/api/agents`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': cookies, // Forward cookies for authentication
        'x-user-id': userSessionId, // Send consistent user ID
      },
    });

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Frontend API: Got agents from backend:', data);
    
    return NextResponse.json({
      agents: data.agents || [],
      total: data.agents?.length || 0
    });
  } catch (error) {
    console.error('Frontend API: Error fetching agents from backend:', error);
    // Fallback to empty array if backend is not available
    return NextResponse.json({
      agents: [],
      total: 0
    });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body: CreateAgentRequest = await request.json();
    console.log('Frontend API: Creating agent with data:', body);

    // Forward cookies from the request
    const cookies = request.headers.get('cookie') || '';
    
    // Get or create a simple user session ID
    let userSessionId = 'default_user';
    const sessionCookie = request.cookies.get('user_session');
    if (sessionCookie) {
      userSessionId = sessionCookie.value;
    }
    
    console.log('Frontend API: Using user session ID for creation:', userSessionId);

    // Forward the request to the backend
    const response = await fetch(`${BACKEND_URL}/api/agents`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': cookies, // Forward cookies for authentication
        'x-user-id': userSessionId, // Send consistent user ID
      },
      body: JSON.stringify({
        name: body.name,
        role: body.role,
        mode: body.mode || 'single',
        personality: body.personality || '',
        description: body.description || ''
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error:', response.status, errorText);
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const result = await response.json();
    console.log('Frontend API: Agent created successfully:', result);

    return NextResponse.json({
      success: true,
      agent: (result as any).agent || result,
      message: 'Agent created successfully'
    }, { status: 201 });

  } catch (error) {
    console.error('Frontend API: Agent creation error:', error);
    return NextResponse.json(
      { error: 'Failed to create agent' },
      { status: 500 }
    );
  }
}

// DELETE method removed - now handled by /api/agents/[id]/route.ts
