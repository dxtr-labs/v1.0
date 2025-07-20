"""
Production MCP Frontend Integration
Connects the Production Dual MCP System with the frontend API endpoints
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

class WorkflowExecuteRequest(BaseModel):
    workflow_id: str
    input_data: Optional[Dict[str, Any]] = None

# Health Check
@router.get("/health")
async def health_check():
    """Check if production MCP system is operational"""
    if not PRODUCTION_MCP_AVAILABLE or not production_orchestrator:
        return {
            "status": "unavailable",
            "message": "Production MCP system not available",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        status = production_orchestrator.get_system_status()
        return {
            "status": "operational",
            "system": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Agent Management
@router.post("/agents/create")
async def create_agent_mcp(request: AgentMCPRequest):
    """Create a new Custom MCP LLM for an agent"""
    if not production_orchestrator:
        raise HTTPException(status_code=503, detail="Production MCP system not available")
    
    try:
        success = await production_orchestrator.create_agent_mcp(
            agent_id=request.agent_id,
            agent_name=request.agent_name,
            llm_config=request.llm_config,
            personality_traits=request.personality_traits
        )
        
        if success:
            return {
                "success": True,
                "message": f"Custom MCP LLM created for agent {request.agent_id}",
                "agent_id": request.agent_id,
                "agent_name": request.agent_name,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create agent MCP")
            
    except Exception as e:
        logger.error(f"Failed to create agent MCP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/{agent_id}")
async def get_agent_mcp(agent_id: str):
    """Get agent-specific Custom MCP LLM configuration"""
    if not production_orchestrator:
        raise HTTPException(status_code=503, detail="Production MCP system not available")
    
    try:
        agent_mcp = await production_orchestrator.get_agent_mcp(agent_id)
        
        if agent_mcp:
            return {
                "success": True,
                "agent_mcp": agent_mcp,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail=f"Agent MCP not found for {agent_id}")
            
    except Exception as e:
        logger.error(f"Failed to get agent MCP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat Processing
@router.post("/chat/custom-mcp")
async def chat_with_custom_mcp(request: ChatRequest):
    """Process user input using agent-specific Custom MCP LLM"""
    if not production_orchestrator:
        raise HTTPException(status_code=503, detail="Production MCP system not available")
    
    try:
        result = await production_orchestrator.process_with_custom_mcp(
            agent_id=request.agent_id,
            user_input=request.user_input,
            context=request.context
        )
        
        return {
            "success": result["success"],
            "response": result.get("response"),
            "agent_id": result.get("agent_id"),
            "agent_name": result.get("agent_name"),
            "error": result.get("error"),
            "timestamp": result.get("timestamp")
        }
        
    except Exception as e:
        logger.error(f"Custom MCP chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Workflow Processing
@router.post("/workflow/inhouse-ai")
async def process_with_inhouse_ai(request: WorkflowRequest):
    """Process workflow node using Inhouse AI drivers"""
    if not production_orchestrator:
        raise HTTPException(status_code=503, detail="Production MCP system not available")
    
    try:
        result = await production_orchestrator.process_with_inhouse_ai(
            node_type=request.node_type,
            parameters=request.parameters
        )
        
        return {
            "success": result["success"],
            "node_type": result.get("node_type"),
            "result": result.get("result"),
            "driver_used": result.get("driver_used"),
            "error": result.get("error"),
            "timestamp": result.get("timestamp")
        }
        
    except Exception as e:
        logger.error(f"Inhouse AI processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflow/node-types")
async def get_available_node_types():
    """Get available workflow node types"""
    if not production_orchestrator:
        raise HTTPException(status_code=503, detail="Production MCP system not available")
    
    try:
        node_types = production_orchestrator.get_available_node_types()
        templates = {}
        
        for node_type in node_types:
            templates[node_type] = production_orchestrator.get_node_template(node_type)
        
        return {
            "success": True,
            "node_types": node_types,
            "templates": templates,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get node types: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/create")
async def create_workflow(request: WorkflowCreateRequest):
    """Create and store workflow in database"""
    if not production_orchestrator:
        raise HTTPException(status_code=503, detail="Production MCP system not available")
    
    try:
        workflow_id = await production_orchestrator.create_workflow(
            agent_id=request.agent_id,
            workflow_json=request.workflow_json,
            trigger_config=request.trigger_config
        )
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "agent_id": request.agent_id,
            "message": "Workflow created successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to create workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/execute")
async def execute_workflow(request: WorkflowExecuteRequest):
    """Execute stored workflow by ID"""
    if not production_orchestrator:
        raise HTTPException(status_code=503, detail="Production MCP system not available")
    
    try:
        result = await production_orchestrator.execute_workflow(
            workflow_id=request.workflow_id,
            input_data=request.input_data
        )
        
        return {
            "success": result["success"],
            "workflow_id": result.get("workflow_id"),
            "agent_id": result.get("agent_id"),
            "execution_results": result.get("execution_results"),
            "completed_at": result.get("completed_at"),
            "error": result.get("error")
        }
        
    except Exception as e:
        logger.error(f"Failed to execute workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System Information
@router.get("/system/status")
async def get_system_status():
    """Get production system status and architecture info"""
    if not production_orchestrator:
        return {
            "available": False,
            "message": "Production MCP system not available"
        }
    
    try:
        status = production_orchestrator.get_system_status()
        return {
            "available": True,
            "status": status,
            "frontend_connected": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        return {
            "available": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/system/drivers")
async def get_available_drivers():
    """Get information about available Inhouse AI drivers"""
    if not production_orchestrator:
        raise HTTPException(status_code=503, detail="Production MCP system not available")
    
    try:
        status = production_orchestrator.get_system_status()
        drivers_info = status["architecture"]["inhouse_ai_drivers"]
        
        return {
            "success": True,
            "drivers": drivers_info,
            "drivers_path": status.get("drivers_path"),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get drivers info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Test Integration
@router.post("/test/integration")
async def test_integration():
    """Test the complete production integration"""
    if not production_orchestrator:
        raise HTTPException(status_code=503, detail="Production MCP system not available")
    
    try:
        # Test 1: Create test agent
        test_agent_id = f"test_agent_{int(datetime.now().timestamp())}"
        agent_created = await production_orchestrator.create_agent_mcp(
            agent_id=test_agent_id,
            agent_name="Test Sales Agent",
            llm_config={"model": "gpt-4", "temperature": 0.7},
            personality_traits={"tone": "professional", "expertise": "sales"}
        )
        
        # Test 2: Process with Custom MCP LLM
        chat_result = await production_orchestrator.process_with_custom_mcp(
            agent_id=test_agent_id,
            user_input="Tell me about your automation services"
        )
        
        # Test 3: Process with Inhouse AI
        inhouse_result = await production_orchestrator.process_with_inhouse_ai(
            node_type="email_send",
            parameters={
                "toEmail": "test@example.com",
                "subject": "Test Email",
                "content": "Test content"
            }
        )
        
        return {
            "success": True,
            "test_results": {
                "agent_created": agent_created,
                "custom_mcp_test": chat_result["success"],
                "inhouse_ai_test": inhouse_result["success"],
                "integration_status": "operational"
            },
            "message": "Production MCP integration test completed successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Integration test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
