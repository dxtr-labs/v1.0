import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import crypto from 'crypto';

// TypeScript interfaces
interface CredentialFields {
  [key: string]: string;
}

interface CreateCredentialBody {
  name: string;
  service: string;
  fields: CredentialFields;
}

interface UpdateCredentialBody {
  id: string;
  name: string;
  service: string;
  fields: CredentialFields;
}

interface Credential {
  id: string;
  userId: string;
  name: string;
  service: string;
  fields: CredentialFields;
  createdAt: string;
  updatedAt: string;
}

// In production, use a proper database and encryption service
// This is a simplified implementation for demonstration

const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY || 'default-key-for-development';

interface EncryptedCredential {
  id: string;
  name: string;
  service: string;
  status: 'connected' | 'disconnected' | 'error';
  encryptedFields: string;
  userId: string;
  lastUsed?: string;
  createdAt: string;
  updatedAt: string;
}

// Simple encryption (use proper encryption service in production)
function encrypt(text: string): string {
  const algorithm = 'aes-256-cbc';
  const key = crypto.scryptSync(ENCRYPTION_KEY, 'salt', 32);
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipher(algorithm, key);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return iv.toString('hex') + ':' + encrypted;
}

function decrypt(encryptedText: string): string {
  const algorithm = 'aes-256-cbc';
  const key = crypto.scryptSync(ENCRYPTION_KEY, 'salt', 32);
  const textParts = encryptedText.split(':');
  const iv = Buffer.from(textParts.shift()!, 'hex');
  const encryptedData = textParts.join(':');
  const decipher = crypto.createDecipher(algorithm, key);
  let decrypted = decipher.update(encryptedData, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
}

// Mock database - replace with actual database in production
let credentialsStore: EncryptedCredential[] = [];

export async function GET(request: NextRequest) {
  try {
    const cookieStore = cookies();
    const sessionToken = cookieStore.get('session')?.value;
    
    // Temporarily disabled for development - TODO: Re-enable for production
    // if (!sessionToken) {
    //   return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    // }

    // In production, decode JWT and get user ID
    const userId = 'user_' + sessionToken; // Simplified for demo

    const userCredentials = credentialsStore
      .filter(cred => cred.userId === userId)
      .map(cred => ({
        ...cred,
        fields: JSON.parse(decrypt(cred.encryptedFields))
      }));

    return NextResponse.json({ credentials: userCredentials });
  } catch (error) {
    console.error('Error fetching credentials:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const cookieStore = cookies();
    const sessionToken = cookieStore.get('session')?.value;
    
    // Temporarily disabled for development - TODO: Re-enable for production
    // if (!sessionToken) {
    //   return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    // }

    const userId = 'user_' + sessionToken; // Simplified for demo
    const body: unknown = await request.json();
    
    // Type guard for CreateCredentialBody
    if (!body || typeof body !== 'object' || 
        !('name' in body) || !('service' in body) || !('fields' in body) ||
        typeof (body as any).name !== 'string' ||
        typeof (body as any).service !== 'string' ||
        typeof (body as any).fields !== 'object') {
      return NextResponse.json({ error: 'Invalid request body' }, { status: 400 });
    }
    
    const { name, service, fields } = body as CreateCredentialBody;

    // Validate required fields
    if (!name || !service || !fields) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }

    const encryptedCredential: EncryptedCredential = {
      id: crypto.randomUUID(),
      name,
      service,
      status: 'connected',
      encryptedFields: encrypt(JSON.stringify(fields)),
      userId,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    credentialsStore.push(encryptedCredential);

    // Test the connection
    const connectionStatus = await testConnection(service, fields);
    encryptedCredential.status = connectionStatus ? 'connected' : 'error';
    encryptedCredential.lastUsed = new Date().toISOString();

    return NextResponse.json({ 
      success: true, 
      credential: {
        ...encryptedCredential,
        fields: JSON.parse(decrypt(encryptedCredential.encryptedFields))
      }
    });
  } catch (error) {
    console.error('Error creating credential:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function PUT(request: NextRequest) {
  try {
    const cookieStore = cookies();
    const sessionToken = cookieStore.get('session')?.value;
    
    // Temporarily disabled for development - TODO: Re-enable for production
    // if (!sessionToken) {
    //   return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    // }

    const userId = 'user_' + sessionToken;
    const body: unknown = await request.json();
    
    // Type guard for UpdateCredentialBody
    if (!body || typeof body !== 'object' || 
        !('id' in body) || !('name' in body) || !('service' in body) || !('fields' in body) ||
        typeof (body as any).id !== 'string' ||
        typeof (body as any).name !== 'string' ||
        typeof (body as any).service !== 'string' ||
        typeof (body as any).fields !== 'object') {
      return NextResponse.json({ error: 'Invalid request body' }, { status: 400 });
    }
    
    const { id, name, service, fields } = body as UpdateCredentialBody;

    const credentialIndex = credentialsStore.findIndex(
      cred => cred.id === id && cred.userId === userId
    );

    if (credentialIndex === -1) {
      return NextResponse.json({ error: 'Credential not found' }, { status: 404 });
    }

    const updatedCredential: EncryptedCredential = {
      ...credentialsStore[credentialIndex],
      name,
      service,
      encryptedFields: encrypt(JSON.stringify(fields)),
      updatedAt: new Date().toISOString(),
    };

    // Test the connection
    const connectionStatus = await testConnection(service, fields);
    updatedCredential.status = connectionStatus ? 'connected' : 'error';
    updatedCredential.lastUsed = new Date().toISOString();

    credentialsStore[credentialIndex] = updatedCredential;

    return NextResponse.json({ 
      success: true, 
      credential: {
        ...updatedCredential,
        fields: JSON.parse(decrypt(updatedCredential.encryptedFields))
      }
    });
  } catch (error) {
    console.error('Error updating credential:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const cookieStore = cookies();
    const sessionToken = cookieStore.get('session')?.value;
    
    // Temporarily disabled for development - TODO: Re-enable for production
    // if (!sessionToken) {
    //   return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    // }

    const userId = 'user_' + sessionToken;
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');

    if (!id) {
      return NextResponse.json({ error: 'Credential ID required' }, { status: 400 });
    }

    const initialLength = credentialsStore.length;
    credentialsStore = credentialsStore.filter(
      cred => !(cred.id === id && cred.userId === userId)
    );

    if (credentialsStore.length === initialLength) {
      return NextResponse.json({ error: 'Credential not found' }, { status: 404 });
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error deleting credential:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

// Connection testing function
async function testConnection(service: string, fields: any): Promise<boolean> {
  try {
    switch (service) {
      case 'twilio':
        // Test Twilio connection
        if (fields.accountSid && fields.authToken) {
          // In production, make actual API call to validate
          return true;
        }
        break;
      
      case 'gmail':
        // Test Gmail connection
        if (fields.clientId && fields.clientSecret && fields.refreshToken) {
          // In production, validate OAuth tokens
          return true;
        }
        break;
      
      case 'openai':
        // Test OpenAI connection
        if (fields.apiKey) {
          // In production, make test API call
          return fields.apiKey.startsWith('sk-');
        }
        break;
      
      default:
        // Basic validation for other services
        return Object.values(fields).some(value => value && typeof value === 'string' && value.length > 0);
    }
    
    return false;
  } catch (error) {
    console.error(`Error testing ${service} connection:`, error);
    return false;
  }
}
