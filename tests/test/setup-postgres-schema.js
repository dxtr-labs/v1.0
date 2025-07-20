/**
 * PostgreSQL Database Schema Setup
 * Creates the required tables for the authentication system
 */

import { Pool } from 'pg';

// PostgreSQL connection using environment variables
const pgPool = new Pool({
  user: process.env.PGUSER || 'postgres',
  host: process.env.PGHOST || '35.202.114.213',
  database: process.env.PGDATABASE || 'postgres',
  password: process.env.PGPASSWORD || 'devhouse',
  port: parseInt(process.env.PGPORT || '5432'),
  ssl: false,
});

const createTables = async () => {
  const client = await pgPool.connect();
  
  try {
    console.log('🔄 Creating PostgreSQL database schema...');
    
    // Create users table
    await client.query(`
      CREATE TABLE IF NOT EXISTS users (
        userid SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        username VARCHAR(50) UNIQUE NOT NULL,
        is_organization BOOLEAN DEFAULT FALSE,
        credits INTEGER DEFAULT 10,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);
    console.log('✅ Users table created/verified');

    // Create waitlist table
    await client.query(`
      CREATE TABLE IF NOT EXISTS waitlist (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        phone VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);
    console.log('✅ Waitlist table created/verified');

    // Create user_sessions table for session management
    await client.query(`
      CREATE TABLE IF NOT EXISTS user_sessions (
        session_id VARCHAR(255) PRIMARY KEY,
        userid INTEGER REFERENCES users(userid) ON DELETE CASCADE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL,
        is_active BOOLEAN DEFAULT TRUE
      );
    `);
    console.log('✅ User sessions table created/verified');

    // Create indexes for better performance
    await client.query(`
      CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
      CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
      CREATE INDEX IF NOT EXISTS idx_sessions_userid ON user_sessions(userid);
      CREATE INDEX IF NOT EXISTS idx_sessions_active ON user_sessions(is_active);
    `);
    console.log('✅ Database indexes created/verified');

    // Check if we can insert and select data
    const testResult = await client.query('SELECT COUNT(*) as user_count FROM users');
    console.log(`📊 Current users in database: ${testResult.rows[0].user_count}`);

    console.log('🎉 PostgreSQL database schema setup completed successfully!');
    
  } catch (error) {
    console.error('❌ Error setting up database schema:', error);
    throw error;
  } finally {
    client.release();
    await pgPool.end();
  }
};

// Test connection first, then create tables
const setupDatabase = async () => {
  try {
    console.log('🚀 Starting PostgreSQL database setup');
    console.log('=' .repeat(50));
    
    // Test connection
    console.log('🔄 Testing database connection...');
    const client = await pgPool.connect();
    await client.query('SELECT 1');
    client.release();
    console.log('✅ Database connection successful');
    
    // Create tables
    await createTables();
    
    console.log('\n' + '=' .repeat(50));
    console.log('✅ Database setup completed successfully!');
    console.log('💡 You can now run the authentication tests');
    
  } catch (error) {
    console.error('\n❌ Database setup failed:', error.message);
    process.exit(1);
  }
};

setupDatabase();
