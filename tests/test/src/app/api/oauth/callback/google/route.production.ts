import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';
import { stateManager } from '../../authorize/route';

const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY;

if (!ENCRYPTION_KEY || ENCRYPTION_KEY.length < 32) {
  throw new Error('ENCRYPTION_KEY must be at least 32 characters long');
}

function encrypt(text: string): string {
  const algorithm = 'aes-256-gcm';
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipher(algorithm, ENCRYPTION_KEY);
  
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  
  const authTag = cipher.getAuthTag();
  return iv.toString('hex') + ':' + authTag.toString('hex') + ':' + encrypted;
}

// Production logging utility
function logSecurityEvent(event: string, details: any) {
  const sanitized = {
    ...details,
    // Never log sensitive data
    access_token: details.access_token ? '[REDACTED]' : undefined,
    refresh_token: details.refresh_token ? '[REDACTED]' : undefined,
    client_secret: '[REDACTED]',
    timestamp: new Date().toISOString()
  };
  
  console.log(`[SECURITY] ${event}:`, JSON.stringify(sanitized));
}

export async function GET(request: NextRequest) {
  const startTime = Date.now();
  
  try {
    const searchParams = request.nextUrl.searchParams;
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    const error = searchParams.get('error');
    const errorDescription = searchParams.get('error_description');

    // Handle OAuth errors
    if (error) {
      logSecurityEvent('Google OAuth Error', { 
        error, 
        errorDescription,
        ip: request.headers.get('x-forwarded-for') 
      });
      
      return NextResponse.redirect(
        `${process.env.NEXTAUTH_URL}/dashboard/connectivity?error=oauth_error&details=${encodeURIComponent(error)}`
      );
    }

    // Validate required parameters
    if (!code || !state) {
      logSecurityEvent('Missing OAuth Parameters', { 
        hasCode: !!code, 
        hasState: !!state,
        ip: request.headers.get('x-forwarded-for')
      });
      
      return NextResponse.redirect(
        `${process.env.NEXTAUTH_URL}/dashboard/connectivity?error=missing_params`
      );
    }

    // Validate and retrieve state
    const stateData = stateManager.retrieve(state);
    if (!stateData || stateData.provider !== 'google') {
      logSecurityEvent('Invalid OAuth State', { 
        state: state.substring(0, 8) + '...',
        hasStateData: !!stateData,
        ip: request.headers.get('x-forwarded-for')
      });
      
      return NextResponse.redirect(
        `${process.env.NEXTAUTH_URL}/dashboard/connectivity?error=invalid_state`
      );
    }

    // Exchange code for access token with timeout
    const tokenController = new AbortController();
    const tokenTimeout = setTimeout(() => tokenController.abort(), 10000); // 10 second timeout

    try {
      const tokenResponse = await fetch('https://oauth2.googleapis.com/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'User-Agent': 'DXTR-AutoFlow/1.0',
        },
        body: new URLSearchParams({
          client_id: process.env.GOOGLE_CLIENT_ID!,
          client_secret: process.env.GOOGLE_CLIENT_SECRET!,
          code,
          grant_type: 'authorization_code',
          redirect_uri: `${process.env.NEXTAUTH_URL}/api/oauth/callback/google`,
        }),
        signal: tokenController.signal,
      });

      clearTimeout(tokenTimeout);

      if (!tokenResponse.ok) {
        const errorText = await tokenResponse.text();
        logSecurityEvent('Token Exchange Failed', { 
          status: tokenResponse.status,
          provider: 'google',
          userId: stateData.userId
        });
        
        return NextResponse.redirect(
          `${process.env.NEXTAUTH_URL}/dashboard/connectivity?error=token_exchange_failed`
        );
      }

      const tokenData = await tokenResponse.json();

      // Get user info with timeout
      const userController = new AbortController();
      const userTimeout = setTimeout(() => userController.abort(), 10000);

      const userResponse = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
        headers: {
          'Authorization': `Bearer ${tokenData.access_token}`,
          'User-Agent': 'DXTR-AutoFlow/1.0',
        },
        signal: userController.signal,
      });

      clearTimeout(userTimeout);

      if (!userResponse.ok) {
        logSecurityEvent('User Info Fetch Failed', { 
          status: userResponse.status,
          provider: 'google',
          userId: stateData.userId
        });
        
        return NextResponse.redirect(
          `${process.env.NEXTAUTH_URL}/dashboard/connectivity?error=user_info_failed`
        );
      }

      const userData = await userResponse.json();

      // Store encrypted credentials with metadata
      const credentials = {
        access_token: encrypt(tokenData.access_token),
        refresh_token: tokenData.refresh_token ? encrypt(tokenData.refresh_token) : null,
        expires_at: Date.now() + (tokenData.expires_in * 1000),
        scope: tokenData.scope,
        token_type: tokenData.token_type,
        user_id: userData.id,
        user_email: userData.email,
        user_name: userData.name,
        user_picture: userData.picture,
        verified_email: userData.verified_email,
        created_at: new Date().toISOString(),
        last_refreshed: new Date().toISOString(),
        provider: 'google',
        service: stateData.service,
      };

      // In production, save to secure database with proper indexing
      // await saveCredentialsToDatabase(stateData.userId, credentials);
      
      logSecurityEvent('OAuth Success', {
        provider: 'google',
        service: stateData.service,
        userId: stateData.userId,
        userEmail: userData.email,
        processingTime: Date.now() - startTime
      });

      return NextResponse.redirect(
        `${process.env.NEXTAUTH_URL}/dashboard/connectivity?success=google_connected&service=${stateData.service}`
      );

    } catch (fetchError) {
      clearTimeout(tokenTimeout);
      
      if (fetchError instanceof Error && fetchError.name === 'AbortError') {
        logSecurityEvent('OAuth Timeout', { 
          provider: 'google',
          userId: stateData.userId,
          stage: 'token_exchange'
        });
        
        return NextResponse.redirect(
          `${process.env.NEXTAUTH_URL}/dashboard/connectivity?error=timeout`
        );
      }
      
      throw fetchError;
    }

  } catch (error) {
    logSecurityEvent('OAuth Callback Error', {
      provider: 'google',
      error: error instanceof Error ? error.message : 'Unknown error',
      processingTime: Date.now() - startTime,
      ip: request.headers.get('x-forwarded-for')
    });
    
    return NextResponse.redirect(
      `${process.env.NEXTAUTH_URL}/dashboard/connectivity?error=callback_error`
    );
  }
}
