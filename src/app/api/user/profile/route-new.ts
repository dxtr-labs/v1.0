// src/app/api/user/profile/route.ts
// User profile management API using structured database

import { NextRequest, NextResponse } from "next/server";
import { getUserStats } from "../../../../../lib/structured-db.js";
import { validateSession, getUserProfile } from "../../../../../lib/structured-auth.js";

export async function GET(req: NextRequest) {
  try {
    // Get session token from cookies
    const sessionToken = req.cookies.get('session_token')?.value;
    
    if (!sessionToken) {
      return NextResponse.json(
        { success: false, error: "Authentication required" },
        { status: 401 }
      );
    }

    // Validate session and get user
    const user = await validateSession(sessionToken);
    if (!user) {
      return NextResponse.json(
        { success: false, error: "Invalid session" },
        { status: 401 }
      );
    }

    console.log('[DEBUG] User object:', user);

    // Get user profile - using the user object directly since validateSession returns full user data
    const profile = user;
    if (!profile) {
      return NextResponse.json(
        { success: false, error: "User profile not found" },
        { status: 404 }
      );
    }

    // Get user statistics (only for database connections)
    let stats = {
      total_workflows: 0,
      completed_workflows: 0,
      failed_workflows: 0,
      total_executions: 0
    };

    try {
      // Try to get stats from structured database
      console.log('[DEBUG] Getting stats for user ID:', user.userid);
      stats = await getUserStats(user.userid);
    } catch (error) {
      // Stats unavailable (probably using fallback auth)
      console.log('Stats unavailable:', error);
    }

    return NextResponse.json({
      success: true,
      user: {
        ...profile,
        stats
      }
    });

  } catch (error) {
    console.error('Profile API error:', error);
    return NextResponse.json(
      { success: false, error: "Internal server error" },
      { status: 500 }
    );
  }
}
