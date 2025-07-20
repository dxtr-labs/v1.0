// src/app/api/auth/session/route.ts
// Session verification API endpoint

import { NextRequest, NextResponse } from "next/server";
import { validateSession } from "../../../../../lib/structured-auth.js";

export async function GET(req: NextRequest) {
  try {
    // Get session token from cookies
    const sessionToken = req.cookies.get('session_token')?.value;
    
    if (!sessionToken) {
      return NextResponse.json(
        { success: false, error: "No session token found" },
        { status: 401 }
      );
    }

    // Verify the session
    const user = await validateSession(sessionToken);
    
    if (!user) {
      return NextResponse.json(
        { success: false, error: "Invalid session" },
        { status: 401 }
      );
    }

    return NextResponse.json({
      success: true,
      user: {
        id: user.userid,
        email: user.email,
        name: `${user.first_name} ${user.last_name}`.trim(),
        firstName: user.first_name,
        lastName: user.last_name,
        credits: 0
      }
    });

  } catch (error: any) {
    console.error('Session verification error:', error);
    return NextResponse.json(
      { success: false, error: "Session verification failed" },
      { status: 500 }
    );
  }
}
