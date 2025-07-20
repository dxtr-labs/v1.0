/**
 * Inspect Sessions Table Structure
 */

import { Pool } from 'pg';

const pgPool = new Pool({
  user: process.env.PGUSER || 'postgres',
  host: process.env.PGHOST || '35.202.114.213',
  database: process.env.PGDATABASE || 'postgres',
  password: process.env.PGPASSWORD || 'devhouse',
  port: parseInt(process.env.PGPORT || '5432'),
  ssl: false,
});

const inspectSessions = async () => {
  const client = await pgPool.connect();
  
  try {
    console.log('🔍 Inspecting sessions table structure...');
    
    // Get sessions table structure
    const sessionsTableCheck = await client.query(`
      SELECT column_name, data_type, is_nullable, column_default
      FROM information_schema.columns 
      WHERE table_name = 'sessions' AND table_schema = 'public'
      ORDER BY ordinal_position;
    `);
    
    if (sessionsTableCheck.rows.length > 0) {
      console.log('📋 Sessions table structure:');
      sessionsTableCheck.rows.forEach(row => {
        console.log(`  - ${row.column_name}: ${row.data_type} ${row.is_nullable === 'NO' ? '(NOT NULL)' : '(nullable)'} ${row.column_default ? `DEFAULT ${row.column_default}` : ''}`);
      });
      
      // Get sample data
      const sampleData = await client.query('SELECT * FROM sessions LIMIT 3');
      console.log(`\n📊 Sample data (${sampleData.rows.length} rows):`);
      if (sampleData.rows.length > 0) {
        console.log(sampleData.rows);
      } else {
        console.log('  No data in sessions table');
      }
    } else {
      console.log('❌ Sessions table does not exist');
    }
    
  } catch (error) {
    console.error('❌ Error inspecting sessions table:', error);
  } finally {
    client.release();
    await pgPool.end();
  }
};

inspectSessions();
