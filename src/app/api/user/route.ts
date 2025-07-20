// API route for user management
// Handles user authentication, data updates, and retrieval
// Updated to use structured-auth with SQLite fallback

import { NextRequest, NextResponse } from 'next/server';
import { validateSession, findUserByEmail, findUserById } from '../../../../lib/structured-auth.js';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const email = searchParams.get('email');
    const userId = searchParams.get('userId');
    
    if (!email && !userId) {
      return NextResponse.json(
        { error: 'Email or userId is required' },
        { status: 400 }
      );
    }
    
    let user;
    if (userId) {
      user = await findUserById(userId);
    } else {
      user = await findUserByEmail(email!);
    }
    
    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    // Return basic user info
    return NextResponse.json({
      success: true,
      user: {
        userid: user.userid,
        email: user.email,
        first_name: user.first_name,
        last_name: user.last_name
      }
    });
    
  } catch (error) {
    console.error('Error in user GET:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json() as any;
    const { action, email } = body;
    
    switch (action) {
      case 'getOrCreate':
        if (!email) {
          return NextResponse.json(
            { error: 'Email is required' },
            { status: 400 }
          );
        }
        
        const user = await findUserByEmail(email);
        if (!user) {
          return NextResponse.json({
            success: false,
            message: 'User not found. Please sign up first.',
            needsSignup: true
          });
        }
        
        return NextResponse.json({
          success: true,
          user: {
            userid: user.userid,
            email: user.email,
            first_name: user.first_name,
            last_name: user.last_name
          },
          created: false
        });
        
      default:
        return NextResponse.json(
          { error: 'Invalid action or action not supported' },
          { status: 400 }
        );
    }
    
  } catch (error) {
    console.error('Error in user POST:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function PUT(request: NextRequest) {
  try {
    return NextResponse.json(
      { error: 'User updates not implemented yet' },
      { status: 501 }
    );
    
  } catch (error) {
    console.error('Error in user PUT:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function DELETE(request: NextRequest) {
  try {
    return NextResponse.json(
      { error: 'User deletion not implemented yet' },
      { status: 501 }
    );
    
  } catch (error) {
    console.error('Error in user DELETE:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
