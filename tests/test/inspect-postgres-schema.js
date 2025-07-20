/**
 * PostgreSQL Database Schema Inspector
 * Examines the existing database schema to understand the current structure
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

const inspectDatabase = async () => {
  const client = await pgPool.connect();
  
  try {
    console.log('🔍 Inspecting PostgreSQL database schema...');
    console.log('=' .repeat(60));
    
    // List all tables
    const tablesResult = await client.query(`
      SELECT tablename 
      FROM pg_tables 
      WHERE schemaname = 'public'
      ORDER BY tablename;
    `);
    
    console.log('📋 Tables in database:');
    tablesResult.rows.forEach(row => {
      console.log(`  - ${row.tablename}`);
    });
    
    // Check if users table exists and get its structure
    const usersTableCheck = await client.query(`
      SELECT column_name, data_type, is_nullable, column_default
      FROM information_schema.columns 
      WHERE table_name = 'users' AND table_schema = 'public'
      ORDER BY ordinal_position;
    `);
    
    if (usersTableCheck.rows.length > 0) {
      console.log('\n📋 Users table structure:');
      usersTableCheck.rows.forEach(row => {
        console.log(`  - ${row.column_name}: ${row.data_type} ${row.is_nullable === 'NO' ? '(NOT NULL)' : '(nullable)'} ${row.column_default ? `DEFAULT ${row.column_default}` : ''}`);
      });
      
      // Get sample data
      const sampleData = await client.query('SELECT * FROM users LIMIT 3');
      console.log(`\n📊 Sample data (${sampleData.rows.length} rows):`);
      if (sampleData.rows.length > 0) {
        console.log(sampleData.rows);
      } else {
        console.log('  No data in users table');
      }
    } else {
      console.log('\n❌ Users table does not exist');
    }
    
    // Check waitlist table
    const waitlistTableCheck = await client.query(`
      SELECT column_name, data_type, is_nullable, column_default
      FROM information_schema.columns 
      WHERE table_name = 'waitlist' AND table_schema = 'public'
      ORDER BY ordinal_position;
    `);
    
    if (waitlistTableCheck.rows.length > 0) {
      console.log('\n📋 Waitlist table structure:');
      waitlistTableCheck.rows.forEach(row => {
        console.log(`  - ${row.column_name}: ${row.data_type} ${row.is_nullable === 'NO' ? '(NOT NULL)' : '(nullable)'} ${row.column_default ? `DEFAULT ${row.column_default}` : ''}`);
      });
    } else {
      console.log('\n❌ Waitlist table does not exist');
    }
    
    console.log('\n' + '=' .repeat(60));
    
  } catch (error) {
    console.error('❌ Error inspecting database:', error);
  } finally {
    client.release();
    await pgPool.end();
  }
};

inspectDatabase();
