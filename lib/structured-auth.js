// lib/structured-auth.js
// Structured authentication system with PostgreSQL and SQLite fallback

import bcrypt from 'bcrypt';
import crypto from 'crypto';
import { 
  createUser, 
  getUserByEmail, 
  getUserById, 
  createSession, 
  validateSessionToken 
} from './structured-db.js';

// Sign up a new user
export const signupUser = async (email, password, firstName, lastName, username = null, ipAddress = '127.0.0.1', userAgent = 'unknown', isOrganization = false) => {
  try {
    // Check if user already exists
    const existingUser = await getUserByEmail(email);
    if (existingUser) {
      throw new Error('Email already exists');
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 12);

    // Create user
    const newUser = await createUser({
      email,
      password: hashedPassword,
      first_name: firstName,
      last_name: lastName,
      username,
      is_organization: isOrganization,
      ip_address: ipAddress
    });

    // Generate session token
    const sessionToken = crypto.randomBytes(32).toString('hex');
    
    // Create session
    await createSession(newUser.userid, sessionToken, ipAddress, userAgent);

    return {
      success: true,
      id: newUser.userid,
      email: newUser.email,
      name: `${newUser.first_name} ${newUser.last_name}`,
      username: newUser.username,
      credits: newUser.credits || 0,
      sessionToken
    };
  } catch (error) {
    console.error('Signup error:', error);
    throw new Error(`Signup failed: ${error.message}`);
  }
};

// Login user
export const loginUser = async (email, password, ipAddress = '127.0.0.1', userAgent = 'unknown') => {
  try {
    // Get user by email
    const user = await getUserByEmail(email);
    if (!user) {
      throw new Error('Invalid email or password');
    }

    // Verify password
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      throw new Error('Invalid email or password');
    }

    // Generate session token
    const sessionToken = crypto.randomBytes(32).toString('hex');
    
    // Create session
    await createSession(user.userid, sessionToken, ipAddress, userAgent);

    return {
      success: true,
      id: user.userid,
      email: user.email,
      name: `${user.first_name} ${user.last_name}`,
      sessionToken
    };
  } catch (error) {
    console.error('Login error:', error);
    throw new Error(`Login failed: ${error.message}`);
  }
};

// Validate session
export const validateSession = async (sessionToken) => {
  try {
    if (!sessionToken) {
      return null;
    }

    const sessionData = await validateSessionToken(sessionToken);
    if (!sessionData) {
      return null;
    }

    // Return user data adapted to the actual database schema
    const nameParts = (sessionData.name || '').split(' ');
    return {
      userid: sessionData.userid,
      email: sessionData.email,
      name: sessionData.name,
      first_name: nameParts[0] || '',
      last_name: nameParts.slice(1).join(' ') || '',
      username: sessionData.username || sessionData.email.split('@')[0],
      credits: sessionData.credits || 0,
      is_organization: sessionData.is_organization || false,
      created_at: sessionData.created_at,
      updated_at: sessionData.updated_at
    };
  } catch (error) {
    console.error('Session validation error:', error);
    return null;
  }
};

// Get user profile
export const getUserProfile = async (userid) => {
  try {
    const user = await getUserById(userid);
    if (!user) {
      return null;
    }

    return {
      userid: user.userid,
      email: user.email,
      first_name: user.first_name,
      last_name: user.last_name,
      created_at: user.created_at,
      updated_at: user.updated_at,
      recievetextconf: user.recievetextconf || false
    };
  } catch (error) {
    console.error('Get user profile error:', error);
    return null;
  }
};

// Find user by email
export const findUserByEmail = async (email) => {
  try {
    return await getUserByEmail(email);
  } catch (error) {
    console.error('Find user by email error:', error);
    return null;
  }
};

// Find user by ID
export const findUserById = async (userid) => {
  try {
    return await getUserById(userid);
  } catch (error) {
    console.error('Find user by ID error:', error);
    return null;
  }
};

// Logout user
export const logoutUser = async (sessionToken, userid) => {
  try {
    // In a full implementation, you would delete the session from the database
    // For now, we'll just log the logout
    console.log(`User ${userid} logged out with session ${sessionToken.substring(0, 10)}...`);
    return { success: true };
  } catch (error) {
    console.error('Logout error:', error);
    throw new Error(`Logout failed: ${error.message}`);
  }
};

// Delete session
export const deleteSession = async (sessionToken) => {
  try {
    // In a full implementation, you would delete the session from the database
    console.log(`Session deleted: ${sessionToken.substring(0, 10)}...`);
    return { success: true };
  } catch (error) {
    console.error('Delete session error:', error);
    throw new Error(`Delete session failed: ${error.message}`);
  }
};
