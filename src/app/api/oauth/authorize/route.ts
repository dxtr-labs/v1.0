import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import crypto from 'crypto';

// Validate required environment variables at startup
const requiredEnvVars = [
  'NEXTAUTH_URL',
  'NEXTAUTH_SECRET',
  'ENCRYPTION_KEY'
];

for (const envVar of requiredEnvVars) {
  if (!process.env[envVar]) {
    throw new Error(`Missing required environment variable: ${envVar}`);
  }
}

// OAuth configuration for different services
const OAUTH_CONFIGS = {
  google: {
    clientId: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    redirectUri: `${process.env.NEXTAUTH_URL}/api/oauth/callback/google`,
    authUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    tokenUrl: 'https://oauth2.googleapis.com/token',
    scopes: {
      gmail: ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly'],
      drive: ['https://www.googleapis.com/auth/drive.file'],
      calendar: ['https://www.googleapis.com/auth/calendar']
    }
  },
  microsoft: {
    clientId: process.env.MICROSOFT_CLIENT_ID,
    clientSecret: process.env.MICROSOFT_CLIENT_SECRET,
    redirectUri: `${process.env.NEXTAUTH_URL}/api/oauth/callback/microsoft`,
    authUrl: 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
    tokenUrl: 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
    scopes: {
      outlook: ['https://graph.microsoft.com/mail.send', 'https://graph.microsoft.com/mail.read'],
      onedrive: ['https://graph.microsoft.com/files.readwrite']
    }
  },
  slack: {
    clientId: process.env.SLACK_CLIENT_ID,
    clientSecret: process.env.SLACK_CLIENT_SECRET,
    redirectUri: `${process.env.NEXTAUTH_URL}/api/oauth/callback/slack`,
    authUrl: 'https://slack.com/oauth/v2/authorize',
    tokenUrl: 'https://slack.com/api/oauth.v2.access',
    scopes: ['chat:write', 'channels:read', 'users:read']
  },
  twitter: {
    clientId: process.env.TWITTER_CLIENT_ID,
    clientSecret: process.env.TWITTER_CLIENT_SECRET,
    redirectUri: `${process.env.NEXTAUTH_URL}/api/oauth/callback/twitter`,
    authUrl: 'https://twitter.com/i/oauth2/authorize',
    tokenUrl: 'https://api.twitter.com/2/oauth2/token',
    scopes: ['tweet.read', 'tweet.write', 'users.read']
  },
  linkedin: {
    clientId: process.env.LINKEDIN_CLIENT_ID,
    clientSecret: process.env.LINKEDIN_CLIENT_SECRET,
    redirectUri: `${process.env.NEXTAUTH_URL}/api/oauth/callback/linkedin`,
    authUrl: 'https://www.linkedin.com/oauth/v2/authorization',
    tokenUrl: 'https://www.linkedin.com/oauth/v2/accessToken',
    scopes: ['r_liteprofile', 'w_member_social']
  },
  github: {
    clientId: process.env.GITHUB_CLIENT_ID,
    clientSecret: process.env.GITHUB_CLIENT_SECRET,
    redirectUri: `${process.env.NEXTAUTH_URL}/api/oauth/callback/github`,
    authUrl: 'https://github.com/login/oauth/authorize',
    tokenUrl: 'https://github.com/login/oauth/access_token',
    scopes: ['repo', 'user:email']
  },
  facebook: {
    clientId: process.env.FACEBOOK_CLIENT_ID,
    clientSecret: process.env.FACEBOOK_CLIENT_SECRET,
    redirectUri: `${process.env.NEXTAUTH_URL}/api/oauth/callback/facebook`,
    authUrl: 'https://www.facebook.com/v18.0/dialog/oauth',
    tokenUrl: 'https://graph.facebook.com/v18.0/oauth/access_token',
    scopes: {
      instagram: ['instagram_basic', 'instagram_content_publish', 'pages_show_list'],
      facebook: ['pages_manage_posts', 'pages_read_engagement']
    }
  },
  dropbox: {
    clientId: process.env.DROPBOX_CLIENT_ID,
    clientSecret: process.env.DROPBOX_CLIENT_SECRET,
    redirectUri: `${process.env.NEXTAUTH_URL}/api/oauth/callback/dropbox`,
    authUrl: 'https://www.dropbox.com/oauth2/authorize',
    tokenUrl: 'https://api.dropboxapi.com/oauth2/token',
    scopes: ['files.content.write', 'files.content.read']
  }
};

// State management - In production, use Redis or a database
class OAuthStateManager {
  private states = new Map<string, { 
    provider: string; 
    service: string; 
    userId: string; 
    timestamp: number;
    nonce: string;
  }>();
  
  // Clean up expired states every 5 minutes
  private cleanupInterval: NodeJS.Timeout;

  constructor() {
    this.cleanupInterval = setInterval(() => {
      this.cleanup();
    }, 5 * 60 * 1000);
  }

  store(state: string, data: { provider: string; service: string; userId: string }) {
    const nonce = crypto.randomBytes(16).toString('hex');
    this.states.set(state, {
      ...data,
      timestamp: Date.now(),
      nonce
    });
    return nonce;
  }

  retrieve(state: string): { provider: string; service: string; userId: string; nonce: string } | null {
    const data = this.states.get(state);
    if (!data) return null;

    // Check if expired (10 minutes)
    if (Date.now() - data.timestamp > 10 * 60 * 1000) {
      this.states.delete(state);
      return null;
    }

    // Remove after retrieval (one-time use)
    this.states.delete(state);
    return data;
  }

  private cleanup() {
    const now = Date.now();
    for (const [key, value] of this.states.entries()) {
      if (now - value.timestamp > 10 * 60 * 1000) {
        this.states.delete(key);
      }
    }
  }

  destroy() {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
  }
}

const stateManager = new OAuthStateManager();

export async function GET(request: NextRequest) {
  try {
    // Rate limiting
    const clientIP = request.headers.get('x-forwarded-for') || 
                    request.headers.get('x-real-ip') || 
                    'unknown';
    
    if (!rateLimiter.isAllowed(clientIP)) {
      return NextResponse.json({ 
        error: 'Too Many Requests',
        message: 'Rate limit exceeded. Please try again later.' 
      }, { status: 429 });
    }

    const { searchParams } = new URL(request.url);
    const provider = searchParams.get('provider');
    const service = searchParams.get('service');

    // Validate required parameters
    if (!provider || !service) {
      return NextResponse.json({ 
        error: 'Bad Request',
        message: 'Provider and service parameters are required' 
      }, { status: 400 });
    }

    // Validate provider exists
    const config = OAUTH_CONFIGS[provider as keyof typeof OAUTH_CONFIGS];
    if (!config) {
      return NextResponse.json({ 
        error: 'Bad Request',
        message: `Unsupported provider: ${provider}` 
      }, { status: 400 });
    }

    // Check if provider credentials are configured
    if (!config.clientId || !config.clientSecret) {
      console.error(`OAuth credentials not configured for provider: ${provider}`);
      return NextResponse.json({ 
        error: 'Configuration Error',
        message: `OAuth credentials not configured for ${provider}` 
      }, { status: 500 });
    }

    // Get and validate session
    const cookieStore = cookies();
    const sessionToken = cookieStore.get('session')?.value;
    
    // Temporarily disabled for development - TODO: Re-enable for production
    // if (!sessionToken) {
    //   return NextResponse.json({ 
    //     error: 'Unauthorized',
    //     message: 'Authentication required' 
    //   }, { status: 401 });
    // }

    // Generate cryptographically secure state parameter
    const state = crypto.randomBytes(32).toString('hex');
    const userId = sessionToken ? 
      `user_${crypto.createHash('sha256').update(sessionToken).digest('hex').substring(0, 16)}` : 
      'dev_user_' + crypto.randomBytes(8).toString('hex');

    // Store state with additional security
    const nonce = stateManager.store(state, {
      provider,
      service,
      userId
    });

    // Build authorization URL with proper validation
    const authUrl = new URL(config.authUrl);
    authUrl.searchParams.set('client_id', config.clientId);
    authUrl.searchParams.set('redirect_uri', config.redirectUri);
    authUrl.searchParams.set('response_type', 'code');
    authUrl.searchParams.set('state', state);
    
    // Set scopes based on service type
    let scopesToUse: string[] = [];
    if (typeof config.scopes === 'object' && service in config.scopes) {
      scopesToUse = config.scopes[service as keyof typeof config.scopes] as string[];
    } else if (Array.isArray(config.scopes)) {
      scopesToUse = config.scopes;
    }
    
    if (scopesToUse.length > 0) {
      authUrl.searchParams.set('scope', scopesToUse.join(' '));
    }

    // Provider-specific parameters for better security and UX
    if (provider === 'google') {
      authUrl.searchParams.set('access_type', 'offline');
      authUrl.searchParams.set('prompt', 'consent');
      authUrl.searchParams.set('include_granted_scopes', 'true');
    }

    if (provider === 'microsoft') {
      authUrl.searchParams.set('response_mode', 'query');
      authUrl.searchParams.set('prompt', 'consent');
    }

    if (provider === 'github') {
      authUrl.searchParams.set('allow_signup', 'true');
    }

    // Add PKCE for enhanced security (where supported)
    if (provider === 'twitter') {
      const codeVerifier = crypto.randomBytes(32).toString('base64url');
      const codeChallenge = crypto.createHash('sha256').update(codeVerifier).digest('base64url');
      authUrl.searchParams.set('code_challenge', codeChallenge);
      authUrl.searchParams.set('code_challenge_method', 'S256');
      
      // Store code verifier for later use (in production, use secure storage)
      stateManager.store(`${state}_verifier`, {
        provider,
        service: 'code_verifier',
        userId: codeVerifier
      });
    }

    return NextResponse.json({ 
      authUrl: authUrl.toString(),
      state,
      provider,
      service
    });

  } catch (error) {
    console.error('OAuth authorization error:', error);
    return NextResponse.json({ 
      error: 'Internal Server Error',
      message: 'Failed to generate authorization URL' 
    }, { status: 500 });
  }
}

// Rate limiting - simple in-memory implementation
class RateLimiter {
  private requests = new Map<string, number[]>();
  private readonly maxRequests = 10; // 10 requests
  private readonly windowMs = 15 * 60 * 1000; // per 15 minutes

  isAllowed(identifier: string): boolean {
    const now = Date.now();
    const windowStart = now - this.windowMs;
    
    if (!this.requests.has(identifier)) {
      this.requests.set(identifier, [now]);
      return true;
    }

    const requestTimes = this.requests.get(identifier)!;
    
    // Remove old requests outside the window
    const validRequests = requestTimes.filter(time => time > windowStart);
    
    if (validRequests.length >= this.maxRequests) {
      return false;
    }

    validRequests.push(now);
    this.requests.set(identifier, validRequests);
    return true;
  }

  cleanup() {
    const now = Date.now();
    const windowStart = now - this.windowMs;
    
    for (const [key, times] of this.requests.entries()) {
      const validTimes = times.filter(time => time > windowStart);
      if (validTimes.length === 0) {
        this.requests.delete(key);
      } else {
        this.requests.set(key, validTimes);
      }
    }
  }
}

const rateLimiter = new RateLimiter();

// Cleanup rate limiter every 5 minutes
setInterval(() => {
  rateLimiter.cleanup();
}, 5 * 60 * 1000);

export { stateManager, rateLimiter };
