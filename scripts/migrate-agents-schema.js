#!/usr/bin/env node

/**
 * Agent Schema Migration Script
 * Adds new columns and tables to support custom MCP code and triggers
 */

const { Client } = require('pg');
require('dotenv').config({ path: '.env.local' });

const config = {
  user: process.env.PGUSER || 'postgres',
  password: process.env.PGPASSWORD || 'devhouse',
  host: process.env.PGHOST || 'localhost',
  port: process.env.PGPORT || 5432,
  database: process.env.PGDATABASE || 'postgres',
};

const MIGRATION_SQL = `
-- Add new columns to existing agents table
ALTER TABLE agents ADD COLUMN IF NOT EXISTS custom_mcp_code TEXT;
ALTER TABLE agents ADD COLUMN IF NOT EXISTS trigger_config JSONB;
ALTER TABLE agents ADD COLUMN IF NOT EXISTS operation_mode VARCHAR(50) DEFAULT 'single_session';

-- Create supporting tables for agent memory and triggers
CREATE TABLE IF NOT EXISTS agent_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL DEFAULT 'system',
    memory_data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(agent_id, user_id)
);

CREATE TABLE IF NOT EXISTS agent_triggers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    trigger_type VARCHAR(50) NOT NULL, -- 'cron', 'webhook', 'email_imap'
    trigger_config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    user_id VARCHAR(255),
    trigger_type VARCHAR(50), -- 'manual', 'cron', 'webhook', 'email_imap'
    input_data JSONB,
    output_data JSONB,
    execution_status VARCHAR(50), -- 'success', 'error', 'pending'
    execution_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_agent_memory_agent_user ON agent_memory(agent_id, user_id);
CREATE INDEX IF NOT EXISTS idx_agent_triggers_active ON agent_triggers(agent_id, is_active);
`;

async function migrateSchema() {
  const client = new Client(config);
  
  try {
    console.log('🔌 Connecting to PostgreSQL database...');
    console.log(`   Host: ${config.host}:${config.port}`);
    console.log(`   Database: ${config.database}`);
    
    await client.connect();
    console.log('✅ Connected to database successfully');

    console.log('🔄 Running agent schema migration...');
    await client.query(MIGRATION_SQL);
    console.log('✅ Agent schema migration completed successfully!');

    // Verify the changes
    console.log('🔍 Verifying schema changes...');
    const result = await client.query(`
      SELECT column_name, data_type, is_nullable 
      FROM information_schema.columns 
      WHERE table_name = 'agents' 
      ORDER BY ordinal_position;
    `);
    
    console.log('📋 Current agents table schema:');
    result.rows.forEach(row => {
      console.log(`   ${row.column_name}: ${row.data_type} (${row.is_nullable === 'YES' ? 'nullable' : 'not null'})`);
    });

    // Check new tables
    const tables = await client.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      AND table_name LIKE 'agent_%'
      ORDER BY table_name;
    `);
    
    console.log('📋 Agent-related tables:');
    tables.rows.forEach(row => {
      console.log(`   ${row.table_name}`);
    });

  } catch (error) {
    console.error('❌ Migration failed:', error.message);
    process.exit(1);
  } finally {
    await client.end();
    console.log('🔚 Database connection closed');
  }
}

if (require.main === module) {
  migrateSchema();
}

module.exports = { migrateSchema };
