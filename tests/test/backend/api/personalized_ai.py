"""
Personalized AI Agent API Endpoints

This module provides REST API endpoints for the personalized AI agent system,
allowing frontend applications to create agents, manage conversations, and
leverage the full power of context-aware AI interactions.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import uuid
import json
from datetime import datetime

# Import the personalized orchestrator
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.personalized_mcp_orchestrator import PersonalizedMCPOrchestrator, AGENT_PRESETS
from core.contextual_agent_manager import AGENT_PRESETS as AGENT_PRESET_CONFIGS
from core.user_memory_manager import USER_MEMORY_TEMPLATES
from db.postgresql_manager import db_manager

# Initialize router
router = APIRouter(prefix="/api/personalized-ai", tags=["Personalized AI"])
security = HTTPBearer()

# Global orchestrator instance (in production, use dependency injection)
orchestrator = None

async def get_orchestrator():
    """Get the PersonalizedMCPOrchestrator instance."""
    global orchestrator
    if orchestrator is None:
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password'),
            'database': os.getenv('DB_NAME', 'automation_db')
        }
        orchestrator = PersonalizedMCPOrchestrator(db_config)
        await orchestrator.initialize()
    return orchestrator

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user ID from JWT token (simplified version)."""
    # In production, decode and verify JWT token
    # For demo, we'll extract user_id from token
    token = credentials.credentials
    
    # Simplified token validation (replace with proper JWT validation)
    if not token or len(token) < 10:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    
    # For demo purposes, assume token contains user_id
    # In production, decode JWT and extract user_id
    return "user_id_from_jwt"  # Replace with actual user_id extraction

# Pydantic models for API requests/responses

class CreateAgentRequest(BaseModel):
    agent_name: str = Field(..., description="Human-readable name for the agent")
    preset_name: Optional[str] = Field(None, description="Preset to use (optional)")
    agent_role: Optional[str] = Field(None, description="Custom role for the agent")
    agent_personality: Optional[str] = Field(None, description="Custom personality")
    agent_expectations: Optional[str] = Field(None, description="Custom expectations")
    customizations: Optional[Dict[str, Any]] = Field(None, description="Additional customizations")

class AgentResponse(BaseModel):
    agent_id: str
    agent_name: str
    agent_role: str
    agent_personality: str
    agent_expectations: str
    created_at: str

class StartSessionRequest(BaseModel):
    agent_id: str = Field(..., description="ID of the agent to chat with")
    session_context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the session")

class SessionResponse(BaseModel):
    session_id: str
    agent_name: str
    agent_role: str
    user_context_summary: str
    ready_for_messages: bool = True

class SendMessageRequest(BaseModel):
    session_id: str = Field(..., description="ID of the active session")
    message: str = Field(..., description="User's message")
    extract_learnings: bool = Field(True, description="Whether to extract and store learnings")

class MessageResponse(BaseModel):
    session_id: str
    agent_name: str
    response: str
    response_type: str
    suggestions: List[str]
    context_used: Dict[str, Any]
    workflow_data: Optional[Dict[str, Any]] = None

class UpdateUserContextRequest(BaseModel):
    company_name: Optional[str] = None
    industry: Optional[str] = None
    role: Optional[str] = None
    communication_preferences: Optional[Dict[str, Any]] = None
    current_projects: Optional[List[str]] = None

class UserContextResponse(BaseModel):
    user_id: str
    memory_context: Dict[str, Any]
    agents_count: int
    total_interactions: int

# API Endpoints

@router.get("/presets", response_model=Dict[str, Any])
async def get_available_presets():
    """Get all available agent presets and user memory templates."""
    return {
        "agent_presets": AGENT_PRESET_CONFIGS,
        "user_templates": USER_MEMORY_TEMPLATES,
        "description": "Use these presets to quickly create specialized agents"
    }

@router.post("/agents", response_model=AgentResponse)
async def create_personalized_agent(
    request: CreateAgentRequest,
    user_id: str = Depends(get_current_user)
):
    """Create a new personalized AI agent."""
    try:
        orchestrator_instance = await get_orchestrator()
        
        if request.preset_name:
            # Create from preset
            agent_id = await orchestrator_instance.create_agent_from_preset(
                user_id=user_id,
                preset_name=request.preset_name,
                agent_name=request.agent_name,
                customizations=request.customizations
            )
            
            # Get the created agent details
            agent_data = await orchestrator_instance.agent_manager.get_agent_with_context(
                agent_id, user_id
            )
        else:
            # Create custom agent
            if not all([request.agent_role, request.agent_personality, request.agent_expectations]):
                raise HTTPException(
                    status_code=400,
                    detail="When not using a preset, agent_role, agent_personality, and agent_expectations are required"
                )
            
            agent_data = await orchestrator_instance.agent_manager.create_personalized_agent(
                user_id=user_id,
                agent_name=request.agent_name,
                agent_role=request.agent_role,
                agent_personality=request.agent_personality,
                agent_expectations=request.agent_expectations
            )
        
        return AgentResponse(
            agent_id=agent_data["agent_id"],
            agent_name=agent_data["agent_name"],
            agent_role=agent_data["agent_role"],
            agent_personality=agent_data["agent_personality"],
            agent_expectations=agent_data["agent_expectations"],
            created_at=agent_data.get("created_at", datetime.now().isoformat())
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")

@router.get("/agents", response_model=List[AgentResponse])
async def get_user_agents(user_id: str = Depends(get_current_user)):
    """Get all agents belonging to the current user."""
    try:
        orchestrator_instance = await get_orchestrator()
        agents = await orchestrator_instance.agent_manager.get_user_agents(user_id)
        
        return [
            AgentResponse(
                agent_id=agent["agent_id"],
                agent_name=agent["agent_name"],
                agent_role=agent["agent_role"],
                agent_personality=agent["agent_personality"],
                agent_expectations=agent["agent_expectations"],
                created_at=agent["created_at"].isoformat()
            )
            for agent in agents
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agents: {str(e)}")

@router.post("/sessions", response_model=SessionResponse)
async def start_personalized_session(
    request: StartSessionRequest,
    user_id: str = Depends(get_current_user)
):
    """Start a new personalized chat session with an agent."""
    try:
        orchestrator_instance = await get_orchestrator()
        
        # Validate agent belongs to user
        try:
            agent_data = await orchestrator_instance.agent_manager.get_agent_with_context(
                request.agent_id, user_id
            )
        except ValueError:
            raise HTTPException(status_code=404, detail="Agent not found or access denied")
        
        # Create session
        session_id = await orchestrator_instance.create_personalized_session(
            user_id=user_id,
            agent_id=request.agent_id,
            session_context=request.session_context
        )
        
        # Generate user context summary
        user_context = await orchestrator_instance.user_memory_manager.get_user_context(user_id)
        context_summary = await orchestrator_instance.user_memory_manager.generate_context_prompt(user_id)
        
        return SessionResponse(
            session_id=session_id,
            agent_name=agent_data["agent_name"],
            agent_role=agent_data["agent_role"],
            user_context_summary=context_summary or "No specific context available"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")

@router.post("/messages", response_model=MessageResponse)
async def send_message(
    request: SendMessageRequest,
    user_id: str = Depends(get_current_user)
):
    """Send a message in a personalized chat session."""
    try:
        orchestrator_instance = await get_orchestrator()
        
        # Process message with full personalization
        response = await orchestrator_instance.process_message(
            session_id=request.session_id,
            user_message=request.message,
            extract_learnings=request.extract_learnings
        )
        
        return MessageResponse(**response)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@router.get("/context", response_model=UserContextResponse)
async def get_user_context(user_id: str = Depends(get_current_user)):
    """Get the current user's context and memory."""
    try:
        orchestrator_instance = await get_orchestrator()
        
        # Get user context
        user_context = await orchestrator_instance.user_memory_manager.get_user_context(user_id)
        
        # Get user's agents count
        agents = await orchestrator_instance.agent_manager.get_user_agents(user_id)
        
        # Extract interaction count
        memory = user_context.get("memory_context", {})
        interaction_history = memory.get("interaction_history", {})
        total_interactions = interaction_history.get("total_interactions", 0)
        
        return UserContextResponse(
            user_id=user_id,
            memory_context=memory,
            agents_count=len(agents),
            total_interactions=total_interactions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user context: {str(e)}")

@router.put("/context", response_model=Dict[str, str])
async def update_user_context(
    request: UpdateUserContextRequest,
    user_id: str = Depends(get_current_user)
):
    """Update user context and memory."""
    try:
        orchestrator_instance = await get_orchestrator()
        
        # Build update dictionary
        updates = {}
        
        if any([request.company_name, request.industry, request.role]):
            updates["user_profile"] = {}
            if request.company_name:
                updates["user_profile"]["company_name"] = request.company_name
            if request.industry:
                updates["user_profile"]["industry"] = request.industry
            if request.role:
                updates["user_profile"]["role"] = request.role
        
        if request.communication_preferences:
            updates["communication_preferences"] = request.communication_preferences
        
        if request.current_projects:
            updates["context_memory"] = {
                "current_projects": request.current_projects
            }
        
        # Update user memory
        await orchestrator_instance.user_memory_manager.update_user_memory(user_id, updates)
        
        return {"status": "success", "message": "User context updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update context: {str(e)}")

@router.get("/sessions/{session_id}/summary")
async def get_session_summary(
    session_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get a summary of a chat session."""
    try:
        orchestrator_instance = await get_orchestrator()
        summary = await orchestrator_instance.get_session_summary(session_id)
        return summary
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session summary: {str(e)}")

@router.delete("/sessions/{session_id}")
async def close_session(
    session_id: str,
    user_id: str = Depends(get_current_user)
):
    """Close a chat session and process any pending learnings."""
    try:
        orchestrator_instance = await get_orchestrator()
        await orchestrator_instance.close_session(session_id)
        return {"status": "success", "message": "Session closed successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to close session: {str(e)}")

@router.delete("/agents/{agent_id}")
async def delete_agent(
    agent_id: str,
    user_id: str = Depends(get_current_user)
):
    """Delete an agent."""
    try:
        orchestrator_instance = await get_orchestrator()
        await orchestrator_instance.agent_manager.delete_agent(agent_id, user_id)
        return {"status": "success", "message": "Agent deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete agent: {str(e)}")

# Health check endpoint
@router.get("/health")
async def health_check():
    """Check if the personalized AI system is healthy."""
    try:
        orchestrator_instance = await get_orchestrator()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "features": [
                "personalized_agents",
                "context_injection", 
                "memory_persistence",
                "learning_extraction",
                "multi_session_support"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

# Demo endpoint for testing
@router.post("/demo/quick-setup")
async def quick_demo_setup(user_id: str = Depends(get_current_user)):
    """Quick setup for demo purposes - creates sample agents and context."""
    try:
        orchestrator_instance = await get_orchestrator()
        
        # Set up user with startup template
        from core.personalized_mcp_orchestrator import setup_user_with_template
        await setup_user_with_template(orchestrator_instance, user_id, "startup_founder")
        
        # Create marketing agent
        marketing_agent_id = await orchestrator_instance.create_agent_from_preset(
            user_id=user_id,
            preset_name="marketing_maestro",
            agent_name="Marketing Maestro"
        )
        
        # Create support agent
        support_agent_id = await orchestrator_instance.create_agent_from_preset(
            user_id=user_id,
            preset_name="support_assistant",
            agent_name="Customer Success Manager"
        )
        
        return {
            "status": "success",
            "message": "Demo setup complete",
            "created_agents": [
                {"id": marketing_agent_id, "name": "Marketing Maestro"},
                {"id": support_agent_id, "name": "Customer Success Manager"}
            ],
            "user_template": "startup_founder"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo setup failed: {str(e)}")

# Include router in main FastAPI app
def include_personalized_ai_routes(app):
    """Include personalized AI routes in the main FastAPI app."""
    app.include_router(router)
