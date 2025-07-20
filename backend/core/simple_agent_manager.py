"""
Simple AgentManager that uses the database manager directly
"""
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class AgentManager:
    def __init__(self, db_pool, email_service=None):
        """Initialize AgentManager with database pool and email service"""
        # For now, we'll use the global db_manager
        from db.postgresql_manager import db_manager
        self.db_manager = db_manager
        self.db_pool = db_pool
        self.email_service = email_service

    async def create_agent(self, user_id: str, agent_name: str, agent_role: str = None, 
                          agent_personality: str = None, agent_expectations: str = None,
                          trigger_config: dict = None, custom_mcp_code: str = None) -> Dict[str, Any]:
        """Create a new agent with enhanced features"""
        return await self.db_manager.create_agent(
            user_id=user_id,
            agent_name=agent_name, 
            agent_role=agent_role,
            agent_personality=agent_personality,
            agent_expectations=agent_expectations,
            trigger_config=trigger_config or {},
            custom_mcp_code=custom_mcp_code
        )
    
    async def get_user_agents(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all agents for a user"""
        return await self.db_manager.get_user_agents(user_id)
    
    async def get_agent_details(self, agent_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get agent details (for now, just get by ID)"""
        agent = await self.db_manager.get_agent_by_id(agent_id)
        # Simple ownership check
        if agent and str(agent['user_id']) == str(user_id):
            return agent
        return None
    
    async def delete_agent(self, agent_id: str, user_id: str) -> bool:
        """Delete an agent"""
        # First check ownership
        agent = await self.get_agent_details(agent_id, user_id)
        if not agent:
            return False
        return await self.db_manager.delete_agent(agent_id)

    async def get_agent_llm(self, agent_id: str):
        """
        Gets or creates a CustomMCPLLM instance for the specified agent.
        Loads agent context from database if needed.
        """
        # Clear cache to ensure latest configuration
        if not hasattr(self, '_llm_instances'):
            self._llm_instances = {}
        
        # Always recreate to ensure latest email service configuration    
        if agent_id in self._llm_instances:
            del self._llm_instances[agent_id]
            logger.info(f"🔄 Cleared cached LLM instance for agent {agent_id}")
            
        # Load agent details from database
        query = """
        SELECT agent_id, agent_name, agent_role, agent_personality, 
               agent_expectations, trigger_config, custom_mcp_code, workflow_id
        FROM agents 
        WHERE agent_id = $1;
        """
        
        async with self.db_pool.acquire() as conn:
            result = await conn.fetchrow(query, agent_id)
            
            if not result:
                raise ValueError(f"Agent {agent_id} not found")
            
            # Get OpenAI API key from environment
            import os
            openai_api_key = os.getenv("OPENAI_API_KEY")
            
            # Prepare agent context
            agent_data = dict(result)
            agent_context = {
                'agent_data': agent_data,
                'memory': {'conversation_history': [], 'context': {'user_preferences': {}}},
                'user_id': 'default_user'
            }
            
            # Initialize CustomMCPLLM with proper context and OpenAI integration
            from mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine
            from mcp.simple_automation_engine import AutomationEngine
            
            # Initialize automation engine for this agent
            automation_engine = AutomationEngine(db_config=self.db_pool)
            
            agent_llm = CustomMCPLLMIterationEngine(
                agent_id=str(result['agent_id']),
                session_id=f"session_{result['agent_id']}",
                db_manager=self.db_pool,
                openai_api_key=openai_api_key,  # Pass OpenAI API key!
                automation_engine=automation_engine,  # FIXED: Pass real automation engine!
                agent_context=agent_context,  # Pass agent context!
                email_service=self.email_service  # Pass global email service!
            )
            
            logger.info(f"✅ Created CustomMCPLLMIterationEngine for agent {agent_id}")
            logger.info(f"📧 Email service provided: {self.email_service is not None}")
            
            # Cache the instance
            self._llm_instances[agent_id] = agent_llm
            
            return agent_llm
