// src/app/api/auth/login/route.ts
// User login API that proxies to FastAPI backend

import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = 'http://127.0.0.1:8002';

export async function POST(req: NextRequest) {
  try {
    const { email, password } = await req.json() as { email: string; password: string };

    if (!email || !password) {
      return NextResponse.json(
        { success: false, error: "Email and password are required" }, 
        { status: 400 }
      );
    }

    // Call FastAPI backend login endpoint
    try {
      console.log('🔄 Proxying login request to FastAPI backend...');
      
      const backendResponse = await fetch(`${BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password
        }),
      });

      const backendResult = await backendResponse.json() as any;
      
      if (!backendResponse.ok) {
        console.error('❌ Backend login failed:', backendResult);
        return NextResponse.json(
          { success: false, error: backendResult.detail || 'Invalid email or password' },
          { status: backendResponse.status }
        );
      }

      console.log('✅ Backend login successful:', backendResult);
      
      // Success response from backend
      const response = NextResponse.json({
        success: true,
        user: backendResult.user,
        message: backendResult.message
      });

      // Set session cookie if we have a session token
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
      console.error('❌ Backend connection error:', error);
      return NextResponse.json(
        { success: false, error: "Unable to connect to authentication service" },
        { status: 503 }
      );
    }

  } catch (error: any) {
    console.error('❌ Login API error:', error);
    return NextResponse.json(
      { success: false, error: "Internal server error" }, 
      { status: 500 }
    );
  }
}
