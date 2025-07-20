// src/app/api/test-auth/route.ts
// Test endpoint to verify authentication system is working

import { NextRequest, NextResponse } from 'next/server';
import { signupUser, loginUser, validateSession } from '../../../../lib/structured-auth.js';

export async function POST(request: NextRequest) {
  try {
    const body: any = await request.json();
    const { action, email, password, firstName, lastName, sessionToken } = body;

    switch (action) {
      case 'signup':
        console.log(`🧪 [TEST-AUTH] Testing signup for: ${email}`);
        const signupResult = await signupUser(
          email,
          password,
          firstName,
          lastName,
          undefined,
          request.ip || '127.0.0.1',
          true
        );
        return NextResponse.json({
          success: true,
          action: 'signup',
          user: {
            id: signupResult.id,
            email: signupResult.email,
            name: signupResult.name
          }
        });

      case 'login':
        console.log(`🧪 [TEST-AUTH] Testing login for: ${email}`);
        const loginResult = await loginUser(
          email,
          password,
          request.ip || '127.0.0.1',
          request.headers.get('user-agent') || 'test-browser'
        );
        return NextResponse.json({
          success: true,
          action: 'login',
          user: {
            id: loginResult.id,
            email: loginResult.email,
            name: loginResult.name,
            sessionToken: loginResult.sessionToken
          }
        });

      case 'validate':
        console.log(`🧪 [TEST-AUTH] Testing session validation`);
        const sessionUser = await validateSession(sessionToken);
        
        if (sessionUser) {
          return NextResponse.json({
            success: true,
            action: 'validate',
            user: {
              id: sessionUser.userid,
              email: sessionUser.email,
              firstName: sessionUser.first_name,
              lastName: sessionUser.last_name
            }
          });
        } else {
          return NextResponse.json({
            success: false,
            action: 'validate',
            error: 'Invalid session'
          }, { status: 401 });
        }

      case 'test-all':
        console.log(`🧪 [TEST-AUTH] Running comprehensive test`);
        const testEmail = `test-${Date.now()}@example.com`;
        const testPassword = 'TestPassword123!';

        // Test signup
        const testSignup = await signupUser(
          testEmail,
          testPassword,
          'Test',
          'User',
          undefined,
          '127.0.0.1',
          true
        );

        // Test login
        const testLogin = await loginUser(
          testEmail,
          testPassword,
          '127.0.0.1',
          'test-browser'
        );

        // Test session validation
        const testSession = await validateSession(testLogin.sessionToken);

        return NextResponse.json({
          success: true,
          action: 'test-all',
          results: {
            signup: {
              success: true,
              user: {
                id: testSignup.id,
                email: testSignup.email,
                name: testSignup.name
              }
            },
            login: {
              success: true,
              user: {
                id: testLogin.id,
                email: testLogin.email,
                name: testLogin.name,
                hasSession: !!testLogin.sessionToken
              }
            },
            sessionValidation: {
              success: !!testSession,
              user: testSession ? {
                id: testSession.userid,
                email: testSession.email
              } : null
            }
          }
        });

      default:
        return NextResponse.json({
          success: false,
          error: 'Invalid action. Use: signup, login, validate, or test-all'
        }, { status: 400 });
    }

  } catch (error: any) {
    console.error('🧪 [TEST-AUTH] Error:', error);
    return NextResponse.json({
      success: false,
      error: error.message,
      stack: error.stack
    }, { status: 500 });
  }
}
