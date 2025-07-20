"""
Enhanced MCP LLM Orchestrator with Personalized Context Injection

This is the core orchestrator that brings together user memory, agent personalities,
and dynamic prompt building to create truly personalized AI interactions.
"""

import json
import os
import asyncio
import asyncpg
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import the enhanced managers
from .contextual_agent_manager import ContextualAgentManager, AGENT_PRESETS
from .user_memory_manager import UserMemoryManager, USER_MEMORY_TEMPLATES

logger = logging.getLogger(__name__)

class PersonalizedMCPOrchestrator:
    """
    Enhanced MCP LLM Orchestrator that creates personalized AI experiences through:
    - Dynamic context injection from user memory
    - Agent personality and role awareness
    - Persistent learning and memory updates
    - Contextual prompt building for each interaction
    """
    
    def __init__(self, db_config: dict, llm_config: dict = None):
        """
        Initialize the PersonalizedMCPOrchestrator.
        
        Args:
            db_config: Database connection configuration
            llm_config: LLM configuration (API keys, model settings, etc.)
        """
        self.db_config = db_config
        self.llm_config = llm_config or {}
        self.db_pool = None
        
        # Initialize managers
        self.agent_manager = None
        self.user_memory_manager = None
        
        # Chat session management
        self.active_sessions = {}  # session_id -> session_data
        
        # Base system prompt template
        self.base_system_prompt = self._get_base_automation_prompt()

    async def initialize(self):
        """Initialize database connections and managers."""
        if self.db_pool is None:
            self.db_pool = await asyncpg.create_pool(**self.db_config)
            self.agent_manager = ContextualAgentManager(self.db_pool)
            self.user_memory_manager = UserMemoryManager(self.db_pool)
            logger.info("✅ PersonalizedMCPOrchestrator initialized")

    def _get_base_automation_prompt(self) -> str:
        """Base system prompt for automation workflow building."""
        return """
        You are an AI automation specialist that helps users build sophisticated workflows.
        
        You have access to these automation capabilities:
        - Email operations (send, read IMAP)
        - HTTP requests and API integrations
        - SMS/voice via Twilio
        - Logic operations (if/else, loops)
        - Trigger systems (cron, webhooks)
        
        Your goal is to understand the user's automation needs and guide them through
        building effective workflows step by step.
        
        Always consider the user's context, preferences, and past interactions when
        providing suggestions and building workflows.
        """

    async def create_personalized_session(
        self, 
        user_id: str, 
        agent_id: str,
        session_context: Dict[str, Any] = None
    ) -> str:
        """
        Create a new personalized chat session.
        
        Args:
            user_id: UUID of the user
            agent_id: UUID of the agent to use
            session_context: Optional additional context for this session
            
        Returns:
            Session ID for future interactions
        """
        await self.initialize()
        
        session_id = f"session_{user_id}_{agent_id}_{datetime.now().timestamp()}"
        
        # Load user and agent context
        user_context = await self.user_memory_manager.get_user_context(user_id)
        agent_context = await self.agent_manager.get_agent_with_context(agent_id, user_id)
        
        # Create session data
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "agent_id": agent_id,
            "user_context": user_context,
            "agent_context": agent_context,
            "conversation_history": [],
            "session_context": session_context or {},
            "created_at": datetime.now().isoformat(),
            "current_workflow": None,
            "learning_buffer": []  # Store learnings for batch updates
        }
        
        self.active_sessions[session_id] = session_data
        
        logger.info(f"✅ Created personalized session {session_id}")
        return session_id

    async def process_message(
        self, 
        session_id: str, 
        user_message: str,
        extract_learnings: bool = True
    ) -> Dict[str, Any]:
        """
        Process a user message with full personalization.
        
        Args:
            session_id: ID of the active session
            user_message: The user's message
            extract_learnings: Whether to extract and store learnings
            
        Returns:
            Dict containing AI response and metadata
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        # Build personalized prompt
        personalized_prompt = await self._build_personalized_prompt(session, user_message)
        
        # Simulate LLM call (replace with actual LLM integration)
        ai_response = await self._call_llm(personalized_prompt, session)
        
        # Update conversation history
        session["conversation_history"].extend([
            {"role": "user", "content": user_message, "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": ai_response["content"], "timestamp": datetime.now().isoformat()}
        ])
        
        # Extract learnings if enabled
        if extract_learnings:
            await self._extract_and_store_learnings(session, user_message, ai_response)
        
        # Prepare response
        response = {
            "session_id": session_id,
            "agent_name": session["agent_context"]["agent_name"],
            "response": ai_response["content"],
            "response_type": ai_response.get("type", "conversational"),
            "workflow_data": ai_response.get("workflow_data"),
            "suggestions": ai_response.get("suggestions", []),
            "context_used": {
                "user_context_injected": bool(session["user_context"].get("memory_context")),
                "agent_personality_active": bool(session["agent_context"].get("agent_personality")),
                "conversation_length": len(session["conversation_history"])
            }
        }
        
        return response

    async def _build_personalized_prompt(self, session: Dict, user_message: str) -> List[Dict]:
        """
        Build a personalized prompt by combining:
        - Agent personality and role
        - User memory and context
        - Conversation history
        - Current workflow state
        """
        messages = []
        
        # 1. System prompt with agent personality
        system_prompt_parts = [self.base_system_prompt]
        
        agent = session["agent_context"]
        if agent:
            system_prompt_parts.extend([
                f"\\n--- Your Personality ---",
                f"You are {agent['agent_name']}, {agent['agent_role']}.",
                f"Your personality: {agent['agent_personality']}",
                f"Your key expectations: {agent['agent_expectations']}"
            ])
        
        # 2. Add user context
        user_context_prompt = await self.user_memory_manager.generate_context_prompt(session["user_id"])
        if user_context_prompt:
            system_prompt_parts.extend([
                f"\\n--- User Context ---", 
                user_context_prompt
            ])
        
        # 3. Add agent-specific memory
        agent_memory = agent.get("agent_memory_context", {})
        if agent_memory:
            memory_text = self._format_agent_memory(agent_memory)
            if memory_text:
                system_prompt_parts.extend([
                    f"\\n--- Your Memory ---",
                    memory_text
                ])
        
        messages.append({
            "role": "system",
            "content": "\\n".join(system_prompt_parts)
        })
        
        # 4. Add relevant conversation history (last 10 messages)
        history = session["conversation_history"][-10:]
        messages.extend([
            {"role": msg["role"], "content": msg["content"]} 
            for msg in history
        ])
        
        # 5. Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages

    def _format_agent_memory(self, memory: Dict) -> str:
        """Format agent memory for prompt injection."""
        if not memory:
            return ""
        
        parts = []
        
        # Recent interactions
        if memory.get("interactions_count", 0) > 0:
            parts.append(f"You've had {memory['interactions_count']} interactions with this user.")
        
        # Learned preferences
        if memory.get("learned_preferences"):
            prefs = memory["learned_preferences"]
            if prefs.get("user_specific_knowledge"):
                parts.append(f"What you know about this user: {prefs['user_specific_knowledge']}")
        
        # Conversation topics
        if memory.get("conversation_topics"):
            topics = ", ".join(memory["conversation_topics"][-3:])  # Last 3 topics
            parts.append(f"Recent topics discussed: {topics}")
        
        return ". ".join(parts)

    async def _call_llm(self, messages: List[Dict], session: Dict) -> Dict[str, Any]:
        """
        Call the LLM with personalized context.
        
        This is a placeholder - replace with actual LLM integration
        (OpenAI, Anthropic, local model, etc.)
        """
        # Simulate LLM response based on context
        agent_name = session["agent_context"]["agent_name"]
        agent_role = session["agent_context"]["agent_role"]
        
        # Mock response - replace with actual LLM call
        mock_response = {
            "content": f"Hello! I'm {agent_name}, your {agent_role}. I understand your context and I'm here to help you build effective automation workflows. What specific automation challenge can I help you solve today?",
            "type": "conversational",
            "suggestions": [
                "Create an email automation workflow",
                "Set up a data processing pipeline", 
                "Build a customer notification system"
            ]
        }
        
        return mock_response

    async def _extract_and_store_learnings(
        self, 
        session: Dict, 
        user_message: str, 
        ai_response: Dict
    ):
        """
        Extract learnings from the conversation and update memory.
        """
        # Extract potential learnings from user message
        learnings = self._extract_conversation_learnings(user_message, ai_response)
        
        if learnings:
            # Store in learning buffer for batch processing
            session["learning_buffer"].append({
                "timestamp": datetime.now().isoformat(),
                "user_message": user_message,
                "learnings": learnings
            })
            
            # If buffer is large enough, process learnings
            if len(session["learning_buffer"]) >= 5:
                await self._process_learning_buffer(session)

    def _extract_conversation_learnings(self, user_message: str, ai_response: Dict) -> Dict:
        """
        Extract learnable information from conversation.
        
        This is a simplified version - in production, you might use
        NLP techniques or additional LLM calls for extraction.
        """
        learnings = {}
        
        # Simple keyword-based extraction (replace with sophisticated NLP)
        user_lower = user_message.lower()
        
        # Company mentions
        if "company" in user_lower or "work at" in user_lower:
            # Extract company information
            pass
        
        # Tool preferences
        tool_keywords = ["slack", "email", "salesforce", "hubspot", "zapier", "github"]
        mentioned_tools = [tool for tool in tool_keywords if tool in user_lower]
        if mentioned_tools:
            learnings["learned_preferences"] = {"favorite_tools": mentioned_tools}
        
        # Project mentions
        if "project" in user_lower or "working on" in user_lower:
            # Extract project information
            pass
        
        return learnings

    async def _process_learning_buffer(self, session: Dict):
        """Process accumulated learnings and update user/agent memory."""
        if not session["learning_buffer"]:
            return
        
        # Aggregate learnings
        aggregated_learnings = {}
        for item in session["learning_buffer"]:
            learnings = item["learnings"]
            for key, value in learnings.items():
                if key not in aggregated_learnings:
                    aggregated_learnings[key] = value
                elif isinstance(value, dict):
                    aggregated_learnings[key].update(value)
                elif isinstance(value, list):
                    aggregated_learnings[key].extend(value)
        
        # Update user memory
        if aggregated_learnings:
            await self.user_memory_manager.update_user_memory(
                session["user_id"],
                aggregated_learnings
            )
        
        # Update agent memory
        agent_learnings = {
            "conversation_topics": [item["user_message"][:50] for item in session["learning_buffer"]],
            "interactions_count": len(session["learning_buffer"])
        }
        
        await self.agent_manager.update_agent_memory(
            session["agent_id"],
            session["user_id"],
            agent_learnings
        )
        
        # Clear buffer
        session["learning_buffer"] = []
        
        logger.info(f"✅ Processed learnings for session {session['session_id']}")

    async def create_agent_from_preset(
        self, 
        user_id: str, 
        preset_name: str, 
        agent_name: str,
        customizations: Dict[str, Any] = None
    ) -> str:
        """
        Create an agent from a preset configuration.
        
        Args:
            user_id: UUID of the user
            preset_name: Name of the preset to use
            agent_name: Custom name for the agent
            customizations: Optional customizations to the preset
            
        Returns:
            Agent ID of the created agent
        """
        if preset_name not in AGENT_PRESETS:
            raise ValueError(f"Preset '{preset_name}' not found")
        
        preset = AGENT_PRESETS[preset_name].copy()
        
        # Apply customizations
        if customizations:
            preset.update(customizations)
        
        # Create agent
        agent_data = await self.agent_manager.create_personalized_agent(
            user_id=user_id,
            agent_name=agent_name,
            agent_role=preset["agent_role"],
            agent_personality=preset["agent_personality"],
            agent_expectations=preset["agent_expectations"]
        )
        
        logger.info(f"✅ Created agent '{agent_name}' from preset '{preset_name}'")
        return agent_data["agent_id"]

    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the current session."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        return {
            "session_id": session_id,
            "agent_name": session["agent_context"]["agent_name"],
            "conversation_length": len(session["conversation_history"]),
            "created_at": session["created_at"],
            "user_context_active": bool(session["user_context"].get("memory_context")),
            "learnings_pending": len(session["learning_buffer"]),
            "current_workflow": session.get("current_workflow")
        }

    async def close_session(self, session_id: str):
        """Close a session and process any pending learnings."""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            
            # Process any remaining learnings
            if session["learning_buffer"]:
                await self._process_learning_buffer(session)
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            logger.info(f"✅ Closed session {session_id}")

    async def close(self):
        """Close database connections and cleanup."""
        if self.db_pool:
            await self.db_pool.close()
            logger.info("✅ PersonalizedMCPOrchestrator closed")

# Quick setup functions for common use cases
async def create_quick_marketing_agent(orchestrator: PersonalizedMCPOrchestrator, user_id: str) -> str:
    """Quick setup for a marketing agent."""
    return await orchestrator.create_agent_from_preset(
        user_id=user_id,
        preset_name="marketing_maestro",
        agent_name="Marketing Maestro"
    )

async def create_quick_support_agent(orchestrator: PersonalizedMCPOrchestrator, user_id: str) -> str:
    """Quick setup for a support agent."""
    return await orchestrator.create_agent_from_preset(
        user_id=user_id,
        preset_name="support_assistant", 
        agent_name="Support Assistant"
    )

async def setup_user_with_template(
    orchestrator: PersonalizedMCPOrchestrator, 
    user_id: str, 
    template_name: str
) -> bool:
    """Initialize user memory with a template."""
    if template_name not in USER_MEMORY_TEMPLATES:
        raise ValueError(f"Template '{template_name}' not found")
    
    template = USER_MEMORY_TEMPLATES[template_name]
    await orchestrator.user_memory_manager.initialize_user_memory(user_id, template)
    
    logger.info(f"✅ Set up user {user_id} with template '{template_name}'")
    return True
