import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function POST(request: NextRequest) {
  try {
    const cookieStore = cookies();
    const sessionToken = cookieStore.get('session')?.value;
    
    if (!sessionToken) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { service, fields } = await request.json();
    
    if (!service || !fields) {
      return NextResponse.json({ error: 'Missing service or fields' }, { status: 400 });
    }

    const success = await testServiceConnection(service, fields);
    
    return NextResponse.json({ success });
  } catch (error) {
    console.error('Error testing connection:', error);
    return NextResponse.json({ success: false, error: 'Connection test failed' });
  }
}

async function testServiceConnection(service: string, fields: any): Promise<boolean> {
  try {
    switch (service) {
      case 'openai':
        return await testOpenAIConnection(fields);
      
      case 'twilio':
        return await testTwilioConnection(fields);
      
      case 'gmail':
        return await testGmailConnection(fields);
      
      case 'slack':
        return await testSlackConnection(fields);
      
      case 'telegram':
        return await testTelegramConnection(fields);
      
      case 'postgres':
        return await testPostgresConnection(fields);
      
      case 'mysql':
        return await testMySQLConnection(fields);
      
      default:
        // Basic validation for other services
        return Object.values(fields).some(value => value && typeof value === 'string' && value.length > 0);
    }
  } catch (error) {
    console.error(`Error testing ${service} connection:`, error);
    return false;
  }
}

async function testOpenAIConnection(fields: any): Promise<boolean> {
  try {
    if (!fields.apiKey || !fields.apiKey.startsWith('sk-')) {
      return false;
    }

    const response = await fetch('https://api.openai.com/v1/models', {
      headers: {
        'Authorization': `Bearer ${fields.apiKey}`,
        'Content-Type': 'application/json',
      },
    });

    return response.ok;
  } catch {
    return false;
  }
}

async function testTwilioConnection(fields: any): Promise<boolean> {
  try {
    if (!fields.accountSid || !fields.authToken) {
      return false;
    }

    // Test Twilio API by fetching account info
    const auth = Buffer.from(`${fields.accountSid}:${fields.authToken}`).toString('base64');
    const response = await fetch(`https://api.twilio.com/2010-04-01/Accounts/${fields.accountSid}.json`, {
      headers: {
        'Authorization': `Basic ${auth}`,
      },
    });

    return response.ok;
  } catch {
    return false;
  }
}

async function testGmailConnection(fields: any): Promise<boolean> {
  try {
    if (!fields.clientId || !fields.clientSecret || !fields.refreshToken) {
      return false;
    }

    // Test by refreshing the access token
    const response = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        client_id: fields.clientId,
        client_secret: fields.clientSecret,
        refresh_token: fields.refreshToken,
        grant_type: 'refresh_token',
      }),
    });

    return response.ok;
  } catch {
    return false;
  }
}

async function testSlackConnection(fields: any): Promise<boolean> {
  try {
    if (!fields.botToken) {
      return false;
    }

    // Test Slack API
    const response = await fetch('https://slack.com/api/auth.test', {
      headers: {
        'Authorization': `Bearer ${fields.botToken}`,
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json();
    return data.ok === true;
  } catch {
    return false;
  }
}

async function testTelegramConnection(fields: any): Promise<boolean> {
  try {
    if (!fields.botToken) {
      return false;
    }

    // Test Telegram Bot API
    const response = await fetch(`https://api.telegram.org/bot${fields.botToken}/getMe`);
    const data = await response.json();
    
    return data.ok === true;
  } catch {
    return false;
  }
}

async function testPostgresConnection(fields: any): Promise<boolean> {
  try {
    if (!fields.host || !fields.database || !fields.username || !fields.password) {
      return false;
    }

    // In a real implementation, you would use a PostgreSQL client library
    // For now, just validate the required fields are present
    return fields.host.length > 0 && fields.database.length > 0;
  } catch {
    return false;
  }
}

async function testMySQLConnection(fields: any): Promise<boolean> {
  try {
    if (!fields.host || !fields.database || !fields.username || !fields.password) {
      return false;
    }

    // In a real implementation, you would use a MySQL client library
    // For now, just validate the required fields are present
    return fields.host.length > 0 && fields.database.length > 0;
  } catch {
    return false;
  }
}
