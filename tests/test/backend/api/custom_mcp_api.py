"""
Enhanced Custom MCP LLM API Integration
Provides API endpoints for the enhanced Custom MCP LLM system
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/custom-mcp", tags=["Custom MCP LLM"])

# Request/Response Models
class CreateAgentRequest(BaseModel):
    agent_name: str
    personality: Dict[str, Any]
    triggers: Dict[str, Any]
    model: Optional[str] = "gpt-4"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000

class ChatRequest(BaseModel):
    agent_id: str
    user_message: str
    context: Optional[Dict[str, Any]] = None

class WorkflowFromChatRequest(BaseModel):
    agent_id: str
    workflow_description: str

class CreateTriggerRequest(BaseModel):
    agent_id: str
    workflow_id: str
    trigger_config: Dict[str, Any]

# Global reference to custom MCP LLM and automation engine
custom_mcp_llm = None
automation_engine = None

def set_instances(mcp_instance, automation_instance):
    """Set the global instances"""
    global custom_mcp_llm, automation_engine
    custom_mcp_llm = mcp_instance
    automation_engine = automation_instance

# Agent Management Endpoints
@router.post("/agents/create")
async def create_agent(request: CreateAgentRequest):
    """Create new custom AI agent with MCP LLM"""
    if not custom_mcp_llm:
        raise HTTPException(status_code=503, detail="Custom MCP LLM not available")
    
    try:
        agent_config = {
            "agent_name": request.agent_name,
            "personality": request.personality,
            "triggers": request.triggers,
            "model": request.model,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens
        }
        
        result = await custom_mcp_llm.create_agent(agent_config)
        
        if result["success"]:
            return {
                "success": True,
                "agent_id": result["agent_id"],
                "agent_name": result["agent_name"],
                "message": "Custom AI agent created successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create agent"))
            
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents")
async def get_all_agents():
    """Get all created custom AI agents"""
    if not custom_mcp_llm:
        raise HTTPException(status_code=503, detail="Custom MCP LLM not available")
    
    try:
        result = custom_mcp_llm.get_all_agents()
        
        return {
            "success": result["success"],
            "agents": result["agents"],
            "total_agents": result["total_agents"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent details"""
    if not custom_mcp_llm:
        raise HTTPException(status_code=503, detail="Custom MCP LLM not available")
    
    try:
        # Load agent if not cached
        await custom_mcp_llm._load_agent_from_db(agent_id)
        
        if agent_id in custom_mcp_llm.agent_configs:
            agent_config = custom_mcp_llm.agent_configs[agent_id]
            return {
                "success": True,
                "agent": agent_config,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
            
    except Exception as e:
        logger.error(f"Failed to get agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat Endpoints
@router.post("/chat")
async def chat_with_agent(request: ChatRequest):
    """Chat with specific custom AI agent"""
    if not custom_mcp_llm:
        raise HTTPException(status_code=503, detail="Custom MCP LLM not available")
    
    try:
        result = await custom_mcp_llm.chat_with_agent(
            agent_id=request.agent_id,
            user_message=request.user_message,
            context=request.context
        )
        
        return {
            "success": result["success"],
            "agent_id": result.get("agent_id"),
            "agent_name": result.get("agent_name"),
            "response": result.get("response"),
            "memory_entries": result.get("memory_entries", 0),
            "error": result.get("error"),
            "timestamp": result.get("timestamp")
        }
        
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Workflow Endpoints
@router.get("/agents/{agent_id}/json-scripts")
async def get_agent_json_scripts(agent_id: str):
    """Get all JSON scripts available for an agent"""
    if not custom_mcp_llm:
        raise HTTPException(status_code=503, detail="Custom MCP LLM not available")
    
    try:
        result = await custom_mcp_llm.get_agent_json_scripts(agent_id)
        
        return {
            "success": result["success"],
            "agent_id": result.get("agent_id"),
            "json_scripts": result.get("json_scripts"),
            "available_nodes": result.get("available_nodes"),
            "total_scripts": result.get("total_scripts"),
            "error": result.get("error")
        }
        
    except Exception as e:
        logger.error(f"Failed to get JSON scripts for agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/create-from-chat")
async def create_workflow_from_chat(request: WorkflowFromChatRequest):
    """Create workflow from natural language description in chat"""
    if not custom_mcp_llm:
        raise HTTPException(status_code=503, detail="Custom MCP LLM not available")
    
    try:
        result = await custom_mcp_llm.create_workflow_from_chat(
            agent_id=request.agent_id,
            workflow_description=request.workflow_description
        )
        
        return {
            "success": result["success"],
            "workflow_id": result.get("workflow_id"),
            "workflow_json": result.get("workflow_json"),
            "message": result.get("message"),
            "ready_for_automation_engine": result.get("ready_for_automation_engine", False),
            "error": result.get("error")
        }
        
    except Exception as e:
        logger.error(f"Failed to create workflow from chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Automation Engine Integration
@router.post("/automation/trigger/create")
async def create_automation_trigger(request: CreateTriggerRequest):
    """Create automation trigger for workflow"""
    if not automation_engine:
        raise HTTPException(status_code=503, detail="Automation Engine not available")
    
    try:
        result = await automation_engine.create_trigger(
            agent_id=request.agent_id,
            workflow_id=request.workflow_id,
            trigger_config=request.trigger_config
        )
        
        return {
            "success": result["success"],
            "trigger_id": result.get("trigger_id"),
            "message": result.get("message"),
            "error": result.get("error")
        }
        
    except Exception as e:
        logger.error(f"Failed to create trigger: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/automation/workflow/execute/{workflow_id}")
async def execute_workflow_manually(workflow_id: str, input_data: Optional[Dict[str, Any]] = None):
    """Manually execute workflow"""
    if not automation_engine:
        raise HTTPException(status_code=503, detail="Automation Engine not available")
    
    try:
        # Get workflow from database
        workflow_data = await automation_engine._get_workflow_from_db(workflow_id)
        
        if not workflow_data:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Execute workflow
        result = await automation_engine.execute_workflow(workflow_data)
        
        return {
            "success": result["success"],
            "workflow_id": result.get("workflow_id"),
            "workflow_name": result.get("workflow_name"),
            "total_nodes": result.get("total_nodes"),
            "successful_nodes": result.get("successful_nodes"),
            "failed_nodes": result.get("failed_nodes"),
            "execution_results": result.get("execution_results"),
            "completed_at": result.get("completed_at"),
            "error": result.get("error")
        }
        
    except Exception as e:
        logger.error(f"Failed to execute workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System Status Endpoints
@router.get("/system/status")
async def get_system_status():
    """Get system status for Custom MCP LLM and Automation Engine"""
    
    status = {
        "custom_mcp_llm": None,
        "automation_engine": None,
        "integration_status": "disconnected",
        "timestamp": datetime.now().isoformat()
    }
    
    if custom_mcp_llm:
        status["custom_mcp_llm"] = custom_mcp_llm.get_system_status()
        
    if automation_engine:
        status["automation_engine"] = automation_engine.get_system_status()
        
    if custom_mcp_llm and automation_engine:
        status["integration_status"] = "connected"
    
    return status

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "operational" if custom_mcp_llm and automation_engine else "partial",
        "custom_mcp_llm_available": custom_mcp_llm is not None,
        "automation_engine_available": automation_engine is not None,
        "timestamp": datetime.now().isoformat()
    }

# Integration Test Endpoint
@router.post("/test/integration")
async def test_integration():
    """Test the complete integration"""
    if not custom_mcp_llm or not automation_engine:
        raise HTTPException(status_code=503, detail="System components not available")
    
    try:
        # Test 1: Create test agent
        test_agent_config = {
            "agent_name": f"Integration Test Agent {int(datetime.now().timestamp())}",
            "personality": {"tone": "professional", "expertise": "testing"},
            "triggers": {"type": "manual"},
            "model": "gpt-4"
        }
        
        agent_result = await custom_mcp_llm.create_agent(test_agent_config)
        
        if not agent_result["success"]:
            raise Exception("Failed to create test agent")
        
        test_agent_id = agent_result["agent_id"]
        
        # Test 2: Chat with agent
        chat_result = await custom_mcp_llm.chat_with_agent(
            test_agent_id,
            "Create a workflow that sends an email and then an SMS"
        )
        
        # Test 3: Create workflow from chat
        workflow_result = await custom_mcp_llm.create_workflow_from_chat(
            test_agent_id,
            "Send email to client then send SMS notification"
        )
        
        # Test 4: Create trigger
        trigger_result = await automation_engine.create_trigger(
            test_agent_id,
            workflow_result["workflow_id"],
            {"type": "manual", "test_trigger": True}
        )
        
        return {
            "success": True,
            "test_results": {
                "agent_creation": agent_result["success"],
                "agent_chat": chat_result["success"],
                "workflow_creation": workflow_result["success"],
                "trigger_creation": trigger_result["success"]
            },
            "test_agent_id": test_agent_id,
            "workflow_id": workflow_result.get("workflow_id"),
            "trigger_id": trigger_result.get("trigger_id"),
            "message": "Integration test completed successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Integration test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
