import { NextRequest, NextResponse } from 'next/server';
import { oauthStates } from '../../authorize/route';
import crypto from 'crypto';

const ENCRYPTION_KEY = process.env.CREDENTIAL_ENCRYPTION_KEY || 'default-key-change-in-production';

interface OAuthCredential {
  id: string;
  name: string;
  service: string;
  provider: string;
  status: 'connected' | 'disconnected' | 'error';
  accessToken: string;
  refreshToken?: string;
  expiresAt?: number;
  userId: string;
  userInfo?: any;
  createdAt: string;
  updatedAt: string;
}

// Mock storage - replace with database in production
let oauthCredentials: OAuthCredential[] = [];

function encrypt(text: string): string {
  const algorithm = 'aes-256-cbc';
  const key = crypto.scryptSync(ENCRYPTION_KEY, 'salt', 32);
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipher(algorithm, key);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return iv.toString('hex') + ':' + encrypted;
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const code = searchParams.get('code');
  const state = searchParams.get('state');
  const error = searchParams.get('error');

  if (error) {
    return NextResponse.redirect(`${process.env.NEXT_PUBLIC_BASE_URL}/dashboard/connectivity?error=${encodeURIComponent(error)}`);
  }

  if (!code || !state) {
    return NextResponse.redirect(`${process.env.NEXT_PUBLIC_BASE_URL}/dashboard/connectivity?error=invalid_callback`);
  }

  // Verify state parameter
  const stateData = oauthStates.get(state);
  if (!stateData) {
    return NextResponse.redirect(`${process.env.NEXT_PUBLIC_BASE_URL}/dashboard/connectivity?error=invalid_state`);
  }

  // Clean up state
  oauthStates.delete(state);

  try {
    const tokenData = await exchangeCodeForToken('google', code);
    const userInfo = await getUserInfo('google', tokenData.access_token);

    // Store the OAuth credential
    const credential: OAuthCredential = {
      id: crypto.randomUUID(),
      name: `Google ${stateData.service.charAt(0).toUpperCase() + stateData.service.slice(1)} - ${userInfo.email}`,
      service: stateData.service,
      provider: 'google',
      status: 'connected',
      accessToken: encrypt(tokenData.access_token),
      refreshToken: tokenData.refresh_token ? encrypt(tokenData.refresh_token) : undefined,
      expiresAt: tokenData.expires_in ? Date.now() + (tokenData.expires_in * 1000) : undefined,
      userId: stateData.userId,
      userInfo,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    oauthCredentials.push(credential);

    return NextResponse.redirect(`${process.env.NEXT_PUBLIC_BASE_URL}/dashboard/connectivity?success=google_connected`);
  } catch (error) {
    console.error('OAuth callback error:', error);
    return NextResponse.redirect(`${process.env.NEXT_PUBLIC_BASE_URL}/dashboard/connectivity?error=oauth_failed`);
  }
}

async function exchangeCodeForToken(provider: string, code: string) {
  const config = {
    google: {
      tokenUrl: 'https://oauth2.googleapis.com/token',
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      redirectUri: `${process.env.NEXT_PUBLIC_BASE_URL}/api/oauth/callback/google`,
    }
  };

  const providerConfig = config[provider as keyof typeof config];
  
  const response = await fetch(providerConfig.tokenUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      client_id: providerConfig.clientId,
      client_secret: providerConfig.clientSecret,
      code,
      redirect_uri: providerConfig.redirectUri,
    }),
  });

  if (!response.ok) {
    throw new Error(`Token exchange failed: ${response.statusText}`);
  }

  return await response.json();
}

async function getUserInfo(provider: string, accessToken: string) {
  const userInfoUrls = {
    google: 'https://www.googleapis.com/oauth2/v2/userinfo',
  };

  const url = userInfoUrls[provider as keyof typeof userInfoUrls];
  
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch user info: ${response.statusText}`);
  }

  return await response.json();
}
