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
      console.error('Slack OAuth error:', error);
      return NextResponse.redirect(`${process.env.NEXTAUTH_URL}/dashboard/connectivity?error=oauth_error`);
    }

    if (!code || !state) {
      return NextResponse.redirect(`${process.env.NEXTAUTH_URL}/dashboard/connectivity?error=missing_params`);
    }

    // Exchange code for access token
    const tokenResponse = await fetch('https://slack.com/api/oauth.v2.access', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        client_id: process.env.SLACK_CLIENT_ID!,
        client_secret: process.env.SLACK_CLIENT_SECRET!,
        code,
        redirect_uri: `${process.env.NEXTAUTH_URL}/api/oauth/callback/slack`,
      }),
    });

    if (!tokenResponse.ok) {
      const errorData = await tokenResponse.text();
      console.error('Token exchange failed:', errorData);
      return NextResponse.redirect(`${process.env.NEXTAUTH_URL}/dashboard/connectivity?error=token_exchange_failed`);
    }

    const tokenData = await tokenResponse.json();

    if (!tokenData.ok) {
      console.error('Slack OAuth error:', tokenData.error);
      return NextResponse.redirect(`${process.env.NEXTAUTH_URL}/dashboard/connectivity?error=slack_oauth_error`);
    }

    // Get user info
    const userResponse = await fetch('https://slack.com/api/users.identity', {
      headers: {
        'Authorization': `Bearer ${tokenData.authed_user.access_token}`,
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
      bot_user_id: tokenData.bot_user_id,
      team_id: tokenData.team.id,
      team_name: tokenData.team.name,
      user_access_token: encrypt(tokenData.authed_user.access_token),
      user_id: userData.user.id,
      user_name: userData.user.name,
      user_email: userData.user.email,
      scope: tokenData.scope,
    };

    // In a real application, save to database here
    console.log('Slack credentials stored for team:', tokenData.team.name);

    return NextResponse.redirect(`${process.env.NEXTAUTH_URL}/dashboard/connectivity?success=slack_connected`);
  } catch (error) {
    console.error('Slack OAuth callback error:', error);
    return NextResponse.redirect(`${process.env.NEXTAUTH_URL}/dashboard/connectivity?error=callback_error`);
  }
}
