#!/usr/bin/env node

/**
 * Database Initialization Script for PostgreSQL
 * This script creates the PostgreSQL database schema using the schema.sql file
 * Run this script to set up your database for the first time.
 */

const { Client } = require('pg');
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: '.env.local' });

// Database connection configuration
const config = {
  user: process.env.PGUSER || 'postgres',
  password: process.env.PGPASSWORD || 'devhouse',
  host: process.env.PGHOST || 'localhost',
  port: process.env.PGPORT || 5432,
  database: process.env.PGDATABASE || 'postgres',
};

async function initializeDatabase() {
  const client = new Client(config);
  
  try {
    // Connect to the database
    console.log('🔌 Connecting to PostgreSQL database...');
    console.log(`   Host: ${config.host}:${config.port}`);
    console.log(`   Database: ${config.database}`);
    console.log(`   User: ${config.user}`);
    
    await client.connect();
    console.log('✅ Connected to database successfully');

    // Read the schema file
    const schemaPath = path.join(__dirname, '..', 'database', 'schema.sql');
    console.log(`📄 Reading schema from: ${schemaPath}`);
    
    if (!fs.existsSync(schemaPath)) {
      throw new Error(`Schema file not found at: ${schemaPath}`);
    }

    const schemaSql = fs.readFileSync(schemaPath, 'utf8');
    
    // Execute the schema
    console.log('🏗️  Creating database schema...');
    await client.query(schemaSql);
    console.log('✅ Database schema created successfully!');

    // Verify tables were created
    const tablesResult = await client.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      ORDER BY table_name;
    `);

    console.log('📋 Created tables:');
    tablesResult.rows.forEach(row => {
      console.log(`   - ${row.table_name}`);
    });

    // Check if pgcrypto extension was installed
    const extensionResult = await client.query(`
      SELECT extname FROM pg_extension WHERE extname = 'pgcrypto';
    `);

    if (extensionResult.rows.length > 0) {
      console.log('🔐 pgcrypto extension enabled for UUID generation');
    } else {
      console.log('⚠️  pgcrypto extension not found - UUIDs may not work');
    }

    // Show indexes
    const indexResult = await client.query(`
      SELECT indexname 
      FROM pg_indexes 
      WHERE schemaname = 'public' 
      ORDER BY indexname;
    `);

    console.log('🔍 Created indexes:');
    indexResult.rows.forEach(row => {
      console.log(`   - ${row.indexname}`);
    });

    console.log('🎉 Database initialization completed successfully!');
    console.log('\n📝 Next steps:');
    console.log('   1. Update your backend to use PostgreSQL');
    console.log('   2. Test user registration and agent creation');
    console.log('   3. Verify UUID generation is working');

  } catch (error) {
    console.error('❌ Database initialization failed:');
    console.error(error.message);
    
    if (error.code === 'ECONNREFUSED') {
      console.error('\n💡 Make sure PostgreSQL is running and accessible at:');
      console.error(`   Host: ${config.host}:${config.port}`);
      console.error(`   Database: ${config.database}`);
      console.error(`   User: ${config.user}`);
      console.error('\n🔧 To start PostgreSQL:');
      console.error('   - Windows: Start PostgreSQL service');
      console.error('   - macOS: brew services start postgresql');
      console.error('   - Linux: sudo systemctl start postgresql');
    } else if (error.code === '28P01') {
      console.error('\n🔑 Authentication failed - check your credentials in .env.local');
    }
    
    process.exit(1);
  } finally {
    await client.end();
    console.log('🔌 Database connection closed');
  }
}

async function testConnection() {
  console.log('🧪 Testing database connection...');
  const client = new Client(config);
  
  try {
    await client.connect();
    const result = await client.query('SELECT version();');
    console.log(`✅ PostgreSQL version: ${result.rows[0].version.split(' ')[0]}`);
    return true;
  } catch (error) {
    console.error('❌ Connection test failed:', error.message);
    return false;
  } finally {
    await client.end();
  }
}

// Run the initialization
async function main() {
  console.log('🚀 Starting AutoFlow database initialization...\n');
  
  const isConnected = await testConnection();
  if (!isConnected) {
    console.error('\n❌ Cannot proceed without database connection');
    process.exit(1);
  }
  
  await initializeDatabase();
}

if (require.main === module) {
  main();
}

module.exports = { initializeDatabase, testConnection };
