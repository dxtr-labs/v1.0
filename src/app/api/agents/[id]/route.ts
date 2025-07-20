import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = 'http://127.0.0.1:8002';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const agentId = params.id;
    console.log('Frontend API: Fetching agent by ID:', agentId);

    // Forward cookies from the request
    const cookies = request.headers.get('cookie') || '';
    
    // Get or create a simple user session ID
    let userSessionId = 'default_user';
    const sessionCookie = request.cookies.get('user_session');
    if (sessionCookie) {
      userSessionId = sessionCookie.value;
    }
    
    console.log('Frontend API: Using user session ID for get:', userSessionId);

    const response = await fetch(`${BACKEND_URL}/api/agents/${agentId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': cookies, // Forward cookies for authentication
        'x-user-id': userSessionId, // Send consistent user ID
      },
    });

    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json(
          { error: 'Agent not found' },
          { status: 404 }
        );
      }
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Frontend API: Got agent from backend:', data);
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Frontend API: Error fetching agent from backend:', error);
    return NextResponse.json(
      { error: 'Failed to fetch agent' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const agentId = params.id;
    console.log('Frontend API: Deleting agent by ID:', agentId);

    // Forward cookies from the request
    const cookies = request.headers.get('cookie') || '';
    
    // Get or create a simple user session ID
    let userSessionId = 'default_user';
    const sessionCookie = request.cookies.get('user_session');
    if (sessionCookie) {
      userSessionId = sessionCookie.value;
    }
    
    console.log('Frontend API: Using user session ID for deletion:', userSessionId);

    const response = await fetch(`${BACKEND_URL}/api/agents/${agentId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': cookies, // Forward cookies for authentication
        'x-user-id': userSessionId, // Send consistent user ID
      },
    });

    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json(
          { error: 'Agent not found' },
          { status: 404 }
        );
      }
      const errorText = await response.text();
      console.error('Backend delete error:', response.status, errorText);
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Frontend API: Agent deleted successfully:', data);
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Frontend API: Error deleting agent from backend:', error);
    return NextResponse.json(
      { error: 'Failed to delete agent' },
      { status: 500 }
    );
  }
}
