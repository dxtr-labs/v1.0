"""
Enhanced MCP LLM Orchestrator with Database Integration
Stores memory, personality, and handles automation workflows with preview
"""
import logging
import asyncio
import asyncpg
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DatabaseMCP_LLM_Orchestrator:
    def __init__(self, db_pool):
        """
        Enhanced MCP LLM Orchestrator with database integration
        """
        self.db_pool = db_pool
        logger.info("Initializing Database MCP LLM Orchestrator")
        self.initialized = True

    async def get_or_create_agent(self, user_id: str, agent_name: str = "Sam - Personal Assistant") -> Dict[str, Any]:
        """
        Get or create an MCP LLM agent for the user
        """
        async with self.db_pool.acquire() as conn:
            # Check if agent exists
            agent = await conn.fetchrow(
                "SELECT * FROM mcp_llm_agents WHERE user_id = $1 AND agent_name = $2",
                uuid.UUID(user_id), agent_name
            )
            
            if agent:
                return dict(agent)
            
            # Create new agent
            agent_id = await conn.fetchval(
                "SELECT create_default_mcp_agent($1, $2)",
                uuid.UUID(user_id), agent_name
            )
            
            # Fetch the created agent
            agent = await conn.fetchrow(
                "SELECT * FROM mcp_llm_agents WHERE agent_id = $1",
                agent_id
            )
            
            return dict(agent)

    async def store_conversation(self, agent_id: str, user_id: str, role: str, message: str, 
                               ai_service: str = None, credits: int = 0, session_id: str = None) -> str:
        """
        Store conversation in database
        """
        async with self.db_pool.acquire() as conn:
            conversation_id = await conn.fetchval("""
                INSERT INTO mcp_llm_conversations 
                (agent_id, user_id, session_id, role, message, ai_service_used, credits_consumed)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING conversation_id
            """, 
            uuid.UUID(agent_id), uuid.UUID(user_id), session_id, 
            role, message, ai_service, credits
            )
            
            return str(conversation_id)

    async def get_conversation_memory(self, agent_id: str, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Get recent conversation history for context
        """
        async with self.db_pool.acquire() as conn:
            conversations = await conn.fetch("""
                SELECT role, message, ai_service_used, created_at
                FROM mcp_llm_conversations 
                WHERE agent_id = $1 AND user_id = $2
                ORDER BY created_at DESC
                LIMIT $3
            """, uuid.UUID(agent_id), uuid.UUID(user_id), limit)
            
            return [dict(conv) for conv in reversed(conversations)]

    async def store_memory(self, agent_id: str, user_id: str, memory_type: str, 
                          memory_key: str, memory_value: Any, importance: int = 5) -> str:
        """
        Store structured memory (facts, preferences, context)
        """
        async with self.db_pool.acquire() as conn:
            memory_id = await conn.fetchval("""
                INSERT INTO mcp_llm_memory 
                (agent_id, user_id, memory_type, memory_key, memory_value, importance_score)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (agent_id, memory_key) DO UPDATE SET
                    memory_value = $5,
                    importance_score = $6,
                    last_accessed = CURRENT_TIMESTAMP
                RETURNING memory_id
            """, 
            uuid.UUID(agent_id), uuid.UUID(user_id), memory_type, 
            memory_key, json.dumps(memory_value), importance
            )
            
            return str(memory_id)

    async def get_relevant_memory(self, agent_id: str, user_id: str, memory_types: List[str] = None) -> List[Dict]:
        """
        Get relevant memories for context
        """
        async with self.db_pool.acquire() as conn:
            if memory_types:
                memories = await conn.fetch("""
                    SELECT memory_type, memory_key, memory_value, importance_score
                    FROM mcp_llm_memory 
                    WHERE agent_id = $1 AND user_id = $2 AND memory_type = ANY($3)
                    ORDER BY importance_score DESC, last_accessed DESC
                    LIMIT 20
                """, uuid.UUID(agent_id), uuid.UUID(user_id), memory_types)
            else:
                memories = await conn.fetch("""
                    SELECT memory_type, memory_key, memory_value, importance_score
                    FROM mcp_llm_memory 
                    WHERE agent_id = $1 AND user_id = $2
                    ORDER BY importance_score DESC, last_accessed DESC
                    LIMIT 20
                """, uuid.UUID(agent_id), uuid.UUID(user_id))
            
            return [dict(memory) for memory in memories]

    async def create_workflow_preview(self, user_id: str, agent_id: str, original_request: str, 
                                    ai_service: str, workflow_json: Dict) -> str:
        """
        Create a workflow in preview state for user confirmation
        """
        async with self.db_pool.acquire() as conn:
            workflow_id = await conn.fetchval("""
                INSERT INTO automation_workflows 
                (user_id, agent_id, workflow_name, original_request, ai_service_used, 
                 workflow_json, status, estimated_credits)
                VALUES ($1, $2, $3, $4, $5, $6, 'previewing', $7)
                RETURNING workflow_id
            """, 
            uuid.UUID(user_id), uuid.UUID(agent_id), 
            f"AI-Generated Workflow ({ai_service})", original_request, 
            ai_service, json.dumps(workflow_json), 
            self._estimate_workflow_credits(workflow_json, ai_service)
            )
            
            return str(workflow_id)

    def _estimate_workflow_credits(self, workflow_json: Dict, ai_service: str) -> int:
        """
        Estimate credits needed for workflow execution
        """
        base_credits = {"inhouse": 2, "openai": 5, "claude": 5}
        ai_credits = base_credits.get(ai_service, 3)
        
        # Count actions in workflow
        actions = workflow_json.get("workflow", {}).get("actions", [])
        email_actions = sum(1 for action in actions if action.get("node") == "emailSend")
        
        return ai_credits + email_actions  # 1 credit per email

    async def process_user_input(self, user_id: str, agent_id: str, user_message: str) -> Dict[str, Any]:
        """
        Process user input with full database integration and memory
        """
        logger.info(f"Processing message from user {user_id} via agent {agent_id}: {user_message}")
        
        try:
            # Get or create agent
            agent = await self.get_or_create_agent(user_id, "Sam - Personal Assistant")
            agent_id = str(agent['agent_id'])
            
            # Store user message
            await self.store_conversation(agent_id, user_id, "user", user_message)
            
            # Get conversation context
            conversation_history = await self.get_conversation_memory(agent_id, user_id, 5)
            relevant_memories = await self.get_relevant_memory(agent_id, user_id, ["preferences", "facts"])
            
            # Build context for AI processing
            context = {
                "agent_personality": agent['personality'],
                "conversation_history": conversation_history,
                "relevant_memories": relevant_memories,
                "user_preferences": agent.get('preferred_ai_service', 'inhouse')
            }
            
            # Process based on message content with enhanced detection
            response = await self._process_with_context(user_id, agent_id, user_message, context)
            
            # Store AI response
            await self.store_conversation(
                agent_id, user_id, "assistant", response['message'],
                response.get('ai_service_used'), response.get('estimated_credits', 0)
            )
            
            # Store relevant memories if new information is detected
            await self._extract_and_store_memories(agent_id, user_id, user_message, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing user input: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Sorry, I encountered an error processing your request: {str(e)}",
                "estimated_credits": 0
            }

    async def _process_with_context(self, user_id: str, agent_id: str, user_message: str, context: Dict) -> Dict[str, Any]:
        """
        Process message with full context and memory
        """
        # Check for AI service selection requests
        if ("using ai" in user_message.lower() or "ai" in user_message.lower() or 
            "draft" in user_message.lower() or "generate" in user_message.lower()) and not ("service:" in user_message.lower()):
            
            return {
                "status": "ai_service_selection",
                "message": "I can help you with AI-powered content generation! Please choose your preferred AI service:",
                "ai_service_options": [
                    {
                        "id": "inhouse",
                        "name": "In-House AI (MCP LLM)",
                        "description": "Our custom MCP LLM - Lower cost, optimized for business automation",
                        "credits": 2,
                        "features": ["Fast response", "Business-focused", "Cost-effective", "Memory-enabled"]
                    },
                    {
                        "id": "openai",
                        "name": "OpenAI GPT",
                        "description": "GPT-4 powered AI - High quality, versatile content generation",
                        "credits": 5,
                        "features": ["Premium quality", "Advanced reasoning", "Creative content"]
                    },
                    {
                        "id": "claude",
                        "name": "Anthropic Claude",
                        "description": "Claude AI - Excellent for analysis and detailed responses",
                        "credits": 5,
                        "features": ["Analytical", "Detailed responses", "Code-friendly"]
                    }
                ],
                "original_request": user_message,
                "estimated_credits": "2-5 depending on service"
            }
        
        # Handle AI + Email automation with service selection
        elif ("service:" in user_message.lower()) and ("email" in user_message.lower() or "@" in user_message):
            return await self._create_ai_email_workflow(user_id, agent_id, user_message, context)
        
        # Handle general automation requests
        elif any(keyword in user_message.lower() for keyword in ["automation", "workflow", "automate", "schedule"]):
            return await self._create_general_workflow(user_id, agent_id, user_message, context)
        
        # Handle sales pitch requests
        elif any(keyword in user_message.lower() for keyword in ["sales", "pitch", "dxtrlabs", "dxtr"]):
            return await self._generate_sales_content(user_id, agent_id, user_message, context)
        
        # Default conversational response with memory
        else:
            return await self._generate_conversational_response(user_id, agent_id, user_message, context)

    async def _create_ai_email_workflow(self, user_id: str, agent_id: str, user_message: str, context: Dict) -> Dict[str, Any]:
        """
        Create AI + Email workflow with preview
        """
        import re
        
        # Extract AI service
        ai_service = "inhouse"  # default
        if "service:openai" in user_message.lower():
            ai_service = "openai"
        elif "service:claude" in user_message.lower():
            ai_service = "claude"
        elif "service:inhouse" in user_message.lower():
            ai_service = "inhouse"
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, user_message)
        to_email = emails[0] if emails else "recipient@example.com"
        
        # Clean request
        clean_request = re.sub(r'service:\s*\w+\s*', '', user_message, flags=re.IGNORECASE).strip()
        
        # Create workflow JSON
        ai_node_map = {"inhouse": "mcpLLM", "openai": "openai", "claude": "claude"}
        workflow_json = {
            "workflow": {
                "trigger": {"node": "manual", "parameters": {}},
                "logic": [],
                "actions": [
                    {
                        "node": ai_node_map[ai_service],
                        "parameters": {
                            "user_input": clean_request,
                            "context": "ai_content_generation"
                        }
                    },
                    {
                        "node": "emailSend",
                        "parameters": {
                            "toEmail": to_email,
                            "subject": f"AI-Generated Content from DXTR Labs ({ai_service.upper()})",
                            "text": "{ai_generated_content}"
                        }
                    }
                ]
            }
        }
        
        # Create workflow preview
        workflow_id = await self.create_workflow_preview(
            user_id, agent_id, clean_request, ai_service, workflow_json
        )
        
        return {
            "status": "workflow_preview",
            "message": f"I'll use {ai_service.upper()} AI to generate content and send it via email to {to_email}.",
            "workflow_json": workflow_json,
            "workflow_id": workflow_id,
            "ai_service_used": ai_service,
            "estimated_credits": self._estimate_workflow_credits(workflow_json, ai_service),
            "preview_details": {
                "ai_service": ai_service.upper(),
                "target_email": to_email,
                "content_type": "AI-generated content",
                "requires_confirmation": True
            }
        }

    async def _generate_conversational_response(self, user_id: str, agent_id: str, user_message: str, context: Dict) -> Dict[str, Any]:
        """
        Generate conversational response with memory integration
        """
        # Use conversation history and memories to create contextual response
        personality = context.get('agent_personality', {})
        memories = context.get('relevant_memories', [])
        
        # Build contextual response based on memory
        memory_context = ""
        if memories:
            memory_context = "Based on what I remember about you: "
            for memory in memories[:3]:  # Use top 3 memories
                memory_context += f"{memory['memory_value']}. "
        
        response_message = f"Hello! I'm Sam, your Personal Assistant powered by DXTR Labs. {memory_context}You said: '{user_message}'. I'm here to help you with automation workflows, AI content generation, and business solutions. How can I assist you today?"
        
        return {
            "status": "completed",
            "message": response_message,
            "ai_service_used": "inhouse",
            "estimated_credits": 1
        }

    async def _extract_and_store_memories(self, agent_id: str, user_id: str, user_message: str, response: Dict):
        """
        Extract and store relevant memories from conversation
        """
        # Extract email preferences
        if "@" in user_message:
            import re
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', user_message)
            if emails:
                await self.store_memory(
                    agent_id, user_id, "preferences", "frequent_email_contacts", 
                    emails, importance=7
                )
        
        # Extract AI service preferences
        if "service:" in user_message.lower():
            if "openai" in user_message.lower():
                await self.store_memory(
                    agent_id, user_id, "preferences", "preferred_ai_service", 
                    "openai", importance=6
                )
            elif "claude" in user_message.lower():
                await self.store_memory(
                    agent_id, user_id, "preferences", "preferred_ai_service", 
                    "claude", importance=6
                )
        
        # Extract automation interests
        automation_keywords = ["automation", "workflow", "automate", "schedule"]
        if any(keyword in user_message.lower() for keyword in automation_keywords):
            await self.store_memory(
                agent_id, user_id, "facts", "interested_in_automation", 
                "User frequently requests automation workflows", importance=8
            )

    async def confirm_workflow(self, workflow_id: str, user_id: str) -> Dict[str, Any]:
        """
        Confirm and execute a workflow
        """
        async with self.db_pool.acquire() as conn:
            # Update workflow status
            await conn.execute("""
                UPDATE automation_workflows 
                SET status = 'confirmed', updated_at = CURRENT_TIMESTAMP
                WHERE workflow_id = $1 AND user_id = $2
            """, uuid.UUID(workflow_id), uuid.UUID(user_id))
            
            # Get workflow details
            workflow = await conn.fetchrow("""
                SELECT * FROM automation_workflows 
                WHERE workflow_id = $1 AND user_id = $2
            """, uuid.UUID(workflow_id), uuid.UUID(user_id))
            
            if not workflow:
                return {"status": "error", "message": "Workflow not found"}
            
            return {
                "status": "confirmed",
                "message": "Workflow confirmed! Ready for execution.",
                "workflow_json": workflow['workflow_json'],
                "estimated_credits": workflow['estimated_credits']
            }
