import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';

const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY || 'your-32-character-encryption-key';

function encrypt(text: string): string {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipher('aes-256-cbc', ENCRYPTION_KEY);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return iv.toString('hex') + ':' + encrypted;
}

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    const error = searchParams.get('error');

    if (error) {
      console.error('Microsoft OAuth error:', error);
      return NextResponse.redirect(`${process.env.NEXTAUTH_URL}/dashboard/connectivity?error=oauth_error`);
    }

    if (!code || !state) {
      return NextResponse.redirect(`${process.env.NEXTAUTH_URL}/dashboard/connectivity?error=missing_params`);
    }

    // Exchange code for access token
    const tokenResponse = await fetch('https://login.microsoftonline.com/common/oauth2/v2.0/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        client_id: process.env.MICROSOFT_CLIENT_ID!,
        client_secret: process.env.MICROSOFT_CLIENT_SECRET!,
        code,
        grant_type: 'authorization_code',
        redirect_uri: `${process.env.NEXTAUTH_URL}/api/oauth/callback/microsoft`,
        scope: 'openid profile email User.Read Mail.Send',
      }),
    });

    if (!tokenResponse.ok) {
      const errorData = await tokenResponse.text();
      console.error('Token exchange failed:', errorData);
      return NextResponse.redirect(`${process.env.NEXTAUTH_URL}/dashboard/connectivity?error=token_exchange_failed`);
    }

    const tokenData = await tokenResponse.json();

    // Get user info
    const userResponse = await fetch('https://graph.microsoft.com/v1.0/me', {
      headers: {
        'Authorization': `Bearer ${tokenData.access_token}`,
      },
    });

    if (!userResponse.ok) {
      console.error('Failed to get user info');
      return NextResponse.redirect(`${process.env.NEXTAUTH_URL}/dashboard/connectivity?error=user_info_failed`);
    }

    const userData = await userResponse.json();

    // Store encrypted credentials (in a real app, you'd use a database)
    const credentials = {
      access_token: encrypt(tokenData.access_token),
      refresh_token: tokenData.refresh_token ? encrypt(tokenData.refresh_token) : null,
      expires_at: Date.now() + (tokenData.expires_in * 1000),
      scope: tokenData.scope,
      user_id: userData.id,
      user_email: userData.mail || userData.userPrincipalName,
      user_name: userData.displayName,
    };

    // In a real application, save to database here
    console.log('Microsoft credentials stored for user:', userData.displayName);

    return NextResponse.redirect(`${process.env.NEXTAUTH_URL}/dashboard/connectivity?success=microsoft_connected`);
  } catch (error) {
    console.error('Microsoft OAuth callback error:', error);
    return NextResponse.redirect(`${process.env.NEXTAUTH_URL}/dashboard/connectivity?error=callback_error`);
  }
}
