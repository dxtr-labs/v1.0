'use server';

import { cookies } from 'next/headers';
import { sql } from '@vercel/postgres';
import bcrypt from 'bcryptjs';
import { v4 as uuidv4 } from 'uuid';
import type { User, AuthResponse, SignupData, LoginData } from '@/types/auth';
import type { QueryResultRow } from '@vercel/postgres';

const SALT_ROUNDS = 10;
const SESSION_DURATION = 30 * 24 * 60 * 60 * 1000; // 30 days

type SafeUser = Omit<User, 'password'>;

function convertToSafeUser(row: QueryResultRow): SafeUser {
  return {
    user_id: row.user_id as string,
    email: row.email as string,
    first_name: row.first_name as string,
    last_name: row.last_name as string,
    middle_name: row.middle_name as string | undefined,
    username: row.username as string,
    organization: row.organization as boolean,
    session_token: row.session_token as string,
    session_expires: new Date(row.session_expires),
    created_at: new Date(row.created_at),
    updated_at: new Date(row.updated_at),
    memory_context: row.memory_context as string | undefined,
    service_keys: row.service_keys as Record<string, any> | undefined,
    credits: row.credits as number,
    want_notifications: row.want_notifications as boolean | undefined
  };
}

async function handleLogin(data: LoginData): Promise<AuthResponse> {
  try {
    // Check if user exists
    const result = await sql`
      SELECT * FROM users WHERE email = ${data.email};
    `;

    if (result.rows.length === 0) {
      return {
        success: false,
        error: 'Invalid email or password'
      };
    }

    const user = result.rows[0];
    const validPassword = await bcrypt.compare(data.password, user.password as string);

    if (!validPassword) {
      return {
        success: false,
        error: 'Invalid email or password'
      };
    }

    // Generate new session token and expiry
    const session_token = uuidv4();
    const session_expires = new Date(Date.now() + SESSION_DURATION);

    // Update user's session
    await sql`
      UPDATE users 
      SET session_token = ${session_token}, 
          session_expires = ${session_expires.toISOString()},
          updated_at = NOW() 
      WHERE user_id = ${user.user_id};
    `;

    // Set cookie
    cookies().set('session_token', session_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      expires: session_expires
    });

    const safeUser = convertToSafeUser(user);

    return {
      success: true,
      user: safeUser,
      session_token
    };
  } catch (error) {
    console.error('Login error:', error);
    return {
      success: false,
      error: 'An error occurred during login'
    };
  }
}

async function handleSignup(data: SignupData): Promise<AuthResponse> {
  try {
    // Check if user already exists
    const existingUser = await sql`
      SELECT email FROM users WHERE email = ${data.email};
    `;

    if (existingUser.rows.length > 0) {
      return {
        success: false,
        error: 'Email already exists'
      };
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(data.password, SALT_ROUNDS);

    // Generate session token
    const session_token = uuidv4();
    const user_id = uuidv4();
    const session_expires = new Date(Date.now() + SESSION_DURATION);

    // Generate username from email
    const username = data.email.split('@')[0] + '_' + Math.random().toString(36).substring(2, 7);

    // Create new user
    const result = await sql`
      INSERT INTO users (
        user_id, email, password, first_name, last_name, middle_name,
        username, organization, session_token, session_expires,
        created_at, updated_at, credits, want_notifications
      ) VALUES (
        ${user_id}, ${data.email}, ${hashedPassword}, ${data.first_name}, ${data.last_name},
        ${data.middle_name || null}, ${username}, ${false},
        ${session_token}, ${session_expires.toISOString()}, NOW(), NOW(), 100,
        ${data.want_notifications || false}
      )
      RETURNING *;
    `;

    const newUser = convertToSafeUser(result.rows[0]);

    // Set cookie
    cookies().set('session_token', session_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      expires: session_expires
    });

    return {
      success: true,
      user: newUser,
      session_token
    };
  } catch (error) {
    console.error('Signup error:', error);
    return {
      success: false,
      error: 'An error occurred during signup'
    };
  }
}

export async function handleAuth(formData: FormData): Promise<AuthResponse> {
  try {
    const type = formData.get('type');
    const email = formData.get('email')?.toString();
    const password = formData.get('password')?.toString();

    if (!email || !password) {
      return { success: false, error: 'Email and password are required' };
    }

    if (type === 'login') {
      return handleLogin({ email, password });
    }
    
    if (type === 'signup') {
      const first_name = formData.get('first_name')?.toString();
      const last_name = formData.get('last_name')?.toString();
      const middle_name = formData.get('middle_name')?.toString();
      const want_notifications = formData.get('want_notifications') === 'true';

      if (!first_name || !last_name) {
        return { success: false, error: 'First and last name are required' };
      }

      return handleSignup({
        email,
        password,
        first_name,
        last_name,
        middle_name,
        want_notifications
      });
    }

    return { success: false, error: 'Invalid auth type' };
  } catch (error) {
    console.error('Auth error:', error);
    return { success: false, error: 'An unexpected error occurred' };
  }
}


