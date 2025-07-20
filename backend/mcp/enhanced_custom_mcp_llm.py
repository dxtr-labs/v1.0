"""
Enhanced Custom MCP LLM for AI Agents
- Individual memory and personality per agent
- JSON script templates for all workflow nodes
- Integration with drivers and automation engine
"""
import logging
import asyncio
import json
import os
import sqlite3
from typing import Dict, Any, Optional, List
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class CustomMCPLLM:
    def __init__(self, db_connection=None):
        """
        Enhanced Custom MCP LLM for individual AI agents
        - Stores memory and personality per agent
        - Has JSON scripts for all workflow nodes
        - Integrates with drivers and automation engine
        """
        logger.info("🤖 Initializing Enhanced Custom MCP LLM System")
        
        # Database connection for agent storage
        self.db_connection = db_connection or self._init_database()
        
        # Agent-specific storage
        self.agent_configs = {}  # Cached agent configurations
        self.agent_memories = {}  # Cached conversation memories
        
        # JSON script templates for all workflow nodes
        self.json_scripts = self._load_json_scripts()
        
        # Drivers integration
        self.drivers_path = os.path.join(os.path.dirname(__file__), 'drivers')
        
        # Conversation memory storage
        self.conversation_memory = {}
        
        logger.info("✅ Enhanced Custom MCP LLM System initialized")

    def _init_database(self):
        """Initialize database for agent storage"""
        try:
            conn = sqlite3.connect('workflow.db')
            cursor = conn.cursor()
            
            # Create agents table with custom MCP LLM configs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS custom_agents (
                    agent_id TEXT PRIMARY KEY,
                    agent_name TEXT NOT NULL,
                    personality TEXT NOT NULL,
                    triggers TEXT NOT NULL,
                    custom_mcp_config TEXT NOT NULL,
                    memory_context TEXT DEFAULT '[]',
                    json_scripts TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create conversations table for chat history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    agent_response TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES custom_agents (agent_id)
                )
            ''')
            
            # Create workflows table for stored automation
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_workflows (
                    workflow_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    workflow_name TEXT NOT NULL,
                    workflow_json TEXT NOT NULL,
                    trigger_config TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES custom_agents (agent_id)
                )
            ''')
            
            conn.commit()
            logger.info("📊 Database initialized for Custom MCP LLM agents")
            return conn
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return None

    def _load_json_scripts(self):
        """Load JSON script templates for all workflow nodes"""
        logger.info("📋 Loading JSON scripts for all workflow nodes")
        
        return {
            # Communication Nodes
            "email_send": {
                "type": "email_send",
                "driver": "email_send_driver",
                "script": {
                    "action": "send_email",
                    "parameters": {
                        "toEmail": "{{recipient_email}}",
                        "subject": "{{email_subject}}",
                        "content": "{{email_content}}",
                        "sender_name": "{{sender_name}}",
                        "template": "{{template_type}}"
                    },
                    "output": "delivery_status"
                }
            },
            
            "twilio_sms": {
                "type": "twilio_sms", 
                "driver": "twilio_driver",
                "script": {
                    "action": "send_sms",
                    "parameters": {
                        "to_number": "{{phone_number}}",
                        "message": "{{sms_content}}",
                        "from_number": "{{twilio_number}}"
                    },
                    "output": "sms_status"
                }
            },
            
            "webhook": {
                "type": "webhook",
                "driver": "web_hook_driver", 
                "script": {
                    "action": "send_webhook",
                    "parameters": {
                        "url": "{{webhook_url}}",
                        "method": "{{http_method}}",
                        "payload": "{{webhook_payload}}",
                        "headers": "{{custom_headers}}"
                    },
                    "output": "webhook_response"
                }
            },
            
            # AI Processing Nodes
            "ai_content_generation": {
                "type": "ai_content_generation",
                "driver": "openai_driver",
                "script": {
                    "action": "generate_content",
                    "parameters": {
                        "prompt": "{{ai_prompt}}",
                        "content_type": "{{output_type}}",
                        "style": "{{writing_style}}",
                        "target_audience": "{{audience}}",
                        "model": "{{ai_model}}"
                    },
                    "output": "generated_content"
                }
            },
            
            "claude_ai": {
                "type": "claude_ai",
                "driver": "claude_driver",
                "script": {
                    "action": "process_with_claude",
                    "parameters": {
                        "prompt": "{{claude_prompt}}",
                        "model": "{{claude_model}}",
                        "max_tokens": "{{token_limit}}",
                        "temperature": "{{creativity_level}}"
                    },
                    "output": "claude_response"
                }
            },
            
            "inhouse_ai": {
                "type": "inhouse_ai",
                "driver": "mcp_llm_driver",
                "script": {
                    "action": "process_with_inhouse_ai",
                    "parameters": {
                        "agent_id": "{{inhouse_agent_id}}",
                        "input_data": "{{processing_data}}",
                        "task_type": "{{ai_task}}",
                        "context": "{{additional_context}}"
                    },
                    "output": "ai_result"
                }
            },
            
            # Data Processing Nodes
            "data_fetch": {
                "type": "data_fetch",
                "driver": "http_request_driver",
                "script": {
                    "action": "fetch_data",
                    "parameters": {
                        "url": "{{api_url}}",
                        "method": "{{request_method}}",
                        "headers": "{{request_headers}}",
                        "authentication": "{{auth_config}}",
                        "query_params": "{{url_parameters}}"
                    },
                    "output": "fetched_data"
                }
            },
            
            "data_transform": {
                "type": "data_transform",
                "driver": "base_driver",
                "script": {
                    "action": "transform_data",
                    "parameters": {
                        "input_data": "{{source_data}}",
                        "transformation_rules": "{{transform_rules}}",
                        "output_format": "{{target_format}}"
                    },
                    "output": "transformed_data"
                }
            },
            
            # Logic Nodes
            "conditional": {
                "type": "conditional",
                "driver": "base_driver",
                "script": {
                    "action": "evaluate_condition",
                    "parameters": {
                        "condition": "{{logical_condition}}",
                        "true_action": "{{if_true_node}}",
                        "false_action": "{{if_false_node}}",
                        "comparison_data": "{{compare_values}}"
                    },
                    "output": "next_node"
                }
            },
            
            "delay": {
                "type": "delay",
                "driver": "base_driver",
                "script": {
                    "action": "wait_delay",
                    "parameters": {
                        "delay_duration": "{{wait_time}}",
                        "delay_unit": "{{time_unit}}",
                        "message": "{{delay_message}}"
                    },
                    "output": "delay_complete"
                }
            },
            
            # Database Nodes
            "database_query": {
                "type": "database_query",
                "driver": "base_driver",
                "script": {
                    "action": "query_database",
                    "parameters": {
                        "query": "{{sql_query}}",
                        "database": "{{db_connection}}",
                        "parameters": "{{query_params}}"
                    },
                    "output": "query_results"
                }
            },
            
            "database_insert": {
                "type": "database_insert",
                "driver": "base_driver",
                "script": {
                    "action": "insert_data",
                    "parameters": {
                        "table": "{{target_table}}",
                        "data": "{{insert_data}}",
                        "database": "{{db_connection}}"
                    },
                    "output": "insert_status"
                }
            }
        }

    async def create_agent(self, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new custom AI agent with MCP LLM
        
        Args:
            agent_config: Agent configuration including personality, triggers, etc.
            
        Returns:
            Created agent details
        """
        try:
            agent_id = agent_config.get('agent_id') or f"agent_{int(datetime.now().timestamp())}"
            agent_name = agent_config.get('agent_name', 'Unnamed Agent')
            personality = agent_config.get('personality', {})
            triggers = agent_config.get('triggers', {})
            
            # Create custom MCP config for this agent
            custom_mcp_config = {
                "model": agent_config.get('model', 'gpt-4'),
                "temperature": agent_config.get('temperature', 0.7),
                "max_tokens": agent_config.get('max_tokens', 1000),
                "personality_traits": personality,
                "conversation_style": personality.get('style', 'professional'),
                "expertise_domain": personality.get('expertise', 'general')
            }
            
            # Store in database
            if self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO custom_agents 
                    (agent_id, agent_name, personality, triggers, custom_mcp_config, json_scripts, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    agent_id,
                    agent_name,
                    json.dumps(personality),
                    json.dumps(triggers),
                    json.dumps(custom_mcp_config),
                    json.dumps(self.json_scripts),
                    datetime.now().isoformat()
                ))
                self.db_connection.commit()
            
            # Cache agent config
            self.agent_configs[agent_id] = {
                "agent_id": agent_id,
                "agent_name": agent_name,
                "personality": personality,
                "triggers": triggers,
                "custom_mcp_config": custom_mcp_config,
                "json_scripts": self.json_scripts
            }
            
            logger.info(f"✅ Created custom AI agent: {agent_name} ({agent_id})")
            
            return {
                "success": True,
                "agent_id": agent_id,
                "agent_name": agent_name,
                "message": "Custom AI agent created successfully",
                "agent_config": self.agent_configs[agent_id]
            }
            
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create custom AI agent"
            }

    async def chat_with_agent(self, agent_id: str, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Chat with specific custom AI agent
        
        Args:
            agent_id: Agent ID to chat with
            user_message: User's message
            context: Additional context
            
        Returns:
            Agent's response with metadata
        """
        try:
            # Load agent if not cached
            if agent_id not in self.agent_configs:
                await self._load_agent_from_db(agent_id)
            
            if agent_id not in self.agent_configs:
                return {
                    "success": False,
                    "error": f"Agent {agent_id} not found",
                    "message": "Agent not found"
                }
            
            agent_config = self.agent_configs[agent_id]
            
            # Get conversation memory
            memory = await self._get_agent_memory(agent_id)
            
            # Generate response using agent's custom MCP LLM
            response = await self._generate_agent_response(
                agent_config,
                user_message,
                memory,
                context or {}
            )
            
            # Store conversation in memory and database
            await self._store_conversation(agent_id, user_message, response)
            
            return {
                "success": True,
                "agent_id": agent_id,
                "agent_name": agent_config["agent_name"],
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "memory_entries": len(memory)
            }
            
        except Exception as e:
            logger.error(f"Chat with agent {agent_id} failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": agent_id
            }

    async def get_agent_json_scripts(self, agent_id: str) -> Dict[str, Any]:
        """Get all JSON scripts available for an agent"""
        try:
            if agent_id not in self.agent_configs:
                await self._load_agent_from_db(agent_id)
            
            if agent_id not in self.agent_configs:
                return {
                    "success": False,
                    "error": "Agent not found"
                }
            
            agent_config = self.agent_configs[agent_id]
            
            return {
                "success": True,
                "agent_id": agent_id,
                "json_scripts": agent_config["json_scripts"],
                "available_nodes": list(agent_config["json_scripts"].keys()),
                "total_scripts": len(agent_config["json_scripts"])
            }
            
        except Exception as e:
            logger.error(f"Failed to get JSON scripts for agent {agent_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def create_workflow_from_chat(self, agent_id: str, workflow_description: str) -> Dict[str, Any]:
        """
        Create workflow from natural language description in chat
        
        Args:
            agent_id: Agent ID that will create the workflow
            workflow_description: Natural language description of desired workflow
            
        Returns:
            Generated workflow with JSON scripts
        """
        try:
            if agent_id not in self.agent_configs:
                await self._load_agent_from_db(agent_id)
            
            agent_config = self.agent_configs[agent_id]
            
            # Parse workflow description and map to JSON scripts
            workflow_nodes = await self._parse_workflow_description(workflow_description, agent_config)
            
            # Generate workflow ID
            workflow_id = f"workflow_{agent_id}_{int(datetime.now().timestamp())}"
            
            # Create complete workflow
            workflow_json = {
                "workflow_id": workflow_id,
                "agent_id": agent_id,
                "name": f"Workflow from {workflow_description[:50]}...",
                "description": workflow_description,
                "nodes": workflow_nodes,
                "created_from": "chat_interface",
                "created_at": datetime.now().isoformat()
            }
            
            # Store workflow in database
            if self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute('''
                    INSERT INTO agent_workflows 
                    (workflow_id, agent_id, workflow_name, workflow_json, trigger_config)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    workflow_id,
                    agent_id,
                    workflow_json["name"],
                    json.dumps(workflow_json),
                    json.dumps({"type": "manual", "created_from": "chat"})
                ))
                self.db_connection.commit()
            
            logger.info(f"✅ Created workflow {workflow_id} for agent {agent_id}")
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "workflow_json": workflow_json,
                "message": "Workflow created successfully from chat",
                "ready_for_automation_engine": True
            }
            
        except Exception as e:
            logger.error(f"Failed to create workflow from chat: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _load_agent_from_db(self, agent_id: str):
        """Load agent configuration from database"""
        if not self.db_connection:
            return
            
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                SELECT agent_name, personality, triggers, custom_mcp_config, json_scripts, memory_context
                FROM custom_agents WHERE agent_id = ?
            ''', (agent_id,))
            
            result = cursor.fetchone()
            if result:
                agent_name, personality, triggers, custom_mcp_config, json_scripts, memory_context = result
                
                self.agent_configs[agent_id] = {
                    "agent_id": agent_id,
                    "agent_name": agent_name,
                    "personality": json.loads(personality),
                    "triggers": json.loads(triggers),
                    "custom_mcp_config": json.loads(custom_mcp_config),
                    "json_scripts": json.loads(json_scripts)
                }
                
                # Load memory
                self.agent_memories[agent_id] = json.loads(memory_context) if memory_context else []
                
                logger.info(f"📥 Loaded agent {agent_id} from database")
                
        except Exception as e:
            logger.error(f"Failed to load agent {agent_id} from database: {e}")

    async def _get_agent_memory(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get conversation memory for agent"""
        if agent_id not in self.agent_memories:
            self.agent_memories[agent_id] = []
            
        return self.agent_memories[agent_id]

    async def _generate_agent_response(self, agent_config: Dict[str, Any], user_message: str, 
                                     memory: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
        """Generate response using agent's custom MCP LLM configuration"""
        
        personality = agent_config["personality"]
        custom_config = agent_config["custom_mcp_config"]
        
        # Apply personality traits
        tone = personality.get("tone", "professional")
        expertise = personality.get("expertise", "general")
        style = personality.get("style", "helpful")
        
        # Build context from memory
        memory_context = ""
        if memory:
            recent_conversations = memory[-3:] if len(memory) > 3 else memory
            memory_context = f" Based on our previous conversations: {', '.join([conv.get('summary', '') for conv in recent_conversations])}"
        
        # Generate response based on agent configuration
        response = f"[Agent: {agent_config['agent_name']} - {tone} tone, {expertise} expertise]\n"
        response += f"Processing your message: {user_message}\n"
        
        if memory_context:
            response += f"Context from memory:{memory_context}\n"
            
        # Add personality-driven response
        if expertise == "sales":
            response += "I can help you with sales automation, lead generation, and customer relationship management. "
        elif expertise == "support":
            response += "I'm here to provide excellent customer support and resolve any issues you may have. "
        elif expertise == "marketing":
            response += "I can assist with marketing automation, content creation, and campaign management. "
        else:
            response += "I'm here to help you with your automation and AI needs. "
            
        response += "What specific aspect would you like to explore further?"
        
        return response

    async def _store_conversation(self, agent_id: str, user_message: str, agent_response: str):
        """Store conversation in memory and database"""
        conversation_entry = {
            "user_message": user_message,
            "agent_response": agent_response,
            "timestamp": datetime.now().isoformat(),
            "summary": user_message[:100] + "..." if len(user_message) > 100 else user_message
        }
        
        # Add to memory cache
        if agent_id not in self.agent_memories:
            self.agent_memories[agent_id] = []
            
        self.agent_memories[agent_id].append(conversation_entry)
        
        # Keep only last 50 conversations in memory
        if len(self.agent_memories[agent_id]) > 50:
            self.agent_memories[agent_id] = self.agent_memories[agent_id][-50:]
        
        # Store in database
        if self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('''
                    INSERT INTO agent_conversations (agent_id, user_message, agent_response)
                    VALUES (?, ?, ?)
                ''', (agent_id, user_message, agent_response))
                
                # Update agent memory context
                cursor.execute('''
                    UPDATE custom_agents SET memory_context = ?, updated_at = ?
                    WHERE agent_id = ?
                ''', (
                    json.dumps(self.agent_memories[agent_id]),
                    datetime.now().isoformat(),
                    agent_id
                ))
                
                self.db_connection.commit()
                
            except Exception as e:
                logger.error(f"Failed to store conversation for agent {agent_id}: {e}")

    async def _parse_workflow_description(self, description: str, agent_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse natural language workflow description into JSON script nodes"""
        
        workflow_nodes = []
        json_scripts = agent_config["json_scripts"]
        
        # Simple keyword-based parsing (in production, use more sophisticated NLP)
        description_lower = description.lower()
        
        # Detect email actions
        if "email" in description_lower or "send email" in description_lower:
            workflow_nodes.append({
                "id": f"email_node_{len(workflow_nodes) + 1}",
                "type": "email_send",
                "script": json_scripts["email_send"]["script"],
                "driver": json_scripts["email_send"]["driver"]
            })
        
        # Detect SMS actions
        if "sms" in description_lower or "text message" in description_lower:
            workflow_nodes.append({
                "id": f"sms_node_{len(workflow_nodes) + 1}",
                "type": "twilio_sms",
                "script": json_scripts["twilio_sms"]["script"],
                "driver": json_scripts["twilio_sms"]["driver"]
            })
        
        # Detect AI content generation
        if "generate" in description_lower or "create content" in description_lower or "ai content" in description_lower:
            workflow_nodes.append({
                "id": f"ai_content_node_{len(workflow_nodes) + 1}",
                "type": "ai_content_generation",
                "script": json_scripts["ai_content_generation"]["script"],
                "driver": json_scripts["ai_content_generation"]["driver"]
            })
        
        # Detect data fetching
        if "fetch data" in description_lower or "get data" in description_lower or "api call" in description_lower:
            workflow_nodes.append({
                "id": f"data_fetch_node_{len(workflow_nodes) + 1}",
                "type": "data_fetch",
                "script": json_scripts["data_fetch"]["script"],
                "driver": json_scripts["data_fetch"]["driver"]
            })
        
        # Detect webhooks
        if "webhook" in description_lower or "send webhook" in description_lower:
            workflow_nodes.append({
                "id": f"webhook_node_{len(workflow_nodes) + 1}",
                "type": "webhook",
                "script": json_scripts["webhook"]["script"],
                "driver": json_scripts["webhook"]["driver"]
            })
        
        # If no specific nodes detected, add a general AI processing node
        if not workflow_nodes:
            workflow_nodes.append({
                "id": "general_ai_node_1",
                "type": "inhouse_ai",
                "script": json_scripts["inhouse_ai"]["script"],
                "driver": json_scripts["inhouse_ai"]["driver"]
            })
        
        return workflow_nodes

    def get_all_agents(self) -> Dict[str, Any]:
        """Get all created agents"""
        try:
            agents = []
            
            if self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute('''
                    SELECT agent_id, agent_name, personality, triggers, created_at
                    FROM custom_agents ORDER BY created_at DESC
                ''')
                
                for row in cursor.fetchall():
                    agent_id, agent_name, personality, triggers, created_at = row
                    agents.append({
                        "agent_id": agent_id,
                        "agent_name": agent_name,
                        "personality": json.loads(personality),
                        "triggers": json.loads(triggers),
                        "created_at": created_at
                    })
            
            return {
                "success": True,
                "agents": agents,
                "total_agents": len(agents)
            }
            
        except Exception as e:
            logger.error(f"Failed to get all agents: {e}")
            return {
                "success": False,
                "error": str(e),
                "agents": []
            }

    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "system": "Enhanced Custom MCP LLM System",
            "status": "operational",
            "features": {
                "custom_agents": len(self.agent_configs),
                "json_scripts": len(self.json_scripts),
                "database_connected": self.db_connection is not None,
                "drivers_available": os.path.exists(self.drivers_path)
            },
            "capabilities": [
                "Individual agent memory storage",
                "Personality-driven responses", 
                "JSON script templates for all nodes",
                "Driver integration",
                "Workflow creation from chat",
                "Database persistence"
            ],
            "timestamp": datetime.now().isoformat()
        }
