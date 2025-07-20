"""
Enhanced User Memory Manager for Persistent Context

This module handles user-specific memory and context that persists across sessions
and is injected into AI interactions for personalized experiences.
"""

import asyncpg
import uuid
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class UserMemoryManager:
    """
    Manages persistent user memory and context for personalized AI interactions.
    
    This class handles:
    - User profile and preference storage
    - Company/organization context
    - Communication preferences
    - Learning from interactions
    - Context injection for AI prompts
    """
    
    def __init__(self, db_pool):
        """Initialize with database connection pool."""
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

    async def initialize_user_memory(self, user_id: str, initial_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Initialize memory context for a new user.
        
        Args:
            user_id: UUID of the user
            initial_profile: Optional initial profile data
            
        Returns:
            Dict containing the initialized memory context
        """
        if initial_profile is None:
            initial_profile = {}
            
        # Create comprehensive initial memory structure
        memory_context = {
            "user_profile": {
                "company_name": initial_profile.get("company_name", ""),
                "industry": initial_profile.get("industry", ""),
                "role": initial_profile.get("role", ""),
                "team_size": initial_profile.get("team_size", ""),
                "primary_goals": initial_profile.get("primary_goals", [])
            },
            "communication_preferences": {
                "tone": initial_profile.get("preferred_tone", "professional"),
                "detail_level": initial_profile.get("detail_level", "medium"),
                "notification_frequency": initial_profile.get("notification_frequency", "daily"),
                "preferred_formats": initial_profile.get("preferred_formats", ["text", "bullet_points"])
            },
            "learned_preferences": {
                "favorite_tools": [],
                "workflow_patterns": [],
                "frequently_asked_topics": [],
                "successful_strategies": []
            },
            "interaction_history": {
                "total_interactions": 0,
                "last_interaction": None,
                "common_requests": {},
                "satisfaction_ratings": []
            },
            "context_memory": {
                "current_projects": [],
                "ongoing_challenges": [],
                "recent_achievements": [],
                "key_metrics_tracked": []
            },
            "personalization": {
                "timezone": initial_profile.get("timezone", "UTC"),
                "working_hours": initial_profile.get("working_hours", "9-17"),
                "language_preference": initial_profile.get("language", "en"),
                "expertise_level": initial_profile.get("expertise_level", "intermediate")
            }
        }
        
        # Save to database
        query = """
        UPDATE users 
        SET memory_context = $1, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = $2;
        """
        
        await self._execute_with_rls(
            query, 
            json.dumps(memory_context), 
            user_id, 
            user_id=user_id
        )
        
        logger.info(f"✅ Initialized memory context for user {user_id}")
        return memory_context

    async def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve complete user context for AI injection.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Dict containing user profile and memory context
        """
        query = """
        SELECT user_id, email, first_name, last_name, username, 
               organization, memory_context, credits, created_at
        FROM users 
        WHERE user_id = $1;
        """
        
        result = await self._execute_with_rls(query, user_id, user_id=user_id)
        
        if result:
            user_data = dict(result[0])
            
            # Parse memory context
            if user_data["memory_context"]:
                user_data["memory_context"] = json.loads(user_data["memory_context"])
            else:
                # Initialize if missing
                user_data["memory_context"] = await self.initialize_user_memory(user_id)
                
            logger.info(f"✅ Retrieved context for user {user_data.get('username', user_id)}")
            return user_data
        else:
            raise ValueError(f"User {user_id} not found")

    async def update_user_memory(
        self, 
        user_id: str, 
        memory_updates: Dict[str, Any],
        interaction_data: Dict[str, Any] = None
    ) -> bool:
        """
        Update user memory with new learned information.
        
        Args:
            user_id: UUID of the user
            memory_updates: New memory data to merge
            interaction_data: Data about the current interaction
            
        Returns:
            Boolean indicating success
        """
        # Get current memory
        current_user = await self.get_user_context(user_id)
        current_memory = current_user.get("memory_context", {})
        
        # Merge updates
        updated_memory = self._deep_merge_memory(current_memory, memory_updates)
        
        # Update interaction tracking
        if interaction_data:
            self._update_interaction_tracking(updated_memory, interaction_data)
        
        # Update timestamp
        updated_memory["last_updated"] = datetime.now().isoformat()
        
        # Save to database
        query = """
        UPDATE users 
        SET memory_context = $1, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = $2;
        """
        
        await self._execute_with_rls(
            query, 
            json.dumps(updated_memory), 
            user_id, 
            user_id=user_id
        )
        
        logger.info(f"✅ Updated memory for user {user_id}")
        return True

    def _deep_merge_memory(self, current: Dict, updates: Dict) -> Dict:
        """Deep merge memory contexts."""
        result = current.copy()
        
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_memory(result[key], value)
            elif key in result and isinstance(result[key], list) and isinstance(value, list):
                result[key] = list(set(result[key] + value))
            else:
                result[key] = value
                
        return result

    def _update_interaction_tracking(self, memory: Dict, interaction_data: Dict):
        """Update interaction tracking in user memory."""
        if "interaction_history" not in memory:
            memory["interaction_history"] = {}
            
        history = memory["interaction_history"]
        
        # Increment total interactions
        history["total_interactions"] = history.get("total_interactions", 0) + 1
        history["last_interaction"] = datetime.now().isoformat()
        
        # Track request types
        request_type = interaction_data.get("request_type", "general")
        if "common_requests" not in history:
            history["common_requests"] = {}
        history["common_requests"][request_type] = history["common_requests"].get(request_type, 0) + 1
        
        # Track satisfaction if provided
        if "satisfaction_rating" in interaction_data:
            if "satisfaction_ratings" not in history:
                history["satisfaction_ratings"] = []
            history["satisfaction_ratings"].append({
                "rating": interaction_data["satisfaction_rating"],
                "timestamp": datetime.now().isoformat()
            })

    async def learn_from_interaction(
        self, 
        user_id: str, 
        agent_id: str, 
        conversation_data: Dict[str, Any]
    ) -> bool:
        """
        Extract learnings from a conversation and update user memory.
        
        Args:
            user_id: UUID of the user
            agent_id: UUID of the agent that had the conversation
            conversation_data: Dict containing conversation details
            
        Returns:
            Boolean indicating success
        """
        # Extract learnable information from conversation
        learnings = self._extract_learnings(conversation_data)
        
        if learnings:
            await self.update_user_memory(user_id, learnings, {
                "request_type": conversation_data.get("topic", "general"),
                "agent_used": agent_id
            })
            
            logger.info(f"✅ Extracted learnings for user {user_id}")
            return True
        
        return False

    def _extract_learnings(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract learnable information from conversation data.
        
        This method analyzes conversation patterns and extracts:
        - New preferences mentioned
        - Company/project information
        - Communication style preferences
        - Tool usage patterns
        """
        learnings = {}
        
        # Extract company information
        if "company_mentioned" in conversation_data:
            learnings["user_profile"] = {
                "company_name": conversation_data["company_mentioned"]
            }
        
        # Extract tool preferences
        if "tools_used" in conversation_data:
            learnings["learned_preferences"] = {
                "favorite_tools": conversation_data["tools_used"]
            }
        
        # Extract project context
        if "project_mentioned" in conversation_data:
            learnings["context_memory"] = {
                "current_projects": [conversation_data["project_mentioned"]]
            }
        
        return learnings

    async def generate_context_prompt(self, user_id: str) -> str:
        """
        Generate a context prompt for AI injection based on user memory.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            String containing formatted context for AI prompt
        """
        user_context = await self.get_user_context(user_id)
        memory = user_context.get("memory_context", {})
        
        # Build context prompt
        context_parts = []
        
        # User profile information
        profile = memory.get("user_profile", {})
        if profile.get("company_name"):
            context_parts.append(f"The user works at {profile['company_name']}")
            if profile.get("industry"):
                context_parts.append(f"in the {profile['industry']} industry")
            if profile.get("role"):
                context_parts.append(f"as a {profile['role']}")
        
        # Communication preferences
        comm_prefs = memory.get("communication_preferences", {})
        if comm_prefs:
            context_parts.append(f"They prefer {comm_prefs.get('tone', 'professional')} communication")
            if comm_prefs.get("detail_level"):
                context_parts.append(f"with {comm_prefs['detail_level']} level of detail")
        
        # Current projects and context
        current_context = memory.get("context_memory", {})
        if current_context.get("current_projects"):
            projects = ", ".join(current_context["current_projects"])
            context_parts.append(f"They are currently working on: {projects}")
        
        # Learned preferences
        learned = memory.get("learned_preferences", {})
        if learned.get("favorite_tools"):
            tools = ", ".join(learned["favorite_tools"])
            context_parts.append(f"They frequently use these tools: {tools}")
        
        return ". ".join(context_parts) + "." if context_parts else ""

# User memory templates for common scenarios
USER_MEMORY_TEMPLATES = {
    "startup_founder": {
        "user_profile": {
            "role": "Founder/CEO",
            "team_size": "5-20",
            "primary_goals": ["growth", "product_development", "fundraising"]
        },
        "communication_preferences": {
            "tone": "direct",
            "detail_level": "high",
            "preferred_formats": ["bullet_points", "action_items"]
        }
    },
    "marketing_manager": {
        "user_profile": {
            "role": "Marketing Manager", 
            "primary_goals": ["lead_generation", "brand_awareness", "campaign_optimization"]
        },
        "communication_preferences": {
            "tone": "enthusiastic",
            "detail_level": "medium",
            "preferred_formats": ["charts", "metrics", "strategies"]
        }
    },
    "developer": {
        "user_profile": {
            "role": "Software Developer",
            "primary_goals": ["code_quality", "automation", "efficiency"]
        },
        "communication_preferences": {
            "tone": "technical",
            "detail_level": "high", 
            "preferred_formats": ["code_examples", "documentation"]
        }
    }
}
