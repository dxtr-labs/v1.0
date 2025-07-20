// lib/database-schema.js
// Database schema setup for the comprehensive automation platform

import { Pool } from 'pg';

// PostgreSQL connection pool using environment variables
const pgPool = new Pool({
  user: process.env.PGUSER || 'postgres',
  host: process.env.PGHOST || '34.44.98.81',
  database: process.env.PGDATABASE || 'automation',
  password: process.env.PGPASSWORD || 'devhouse',
  port: parseInt(process.env.PGPORT || '5432'),
  ssl: false, // Set to true if your database requires SSL
});

// Initialize database with all required tables
export const initializeDatabase = async () => {
  const client = await pgPool.connect();
  
  try {
    console.log('🗄️ Initializing database schema...');

    // 1. Waitlist Table
    await client.query(`
      CREATE TABLE IF NOT EXISTS waitlist (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        phone VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // 2. Users Table (Main Members)
    await client.query(`
      CREATE TABLE IF NOT EXISTS users (
        userid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        email VARCHAR(255) UNIQUE NOT NULL,
        password TEXT NOT NULL,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        username VARCHAR(50) UNIQUE,
        is_organization BOOLEAN DEFAULT FALSE,
        session_token TEXT,
        session_expires_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ai_memory JSONB DEFAULT '{}',
        service_keys JSONB DEFAULT '{}',
        credits INTEGER DEFAULT 0,
        ip_address INET,
        recievetextconf BOOLEAN DEFAULT TRUE
      )
    `);

    // 3. Credit Logs Table
    await client.query(`
      CREATE TABLE IF NOT EXISTS credit_logs (
        id SERIAL PRIMARY KEY,
        userid UUID NOT NULL REFERENCES users(userid) ON DELETE CASCADE,
        credit_change INTEGER NOT NULL,
        reason VARCHAR(255) NOT NULL,
        service_used VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // 4. AI Workflow Requests Table
    await client.query(`
      CREATE TABLE IF NOT EXISTS ai_workflow_requests (
        id SERIAL PRIMARY KEY,
        userid UUID NOT NULL REFERENCES users(userid) ON DELETE CASCADE,
        prompt TEXT NOT NULL,
        ai_response JSONB,
        status VARCHAR(50) DEFAULT 'pending',
        iteration_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // 5. Chat Sessions Table
    await client.query(`
      CREATE TABLE IF NOT EXISTS chat_sessions (
        id SERIAL PRIMARY KEY,
        workflow_request_id INTEGER NOT NULL REFERENCES ai_workflow_requests(id) ON DELETE CASCADE,
        userid UUID NOT NULL REFERENCES users(userid) ON DELETE CASCADE,
        sender VARCHAR(20) NOT NULL CHECK (sender IN ('user', 'ai', 'system')),
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // 6. Automations Table
    await client.query(`
      CREATE TABLE IF NOT EXISTS automations (
        id SERIAL PRIMARY KEY,
        userid UUID NOT NULL REFERENCES users(userid) ON DELETE CASCADE,
        workflow_request_id INTEGER REFERENCES ai_workflow_requests(id) ON DELETE SET NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        workflow_json JSONB NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        last_run_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Create indexes for better performance
    await client.query('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)');
    await client.query('CREATE INDEX IF NOT EXISTS idx_users_session_token ON users(session_token)');
    await client.query('CREATE INDEX IF NOT EXISTS idx_credit_logs_userid ON credit_logs(userid)');
    await client.query('CREATE INDEX IF NOT EXISTS idx_ai_workflow_requests_userid ON ai_workflow_requests(userid)');
    await client.query('CREATE INDEX IF NOT EXISTS idx_chat_sessions_workflow_request ON chat_sessions(workflow_request_id)');
    await client.query('CREATE INDEX IF NOT EXISTS idx_automations_userid ON automations(userid)');

    console.log('✅ Database schema initialized successfully!');
    
  } catch (error) {
    console.error('❌ Error initializing database:', error);
    throw error;
  } finally {
    client.release();
  }
};

// Test database connection
export const testDatabaseConnection = async () => {
  try {
    const client = await pgPool.connect();
    await client.query('SELECT 1');
    client.release();
    console.log('✅ Database connection successful');
    return true;
  } catch (error) {
    console.error('❌ Database connection failed:', error);
    return false;
  }
};

export { pgPool };
