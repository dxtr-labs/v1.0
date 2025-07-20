"""
Enhanced Agent Database Schema
Includes custom MCP LLM code storage and trigger configurations
"""

ENHANCED_AGENT_SCHEMA = """
-- Enhanced agents table with trigger support and custom code
ALTER TABLE agents ADD COLUMN IF NOT EXISTS custom_mcp_code TEXT;
ALTER TABLE agents ADD COLUMN IF NOT EXISTS trigger_config JSONB;
ALTER TABLE agents ADD COLUMN IF NOT EXISTS operation_mode VARCHAR(50) DEFAULT 'single_session';

-- Agent memory for conversation history
CREATE TABLE IF NOT EXISTS agent_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL DEFAULT 'system',
    memory_data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(agent_id, user_id)
);

-- Agent trigger schedules for cron/webhook/email triggers
CREATE TABLE IF NOT EXISTS agent_triggers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    trigger_type VARCHAR(50) NOT NULL, -- 'cron', 'webhook', 'email_imap'
    trigger_config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent execution logs
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

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_agent_memory_agent_user ON agent_memory(agent_id, user_id);
CREATE INDEX IF NOT EXISTS idx_agent_triggers_active ON agent_triggers(agent_id, is_active);
CREATE INDEX IF NOT EXISTS idx_agent_executions_agent ON agent_executions(agent_id, created_at);
"""

# Default custom MCP LLM code template
DEFAULT_CUSTOM_MCP_CODE = '''
"""
Custom MCP LLM Code for Agent: {agent_name}
Role: {agent_role}

This code is executed when users interact with this agent.
It has access to:
- context: Full interaction context including agent details, user input, memory
- automation_engine: For creating workflows and automations
"""

async def process_user_input(context):
    """
    Main processing function for user interactions
    
    Args:
        context: Dict containing:
            - agent: Agent details (name, role, personality, etc.)
            - user_input: The user's message
            - user_id: User identifier  
            - memory: Previous conversation history
            - automation_engine: For creating workflows
    
    Returns:
        Dict with status and response
    """
    
    agent = context['agent']
    user_input = context['user_input']
    memory = context['memory']
    
    # Basic intent detection
    intent = detect_intent(user_input)
    
    if intent == 'automation':
        return await handle_automation_request(context)
    elif intent == 'conversation':
        return await handle_conversation(context)
    else:
        return await handle_default(context)

def detect_intent(user_input):
    """Detect user intent from input"""
    automation_keywords = ['send email', 'create workflow', 'automate', 'schedule', 'trigger']
    
    if any(keyword in user_input.lower() for keyword in automation_keywords):
        return 'automation'
    else:
        return 'conversation'

async def handle_automation_request(context):
    """Handle automation-related requests"""
    user_input = context['user_input']
    agent = context['agent']
    
    # Email automation detection
    if 'email' in user_input.lower():
        import re
        email_pattern = r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{{2,}}\\b'
        emails = re.findall(email_pattern, user_input)
        
        if emails:
            return {{
                "status": "workflow_preview",
                "message": f"I'll send an email to {{emails[0]}} with content based on your request.",
                "workflow_json": {{
                    "type": "email_automation",
                    "recipient": emails[0],
                    "agent_id": agent['id'],
                    "content_type": "personalized email",
                    "needs_ai_generation": True
                }}
            }}
        else:
            return {{
                "status": "info_needed",
                "message": "I can help you send an email. Please provide the recipient's email address."
            }}
    
    return {{
        "status": "conversational",
        "message": f"I'm {{agent['name']}}, ready to help you automate tasks. What would you like me to set up?"
    }}

async def handle_conversation(context):
    """Handle general conversation"""
    agent = context['agent']
    user_input = context['user_input']
    personality = agent.get('personality', {{}})
    
    # Personality-based response
    tone = personality.get('tone', 'friendly')
    
    if tone == 'friendly':
        response = f"Hi there! I'm {{agent['name']}}, your {{agent['role']}}. I'd love to help you with that!"
    elif tone == 'professional':
        response = f"Good day. I am {{agent['name']}}, your {{agent['role']}}. How may I assist you?"
    else:
        response = f"Hello! I'm {{agent['name']}}. As your {{agent['role']}}, I'm here to help."
    
    return {{
        "status": "conversational",
        "message": response
    }}

async def handle_default(context):
    """Default handler"""
    agent = context['agent']
    return {{
        "status": "conversational", 
        "message": f"I'm {{agent['name']}}, your {{agent['role']}}. How can I help you today?"
    }}
'''

# Trigger configuration templates
TRIGGER_TEMPLATES = {
    "cron": {
        "description": "Time-based scheduling triggers",
        "schema": {
            "triggerTimes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "hour": {"type": "integer", "minimum": 0, "maximum": 23},
                        "minute": {"type": "integer", "minimum": 0, "maximum": 59},
                        "weekday": {"type": "string", "description": "0-6 or * or 1-5"},
                        "dayOfMonth": {"type": ["integer", "string"], "description": "1-31 or *"},
                        "month": {"type": ["integer", "string"], "description": "1-12 or *"}
                    },
                    "required": ["hour", "minute"]
                }
            }
        },
        "example": {
            "triggerTimes": [
                {"hour": 9, "minute": 0, "weekday": "1-5"},  # Weekdays at 9 AM
                {"hour": 18, "minute": 30, "weekday": "*"}    # Daily at 6:30 PM  
            ]
        }
    },
    
    "webhook": {
        "description": "HTTP webhook triggers", 
        "schema": {
            "path": {"type": "string", "description": "Webhook URL path"},
            "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"], "default": "POST"},
            "authentication": {"type": "string", "enum": ["none", "token", "basic"], "default": "none"}
        },
        "example": {
            "path": "/webhook/agent-trigger",
            "method": "POST",
            "authentication": "token"
        }
    },
    
    "email_imap": {
        "description": "Email monitoring triggers",
        "schema": {
            "mailbox": {"type": "string", "default": "INBOX"},
            "postProcessAction": {"type": "string", "enum": ["read", "delete"], "default": "read"},
            "format": {"type": "string", "enum": ["simple", "resolved"], "default": "simple"},
            "downloadAttachments": {"type": "boolean", "default": False},
            "searchCriteria": {
                "type": "object",
                "properties": {
                    "unseen": {"type": "boolean", "default": True},
                    "subject_contains": {"type": "string"},
                    "from_contains": {"type": "string"}
                }
            }
        },
        "example": {
            "mailbox": "INBOX",
            "postProcessAction": "read", 
            "format": "simple",
            "searchCriteria": {
                "unseen": True,
                "subject_contains": "automation"
            }
        }
    }
}
