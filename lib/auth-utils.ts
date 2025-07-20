// Database configuration and utilities for authentication
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { randomBytes } from 'crypto';

// Environment variables (make sure these are set in your .env.local)
const JWT_SECRET = process.env.JWT_SECRET || 'your-super-secret-jwt-key';
const DATABASE_URL = process.env.DATABASE_URL || 'postgresql://localhost:5432/devlabs';

// Types for our database entities
export interface User {
  user_id: number;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  username: string;
  organization: boolean;
  session_token?: string;
  session_expires?: Date;
  created_at: Date;
  updated_at: Date;
  memory_context?: string;
  service_keys?: Record<string, any>;
  credits: number;
}

export interface CreateUserData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  username?: string;
  organization?: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface WaitlistEntry {
  id: number;
  email: string;
  phone_number?: string;
  created_at: Date;
}

// Utility functions
export class AuthUtils {
  // Hash password
  static async hashPassword(password: string): Promise<string> {
    const saltRounds = 12;
    return bcrypt.hash(password, saltRounds);
  }

  // Verify password
  static async verifyPassword(password: string, hash: string): Promise<boolean> {
    return bcrypt.compare(password, hash);
  }

  // Generate JWT token
  static generateJWT(userId: number, email: string): string {
    return jwt.sign(
      { userId, email },
      JWT_SECRET,
      { expiresIn: '7d' }
    );
  }

  // Verify JWT token
  static verifyJWT(token: string): { userId: number; email: string } | null {
    try {
      return jwt.verify(token, JWT_SECRET) as { userId: number; email: string };
    } catch {
      return null;
    }
  }

  // Generate session token
  static generateSessionToken(): string {
    return randomBytes(32).toString('hex');
  }

  // Generate username from email
  static generateUsername(email: string): string {
    const baseUsername = email.split('@')[0].toLowerCase().replace(/[^a-z0-9]/g, '');
    const randomSuffix = Math.floor(Math.random() * 10000);
    return `${baseUsername}${randomSuffix}`;
  }

  // Validate email format
  static isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  // Validate password strength
  static isValidPassword(password: string): { valid: boolean; message?: string } {
    if (password.length < 8) {
      return { valid: false, message: 'Password must be at least 8 characters long' };
    }
    if (!/(?=.*[a-z])/.test(password)) {
      return { valid: false, message: 'Password must contain at least one lowercase letter' };
    }
    if (!/(?=.*[A-Z])/.test(password)) {
      return { valid: false, message: 'Password must contain at least one uppercase letter' };
    }
    if (!/(?=.*\d)/.test(password)) {
      return { valid: false, message: 'Password must contain at least one number' };
    }
    return { valid: true };
  }
}

// Database connection (you'll need to implement this based on your preferred DB client)
// This is a placeholder - replace with your actual database client
export class DatabaseClient {
  // Add user to waitlist
  static async addToWaitlist(email: string, phoneNumber?: string): Promise<WaitlistEntry> {
    // Implementation depends on your database client
    throw new Error('Database client not implemented');
  }

  // Create new user
  static async createUser(userData: CreateUserData): Promise<User> {
    // Implementation depends on your database client
    throw new Error('Database client not implemented');
  }

  // Find user by email
  static async findUserByEmail(email: string): Promise<User | null> {
    // Implementation depends on your database client
    throw new Error('Database client not implemented');
  }

  // Find user by username
  static async findUserByUsername(username: string): Promise<User | null> {
    // Implementation depends on your database client
    throw new Error('Database client not implemented');
  }

  // Update user session
  static async updateUserSession(userId: number, sessionToken: string, expiresAt: Date): Promise<void> {
    // Implementation depends on your database client
    throw new Error('Database client not implemented');
  }

  // Add credits to user
  static async addCredits(userId: number, amount: number, reason: string, serviceUsed?: string): Promise<void> {
    // Implementation depends on your database client
    throw new Error('Database client not implemented');
  }

  // Get user credits
  static async getUserCredits(userId: number): Promise<number> {
    // Implementation depends on your database client
    throw new Error('Database client not implemented');
  }
}

// API Response types
export interface AuthResponse {
  success: boolean;
  message: string;
  data?: {
    user: Omit<User, 'password'>;
    token: string;
  };
  error?: string;
}
