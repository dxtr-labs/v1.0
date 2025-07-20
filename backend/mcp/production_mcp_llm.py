"""
Production Dual MCP LLM Orchestrator
Implements the production architecture with dual MCP system:
1. Custom MCP LLM - Database-stored agent-specific AI with memory & personality
2. Inhouse AI - Driver-based general purpose AI for workflow nodes
"""
import logging
import asyncio
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import sqlite3

logger = logging.getLogger(__name__)

class ProductionMCPOrchestrator:
    def __init__(self, db_connection=None):
        """
        Production Dual MCP LLM Orchestrator:
        1. Custom MCP LLM - Database-stored agent-specific AI with memory & personality
        2. Inhouse AI - Driver-based general purpose AI for workflow nodes
        """
        logger.info("🚀 Initializing Production Dual MCP LLM Orchestrator")
        
        # Database connection for custom agent MCP LLMs
        self.db_connection = db_connection or self._init_database()
        
        # Inhouse AI drivers (general purpose AI nodes) 
        self.inhouse_drivers = self._initialize_inhouse_ai_drivers()
        
        # Custom MCP LLM storage (agent-specific) - loaded from database
        self.agent_mcps = {}  # Cached agent MCP instances
        
        # JSON script templates for all workflow nodes
        self.node_templates = self._load_node_templates()
        
        # Conversation memory for real-time processing
        self.conversation_memory = {}
        
        # Drivers directory path
        self.drivers_path = os.path.join(os.path.dirname(__file__), 'drivers')
        
        logger.info("✅ Production MCP architecture initialized - Dual system ready")

    def _init_database(self):
        """Initialize database connection for agent MCP storage"""
        try:
            conn = sqlite3.connect('workflow.db')
            cursor = conn.cursor()
            
            # Create agent MCP LLM storage table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_mcps (
                    agent_id TEXT PRIMARY KEY,
                    agent_name TEXT NOT NULL,
                    llm_config TEXT NOT NULL,
                    memory_context TEXT,
                    personality_traits TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create workflow storage table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflows (
                    workflow_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    workflow_json TEXT NOT NULL,
                    trigger_config TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agent_mcps (agent_id)
                )
            ''')
            
            conn.commit()
            logger.info("📊 Database initialized for agent MCP storage")
            return conn
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return None

    def _initialize_inhouse_ai_drivers(self):
        """Initialize inhouse AI drivers for general purpose workflow nodes"""
        logger.info("🔧 Initializing Inhouse AI Drivers")
        
        return {
            "general": self._init_general_ai_driver(),
            "email": self._init_email_ai_driver(), 
            "content": self._init_content_ai_driver(),
            "data_processing": self._init_data_processing_driver(),
            "webhook": self._init_webhook_driver(),
            "conditional": self._init_conditional_driver()
        }

    def _init_general_ai_driver(self):
        """Initialize general purpose AI driver"""
        return {
            "type": "general_ai",
            "capabilities": ["text_processing", "decision_making", "context_analysis"],
            "driver_path": os.path.join(self.drivers_path, "openai_driver.py")
        }

    def _init_email_ai_driver(self):
        """Initialize email AI driver"""
        return {
            "type": "email_ai",
            "capabilities": ["email_generation", "subject_optimization", "personalization"],
            "driver_path": os.path.join(self.drivers_path, "email_send_driver.py")
        }

    def _init_content_ai_driver(self):
        """Initialize content generation AI driver"""
        return {
            "type": "content_ai", 
            "capabilities": ["content_generation", "style_adaptation", "audience_targeting"],
            "driver_path": os.path.join(self.drivers_path, "openai_driver.py")
        }

    def _init_data_processing_driver(self):
        """Initialize data processing driver"""
        return {
            "type": "data_processing",
            "capabilities": ["data_fetch", "api_integration", "data_transformation"],
            "driver_path": os.path.join(self.drivers_path, "http_request_driver.py")
        }

    def _init_webhook_driver(self):
        """Initialize webhook driver"""
        return {
            "type": "webhook",
            "capabilities": ["webhook_sending", "payload_formatting", "response_handling"],
            "driver_path": os.path.join(self.drivers_path, "web_hook_driver.py")
        }

    def _init_conditional_driver(self):
        """Initialize conditional logic driver"""
        return {
            "type": "conditional",
            "capabilities": ["condition_evaluation", "branching_logic", "decision_trees"],
            "driver_path": os.path.join(self.drivers_path, "base_driver.py")
        }

    def _load_node_templates(self):
        """Load JSON script templates for all workflow nodes"""
        logger.info("📋 Loading JSON script templates for workflow nodes")
        
        return {
            "email_send": {
                "type": "email_send",
                "parameters": ["toEmail", "subject", "content", "sender_name"],
                "output": "delivery_status",
                "driver": "email_send_driver"
            },
            "ai_content_generation": {
                "type": "ai_content_generation", 
                "parameters": ["prompt", "content_type", "style", "target_audience"],
                "output": "generated_content",
                "driver": "openai_driver"
            },
            "data_fetch": {
                "type": "data_fetch",
                "parameters": ["url", "method", "headers", "authentication"],
                "output": "fetched_data",
                "driver": "http_request_driver"
            },
            "conditional": {
                "type": "conditional",
                "parameters": ["condition", "true_action", "false_action"],
                "output": "next_node",
                "driver": "base_driver"
            },
            "webhook": {
                "type": "webhook",
                "parameters": ["url", "method", "payload", "headers"],
                "output": "response_data",
                "driver": "web_hook_driver"
            },
            "twilio_sms": {
                "type": "twilio_sms",
                "parameters": ["to_number", "message", "from_number"],
                "output": "sms_status",
                "driver": "twilio_driver"
            },
            "claude_ai": {
                "type": "claude_ai",
                "parameters": ["prompt", "model", "max_tokens"],
                "output": "ai_response",
                "driver": "claude_driver"
            }
        }

    async def get_agent_mcp(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get or load agent-specific Custom MCP LLM from database
        
        Args:
            agent_id: Agent ID to retrieve MCP for
            
        Returns:
            Agent MCP configuration or None if not found
        """
        # Check cache first
        if agent_id in self.agent_mcps:
            return self.agent_mcps[agent_id]
            
        # Load from database
        if self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute(
                    "SELECT agent_name, llm_config, memory_context, personality_traits FROM agent_mcps WHERE agent_id = ?",
                    (agent_id,)
                )
                result = cursor.fetchone()
                
                if result:
                    agent_name, llm_config, memory_context, personality_traits = result
                    
                    agent_mcp = {
                        "agent_id": agent_id,
                        "agent_name": agent_name,
                        "llm_config": json.loads(llm_config) if llm_config else {},
                        "memory_context": json.loads(memory_context) if memory_context else [],
                        "personality_traits": json.loads(personality_traits) if personality_traits else {}
                    }
                    
                    # Cache the agent MCP
                    self.agent_mcps[agent_id] = agent_mcp
                    logger.info(f"📥 Loaded Custom MCP LLM for agent {agent_id}")
                    return agent_mcp
                    
            except Exception as e:
                logger.error(f"Failed to load agent MCP for {agent_id}: {e}")
                
        return None

    async def create_agent_mcp(self, agent_id: str, agent_name: str, llm_config: Dict[str, Any], 
                              personality_traits: Dict[str, Any] = None) -> bool:
        """
        Create new Custom MCP LLM for agent and store in database
        
        Args:
            agent_id: Unique agent ID
            agent_name: Human-readable agent name
            llm_config: LLM configuration (model, parameters, etc.)
            personality_traits: Agent personality configuration
            
        Returns:
            True if created successfully, False otherwise
        """
        if not self.db_connection:
            logger.error("No database connection available")
            return False
            
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO agent_mcps 
                (agent_id, agent_name, llm_config, memory_context, personality_traits, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                agent_id,
                agent_name,
                json.dumps(llm_config),
                json.dumps([]),  # Empty memory context for new agent
                json.dumps(personality_traits or {}),
                datetime.now().isoformat()
            ))
            
            self.db_connection.commit()
            
            # Cache the new agent MCP
            self.agent_mcps[agent_id] = {
                "agent_id": agent_id,
                "agent_name": agent_name,
                "llm_config": llm_config,
                "memory_context": [],
                "personality_traits": personality_traits or {}
            }
            
            logger.info(f"✅ Created Custom MCP LLM for agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create agent MCP for {agent_id}: {e}")
            return False

    async def process_with_custom_mcp(self, agent_id: str, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process user input using agent-specific Custom MCP LLM
        
        Args:
            agent_id: Agent ID to use for processing
            user_input: User's input message
            context: Additional context for processing
            
        Returns:
            Processing result with response and metadata
        """
        agent_mcp = await self.get_agent_mcp(agent_id)
        
        if not agent_mcp:
            logger.warning(f"No Custom MCP LLM found for agent {agent_id}")
            return {
                "success": False,
                "error": "Agent MCP not found",
                "agent_id": agent_id
            }
            
        try:
            # Apply agent personality and memory context
            personality = agent_mcp.get("personality_traits", {})
            memory = agent_mcp.get("memory_context", [])
            
            # Generate response using agent-specific LLM config
            response = await self._generate_agent_response(
                agent_mcp["llm_config"],
                user_input,
                personality,
                memory,
                context or {}
            )
            
            # Update memory context
            await self._update_agent_memory(agent_id, user_input, response)
            
            return {
                "success": True,
                "response": response,
                "agent_id": agent_id,
                "agent_name": agent_mcp["agent_name"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to process with Custom MCP for agent {agent_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": agent_id
            }

    async def process_with_inhouse_ai(self, node_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process workflow node using Inhouse AI drivers
        
        Args:
            node_type: Type of workflow node (email_send, data_fetch, etc.)
            parameters: Node parameters
            
        Returns:
            Processing result
        """
        if node_type not in self.node_templates:
            return {
                "success": False,
                "error": f"Unknown node type: {node_type}"
            }
            
        template = self.node_templates[node_type]
        driver_name = template["driver"]
        
        try:
            # Load appropriate inhouse AI driver
            driver = await self._load_driver(driver_name)
            
            # Execute node using driver
            result = await self._execute_node_with_driver(driver, node_type, parameters)
            
            return {
                "success": True,
                "node_type": node_type,
                "result": result,
                "driver_used": driver_name,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to process node {node_type} with Inhouse AI: {e}")
            return {
                "success": False,
                "error": str(e),
                "node_type": node_type
            }

    async def _generate_agent_response(self, llm_config: Dict[str, Any], user_input: str, 
                                     personality: Dict[str, Any], memory: List[Dict[str, Any]], 
                                     context: Dict[str, Any]) -> str:
        """Generate response using agent-specific LLM configuration"""
        # This would integrate with actual LLM service (OpenAI, Claude, etc.)
        # For now, return a formatted response based on personality
        
        tone = personality.get("tone", "professional")
        expertise = personality.get("expertise", "general")
        
        response = f"[Agent Response - {tone} tone, {expertise} expertise]\n"
        response += f"Processing: {user_input}\n"
        
        if memory:
            response += f"Context from {len(memory)} previous interactions.\n"
            
        response += "This response would be generated by the agent's Custom MCP LLM."
        
        return response

    async def _update_agent_memory(self, agent_id: str, user_input: str, response: str):
        """Update agent memory context in database"""
        if not self.db_connection:
            return
            
        try:
            # Get current memory
            agent_mcp = self.agent_mcps.get(agent_id)
            if not agent_mcp:
                return
                
            memory = agent_mcp["memory_context"]
            
            # Add new interaction
            memory.append({
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "agent_response": response
            })
            
            # Keep only last 50 interactions
            if len(memory) > 50:
                memory = memory[-50:]
                
            # Update database
            cursor = self.db_connection.cursor()
            cursor.execute(
                "UPDATE agent_mcps SET memory_context = ?, updated_at = ? WHERE agent_id = ?",
                (json.dumps(memory), datetime.now().isoformat(), agent_id)
            )
            self.db_connection.commit()
            
            # Update cache
            agent_mcp["memory_context"] = memory
            
        except Exception as e:
            logger.error(f"Failed to update agent memory for {agent_id}: {e}")

    async def _load_driver(self, driver_name: str):
        """Load driver from drivers folder"""
        driver_path = os.path.join(self.drivers_path, f"{driver_name}.py")
        
        if not os.path.exists(driver_path):
            raise Exception(f"Driver not found: {driver_path}")
            
        # This would dynamically import and instantiate the driver
        logger.info(f"Loading driver: {driver_name}")
        return f"Driver_{driver_name}_loaded"

    async def _execute_node_with_driver(self, driver, node_type: str, parameters: Dict[str, Any]):
        """Execute workflow node using loaded driver"""
        # This would execute the actual driver with parameters
        logger.info(f"Executing {node_type} node with driver {driver}")
        
        return {
            "status": "completed",
            "output": f"Node {node_type} executed successfully",
            "parameters_used": parameters
        }

    def get_available_node_types(self) -> List[str]:
        """Get list of available workflow node types"""
        return list(self.node_templates.keys())

    def get_node_template(self, node_type: str) -> Optional[Dict[str, Any]]:
        """Get JSON template for specific node type"""
        return self.node_templates.get(node_type)

    async def create_workflow(self, agent_id: str, workflow_json: Dict[str, Any], 
                             trigger_config: Dict[str, Any] = None) -> str:
        """Create and store workflow in database"""
        if not self.db_connection:
            raise Exception("No database connection available")
            
        workflow_id = f"workflow_{agent_id}_{int(datetime.now().timestamp())}"
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO workflows 
                (workflow_id, agent_id, workflow_json, trigger_config, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                workflow_id,
                agent_id,
                json.dumps(workflow_json),
                json.dumps(trigger_config or {}),
                datetime.now().isoformat()
            ))
            
            self.db_connection.commit()
            logger.info(f"✅ Created workflow {workflow_id} for agent {agent_id}")
            return workflow_id
            
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            raise

    async def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute stored workflow by ID"""
        if not self.db_connection:
            return {"success": False, "error": "No database connection"}
            
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "SELECT agent_id, workflow_json FROM workflows WHERE workflow_id = ? AND status = 'active'",
                (workflow_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                return {"success": False, "error": "Workflow not found or inactive"}
                
            agent_id, workflow_json = result
            workflow = json.loads(workflow_json)
            
            logger.info(f"🚀 Executing workflow {workflow_id} for agent {agent_id}")
            
            # Execute workflow nodes in sequence
            execution_results = []
            
            for node in workflow.get("nodes", []):
                node_type = node["type"]
                parameters = node.get("parameters", {})
                
                # Merge input data if this is the first node
                if not execution_results and input_data:
                    parameters.update(input_data)
                    
                result = await self.process_with_inhouse_ai(node_type, parameters)
                execution_results.append(result)
                
                # Stop if node failed
                if not result.get("success", False):
                    break
                    
            return {
                "success": True,
                "workflow_id": workflow_id,
                "agent_id": agent_id,
                "execution_results": execution_results,
                "completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to execute workflow {workflow_id}: {e}")
            return {"success": False, "error": str(e)}

    def get_system_status(self) -> Dict[str, Any]:
        """Get production system status"""
        return {
            "system": "Production Dual MCP LLM Orchestrator",
            "status": "operational",
            "architecture": {
                "custom_mcp_llms": {
                    "cached_agents": len(self.agent_mcps),
                    "database_connected": self.db_connection is not None
                },
                "inhouse_ai_drivers": {
                    "available_drivers": len(self.inhouse_drivers),
                    "driver_types": list(self.inhouse_drivers.keys())
                },
                "workflow_nodes": {
                    "available_templates": len(self.node_templates),
                    "node_types": list(self.node_templates.keys())
                }
            },
            "drivers_path": self.drivers_path,
            "timestamp": datetime.now().isoformat()
        }
