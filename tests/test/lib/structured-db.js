// lib/structured-db.js
// Structured database operations for PostgreSQL with comprehensive schema

import { Pool } from 'pg';
import crypto from 'crypto';

// PostgreSQL connection pool using environment variables
const pgPool = new Pool({
  user: process.env.PGUSER || 'postgres',
  host: process.env.PGHOST || '34.44.98.81',
  database: process.env.PGDATABASE || 'automation',
  password: process.env.PGPASSWORD || 'devhouse',
  port: parseInt(process.env.PGPORT || '5432'),
  ssl: false, // Set to true if your database requires SSL
});

// Test database connection
export const testDatabaseConnection = async () => {
  try {
    console.log('Testing PostgreSQL connection...');
    const client = await pgPool.connect();
    await client.query('SELECT 1');
    client.release();
    console.log('✅ PostgreSQL connection successful');
    return true;
  } catch (error) {
    console.log('❌ PostgreSQL connection failed:', error.message);
    return false;
  }
};

// Create user in waitlist
export const addToWaitlist = async (email, phone = null) => {
  const client = await pgPool.connect();
  try {
    const result = await client.query(`
      INSERT INTO waitlist (email, phone)
      VALUES ($1, $2)
      RETURNING id, email, phone, created_at
    `, [email, phone]);
    
    return result.rows[0];
  } catch (error) {
    if (error.code === '23505') { // Unique violation
      throw new Error('Email already exists in waitlist');
    }
    throw error;
  } finally {
    client.release();
  }
};

// Create user account
export const createUser = async (userData) => {
  const { email, password, first_name, last_name, username, is_organization = false } = userData;
  
  // Combine first_name and last_name into name field to match database schema
  const fullName = `${first_name} ${last_name}`.trim();
  
  const client = await pgPool.connect();
  try {
    const result = await client.query(`
      INSERT INTO users (email, password, name, credits)
      VALUES ($1, $2, $3, $4)
      RETURNING userid, email, name, credits, created_at
    `, [email, password, fullName, 10]); // Start with 10 free credits
    
    // Transform the result to match expected structure
    const user = result.rows[0];
    return {
      ...user,
      first_name: first_name,
      last_name: last_name,
      username: username || email.split('@')[0], // Generate username from email if not provided
      is_organization: is_organization
    };
  } catch (error) {
    if (error.code === '23505') { // Unique violation
      if (error.constraint === 'users_email_key') {
        throw new Error('Email already exists');
      }
    }
    throw error;
  } finally {
    client.release();
  }
};

// Get user by email
export const getUserByEmail = async (email) => {
  const client = await pgPool.connect();
  try {
    const result = await client.query('SELECT * FROM users WHERE email = $1', [email]);
    const user = result.rows[0];
    
    if (!user) return null;
    
    // Transform to match expected structure
    const nameParts = (user.name || '').split(' ');
    return {
      ...user,
      first_name: nameParts[0] || '',
      last_name: nameParts.slice(1).join(' ') || '',
      username: user.username || email.split('@')[0],
      is_organization: user.is_organization || false
    };
  } catch (error) {
    console.error('getUserByEmail error:', error);
    return null;
  } finally {
    client.release();
  }
};

// Get user by ID
export const getUserById = async (userid) => {
  const client = await pgPool.connect();
  try {
    const result = await client.query('SELECT * FROM users WHERE userid = $1', [userid]);
    const user = result.rows[0];
    
    if (!user) return null;
    
    // Transform to match expected structure
    const nameParts = (user.name || '').split(' ');
    return {
      ...user,
      first_name: nameParts[0] || '',
      last_name: nameParts.slice(1).join(' ') || '',
      username: user.username || user.email.split('@')[0],
      is_organization: user.is_organization || false
    };
  } catch (error) {
    console.error('getUserById error:', error);
    return null;
  } finally {
    client.release();
  }
};

// Get user statistics
export const getUserStats = async (userid) => {
  try {
    // Try PostgreSQL first
    const client = await pgPool.connect();
    try {
      const result = await client.query(`
        SELECT 
          COALESCE(total_workflows, 0) as total_workflows,
          COALESCE(completed_workflows, 0) as completed_workflows,
          COALESCE(failed_workflows, 0) as failed_workflows,
          COALESCE(total_executions, 0) as total_executions,
          COALESCE(saved_workflows, 0) as saved_workflows,
          COALESCE(total_n8n_logs, 0) as total_n8n_logs
        FROM user_stats WHERE userid = $1
      `, [userid]);
      
      client.release();
      return result.rows[0] || {
        total_workflows: 0,
        completed_workflows: 0,
        failed_workflows: 0,
        total_executions: 0,
        saved_workflows: 0,
        total_n8n_logs: 0
      };
    } catch (error) {
      client.release();
      throw error;
    }
  } catch (error) {
    console.log('PostgreSQL getUserStats failed, using SQLite:', error.message);
    // Fallback to SQLite
    const db = await getSqliteDb();
    const result = await db.get('SELECT * FROM user_stats WHERE userid = ?', [userid]);
    return result || {
      total_workflows: 0,
      completed_workflows: 0,
      failed_workflows: 0,
      total_executions: 0,
      saved_workflows: 0,
      total_n8n_logs: 0
    };
  }
};

// Get user chat history
export const getUserChatHistory = async (userid) => {
  try {
    // Try PostgreSQL first
    const client = await pgPool.connect();
    try {
      const result = await client.query(`
        SELECT * FROM chat_history 
        WHERE userid = $1 
        ORDER BY timestamp DESC 
        LIMIT 100
      `, [userid]);
      
      client.release();
      return result.rows;
    } catch (error) {
      client.release();
      throw error;
    }
  } catch (error) {
    console.log('PostgreSQL getUserChatHistory failed, using SQLite:', error.message);
    // Fallback to SQLite
    const db = await getSqliteDb();
    const result = await db.all(`
      SELECT * FROM chat_history 
      WHERE userid = ? 
      ORDER BY timestamp DESC 
      LIMIT 100
    `, [userid]);
    return result || [];
  }
};

// Get user memory
export const getUserMemory = async (userid) => {
  try {
    // Try PostgreSQL first
    const client = await pgPool.connect();
    try {
      const result = await client.query(`
        SELECT memory_data FROM user_memory WHERE userid = $1
      `, [userid]);
      
      client.release();
      const memoryData = result.rows[0]?.memory_data;
      return memoryData ? JSON.parse(memoryData) : {};
    } catch (error) {
      client.release();
      throw error;
    }
  } catch (error) {
    console.log('PostgreSQL getUserMemory failed, using SQLite:', error.message);
    // Fallback to SQLite
    const db = await getSqliteDb();
    const result = await db.get('SELECT memory_data FROM user_memory WHERE userid = ?', [userid]);
    const memoryData = result?.memory_data;
    return memoryData ? JSON.parse(memoryData) : {};
  }
};

// Create session - use the existing sessions table with correct column names
export const createSession = async (userid, sessionToken, ipAddress, userAgent) => {
  const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 days
  
  const client = await pgPool.connect();
  try {
    // First, clean up any existing sessions for this user
    await client.query(`
      DELETE FROM sessions WHERE userid = $1
    `, [userid]);
    
    // Create new session in sessions table using correct column names
    const result = await client.query(`
      INSERT INTO sessions (userid, token, expires_at) 
      VALUES ($1, $2, $3)
      RETURNING *
    `, [userid, sessionToken, expiresAt]);
    
    return result.rows[0];
  } catch (error) {
    console.error('createSession error:', error);
    throw error;
  } finally {
    client.release();
  }
};

// Validate session
export const validateSessionToken = async (sessionToken) => {
  const client = await pgPool.connect();
  try {
    // Join sessions with users table to get complete user info
    const result = await client.query(`
      SELECT u.*, s.token as session_token, s.expires_at as session_expires_at
      FROM users u
      JOIN sessions s ON u.userid = s.userid
      WHERE s.token = $1 AND s.expires_at > CURRENT_TIMESTAMP
    `, [sessionToken]);
    
    return result.rows[0];
  } catch (error) {
    console.error('validateSessionToken error:', error);
    return null;
  } finally {
    client.release();
  }
};

// Additional functions that might be needed
export const getN8NWorkflowLogs = async (userid, requestId = null) => {
  // Placeholder implementation
  return [];
};

export const createN8NWorkflowLog = async (logData) => {
  // Placeholder implementation
  return { id: Date.now() };
};

export const updateN8NWorkflowLog = async (logId, updateData) => {
  // Placeholder implementation
  return { success: true };
};

export const saveUserWorkflow = async (workflowData) => {
  // Placeholder implementation
  return { id: Date.now(), ...workflowData };
};

export const getUserSavedWorkflows = async (userid) => {
  // Placeholder implementation
  return [];
};

export const deleteSavedWorkflow = async (workflowId) => {
  // Placeholder implementation
  return { success: true };
};

export const getSavedWorkflow = async (workflowId) => {
  // Placeholder implementation
  return null;
};

// Additional workflow iteration functions
export const getAIIterationVersions = async (requestId) => {
  // Placeholder implementation
  return [];
};

export const markIterationAsFinal = async (requestId, versionNumber) => {
  // Placeholder implementation
  return { success: true };
};

export const getAIWorkflowRequest = async (requestId) => {
  // Placeholder implementation
  return null;
};
