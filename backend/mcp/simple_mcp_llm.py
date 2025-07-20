"""
Enhanced Custom MCP LLM System with Memory, Personality & JSON Script Generation
Connects natural language to automation workflows via driver-based execution
"""
import logging
import asyncio
import json
import sqlite3
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class CustomMCPLLMAgent:
    """Custom MCP LLM Agent with memory, personality and JSON script generation"""
    
    def __init__(self, agent_id: str, agent_name: str, personality: Dict[str, Any], llm_config: Dict[str, Any]):
        """
        Initialize Custom MCP LLM Agent
        
        Args:
            agent_id: Unique agent identifier
            agent_name: Human-readable agent name
            personality: Agent personality traits and behaviors
            llm_config: LLM configuration (model, parameters, etc.)
        """
        logger.info(f"🤖 Initializing Custom MCP LLM Agent: {agent_name}")
        
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.personality = personality
        self.llm_config = llm_config
        
        # Conversation memory storage
        self.memory = []
        
        # JSON Script Templates for all workflow node types
        self.json_script_templates = self._initialize_json_templates()
        
        # Node schemas for validation
        self.node_schemas = self._initialize_node_schemas()
        
        # System prompt for Code Builder AI functionality
        self.system_prompt = self._build_system_prompt()
        
        logger.info(f"✅ Custom MCP LLM Agent {agent_name} initialized with {len(self.json_script_templates)} node templates")
    
    def _initialize_json_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize JSON script templates for all workflow nodes"""
        
        return {
            "email_send": {
                "driver": "email_send_driver",
                "schema": {
                    "type": "object",
                    "properties": {
                        "to_email": {"type": "string", "format": "email"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                        "smtp_config": {
                            "type": "object",
                            "properties": {
                                "host": {"type": "string"},
                                "port": {"type": "integer"},
                                "username": {"type": "string"},
                                "password": {"type": "string"}
                            }
                        }
                    },
                    "required": ["to_email", "subject", "body"]
                },
                "example": {
                    "to_email": "user@example.com",
                    "subject": "{{subject_template}}",
                    "body": "{{body_template}}",
                    "smtp_config": {
                        "host": "smtp.gmail.com",
                        "port": 587,
                        "username": "{{smtp_user}}",
                        "password": "{{smtp_password}}"
                    }
                }
            },
            
            "ai_content_generation": {
                "driver": "openai_driver",
                "schema": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string"},
                        "model": {"type": "string"},
                        "max_tokens": {"type": "integer"},
                        "temperature": {"type": "number"}
                    },
                    "required": ["prompt"]
                },
                "example": {
                    "prompt": "{{generation_prompt}}",
                    "model": "gpt-3.5-turbo",
                    "max_tokens": 500,
                    "temperature": 0.7
                }
            },
            
            "data_fetch": {
                "driver": "http_request_driver",
                "schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "format": "uri"},
                        "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
                        "headers": {"type": "object"},
                        "data": {"type": "object"}
                    },
                    "required": ["url", "method"]
                },
                "example": {
                    "url": "{{api_endpoint}}",
                    "method": "GET",
                    "headers": {
                        "Authorization": "Bearer {{api_token}}",
                        "Content-Type": "application/json"
                    }
                }
            },
            
            "webhook": {
                "driver": "webhook_driver",
                "schema": {
                    "type": "object",
                    "properties": {
                        "webhook_url": {"type": "string", "format": "uri"},
                        "payload": {"type": "object"},
                        "method": {"type": "string", "enum": ["POST", "PUT"]},
                        "headers": {"type": "object"}
                    },
                    "required": ["webhook_url", "payload"]
                },
                "example": {
                    "webhook_url": "{{webhook_endpoint}}",
                    "payload": {
                        "event": "{{event_type}}",
                        "data": "{{event_data}}"
                    },
                    "method": "POST",
                    "headers": {
                        "Content-Type": "application/json"
                    }
                }
            },
            
            "twilio_sms": {
                "driver": "twilio_driver",
                "schema": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string"},
                        "body": {"type": "string"},
                        "from": {"type": "string"},
                        "account_sid": {"type": "string"},
                        "auth_token": {"type": "string"}
                    },
                    "required": ["to", "body"]
                },
                "example": {
                    "to": "{{phone_number}}",
                    "body": "{{sms_message}}",
                    "from": "{{twilio_number}}",
                    "account_sid": "{{twilio_sid}}",
                    "auth_token": "{{twilio_token}}"
                }
            },
            
            "conditional": {
                "driver": "conditional_driver",
                "schema": {
                    "type": "object",
                    "properties": {
                        "condition": {"type": "string"},
                        "if_true": {"type": "array"},
                        "if_false": {"type": "array"}
                    },
                    "required": ["condition", "if_true"]
                },
                "example": {
                    "condition": "{{condition_expression}}",
                    "if_true": [
                        {"node_type": "email_send", "parameters": {}}
                    ],
                    "if_false": [
                        {"node_type": "data_fetch", "parameters": {}}
                    ]
                }
            },
            
            "claude_ai": {
                "driver": "claude_driver",
                "schema": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string"},
                        "model": {"type": "string"},
                        "max_tokens": {"type": "integer"},
                        "system": {"type": "string"}
                    },
                    "required": ["prompt"]
                },
                "example": {
                    "prompt": "{{claude_prompt}}",
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 1000,
                    "system": "{{system_instructions}}"
                }
            }
        }
    
    def _initialize_node_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Initialize validation schemas for workflow nodes"""
        
        return {
            "workflow_definition": {
                "type": "object",
                "properties": {
                    "workflow_id": {"type": "string"},
                    "workflow_name": {"type": "string"},
                    "trigger": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["manual", "webhook", "schedule", "interval"]},
                            "config": {"type": "object"}
                        },
                        "required": ["type"]
                    },
                    "nodes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "type": {"type": "string"},
                                "script": {"type": "object"},
                                "parameters": {"type": "object"}
                            },
                            "required": ["id", "type", "script", "parameters"]
                        }
                    }
                },
                "required": ["workflow_id", "nodes"]
            }
        }
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for Code Builder AI functionality"""
        
        personality_description = self._format_personality()
        available_nodes = list(self.json_script_templates.keys())
        
        return f"""You are {self.agent_name}, a Custom MCP LLM Agent with Code Builder AI capabilities.

PERSONALITY:
{personality_description}

CODE BUILDER AI CAPABILITIES:
You can understand natural language requests and generate executable JSON workflows using these automation nodes:
{', '.join(available_nodes)}

WORKFLOW GENERATION RULES:
1. Always generate complete, executable JSON workflows
2. Use appropriate drivers for each node type
3. Include parameter templates that can be resolved at runtime
4. Validate against node schemas before responding
5. Explain the workflow logic in human-readable terms

MEMORY CONTEXT:
You maintain conversation memory to provide personalized responses and remember user preferences, past interactions, and context.

RESPONSE FORMAT:
For workflow requests, respond with:
- Human explanation of the workflow
- Complete JSON workflow structure
- Validation status and any issues

For conversational requests, respond naturally while maintaining your personality and leveraging conversation memory.
"""
    
    def _format_personality(self) -> str:
        """Format personality traits for system prompt"""
        
        if not self.personality:
            return "Professional, helpful, and efficient assistant"
        
        traits = []
        for key, value in self.personality.items():
            traits.append(f"- {key}: {value}")
        
        return "\n".join(traits)
    
    async def process_message(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process user message with Code Builder AI capabilities
        
        Args:
            user_input: User's natural language input
            context: Additional context data
            
        Returns:
            Response with either conversational reply or workflow JSON
        """
        logger.info(f"🧠 Processing message for agent {self.agent_name}")
        
        # Add to memory
        self.memory.append({
            "timestamp": datetime.now().isoformat(),
            "type": "user_input",
            "content": user_input,
            "context": context or {}
        })
        
        # Determine if this is a workflow request or conversational
        is_workflow_request = await self._detect_workflow_intent(user_input)
        
        if is_workflow_request:
            return await self._generate_workflow(user_input, context)
        else:
            return await self._generate_conversational_response(user_input, context)
    
    async def _detect_workflow_intent(self, user_input: str) -> bool:
        """Detect if user input is requesting a workflow creation"""
        
        workflow_keywords = [
            "create", "workflow", "automation", "send email", "fetch data",
            "webhook", "sms", "schedule", "if", "when", "trigger",
            "automate", "generate", "process", "execute"
        ]
        
        user_lower = user_input.lower()
        return any(keyword in user_lower for keyword in workflow_keywords)
    
    async def _generate_workflow(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate JSON workflow from natural language using Code Builder AI"""
        
        logger.info(f"🔧 Generating workflow for: {user_input[:100]}...")
        
        # Simulate Code Builder AI workflow generation
        # In production, this would use the LLM with the system prompt
        workflow_json = await self._simulate_llm_workflow_generation(user_input, context)
        
        # Validate workflow
        validation_result = self._validate_workflow(workflow_json)
        
        if validation_result["valid"]:
            response_text = f"I've created a workflow for your request:\n\n{self._explain_workflow(workflow_json)}\n\nShould I proceed with this automation?"
            
            # Add to memory
            self.memory.append({
                "timestamp": datetime.now().isoformat(),
                "type": "workflow_generation",
                "content": response_text,
                "workflow_json": workflow_json,
                "validation": validation_result
            })
            
            return {
                "success": True,
                "response_type": "workflow",
                "response": response_text,
                "workflow_json": workflow_json,
                "validation": validation_result,
                "action_required": "confirm_workflow"
            }
        else:
            error_response = f"I encountered issues generating the workflow: {validation_result['errors']}"
            
            self.memory.append({
                "timestamp": datetime.now().isoformat(),
                "type": "workflow_error",
                "content": error_response,
                "validation": validation_result
            })
            
            return {
                "success": False,
                "response_type": "error",
                "response": error_response,
                "validation": validation_result
            }
    
    async def _simulate_llm_workflow_generation(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate workflow using actual OpenAI API"""
        
        try:
            # Import OpenAI client
            from openai import AsyncOpenAI
            import os
            
            # Initialize OpenAI client
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.warning("No OpenAI API key found, using fallback workflow generation")
                return await self._fallback_workflow_generation(user_input)
            
            client = AsyncOpenAI(api_key=api_key)
            
            # Build workflow generation system prompt
            system_prompt = self._build_workflow_system_prompt()
            
            # Create messages for workflow generation
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a workflow for: {user_input}"}
            ]
            
            # Call OpenAI API for workflow generation
            response = await client.chat.completions.create(
                model=self.llm_config.get("model", "gpt-3.5-turbo"),
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent JSON output
                max_tokens=2000
            )
            
            workflow_response = response.choices[0].message.content.strip()
            
            # Try to parse the JSON response
            try:
                workflow_json = json.loads(workflow_response)
                logger.info(f"✅ OpenAI workflow generated for {self.agent_name}")
                return workflow_json
            except json.JSONDecodeError:
                logger.warning("OpenAI response was not valid JSON, using fallback")
                return await self._fallback_workflow_generation(user_input)
                
        except Exception as e:
            logger.error(f"❌ OpenAI workflow generation error: {e}")
            return await self._fallback_workflow_generation(user_input)
    
    def _build_workflow_system_prompt(self) -> str:
        """Build system prompt for workflow generation"""
        
        available_nodes = list(self.json_script_templates.keys())
        
        prompt = f"""You are an expert workflow automation engineer. Create JSON workflows from natural language descriptions.

Available Node Types: {', '.join(available_nodes)}

IMPORTANT: You must respond with ONLY valid JSON in this exact format:

{{
    "workflow_id": "workflow_unique_id",
    "workflow_name": "Descriptive Name",
    "trigger": {{
        "type": "manual",
        "config": {{}}
    }},
    "nodes": [
        {{
            "id": "node_1",
            "type": "node_type_from_available_list",
            "script": {{"driver": "driver_name", "action": "action_name", "parameters": {{}}}},
            "parameters": {{
                "param1": "{{{{variable_name}}}}",
                "param2": "value"
            }}
        }}
    ]
}}

Guidelines:
1. Use only node types from the available list
2. Create meaningful variable names in double curly braces
3. Include appropriate parameters for each node type
4. Keep workflows simple but functional
5. Use descriptive IDs and names

Respond with ONLY the JSON, no explanation or additional text."""
        
        return prompt
    
    async def _fallback_workflow_generation(self, user_input: str) -> Dict[str, Any]:
        """Fallback workflow generation when OpenAI API is unavailable"""
        
        workflow_id = f"workflow_{uuid.uuid4().hex[:8]}"
        
        # Example workflow based on common patterns
        if "email" in user_input.lower():
            return {
                "workflow_id": workflow_id,
                "workflow_name": "Email Automation",
                "trigger": {
                    "type": "manual",
                    "config": {}
                },
                "nodes": [
                    {
                        "id": "email_node_1",
                        "type": "email_send",
                        "script": self.json_script_templates["email_send"],
                        "parameters": {
                            "to_email": "{{recipient_email}}",
                            "subject": "{{email_subject}}",
                            "body": "{{email_body}}"
                        }
                    }
                ]
            }
        
        elif "data" in user_input.lower() or "fetch" in user_input.lower():
            return {
                "workflow_id": workflow_id,
                "workflow_name": "Data Fetch Automation",
                "trigger": {
                    "type": "manual",
                    "config": {}
                },
                "nodes": [
                    {
                        "id": "fetch_node_1",
                        "type": "data_fetch",
                        "script": self.json_script_templates["data_fetch"],
                        "parameters": {
                            "url": "{{api_endpoint}}",
                            "method": "GET"
                        }
                    }
                ]
            }
        
        else:
            # Generic workflow
            return {
                "workflow_id": workflow_id,
                "workflow_name": "Custom Automation",
                "trigger": {
                    "type": "manual",
                    "config": {}
                },
                "nodes": [
                    {
                        "id": "ai_node_1",
                        "type": "ai_content_generation",
                        "script": self.json_script_templates["ai_content_generation"],
                        "parameters": {
                            "prompt": user_input
                        }
                    }
                ]
            }
    
    def _validate_workflow(self, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow JSON against schemas"""
        
        try:
            # Basic structure validation
            required_fields = ["workflow_id", "nodes"]
            missing_fields = [field for field in required_fields if field not in workflow_json]
            
            if missing_fields:
                return {
                    "valid": False,
                    "errors": f"Missing required fields: {missing_fields}"
                }
            
            # Validate nodes
            for node in workflow_json.get("nodes", []):
                node_type = node.get("type")
                if node_type not in self.json_script_templates:
                    return {
                        "valid": False,
                        "errors": f"Unknown node type: {node_type}"
                    }
            
            return {
                "valid": True,
                "errors": None,
                "validated_nodes": len(workflow_json.get("nodes", []))
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": f"Validation error: {str(e)}"
            }
    
    def _explain_workflow(self, workflow_json: Dict[str, Any]) -> str:
        """Generate human-readable explanation of the workflow"""
        
        workflow_name = workflow_json.get("workflow_name", "Automation")
        nodes = workflow_json.get("nodes", [])
        
        explanation = f"**{workflow_name}**\n"
        explanation += f"Trigger: {workflow_json.get('trigger', {}).get('type', 'manual')}\n\n"
        explanation += "Steps:\n"
        
        for i, node in enumerate(nodes, 1):
            node_type = node.get("type", "unknown")
            node_id = node.get("id", f"node_{i}")
            
            if node_type == "email_send":
                explanation += f"{i}. Send email (Node: {node_id})\n"
            elif node_type == "data_fetch":
                explanation += f"{i}. Fetch data from API (Node: {node_id})\n"
            elif node_type == "ai_content_generation":
                explanation += f"{i}. Generate AI content (Node: {node_id})\n"
            elif node_type == "webhook":
                explanation += f"{i}. Send webhook notification (Node: {node_id})\n"
            elif node_type == "twilio_sms":
                explanation += f"{i}. Send SMS message (Node: {node_id})\n"
            else:
                explanation += f"{i}. Execute {node_type} (Node: {node_id})\n"
        
        return explanation
    
    async def _generate_conversational_response(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate conversational response using memory and personality"""
        
        logger.info(f"💬 Generating conversational response for agent {self.agent_name}")
        
        # Use memory context for personalized response
        memory_context = self._get_relevant_memory(user_input)
        
        # Simulate personalized response based on personality and memory
        response = await self._simulate_conversational_llm(user_input, memory_context, context)
        
        # Add to memory
        self.memory.append({
            "timestamp": datetime.now().isoformat(),
            "type": "assistant_response",
            "content": response
        })
        
        return {
            "success": True,
            "response_type": "conversational",
            "response": response,
            "memory_updated": True
        }
    
    def _get_relevant_memory(self, user_input: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get relevant memory entries for context"""
        
        # Simple relevance: return last N entries
        # In production, this could use semantic similarity
        return self.memory[-limit:] if self.memory else []
    
    async def _simulate_conversational_llm(self, user_input: str, memory_context: List[Dict[str, Any]], context: Dict[str, Any] = None) -> str:
        """Generate conversational response using actual OpenAI API"""
        
        try:
            # Import OpenAI client
            from openai import AsyncOpenAI
            import os
            
            # Initialize OpenAI client
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.warning("No OpenAI API key found, using fallback response")
                return await self._fallback_conversational_response(user_input)
            
            client = AsyncOpenAI(api_key=api_key)
            
            # Build conversation context from memory
            messages = [
                {
                    "role": "system",
                    "content": self._build_conversational_system_prompt()
                }
            ]
            
            # Add relevant memory context
            for entry in memory_context[-3:]:  # Last 3 memory entries
                if entry.get("type") == "user_input":
                    messages.append({"role": "user", "content": entry.get("content", "")})
                elif entry.get("type") == "assistant_response":
                    messages.append({"role": "assistant", "content": entry.get("content", "")})
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            # Call OpenAI API
            response = await client.chat.completions.create(
                model=self.llm_config.get("model", "gpt-3.5-turbo"),
                messages=messages,
                temperature=self.llm_config.get("temperature", 0.7),
                max_tokens=self.llm_config.get("max_tokens", 1000)
            )
            
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"✅ OpenAI response generated for {self.agent_name}")
            return ai_response
            
        except Exception as e:
            logger.error(f"❌ OpenAI API error: {e}")
            return await self._fallback_conversational_response(user_input)
    
    def _build_conversational_system_prompt(self) -> str:
        """Build system prompt for conversational mode"""
        
        personality = self.personality
        agent_name = self.agent_name
        role = personality.get("role", "AI assistant")
        style = personality.get("communication_style", "professional")
        expertise = personality.get("expertise", [])
        
        prompt = f"""You are {agent_name}, a {role}.

Communication Style: {style}
Expertise Areas: {', '.join(expertise) if expertise else 'General assistance'}

Personality Traits:
- Be helpful, knowledgeable, and {style}
- Stay in character as {agent_name}
- Provide accurate and useful information
- If you don't know something, admit it honestly
- Focus on assisting with {role} related tasks

You can help with:
1. General conversation and questions
2. Automation and workflow advice
3. Technical assistance
4. Information and explanations

Respond naturally and conversationally while maintaining your helpful assistant persona."""
        
        return prompt
    
    async def _fallback_conversational_response(self, user_input: str) -> str:
        """Fallback response when OpenAI API is unavailable"""
        
        personality_style = self.personality.get("communication_style", "professional")
        agent_role = self.personality.get("role", "assistant")
        
        user_lower = user_input.lower()
        
        if "hello" in user_lower or "hi" in user_lower:
            if personality_style == "friendly":
                return f"Hi there! I'm {self.agent_name}, your {agent_role}. How can I help you today?"
            else:
                return f"Hello. I'm {self.agent_name}, ready to assist you."
        
        elif any(phrase in user_lower for phrase in ['how are you', 'how do you do']):
            return f"I'm doing great, thank you for asking! I'm {self.agent_name} and I'm here to help you. What can I assist you with?"
        
        elif "name" in user_lower and "remember" in user_input.lower():
            # Check memory for stored name
            for entry in self.memory:
                if "name" in entry.get("content", "").lower():
                    return f"I remember! Based on our previous conversation, you mentioned your name. How can I help you further?"
            
            return f"I'll remember that information for our future conversations. What else can I help you with?"
        
        else:
            return f"As your {agent_role}, I understand you said: '{user_input}'. I'm here to help! Could you tell me more about what you'd like assistance with?"
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information"""
        
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "personality": self.personality,
            "memory_entries": len(self.memory),
            "available_nodes": list(self.json_script_templates.keys()),
            "llm_config": self.llm_config
        }
    
    def clear_memory(self) -> bool:
        """Clear conversation memory"""
        
        self.memory.clear()
        logger.info(f"🧹 Cleared memory for agent {self.agent_name}")
        return True


class MCP_LLM_Orchestrator:
    """Custom MCP LLM Orchestrator managing multiple agents with database storage"""
    
    def __init__(self, db_path: str = "workflow.db"):
        """Initialize the Custom MCP LLM Orchestrator"""
        
        logger.info("🚀 Initializing Custom MCP LLM Orchestrator")
        
        self.db_path = db_path
        self.agents: Dict[str, CustomMCPLLMAgent] = {}
        
        # Initialize database
        self._init_database()
        
        # Load existing agents from database
        asyncio.create_task(self._load_agents_from_db())
        
        logger.info("✅ Custom MCP LLM Orchestrator initialized")
    
    def _init_database(self):
        """Initialize SQLite database for Custom MCP system"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Custom agents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS custom_agents (
                    agent_id TEXT PRIMARY KEY,
                    agent_name TEXT NOT NULL,
                    personality TEXT NOT NULL,
                    llm_config TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Agent conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_conversations (
                    conversation_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    user_id TEXT,
                    memory_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES custom_agents (agent_id)
                )
            ''')
            
            # Agent workflows table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_workflows (
                    workflow_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    workflow_name TEXT NOT NULL,
                    workflow_json TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES custom_agents (agent_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("📊 Custom MCP database initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
    
    async def _load_agents_from_db(self):
        """Load existing agents from database"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT agent_id, agent_name, personality, llm_config FROM custom_agents")
            rows = cursor.fetchall()
            
            for agent_id, agent_name, personality_json, llm_config_json in rows:
                personality = json.loads(personality_json)
                llm_config = json.loads(llm_config_json)
                
                agent = CustomMCPLLMAgent(agent_id, agent_name, personality, llm_config)
                self.agents[agent_id] = agent
                
                logger.info(f"📂 Loaded agent {agent_name} from database")
            
            conn.close()
            logger.info(f"✅ Loaded {len(self.agents)} agents from database")
            
        except Exception as e:
            logger.error(f"Failed to load agents from database: {e}")
    
    async def create_agent(self, agent_id: str, agent_name: str, personality: Dict[str, Any], llm_config: Dict[str, Any]) -> bool:
        """Create a new Custom MCP LLM agent"""
        
        try:
            # Create agent instance
            agent = CustomMCPLLMAgent(agent_id, agent_name, personality, llm_config)
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO custom_agents 
                (agent_id, agent_name, personality, llm_config, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                agent_id,
                agent_name,
                json.dumps(personality),
                json.dumps(llm_config),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            # Add to memory
            self.agents[agent_id] = agent
            
            logger.info(f"✅ Created Custom MCP agent: {agent_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create agent {agent_name}: {e}")
            return False
    
    async def get_agent(self, agent_id: str) -> Optional[CustomMCPLLMAgent]:
        """Get agent by ID"""
        
        return self.agents.get(agent_id)
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents"""
        
        return [agent.get_info() for agent in self.agents.values()]
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete agent"""
        
        try:
            # Remove from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM custom_agents WHERE agent_id = ?", (agent_id,))
            cursor.execute("DELETE FROM agent_conversations WHERE agent_id = ?", (agent_id,))
            cursor.execute("DELETE FROM agent_workflows WHERE agent_id = ?", (agent_id,))
            
            conn.commit()
            conn.close()
            
            # Remove from memory
            if agent_id in self.agents:
                del self.agents[agent_id]
            
            logger.info(f"🗑️ Deleted agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete agent {agent_id}: {e}")
            return False
    
    async def process_with_agent(self, agent_id: str, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process message with specific agent"""
        
        agent = await self.get_agent(agent_id)
        if not agent:
            return {
                "success": False,
                "error": f"Agent {agent_id} not found"
            }
        
        return await agent.process_message(user_input, context)
    
    async def create_workflow(self, agent_id: str, workflow_json: Dict[str, Any]) -> str:
        """Create workflow for agent"""
        
        try:
            workflow_id = workflow_json.get("workflow_id", f"workflow_{uuid.uuid4().hex[:8]}")
            workflow_name = workflow_json.get("workflow_name", "Custom Workflow")
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO agent_workflows 
                (workflow_id, agent_id, workflow_name, workflow_json, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                workflow_id,
                agent_id,
                workflow_name,
                json.dumps(workflow_json),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Created workflow {workflow_name} for agent {agent_id}")
            return workflow_id
            
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            raise
    
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute workflow (integrates with automation engine)"""
        
        try:
            # Get workflow from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT agent_id, workflow_json FROM agent_workflows WHERE workflow_id = ? AND status = 'active'",
                (workflow_id,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return {
                    "success": False,
                    "error": f"Workflow {workflow_id} not found or inactive"
                }
            
            agent_id, workflow_json = result
            workflow = json.loads(workflow_json)
            
            # Import and use automation engine
            from simple_automation_engine import get_automation_engine
            automation_engine = get_automation_engine()
            
            # Execute workflow using automation engine
            execution_result = await automation_engine.execute_workflow_nodes(workflow)
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "execution_result": execution_result
            }
            
        except Exception as e:
            logger.error(f"Failed to execute workflow {workflow_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_agent_memory(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get agent memory"""
        
        agent = await self.get_agent(agent_id)
        if agent:
            return agent.memory
        return []
    
    async def clear_agent_memory(self, agent_id: str) -> bool:
        """Clear agent memory"""
        
        agent = await self.get_agent(agent_id)
        if agent:
            return agent.clear_memory()
        return False
    
    def get_available_node_types(self) -> List[str]:
        """Get available workflow node types"""
        
        # Return node types from any agent (they all have the same templates)
        if self.agents:
            first_agent = list(self.agents.values())[0]
            return list(first_agent.json_script_templates.keys())
        
        # Fallback list
        return ["email_send", "ai_content_generation", "data_fetch", "webhook", "twilio_sms", "conditional", "claude_ai"]
    
    def get_node_template(self, node_type: str) -> Dict[str, Any]:
        """Get JSON template for node type"""
        
        if self.agents:
            first_agent = list(self.agents.values())[0]
            return first_agent.json_script_templates.get(node_type, {})
        
        return {}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        
        return {
            "status": "operational",
            "agents_count": len(self.agents),
            "available_nodes": len(self.get_available_node_types()),
            "database": "connected",
            "version": "1.0.0"
        }


# Global orchestrator instance
mcp_orchestrator = None

def get_mcp_orchestrator() -> MCP_LLM_Orchestrator:
    """Get or create MCP orchestrator instance"""
    
    global mcp_orchestrator
    if mcp_orchestrator is None:
        mcp_orchestrator = MCP_LLM_Orchestrator()
    return mcp_orchestrator

# Utility functions for API integration
async def create_custom_agent(agent_id: str, agent_name: str, personality: Dict[str, Any], llm_config: Dict[str, Any]) -> bool:
    """Create custom agent via orchestrator"""
    
    orchestrator = get_mcp_orchestrator()
    return await orchestrator.create_agent(agent_id, agent_name, personality, llm_config)

async def process_agent_message(agent_id: str, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Process message with agent"""
    
    orchestrator = get_mcp_orchestrator()
    return await orchestrator.process_with_agent(agent_id, user_input, context)

async def create_agent_workflow(agent_id: str, workflow_json: Dict[str, Any]) -> str:
    """Create workflow for agent"""
    
    orchestrator = get_mcp_orchestrator()
    return await orchestrator.create_workflow(agent_id, workflow_json)

if __name__ == "__main__":
    # Test the Custom MCP LLM system
    async def test_custom_mcp():
        logger.info("🧪 Testing Custom MCP LLM System")
        
        orchestrator = get_mcp_orchestrator()
        
        # Create test agent
        agent_id = "test_agent"
        personality = {
            "role": "Marketing Assistant",
            "communication_style": "friendly",
            "expertise": "Email marketing and content generation"
        }
        llm_config = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.7
        }
        
        success = await orchestrator.create_agent(agent_id, "Marketing Assistant", personality, llm_config)
        logger.info(f"Agent creation: {'✅' if success else '❌'}")
        
        # Test conversation
        response = await orchestrator.process_with_agent(
            agent_id, 
            "Create an email marketing campaign for our new fitness app"
        )
        logger.info(f"Workflow response: {response}")
        
        logger.info("✅ Custom MCP LLM test completed")
    
    asyncio.run(test_custom_mcp())
