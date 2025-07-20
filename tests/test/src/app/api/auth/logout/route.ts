// src/app/api/auth/logout/route.ts
// Logout API endpoint using comprehensive auth system

import { NextRequest, NextResponse } from "next/server";
import { logoutUser, validateSession } from "../../../../../lib/structured-auth.js";

export async function POST(req: NextRequest) {
  try {
    // Get session token from cookies or headers
    const sessionToken = req.cookies.get('session_token')?.value || 
                        req.headers.get('authorization')?.replace('Bearer ', '');

    if (sessionToken) {
      // Validate session to get user ID
      const user = await validateSession(sessionToken);
      
      if (user) {
        // Logout user with comprehensive auth system
        await logoutUser(sessionToken, typeof user.userid === 'string' ? parseInt(user.userid) : user.userid);
      }
    }

    // Create response and clear any session cookies
    const response = NextResponse.json({ 
      success: true, 
      message: "Logged out successfully" 
    });

    // Clear session cookie
    response.cookies.set('session_token', '', {
      expires: new Date(0),
      path: '/',
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax'
    });

    return response;
  } catch (error: any) {
    console.error('Logout error:', error);
    return NextResponse.json(
      { success: false, error: "Logout failed" },
      { status: 500 }
    );
  }
}
