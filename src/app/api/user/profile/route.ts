// src/app/api/user/profile/route.ts
// User profile management API using structured database

import { NextRequest, NextResponse } from "next/server";
import { getUserStats, getUserChatHistory, getUserMemory, testDatabaseConnection } from "../../../../../lib/structured-db.js";
import { validateSession, getUserProfile } from "../../../../../lib/structured-auth.js";

export async function GET(req: NextRequest) {
  try {
    // Get session token from cookies (using the correct name)
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

    // Get user profile - use the correct ID field
    const userId = user.userid;
    
    const profile = await getUserProfile(userId);
    
    if (!profile) {
      return NextResponse.json(
        { success: false, error: "User profile not found" },
        { status: 404 }
      );
    }

    // Get user statistics
    let stats = {
      total_workflows: 0,
      completed_workflows: 0,
      failed_workflows: 0,
      total_executions: 0,
      saved_workflows: 0,
      total_n8n_logs: 0
    };

    let chatHistory: any[] = [];
    let userMemory: any = {};

    // Check if database is available before trying to fetch database-specific data
    const isDatabaseConnected = await testDatabaseConnection();
    
    if (isDatabaseConnected) {
      try {
        // Get comprehensive user data from structured database
        const [userStats, history, memory] = await Promise.all([
          getUserStats(user.userid),
          getUserChatHistory(user.userid),
          getUserMemory(user.userid)
        ]);

        stats = userStats;
        chatHistory = history;
        userMemory = memory;
      } catch (error) {
        // Database operation failed
        console.log('Database operation failed:', error);
      }
    } else {
      console.log('📝 [PROFILE] Using fallback mode - skipping database-specific data');
    }

    return NextResponse.json({
      success: true,
      user: {
        ...profile,
        stats,
        preferences: {
          recievetextconf: profile.recievetextconf || false,
          preferredNodes: userMemory.preferredNodes || {},
          totalWorkflowsGenerated: userMemory.totalWorkflowsGenerated || 0
        },
        recentActivity: {
          lastWorkflowGenerated: userMemory.lastWorkflowGenerated,
          recentInteractions: chatHistory.slice(-5) // Last 5 interactions
        }
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
