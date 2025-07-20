import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = 'http://127.0.0.1:8002';

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const agentId = params.id;
    const body = await request.json();
    
    console.log('Frontend Chat API: Chat request for agent:', agentId);
    console.log('Frontend Chat API: Message:', body.message);

    // Forward cookies from the request
    const cookies = request.headers.get('cookie') || '';
    
    // Get or create a simple user session ID
    let userSessionId = 'default_user';
    const sessionCookie = request.cookies.get('user_session');
    if (sessionCookie) {
      userSessionId = sessionCookie.value;
    }
    
    console.log('Frontend Chat API: Using user session ID:', userSessionId);

    const response = await fetch(`${BACKEND_URL}/agents/${agentId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': cookies,
        'x-user-id': userSessionId,
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Frontend Chat API: Backend error:', response.status, errorText);
      return NextResponse.json({ 
        success: false, 
        error: `Backend error: ${response.status}` 
      }, { status: response.status });
    }

    const data = await response.json();
    console.log('Frontend Chat API: Backend response:', data);
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Frontend Chat API: Error:', error);
    return NextResponse.json({ 
      success: false, 
      error: 'Internal server error' 
    }, { status: 500 });
  }
}
