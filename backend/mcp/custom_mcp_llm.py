"""
Custom MCP LLM - Database-stored, Agent-specific AI
This handles personalized AI for each agent with database persistence
"""
import logging
import asyncio
from typing import Dict, Any, Optional
import json
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class CustomMCPLLM:
    def __init__(self, db_pool):
        """
        Initialize Custom MCP LLM with database connection
        This is agent-specific AI stored in database
        """
        self.db_pool = db_pool
        logger.info("✅ Custom MCP LLM (Database-stored) initialized")
    
    async def get_agent_configuration(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent-specific configuration from database
        """
        try:
            async with self.db_pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT agent_id, agent_name, personality, system_prompt, 
                           preferred_ai_service, memory_enabled, automation_enabled
                    FROM mcp_llm_agents 
                    WHERE agent_id = $1
                """, agent_id)
                
                if result:
                    return {
                        "agent_id": str(result['agent_id']),
                        "agent_name": result['agent_name'],
                        "personality": result['personality'] or {},
                        "system_prompt": result['system_prompt'],
                        "preferred_ai_service": result['preferred_ai_service'],
                        "memory_enabled": result['memory_enabled'],
                        "automation_enabled": result['automation_enabled']
                    }
                else:
                    # Return default configuration if agent not found
                    return self._get_default_agent_config(agent_id)
                    
        except Exception as e:
            logger.error(f"❌ Error getting agent configuration: {e}")
            return self._get_default_agent_config(agent_id)
    
    async def get_agent_memory(self, agent_id: str, user_id: str, memory_type: str = "conversation") -> list:
        """
        Retrieve agent-specific memory from database
        """
        try:
            async with self.db_pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT memory_key, memory_value, importance_score, last_accessed
                    FROM mcp_llm_memory 
                    WHERE agent_id = $1 AND user_id = $2 AND memory_type = $3
                    ORDER BY last_accessed DESC
                    LIMIT 20
                """, agent_id, user_id, memory_type)
                
                return [
                    {
                        "key": result['memory_key'],
                        "value": result['memory_value'],
                        "importance": result['importance_score'],
                        "accessed": result['last_accessed']
                    }
                    for result in results
                ]
                
        except Exception as e:
            logger.error(f"❌ Error getting agent memory: {e}")
            return []
    
    async def store_agent_memory(self, agent_id: str, user_id: str, memory_type: str, 
                                key: str, value: Dict[str, Any], importance: int = 5) -> bool:
        """
        Store agent-specific memory in database
        """
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO mcp_llm_memory 
                    (agent_id, user_id, memory_type, memory_key, memory_value, importance_score)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (agent_id, user_id, memory_type, memory_key) 
                    DO UPDATE SET memory_value = $5, importance_score = $6, last_accessed = CURRENT_TIMESTAMP
                """, agent_id, user_id, memory_type, key, json.dumps(value), importance)
                
                logger.info(f"✅ Stored memory for agent {agent_id}: {key}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error storing agent memory: {e}")
            return False
    
    async def get_conversation_history(self, agent_id: str, user_id: str, limit: int = 10) -> list:
        """
        Get recent conversation history for this agent
        """
        try:
            async with self.db_pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT role, message, metadata, ai_service_used, created_at
                    FROM mcp_llm_conversations 
                    WHERE agent_id = $1 AND user_id = $2
                    ORDER BY created_at DESC
                    LIMIT $3
                """, agent_id, user_id, limit)
                
                return [
                    {
                        "role": result['role'],
                        "message": result['message'],
                        "metadata": result['metadata'] or {},
                        "ai_service": result['ai_service_used'],
                        "timestamp": result['created_at']
                    }
                    for result in reversed(results)  # Return in chronological order
                ]
                
        except Exception as e:
            logger.error(f"❌ Error getting conversation history: {e}")
            return []
    
    async def store_conversation(self, agent_id: str, user_id: str, role: str, 
                                message: str, metadata: Dict[str, Any] = None, 
                                ai_service: str = None) -> bool:
        """
        Store conversation message in database
        """
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO mcp_llm_conversations 
                    (agent_id, user_id, role, message, metadata, ai_service_used)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, agent_id, user_id, role, message, 
                    json.dumps(metadata or {}), ai_service)
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Error storing conversation: {e}")
            return False
    
    async def process_user_input(self, user_id: str, agent_id: str, user_message: str) -> Dict[str, Any]:
        """
        Process user input using agent-specific Custom MCP LLM
        """
        logger.info(f"🤖 Custom MCP LLM processing for agent {agent_id}")
        
        # Get agent configuration
        agent_config = await self.get_agent_configuration(agent_id)
        
        # Get conversation history
        conversation_history = await self.get_conversation_history(agent_id, user_id)
        
        # Get agent memory
        agent_memory = await self.get_agent_memory(agent_id, user_id)
        
        # Store user message
        await self.store_conversation(agent_id, user_id, "user", user_message)
        
        # Generate response using agent's personality and memory
        response = await self._generate_personalized_response(
            agent_config, conversation_history, agent_memory, user_message
        )
        
        # Store assistant response
        await self.store_conversation(agent_id, user_id, "assistant", 
                                    response['message'], response.get('metadata'))
        
        # Update memory if significant interaction
        if self._is_significant_interaction(user_message, response):
            await self._update_agent_memory(agent_id, user_id, user_message, response)
        
        return response
    
    async def _generate_personalized_response(self, agent_config: Dict[str, Any], 
                                            conversation_history: list, 
                                            agent_memory: list, 
                                            user_message: str) -> Dict[str, Any]:
        """
        Generate response using agent's personality and memory
        """
        agent_name = agent_config.get('agent_name', 'Assistant')
        personality = agent_config.get('personality', {})
        system_prompt = agent_config.get('system_prompt', '')
        
        # Build context from memory and history
        context = self._build_context(conversation_history, agent_memory, personality)
        
        # Generate personalized response
        if any(keyword in user_message.lower() for keyword in ["remember", "recall", "what did i"]):
            response_text = self._generate_memory_response(agent_memory, user_message, agent_name)
        elif any(keyword in user_message.lower() for keyword in ["email", "send", "generate"]):
            response_text = self._generate_workflow_response(user_message, agent_name, personality)
        else:
            response_text = self._generate_contextual_response(user_message, context, agent_name, personality)
        
        return {
            "status": "success",
            "message": response_text,
            "agent_id": agent_config['agent_id'],
            "agent_name": agent_name,
            "ai_service": "custom_mcp_llm",
            "memory_used": len(agent_memory) > 0,
            "metadata": {
                "personality_traits": list(personality.keys()),
                "context_length": len(context),
                "response_type": "personalized"
            }
        }
    
    def _build_context(self, conversation_history: list, agent_memory: list, personality: Dict[str, Any]) -> str:
        """
        Build context string from history and memory
        """
        context_parts = []
        
        # Add personality context
        if personality:
            traits = [f"{k}: {v}" for k, v in personality.items()]
            context_parts.append(f"Agent personality: {', '.join(traits)}")
        
        # Add relevant memory
        if agent_memory:
            memory_items = [f"{mem['key']}: {json.dumps(mem['value'])}" for mem in agent_memory[:3]]
            context_parts.append(f"Relevant memories: {'; '.join(memory_items)}")
        
        # Add recent conversation
        if conversation_history:
            recent_messages = [f"{msg['role']}: {msg['message']}" for msg in conversation_history[-3:]]
            context_parts.append(f"Recent conversation: {'; '.join(recent_messages)}")
        
        return " | ".join(context_parts)
    
    def _generate_memory_response(self, agent_memory: list, user_message: str, agent_name: str) -> str:
        """
        Generate response for memory-related queries
        """
        if not agent_memory:
            return f"I don't have any stored memories yet. Let's create some by having a conversation!"
        
        # Search for relevant memories
        relevant_memories = []
        for memory in agent_memory:
            if any(word in str(memory['value']).lower() for word in user_message.lower().split()):
                relevant_memories.append(memory)
        
        if relevant_memories:
            memory_text = []
            for mem in relevant_memories[:3]:
                memory_text.append(f"{mem['key']}: {json.dumps(mem['value'])}")
            return f"Based on our previous conversations, I remember: {'; '.join(memory_text)}"
        else:
            return f"I have memories stored, but none seem directly related to your current question. Could you be more specific?"
    
    def _generate_workflow_response(self, user_message: str, agent_name: str, personality: Dict[str, Any]) -> str:
        """
        Generate response for workflow/automation requests
        """
        tone = personality.get('communication_style', 'professional')
        
        if 'email' in user_message.lower():
            if tone == 'friendly':
                return f"I'd love to help you with that email! Could you tell me who you'd like to send it to and what kind of content you need?"
            else:
                return f"I can assist with email generation and automation. Please provide the recipient and content requirements."
        else:
            return f"I understand you need help with automation. Could you provide more details about what you'd like me to do?"
    
    def _generate_contextual_response(self, user_message: str, context: str, 
                                    agent_name: str, personality: Dict[str, Any]) -> str:
        """
        Generate contextual response using agent personality
        """
        communication_style = personality.get('communication_style', 'professional')
        expertise_area = personality.get('expertise_area', 'general assistance')
        
        if communication_style == 'friendly':
            greeting = "Hi there!"
        elif communication_style == 'formal':
            greeting = "Good day."
        else:
            greeting = "Hello!"
        
        if expertise_area and expertise_area != 'general assistance':
            return f"{greeting} As your {expertise_area} specialist, I'm here to help. Regarding your message about '{user_message[:50]}...', I can provide specialized assistance. What would you like me to focus on?"
        else:
            return f"{greeting} I'm {agent_name}, and I'm here to provide personalized assistance based on our ongoing relationship. How can I help you today?"
    
    def _is_significant_interaction(self, user_message: str, response: Dict[str, Any]) -> bool:
        """
        Determine if interaction should be stored as memory
        """
        # Store as memory if user provides personal info or makes important requests
        memory_triggers = ["my name", "i work", "i am", "remember", "important", "prefer"]
        return any(trigger in user_message.lower() for trigger in memory_triggers)
    
    async def _update_agent_memory(self, agent_id: str, user_id: str, 
                                 user_message: str, response: Dict[str, Any]) -> None:
        """
        Update agent memory with significant interactions
        """
        memory_key = f"interaction_{int(time.time())}"
        memory_value = {
            "user_message": user_message,
            "response": response['message'],
            "timestamp": datetime.now().isoformat(),
            "context": "significant_interaction"
        }
        
        await self.store_agent_memory(agent_id, user_id, "conversation", 
                                    memory_key, memory_value, importance=7)
    
    def _get_default_agent_config(self, agent_id: str) -> Dict[str, Any]:
        """
        Return default agent configuration
        """
        return {
            "agent_id": agent_id,
            "agent_name": "Custom Assistant",
            "personality": {
                "communication_style": "professional",
                "expertise_area": "general assistance"
            },
            "system_prompt": "You are a helpful, personalized AI assistant.",
            "preferred_ai_service": "custom_mcp_llm",
            "memory_enabled": True,
            "automation_enabled": True
        }
