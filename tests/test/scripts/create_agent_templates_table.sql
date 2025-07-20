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

-- Policy to allow admin users to manage templates
CREATE POLICY "admin_agent_templates_policy" ON agent_templates
    FOR ALL USING (
        -- Allow admin users (you can adjust this condition based on your admin identification)
        current_setting('app.current_user_id', true) = '00000000-0000-0000-0000-000000000000'
        OR pg_has_role(current_user, 'app_admin', 'member')
    );

-- Grant necessary permissions
GRANT ALL ON agent_templates TO app_admin;
GRANT SELECT ON agent_templates TO authenticated;
