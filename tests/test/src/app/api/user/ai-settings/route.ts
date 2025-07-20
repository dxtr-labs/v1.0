import { NextRequest, NextResponse } from 'next/server';
import { validateSession } from '../../../../../lib/structured-auth.js';

interface AISettingsRequest {
  selectedModel: string;
  apiKey: string;
}

export async function GET(req: NextRequest) {
  try {
    // Get session token from cookies
    const sessionToken = req.cookies.get('session_token')?.value;
    
    if (!sessionToken) {
      return NextResponse.json(
        { error: "Authentication required" },
        { status: 401 }
      );
    }

    // Validate session and get user
    const user = await validateSession(sessionToken);
    if (!user) {
      return NextResponse.json(
        { error: "Invalid session" },
        { status: 401 }
      );
    }

    // For now, return empty settings - you can extend this to read from database
    const aiSettings = {
      selectedModel: '',
      apiKey: '',
    };

    return NextResponse.json(aiSettings);

  } catch (error) {
    console.error('Error fetching AI settings:', error);
    return NextResponse.json(
      { error: "Failed to fetch AI settings" },
      { status: 500 }
    );
  }
}

export async function POST(req: NextRequest) {
  try {
    // Get session token from cookies
    const sessionToken = req.cookies.get('session_token')?.value;
    
    if (!sessionToken) {
      return NextResponse.json(
        { error: "Authentication required" },
        { status: 401 }
      );
    }

    // Validate session and get user
    const user = await validateSession(sessionToken);
    if (!user) {
      return NextResponse.json(
        { error: "Invalid session" },
        { status: 401 }
      );
    }

    const body = await req.json() as AISettingsRequest;
    const { selectedModel, apiKey } = body;

    if (!selectedModel || !apiKey) {
      return NextResponse.json(
        { error: "Model and API key are required" },
        { status: 400 }
      );
    }

    // Log the settings (in production, save to database)
    console.log(`🤖 Saving AI settings for user ${user.email}:`, { 
      selectedModel, 
      apiKey: apiKey.slice(0, 10) + '...' 
    });
    
    // For now, we'll store in memory or file system
    // In production, you would save to database:
    // await updateUserAISettings(user.userid, selectedModel, apiKey);

    return NextResponse.json({
      success: true,
      message: "AI settings saved successfully"
    });

  } catch (error) {
    console.error('Error saving AI settings:', error);
    return NextResponse.json(
      { error: "Failed to save AI settings" },
      { status: 500 }
    );
  }
}
