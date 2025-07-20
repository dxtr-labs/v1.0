// src/app/api/auth/me/route.ts
// Get current user information endpoint

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = 'http://127.0.0.1:8002';

export async function GET(request: NextRequest) {
  try {
    // Get session token from cookies
    const sessionToken = request.cookies.get('session_token')?.value;
    
    if (!sessionToken) {
      return NextResponse.json(
        { success: false, error: 'No session found' },
        { status: 401 }
      );
    }
    
    // Call FastAPI backend to verify session and get user info
    try {
      console.log('🔄 Verifying session with FastAPI backend...');
      
      const backendResponse = await fetch(`${BACKEND_URL}/api/auth/me`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Cookie': `session_token=${sessionToken}`,
        },
      });

      const backendResult = await backendResponse.json() as any;
      
      if (!backendResponse.ok) {
        console.error('❌ Backend session verification failed:', backendResult);
        return NextResponse.json(
          { success: false, error: backendResult.detail || 'Session invalid' },
          { status: backendResponse.status }
        );
      }

      console.log('✅ Backend session verification successful');
      
      // Success response from backend
      return NextResponse.json({
        success: true,
        user: backendResult.user
      });

    } catch (error) {
      console.error('❌ Backend connection error:', error);
      return NextResponse.json(
        { success: false, error: "Unable to connect to authentication service" },
        { status: 503 }
      );
    }
    
  } catch (error) {
    console.error('❌ Session validation error:', error);
    return NextResponse.json(
      { success: false, error: 'Session validation failed' },
      { status: 500 }
    );
  }
}
