import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

// Environment variable mappings for common services
const ENV_MAPPINGS = {
  openai: {
    apiKey: 'OPENAI_API_KEY',
    organizationId: 'OPENAI_ORG_ID'
  },
  twilio: {
    accountSid: 'TWILIO_ACCOUNT_SID',
    authToken: 'TWILIO_AUTH_TOKEN',
    phoneNumber: 'TWILIO_PHONE_NUMBER'
  },
  gmail: {
    clientId: 'GMAIL_CLIENT_ID',
    clientSecret: 'GMAIL_CLIENT_SECRET',
    refreshToken: 'GMAIL_REFRESH_TOKEN'
  },
  slack: {
    botToken: 'SLACK_BOT_TOKEN',
    signingSecret: 'SLACK_SIGNING_SECRET'
  },
  telegram: {
    botToken: 'TELEGRAM_BOT_TOKEN',
    chatId: 'TELEGRAM_CHAT_ID'
  },
  postgres: {
    host: 'POSTGRES_HOST',
    port: 'POSTGRES_PORT',
    database: 'POSTGRES_DB',
    username: 'POSTGRES_USER',
    password: 'POSTGRES_PASSWORD'
  },
  mysql: {
    host: 'MYSQL_HOST',
    port: 'MYSQL_PORT',
    database: 'MYSQL_DATABASE',
    username: 'MYSQL_USER',
    password: 'MYSQL_PASSWORD'
  }
};

export async function GET(request: NextRequest) {
  try {
    const cookieStore = cookies();
    const sessionToken = cookieStore.get('session')?.value;
    
    if (!sessionToken) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Get available environment variables for all services
    const environment: { [service: string]: { [field: string]: string } } = {};

    Object.entries(ENV_MAPPINGS).forEach(([service, mapping]) => {
      const serviceEnv: { [field: string]: string } = {};
      
      Object.entries(mapping).forEach(([field, envVar]) => {
        const value = process.env[envVar];
        if (value) {
          // Mask sensitive values for display
          serviceEnv[field] = value.length > 10 
            ? `${value.substring(0, 8)}...` 
            : '***';
        }
      });

      if (Object.keys(serviceEnv).length > 0) {
        environment[service] = serviceEnv;
      }
    });

    return NextResponse.json({ environment });
  } catch (error) {
    console.error('Error fetching environment credentials:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

// Get full environment variables for a specific service (for internal use)
export async function POST(request: NextRequest) {
  try {
    const cookieStore = cookies();
    const sessionToken = cookieStore.get('session')?.value;
    
    if (!sessionToken) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { service } = await request.json();
    
    if (!service || !ENV_MAPPINGS[service as keyof typeof ENV_MAPPINGS]) {
      return NextResponse.json({ error: 'Invalid service' }, { status: 400 });
    }

    const mapping = ENV_MAPPINGS[service as keyof typeof ENV_MAPPINGS];
    const credentials: { [key: string]: string } = {};

    Object.entries(mapping).forEach(([field, envVar]) => {
      const value = process.env[envVar];
      if (value) {
        credentials[field] = value;
      }
    });

    return NextResponse.json({ credentials });
  } catch (error) {
    console.error('Error fetching service environment credentials:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
