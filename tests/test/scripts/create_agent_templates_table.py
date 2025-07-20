#!/usr/bin/env python3
"""
Create Agent Templates Table Script
Creates the agent_templates table needed for n8n workflow ingestion
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('.env.local')

# Database configuration
DB_CONFIG = {
    "host": os.getenv("PGHOST", "34.44.98.81"),
    "port": int(os.getenv("PGPORT", 5432)),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", "devhouse"),
    "database": os.getenv("PGDATABASE", "postgres")
}

SQL_SCHEMA = """
-- Agent Templates Table for N8N Workflow Ingestion
-- This table stores pre-built agent templates based on n8n workflows

CREATE TABLE IF NOT EXISTS agent_templates (
    template_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_name VARCHAR(255) NOT NULL UNIQUE,
    template_description TEXT,
    category VARCHAR(100) DEFAULT 'General',
    
    -- Agent configuration templates
    agent_name_template VARCHAR(255) NOT NULL,
    agent_role_template TEXT,
    agent_personality_template JSONB DEFAULT '{}',
    agent_expectations_template TEXT,
    
    -- N8N workflow definition
    initial_workflow_definition JSONB NOT NULL,
    
    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for better performance
CREATE INDEX IF NOT EXISTS idx_agent_templates_category ON agent_templates(category);
CREATE INDEX IF NOT EXISTS idx_agent_templates_active ON agent_templates(is_active);

-- Row Level Security (RLS) for admin access
ALTER TABLE agent_templates ENABLE ROW LEVEL SECURITY;

-- Policy to allow admin users to manage templates (skip if exists)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE policyname = 'admin_agent_templates_policy' 
        AND tablename = 'agent_templates'
    ) THEN
        CREATE POLICY admin_agent_templates_policy ON agent_templates
            FOR ALL USING (
                current_setting('app.current_user_id', true) = '00000000-0000-0000-0000-000000000000'
                OR pg_has_role(current_user, 'app_admin', 'member')
            );
    END IF;
END $$;

-- Grant necessary permissions (ignore errors if roles don't exist)
DO $$ 
BEGIN
    -- Try to grant to app_admin if it exists
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_admin') THEN
        GRANT ALL ON agent_templates TO app_admin;
    END IF;
    
    -- Try to grant to authenticated if it exists
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
        GRANT SELECT ON agent_templates TO authenticated;
    END IF;
EXCEPTION WHEN OTHERS THEN
    -- Ignore permission errors
    NULL;
END $$;
"""

async def create_agent_templates_table():
    conn = None
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        print("Connected to database successfully.")
        
        # Execute the schema creation
        await conn.execute(SQL_SCHEMA)
        print("Agent templates table created successfully!")
        
        # Verify the table exists
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'agent_templates'
            );
        """)
        
        if result:
            print("✅ agent_templates table verified to exist.")
        else:
            print("❌ Failed to create agent_templates table.")
            
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        if conn:
            await conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    asyncio.run(create_agent_templates_table())
