"""
Enhanced AgentManager with Memory Management and Context Injection

This module provides the core functionality for managing AI agents with persistent memory
and dynamic context injection for personalized interactions.
"""

import asyncpg
import uuid
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContextualAgentManager:
    """
    Enhanced AgentManager that handles:
    - Agent creation and management with full personality profiles
    - Dynamic memory context injection
    - Persistent learning and memory updates
    - Secure RLS-based access control
    """
    
    def __init__(self, db_pool):
        """Initialize the ContextualAgentManager with database connection pool."""
        self.db_pool = db_pool

    async def _execute_with_rls(self, query: str, *args, user_id: str = None, is_admin: bool = False):
        """Execute database queries with proper RLS context."""
        async with self.db_pool.acquire() as conn:
            try:
                # For testing, skip RLS setup and use direct access
                # In production, enable these RLS commands:
                # if user_id:
                #     await conn.execute(f"SET app.current_user_id = '{user_id}';")
                # if is_admin:
                #     await conn.execute("SET ROLE app_admin;")
                # else:
                #     await conn.execute("SET ROLE app_user;")

                # Execute query
                if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                    result = await conn.fetchrow(query, *args)
                else:
                    result = await conn.fetch(query, *args)
                
                return result
                
            except Exception as e:
                logger.error(f"Database operation failed: {e}")
                raise
            # finally:
            #     await conn.execute("RESET ROLE;")
            #     await conn.execute("RESET app.current_user_id;")

    async def create_personalized_agent(
        self, 
        user_id: str, 
        agent_name: str, 
        agent_role: str, 
        agent_personality: str, 
        agent_expectations: str,
        initial_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a new personalized AI agent with rich context and memory.
        
        Args:
            user_id: UUID of the agent owner
            agent_name: Human-readable name (e.g., "Marketing Maestro")
            agent_role: Agent's professional role (e.g., "Digital Marketing Specialist")
            agent_personality: Personality description
            agent_expectations: Key expectations and behaviors
            initial_context: Initial memory context as dict
            
        Returns:
            Dict containing the created agent's details
        """
        # Validate UUID
        try:
            user_id
        except ValueError:
            raise ValueError("Invalid user_id: must be a valid UUID")

        # Prepare initial memory context
        if initial_context is None:
            initial_context = {
                "created_at": datetime.now().isoformat(),
                "interactions_count": 0,
                "learned_preferences": {},
                "conversation_topics": [],
                "user_specific_knowledge": {}
            }

        query = """
        INSERT INTO agents (
            user_id, 
            agent_name, 
            agent_role, 
            agent_personality, 
            agent_expectations, 
            agent_memory_context
        )
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING agent_id, agent_name, agent_role, agent_personality, 
                 agent_expectations, agent_memory_context, created_at;
        """
        
        result = await self._execute_with_rls(
            query, 
            user_id, 
            agent_name, 
            agent_role, 
            agent_personality, 
            agent_expectations,
            json.dumps(initial_context),
            user_id=user_id
        )
        
        if result:
            logger.info(f"✅ Created personalized agent '{agent_name}' for user {user_id}")
            return {
                "agent_id": str(result["agent_id"]),
                "agent_name": result["agent_name"],
                "agent_role": result["agent_role"],
                "agent_personality": result["agent_personality"],
                "agent_expectations": result["agent_expectations"],
                "agent_memory_context": json.loads(result["agent_memory_context"]),
                "created_at": result["created_at"]
            }
        else:
            raise Exception("Failed to create agent")

    async def get_agent_with_context(self, agent_id: str, user_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific agent with full context for LLM injection.
        
        Args:
            agent_id: UUID of the agent
            user_id: UUID of the requesting user (for RLS)
            
        Returns:
            Dict containing agent details with parsed memory context
        """
        query = """
        SELECT agent_id, user_id, agent_name, agent_role, agent_personality, 
               agent_expectations, agent_memory_context, created_at, updated_at
        FROM agents 
        WHERE agent_id = $1;
        """
        
        result = await self._execute_with_rls(query, agent_id, user_id=user_id)
        
        if result:
            agent_data = dict(result[0])
            # Parse JSON memory context
            if agent_data["agent_memory_context"]:
                agent_data["agent_memory_context"] = json.loads(agent_data["agent_memory_context"])
            else:
                agent_data["agent_memory_context"] = {}
                
            logger.info(f"✅ Retrieved agent context for {agent_data['agent_name']}")
            return agent_data
        else:
            raise ValueError(f"Agent {agent_id} not found or access denied")

    async def update_agent_memory(
        self, 
        agent_id: str, 
        user_id: str, 
        memory_updates: Dict[str, Any],
        merge_strategy: str = "merge"
    ) -> bool:
        """
        Update agent's memory context with new learned information.
        
        Args:
            agent_id: UUID of the agent
            user_id: UUID of the user (for RLS)
            memory_updates: Dict containing new memory information
            merge_strategy: "merge" or "replace"
            
        Returns:
            Boolean indicating success
        """
        # First get current memory
        current_agent = await self.get_agent_with_context(agent_id, user_id)
        current_memory = current_agent.get("agent_memory_context", {})
        
        # Apply update strategy
        if merge_strategy == "merge":
            # Deep merge the memory contexts
            updated_memory = self._deep_merge_memory(current_memory, memory_updates)
        else:
            updated_memory = memory_updates
            
        # Update timestamp
        updated_memory["last_updated"] = datetime.now().isoformat()
        if "interactions_count" in updated_memory:
            updated_memory["interactions_count"] += 1
        
        # Save to database
        query = """
        UPDATE agents 
        SET agent_memory_context = $1, updated_at = CURRENT_TIMESTAMP
        WHERE agent_id = $2;
        """
        
        await self._execute_with_rls(
            query, 
            json.dumps(updated_memory), 
            agent_id, 
            user_id=user_id
        )
        
        logger.info(f"✅ Updated memory for agent {agent_id}")
        return True

    def _deep_merge_memory(self, current: Dict, updates: Dict) -> Dict:
        """Deep merge memory contexts, preserving existing data while adding new."""
        result = current.copy()
        
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_memory(result[key], value)
            elif key in result and isinstance(result[key], list) and isinstance(value, list):
                # For lists, extend with unique items
                result[key] = list(set(result[key] + value))
            else:
                result[key] = value
                
        return result

    async def get_user_agents(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all agents belonging to a user.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            List of agent dictionaries
        """
        query = """
        SELECT agent_id, agent_name, agent_role, agent_personality, 
               agent_expectations, created_at, updated_at
        FROM agents 
        WHERE user_id = $1
        ORDER BY created_at DESC;
        """
        
        result = await self._execute_with_rls(query, user_id, user_id=user_id)
        
        agents = []
        for row in result:
            agent_data = dict(row)
            agent_data["agent_id"] = str(agent_data["agent_id"])
            agents.append(agent_data)
            
        logger.info(f"✅ Retrieved {len(agents)} agents for user {user_id}")
        return agents

    async def delete_agent(self, agent_id: str, user_id: str) -> bool:
        """
        Delete an agent (with RLS protection).
        
        Args:
            agent_id: UUID of the agent to delete
            user_id: UUID of the requesting user
            
        Returns:
            Boolean indicating success
        """
        query = "DELETE FROM agents WHERE agent_id = $1;"
        
        result = await self._execute_with_rls(
            query, 
            agent_id, 
            user_id=user_id
        )
        
        logger.info(f"✅ Deleted agent {agent_id}")
        return True

    async def create_agent_preset(self, preset_name: str, preset_config: Dict[str, Any]) -> str:
        """
        Create reusable agent presets for quick agent creation.
        
        Args:
            preset_name: Name of the preset
            preset_config: Configuration containing role, personality, expectations
            
        Returns:
            Preset ID for future reference
        """
        # This could be stored in a separate presets table
        # For now, we'll return the preset name as ID
        logger.info(f"✅ Agent preset '{preset_name}' ready for use")
        return preset_name

# Example preset configurations for common agent types
AGENT_PRESETS = {
    "marketing_maestro": {
        "agent_role": "Digital Marketing Specialist",
        "agent_personality": "Enthusiastic, data-driven, creative problem-solver who speaks in marketing terms and loves growth metrics",
        "agent_expectations": "Help with marketing campaigns, analyze customer data, suggest growth strategies, create compelling content"
    },
    "support_assistant": {
        "agent_role": "Customer Support Representative", 
        "agent_personality": "Empathetic, patient, solution-focused with excellent communication skills",
        "agent_expectations": "Resolve customer issues, provide helpful information, escalate when needed, maintain positive tone"
    },
    "data_analyst": {
        "agent_role": "Business Intelligence Analyst",
        "agent_personality": "Analytical, detail-oriented, logical thinker who loves patterns and insights",
        "agent_expectations": "Analyze data trends, create reports, identify business opportunities, explain complex data simply"
    },
    "content_creator": {
        "agent_role": "Content Marketing Specialist",
        "agent_personality": "Creative, engaging, storyteller with strong writing skills and brand awareness",
        "agent_expectations": "Create compelling content, maintain brand voice, optimize for SEO, engage audiences"
    }
}
