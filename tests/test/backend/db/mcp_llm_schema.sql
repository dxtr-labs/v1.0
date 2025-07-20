-- MCP LLM Enhanced Database Schema
-- This creates the tables needed for custom MCP LLM with memory, personality, and automation

-- 1. MCP LLM Agents Table (Enhanced agent configurations)
CREATE TABLE IF NOT EXISTS mcp_llm_agents (
    agent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(userid) ON DELETE CASCADE,
    agent_name VARCHAR(255) NOT NULL,
    personality JSONB DEFAULT '{}',
    system_prompt TEXT,
    preferred_ai_service VARCHAR(50) DEFAULT 'inhouse',
    memory_enabled BOOLEAN DEFAULT TRUE,
    automation_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. MCP LLM Memory Table (Conversation and context memory)
CREATE TABLE IF NOT EXISTS mcp_llm_memory (
    memory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES mcp_llm_agents(agent_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(userid) ON DELETE CASCADE,
    memory_type VARCHAR(50) NOT NULL, -- 'conversation', 'facts', 'preferences', 'context'
    memory_key VARCHAR(255),
    memory_value JSONB NOT NULL,
    importance_score INTEGER DEFAULT 5, -- 1-10 scale
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. MCP LLM Conversations Table (Full conversation history)
CREATE TABLE IF NOT EXISTS mcp_llm_conversations (
    conversation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES mcp_llm_agents(agent_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(userid) ON DELETE CASCADE,
    session_id VARCHAR(255),
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    ai_service_used VARCHAR(50),
    credits_consumed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Automation Workflows Table (Enhanced for preview and confirmation)
CREATE TABLE IF NOT EXISTS automation_workflows (
    workflow_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(userid) ON DELETE CASCADE,
    agent_id UUID REFERENCES mcp_llm_agents(agent_id) ON DELETE SET NULL,
    workflow_name VARCHAR(255) NOT NULL,
    original_request TEXT NOT NULL,
    ai_service_used VARCHAR(50) NOT NULL,
    workflow_json JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'previewing', 'confirmed', 'executing', 'completed', 'failed'
    preview_data JSONB DEFAULT '{}',
    execution_results JSONB DEFAULT '{}',
    estimated_credits INTEGER DEFAULT 0,
    actual_credits INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Automation Executions Table (Track each execution)
CREATE TABLE IF NOT EXISTS automation_executions (
    execution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES automation_workflows(workflow_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(userid) ON DELETE CASCADE,
    trigger_type VARCHAR(50) NOT NULL, -- 'manual', 'scheduled', 'webhook'
    status VARCHAR(50) DEFAULT 'running', -- 'running', 'completed', 'failed', 'cancelled'
    execution_log JSONB DEFAULT '[]',
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    credits_used INTEGER DEFAULT 0
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_mcp_llm_agents_user_id ON mcp_llm_agents(user_id);
CREATE INDEX IF NOT EXISTS idx_mcp_llm_memory_agent_id ON mcp_llm_memory(agent_id);
CREATE INDEX IF NOT EXISTS idx_mcp_llm_memory_type ON mcp_llm_memory(memory_type);
CREATE INDEX IF NOT EXISTS idx_mcp_llm_conversations_agent_id ON mcp_llm_conversations(agent_id);
CREATE INDEX IF NOT EXISTS idx_mcp_llm_conversations_session ON mcp_llm_conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_automation_workflows_user_id ON automation_workflows(user_id);
CREATE INDEX IF NOT EXISTS idx_automation_workflows_status ON automation_workflows(status);
CREATE INDEX IF NOT EXISTS idx_automation_executions_workflow_id ON automation_executions(workflow_id);

-- Create default MCP LLM agent function
CREATE OR REPLACE FUNCTION create_default_mcp_agent(p_user_id UUID, p_agent_name VARCHAR DEFAULT 'Sam - Personal Assistant')
RETURNS UUID AS $$
DECLARE
    v_agent_id UUID;
BEGIN
    INSERT INTO mcp_llm_agents (
        user_id,
        agent_name,
        personality,
        system_prompt,
        preferred_ai_service,
        memory_enabled,
        automation_enabled
    ) VALUES (
        p_user_id,
        p_agent_name,
        '{
            "traits": ["helpful", "professional", "automation-focused"],
            "communication_style": "clear and concise",
            "expertise": ["automation", "workflow creation", "AI integration"],
            "response_format": "structured and actionable"
        }'::jsonb,
        'You are Sam, a Personal Assistant specialized in automation and AI integration. You help users create workflows, automate tasks, and integrate AI services. Always be helpful, professional, and focus on practical solutions.',
        'inhouse',
        true,
        true
    ) RETURNING agent_id INTO v_agent_id;
    
    RETURN v_agent_id;
END;
$$ LANGUAGE plpgsql;
