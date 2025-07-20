// scripts/create-database.js
// Create the automation database if it doesn't exist

import dotenv from 'dotenv';
import { Pool } from 'pg';

// Load environment variables
dotenv.config({ path: '.env.local' });

async function main() {
  console.log('🚀 Creating automation database...');
  
  // Connect to default postgres database first
  const pgPool = new Pool({
    user: process.env.PGUSER || 'postgres',
    host: process.env.PGHOST || '34.44.98.81',
    database: 'postgres', // Connect to default database
    password: process.env.PGPASSWORD || 'devhouse',
    port: parseInt(process.env.PGPORT || '5432'),
    ssl: false,
  });
  
  try {
    const client = await pgPool.connect();
    
    // Check if automation database exists
    const result = await client.query(`
      SELECT 1 FROM pg_database WHERE datname = 'automation'
    `);
    
    if (result.rows.length === 0) {
      console.log('📋 Creating automation database...');
      await client.query('CREATE DATABASE automation');
      console.log('✅ Database "automation" created successfully!');
    } else {
      console.log('✅ Database "automation" already exists!');
    }
    
    client.release();
    await pgPool.end();
    
  } catch (error) {
    console.error('❌ Database creation failed:', error);
    process.exit(1);
  }
}

main();
