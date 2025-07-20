"""
Custom MCP Frontend Integration
Connects the Custom MCP LLM System with the frontend API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import json
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

# Import the Custom MCP LLM orchestrator and automation engine
try:
    from mcp.simple_mcp_llm import MCP_LLM_Orchestrator
    from mcp.simple_automation_engine import get_automation_engine, execute_webhook_trigger, register_workflow_trigger
    CUSTOM_MCP_AVAILABLE = True
    logger.info("✅ Custom MCP LLM Orchestrator imported successfully")
except ImportError as e:
    CUSTOM_MCP_AVAILABLE = False
    logger.error(f"❌ Custom MCP import failed: {e}")

router = APIRouter(prefix="/api/custom-mcp", tags=["Custom MCP"])

# Initialize the Custom MCP orchestrator
custom_orchestrator = None
if CUSTOM_MCP_AVAILABLE:
    custom_orchestrator = MCP_LLM_Orchestrator()

# Request/Response Models
class AgentMCPRequest(BaseModel):
    agent_id: str
    agent_name: str
    llm_config: Dict[str, Any]
    personality_traits: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    agent_id: str
    user_input: str
    context: Optional[Dict[str, Any]] = None

class WorkflowRequest(BaseModel):
    node_type: str
    parameters: Dict[str, Any]

class WorkflowCreateRequest(BaseModel):
    agent_id: str
    workflow_json: Dict[str, Any]
    trigger_config: Optional[Dict[str, Any]] = None

@router.get("/health")
async def check_custom_mcp_health():
    """Check Custom MCP system health"""
    try:
        if not CUSTOM_MCP_AVAILABLE or not custom_orchestrator:
            return {
                "status": "error",
                "message": "Custom MCP Orchestrator not available",
                "available": False
            }
        
        status = custom_orchestrator.get_system_status()
        
        return {
            "status": "healthy",
            "message": "Custom MCP system operational",
            "orchestrator": status,
            "available": True
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents")
async def create_custom_agent_mcp(request: AgentMCPRequest):
    """Create a new Custom MCP LLM agent"""
    try:
        if not custom_orchestrator:
            raise HTTPException(status_code=503, detail="Custom MCP Orchestrator not available")
        
        success = await custom_orchestrator.create_agent(
            agent_id=request.agent_id,
            agent_name=request.agent_name,
            personality=request.personality_traits or {},
            llm_config=request.llm_config
        )
        
        if success:
            return {
                "status": "success", 
                "message": f"Custom agent {request.agent_name} created successfully",
                "agent_id": request.agent_id
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create Custom agent")
            
    except Exception as e:
        logger.error(f"Failed to create Custom agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/{agent_id}")
async def get_custom_agent_mcp(agent_id: str):
    """Get Custom MCP agent details"""
    try:
        if not custom_orchestrator:
            raise HTTPException(status_code=503, detail="Custom MCP Orchestrator not available")
        
        agent_mcp = await custom_orchestrator.get_agent(agent_id)
        
        if agent_mcp:
            return {
                "status": "success",
                "agent": agent_mcp.get_info(),
                "memory_count": len(agent_mcp.memory),
                "personality": agent_mcp.personality
            }
        else:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
            
    except Exception as e:
        logger.error(f"Failed to get Custom agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/{agent_id}/chat")  
async def chat_with_custom_mcp(agent_id: str, request: ChatRequest):
    """Chat with Custom MCP LLM agent"""
    try:
        if not custom_orchestrator:
            raise HTTPException(status_code=503, detail="Custom MCP Orchestrator not available")
        
        result = await custom_orchestrator.process_with_agent(
            agent_id=agent_id,
            user_input=request.user_input,
            context=request.context
        )
        
        return {
            "status": "success",
            "agent_id": agent_id,
            "response": result["response"],
            "memory_updated": result.get("memory_updated", False),
            "context": result.get("context", {})
        }
        
    except Exception as e:
        logger.error(f"Chat with Custom agent {agent_id} failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflows")
async def process_with_custom_automation(request: WorkflowRequest):
    """Process workflow with Custom Automation Engine"""
    try:
        automation_engine = get_automation_engine()
        
        result = await automation_engine.execute_json_script_to_api(
            node_type=request.node_type,
            json_script={},
            parameters=request.parameters
        )
        
        return {
            "status": "success",
            "node_type": request.node_type,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Custom automation processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_custom_node_templates():
    """Get Custom MCP node templates"""
    try:
        if not custom_orchestrator:
            raise HTTPException(status_code=503, detail="Custom MCP Orchestrator not available")
        
        node_types = custom_orchestrator.get_available_node_types()
        templates = {}
        
        for node_type in node_types:
            templates[node_type] = custom_orchestrator.get_node_template(node_type)
        
        return {
            "status": "success",
            "templates": templates,
            "count": len(templates)
        }
        
    except Exception as e:
        logger.error(f"Failed to get Custom node templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/{agent_id}/workflows")
async def create_custom_workflow(agent_id: str, request: WorkflowCreateRequest):
    """Create workflow for Custom agent"""
    try:
        if not custom_orchestrator:
            raise HTTPException(status_code=503, detail="Custom MCP Orchestrator not available")
        
        workflow_id = await custom_orchestrator.create_workflow(
            agent_id=agent_id,
            workflow_json=request.workflow_json
        )
        
        # Register trigger if provided
        trigger_id = None
        if request.trigger_config:
            trigger_id = await register_workflow_trigger(
                workflow_id=workflow_id,
                trigger_type=request.trigger_config.get("type", "manual"),
                trigger_config=request.trigger_config
            )
        
        return {
            "status": "success",
            "workflow_id": workflow_id,
            "trigger_id": trigger_id,
            "agent_id": agent_id
        }
        
    except Exception as e:
        logger.error(f"Failed to create Custom workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflows/{workflow_id}/execute")
async def execute_custom_workflow(workflow_id: str):
    """Execute Custom workflow"""
    try:
        if not custom_orchestrator:
            raise HTTPException(status_code=503, detail="Custom MCP Orchestrator not available")
        
        result = await custom_orchestrator.execute_workflow(workflow_id)
        
        return {
            "status": "success",
            "workflow_id": workflow_id,
            "execution_result": result
        }
        
    except Exception as e:
        logger.error(f"Failed to execute Custom workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhooks/{webhook_id}")
async def trigger_custom_webhook(webhook_id: str, payload: Dict[str, Any]):
    """Trigger Custom webhook workflow"""
    try:
        result = await execute_webhook_trigger(webhook_id, payload)
        
        return {
            "status": "success",
            "webhook_id": webhook_id,
            "execution_result": result
        }
        
    except Exception as e:
        logger.error(f"Failed to trigger Custom webhook {webhook_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-info")
async def get_custom_system_info():
    """Get Custom MCP system information"""
    try:
        if not custom_orchestrator:
            raise HTTPException(status_code=503, detail="Custom MCP Orchestrator not available")
        
        status = custom_orchestrator.get_system_status()
        
        return {
            "status": "success",
            "system": "Custom MCP LLM with Automation Engine",
            "version": "1.0.0",
            "components": {
                "custom_mcp_orchestrator": status,
                "automation_engine": "Enhanced with Trigger Sync"
            },
            "available": CUSTOM_MCP_AVAILABLE
        }
        
    except Exception as e:
        logger.error(f"Failed to get Custom system info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents")
async def list_custom_agents():
    """List all Custom MCP agents"""
    try:
        if not custom_orchestrator:
            raise HTTPException(status_code=503, detail="Custom MCP Orchestrator not available")
        
        agents = await custom_orchestrator.list_agents()
        
        return {
            "status": "success",
            "agents": agents,
            "count": len(agents)
        }
        
    except Exception as e:
        logger.error(f"Failed to list Custom agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/agents/{agent_id}")
async def delete_custom_agent(agent_id: str):
    """Delete Custom MCP agent"""
    try:
        if not custom_orchestrator:
            raise HTTPException(status_code=503, detail="Custom MCP Orchestrator not available")
        
        success = await custom_orchestrator.delete_agent(agent_id)
        
        if success:
            return {
                "status": "success",
                "message": f"Agent {agent_id} deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
            
    except Exception as e:
        logger.error(f"Failed to delete Custom agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/{agent_id}/memory")
async def get_agent_memory(agent_id: str):
    """Get Custom agent memory"""
    try:
        if not custom_orchestrator:
            raise HTTPException(status_code=503, detail="Custom MCP Orchestrator not available")
        
        memory = await custom_orchestrator.get_agent_memory(agent_id)
        
        return {
            "status": "success",
            "agent_id": agent_id,
            "memory": memory,
            "count": len(memory)
        }
        
    except Exception as e:
        logger.error(f"Failed to get Custom agent memory {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/{agent_id}/memory/clear")
async def clear_agent_memory(agent_id: str):
    """Clear Custom agent memory"""
    try:
        if not custom_orchestrator:
            raise HTTPException(status_code=503, detail="Custom MCP Orchestrator not available")
        
        success = await custom_orchestrator.clear_agent_memory(agent_id)
        
        if success:
            return {
                "status": "success",
                "message": f"Memory cleared for agent {agent_id}"
            }
        else:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
            
    except Exception as e:
        logger.error(f"Failed to clear Custom agent memory {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/triggers")
async def get_all_triggers():
    """Get all active triggers"""
    try:
        automation_engine = get_automation_engine()
        triggers = await automation_engine.get_active_triggers()
        
        return {
            "status": "success",
            "triggers": triggers,
            "count": len(triggers)
        }
        
    except Exception as e:
        logger.error(f"Failed to get triggers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/triggers/{trigger_id}/pause")
async def pause_trigger(trigger_id: str):
    """Pause a workflow trigger"""
    try:
        automation_engine = get_automation_engine()
        success = await automation_engine.pause_workflow_trigger(trigger_id)
        
        if success:
            return {
                "status": "success",
                "message": f"Trigger {trigger_id} paused"
            }
        else:
            raise HTTPException(status_code=404, detail=f"Trigger {trigger_id} not found")
            
    except Exception as e:
        logger.error(f"Failed to pause trigger {trigger_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/triggers/{trigger_id}/resume")
async def resume_trigger(trigger_id: str):
    """Resume a workflow trigger"""
    try:
        automation_engine = get_automation_engine()
        success = await automation_engine.resume_workflow_trigger(trigger_id)
        
        if success:
            return {
                "status": "success",
                "message": f"Trigger {trigger_id} resumed"
            }
        else:
            raise HTTPException(status_code=404, detail=f"Trigger {trigger_id} not found")
            
    except Exception as e:
        logger.error(f"Failed to resume trigger {trigger_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/triggers/{trigger_id}")
async def delete_trigger(trigger_id: str):
    """Delete a workflow trigger"""
    try:
        automation_engine = get_automation_engine()
        success = await automation_engine.delete_workflow_trigger(trigger_id)
        
        if success:
            return {
                "status": "success",
                "message": f"Trigger {trigger_id} deleted"
            }
        else:
            raise HTTPException(status_code=404, detail=f"Trigger {trigger_id} not found")
            
    except Exception as e:
        logger.error(f"Failed to delete trigger {trigger_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflows/{workflow_id}/history")
async def get_workflow_history(workflow_id: str, limit: int = 50):
    """Get workflow execution history"""
    try:
        automation_engine = get_automation_engine()
        history = await automation_engine.get_workflow_execution_history(workflow_id, limit)
        
        return {
            "status": "success",
            "workflow_id": workflow_id,
            "history": history,
            "count": len(history)
        }
        
    except Exception as e:
        logger.error(f"Failed to get workflow history {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
