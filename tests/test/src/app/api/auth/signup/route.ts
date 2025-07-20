// src/app/api/auth/signup/route.ts
// User registration API that proxies to FastAPI backend

import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = 'http://127.0.0.1:8002';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json() as {
      email: string;
      password?: string;
      firstName?: string;
      lastName?: string;
      username?: string;
      isOrganization?: boolean;
      joinWaitlist?: boolean;
    };
    
    const { 
      email, 
      password, 
      firstName, 
      lastName, 
      username,
      isOrganization = false,
      joinWaitlist = false 
    } = body;

    // Validate required fields
    if (!email) {
      return NextResponse.json(
        { success: false, error: "Email is required" },
        { status: 400 }
      );
    }

    // If user just wants to join waitlist
    if (joinWaitlist && !password) {
      // For waitlist, we still need to implement this in backend
      return NextResponse.json(
        { success: false, error: "Waitlist feature not yet implemented" },
        { status: 501 }
      );
    }

    // For full signup, proxy to FastAPI backend
    if (!password) {
      return NextResponse.json(
        { success: false, error: "Password is required for signup" },
        { status: 400 }
      );
    }

    // Call FastAPI backend signup endpoint
    try {
      console.log('🔄 Proxying signup request to FastAPI backend...');
      
      const backendResponse = await fetch(`${BACKEND_URL}/api/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          first_name: firstName || '',
          last_name: lastName || '',
          username: username || null,
          is_organization: isOrganization
        }),
      });

      const backendResult = await backendResponse.json() as any;
      
      if (!backendResponse.ok) {
        console.error('❌ Backend signup failed:', backendResult);
        return NextResponse.json(
          { success: false, error: backendResult.error || backendResult.detail || 'Signup failed' },
          { status: backendResponse.status }
        );
      }

      console.log('✅ Backend signup successful:', backendResult);
      
      // Success response from backend with automatic login
      const response = NextResponse.json({
        success: true,
        user: backendResult.user,
        message: backendResult.message,
        isLoggedIn: true // Add flag to indicate user is now logged in
      });

      // Set session cookie for automatic login after signup
      // Note: FastAPI backend returns session_token for session management
      if (backendResult.session_token) {
        response.cookies.set('session_token', backendResult.session_token, {
          httpOnly: true,
          secure: process.env.NODE_ENV === 'production',
          sameSite: 'lax',
          maxAge: 60 * 60 * 24 * 7, // 7 days
          path: '/'
        });
      }

      return response;

    } catch (error) {
      console.error('Backend connection error:', error);
      return NextResponse.json(
        { success: false, error: "Unable to connect to authentication service" },
        { status: 503 }
      );
    }
    
  } catch (error: any) {
    console.error('❌ Signup API error:', error);
    return NextResponse.json(
      { success: false, error: "Internal server error" },
      { status: 500 }
    );
  }
}
