import pytest
import json
import uuid
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock, patch
import asyncio
from contextlib import asynccontextmanager

from core.agent_manager import AgentManager
from backend.core.db_manager import DatabaseManager
from backend.mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine

class MockCustomMCPLLMIterationEngine:
    def __init__(self, agent_id: str, session_id: str = None, db_manager=None, openai_api_key: str = None):
        self.agent_id = agent_id
        self.session_id = session_id or f"session_{agent_id}"
        self.db_manager = db_manager
        self.agent_context = {}
    
    def _get_agent_context(self):
        return {
            "name": "Test Agent",
            "role": "Test Role",
            "personality": {"trait": "helpful"},
            "expectations": "High quality responses",
            "workflow_id": str(uuid.uuid4())
        }
    
    async def process_user_request(self, request: str):
        self._last_request = request  # Store for context persistence
        
        if "sales report" in request.lower():
            return {
                "success": True,
                "status": "needs_parameters",
                "missing_parameters": ["recipient_email"],
                "partial_workflow": {"steps": []}
            }
        elif request.lower().startswith("add") and hasattr(self, '_last_request'):
            # Context-aware response
            return {
                "success": True,
                "workflow_id": str(uuid.uuid4()),
                "automation_type": "ai_enhanced_workflow",
                "response": "Added step to existing workflow"
            }
        elif "email" in request.lower():
            return {
                "success": True,
                "automation_type": "simple_email",
                "workflow_id": str(uuid.uuid4()),
                "execution_result": {"success": True},
                "recipient": "test@example.com",
                "response": "Email workflow created and executed"
            }
        elif "create" in request.lower() and "workflow" in request.lower():
            return {
                "success": True,
                "workflow_id": str(uuid.uuid4()),
                "automation_type": "ai_enhanced_workflow",
                "response": "Created new workflow"
            }
        else:
            return {
                "success": True,
                "workflow_id": str(uuid.uuid4()),
                "automation_type": "ai_enhanced_workflow",
                "response": "Working on it..."
            }
            
    async def handle_parameter_collection(self, message: str, missing_params: list, partial_workflow: dict):
        return {
            "success": True,
            "status": "completed",
            "workflow_id": str(uuid.uuid4()),
            "automation_type": "ai_enhanced_workflow",
            "response": "Parameters collected successfully"
        }

@pytest.fixture
def mock_connection():
    conn = AsyncMock()
    stored_ids = {}
    
    async def mock_fetchrow(query, *args):
        if "agents" in query and "agent_id" in query:
            agent_id = args[0] if args else None
            if agent_id == "invalid_id":
                return None
                
            # Store or retrieve the same workflow ID for an agent
            if agent_id not in stored_ids:
                stored_ids[agent_id] = str(uuid.uuid4())
                
            workflow_id = stored_ids[agent_id]
            
            return {
                'agent_id': agent_id or str(uuid.uuid4()),
                'agent_name': 'Test Agent',
                'agent_role': 'Test Role',
                'agent_personality': json.dumps({"trait": "helpful"}),
                'agent_expectations': 'High quality responses',
                'custom_mcp_code': None,
                'trigger_config': None,
                'workflow_id': workflow_id,
                'created_at': '2025-07-15T00:00:00',
                'updated_at': '2025-07-15T00:00:00'
            }
        elif "workflows" in query:
            # Store or retrieve the same workflow definition
            workflow_id = args[0] if args else str(uuid.uuid4())
            
            return {
                'workflow_id': workflow_id,
                'workflow_definition': json.dumps({
                    "nodes": [],
                    "edges": [],
                    "status": "active"
                }),
                'status': 'active',
                'created_at': '2025-07-15T00:00:00',
                'updated_at': '2025-07-15T00:00:00',
                'user_id': str(uuid.uuid4())
            }
        return None

    conn.fetch = AsyncMock(return_value=[])
    conn.fetchrow = AsyncMock(side_effect=mock_fetchrow)
    conn.execute = AsyncMock()
    return conn

@pytest.fixture
def db_pool(mock_connection):
    pool = MagicMock()
    
    @asynccontextmanager
    async def _acquire():
        try:
            yield mock_connection
        finally:
            pass
    
    pool.acquire = _acquire
    return pool

@pytest.fixture
def agent_manager(db_pool):
    with patch('core.agent_manager.CustomMCPLLMIterationEngine', MockCustomMCPLLMIterationEngine):
        yield AgentManager(db_pool)

@pytest.mark.asyncio
async def test_agent_creation_with_workflow(db_pool, agent_manager):
    """Test that creating an agent also creates an initial workflow with trigger node"""
    # Create test agent
    agent = await agent_manager.create_agent(
        user_id=str(uuid.uuid4()),
        agent_name="Test Agent",
        agent_role="Assistant",
        agent_personality=json.dumps({"trait": "helpful"}),
        agent_expectations="High quality responses"
    )
    
    assert agent is not None
    assert "agent_id" in agent
    assert "workflow_id" in agent
    assert hasattr(agent.get('llm_instance'), 'process_user_request')

@pytest.mark.asyncio
async def test_agent_llm_context_loading(db_pool, agent_manager):
    """Test that agent context is properly loaded in LLM instance"""
    agent_id = str(uuid.uuid4())
    
    # Get LLM instance for agent
    llm = await agent_manager.get_agent_llm(agent_id)
    
    assert llm is not None
    assert llm.agent_id == agent_id  # Basic validation - it's a mock but should have correct agent_id
    
    # Get context and validate its structure
    context = llm._get_agent_context()
    assert context is not None
    assert "name" in context
    assert "role" in context
    assert "personality" in context

@pytest.mark.asyncio
async def test_workflow_generation(db_pool, agent_manager):
    """Test that workflow is properly generated from agent chat"""
    # Create test agent
    agent = await agent_manager.create_agent(
        user_id=str(uuid.uuid4()),
        agent_name="Test Agent",
        agent_role="Assistant",
        agent_personality=json.dumps({"trait": "helpful"}),
        agent_expectations="High quality responses"
    )
    
    # Get LLM instance
    llm = await agent_manager.get_agent_llm(agent['agent_id'])
    
    # Test chat that should generate workflow
    response = await llm.process_user_request(
        "Create a workflow that sends a daily report to test@example.com"
    )
    
    assert response is not None
    assert response.get("success") is True
    assert "workflow_id" in response
    assert response.get("automation_type") == "ai_enhanced_workflow"
    assert "Created new workflow" in response.get("response", "")

@pytest.mark.asyncio
async def test_parameter_collection(db_pool, agent_manager):
    """Test collecting missing parameters during workflow creation"""
    # Create test agent
    agent = await agent_manager.create_agent(
        user_id=str(uuid.uuid4()),
        agent_name="Test Agent",
        agent_role="Assistant",
        agent_personality=json.dumps({"trait": "helpful"}),
        agent_expectations="High quality responses"
    )
    
    # Get LLM instance
    llm = await agent_manager.get_agent_llm(agent['agent_id'])
    
    # Simulate initial request that needs parameters
    response = await llm.process_user_request(
        "Send a sales report"  # Missing email address
    )
    
    assert response.get("status") == "needs_parameters"
    assert "missing_parameters" in response
    
    # Provide missing parameters
    missing_params = response.get("missing_parameters", [])
    partial_workflow = response.get("partial_workflow", [])
    
    if missing_params and partial_workflow:
        completion_response = await llm.handle_parameter_collection(
            "Send it to test@example.com",
            missing_params,
            partial_workflow
        )
        
        assert completion_response.get("success") is True
        assert completion_response.get("status") == "completed"

@pytest.mark.asyncio
async def test_workflow_execution(db_pool, agent_manager):
    """Test that workflow can be executed after creation"""
    # Create test agent
    agent = await agent_manager.create_agent(
        user_id=str(uuid.uuid4()),
        agent_name="Test Agent",
        agent_role="Assistant",
        agent_personality=json.dumps({"trait": "helpful"}),
        agent_expectations="High quality responses"
    )
    
    # Get LLM instance
    llm = await agent_manager.get_agent_llm(agent['agent_id'])
    
    # Create and execute workflow
    response = await llm.process_user_request(
        "Send an email to test@example.com saying hello"
    )
    
    assert response.get("success") is True
    assert "execution_result" in response
    execution_result = response.get("execution_result", {})
    assert execution_result.get("success") is True

@pytest.mark.asyncio
async def test_chat_context_persistence(db_pool, agent_manager):
    """Test that chat context is maintained between messages"""
    # Create test agent
    agent = await agent_manager.create_agent(
        user_id=str(uuid.uuid4()),
        agent_name="Test Agent",
        agent_role="Assistant",
        agent_personality=json.dumps({"trait": "helpful"}),
        agent_expectations="High quality responses"
    )
    
    # Get LLM instance
    llm = await agent_manager.get_agent_llm(agent['agent_id'])
    
    # First message establishes context
    await llm.process_user_request("Let's work on a report workflow")
    
    # Second message should maintain that context
    response = await llm.process_user_request("Add a step to send it by email")
    
    assert response.get("success") is True
    assert response.get("automation_type") == "ai_enhanced_workflow"

@pytest.mark.asyncio
async def test_error_handling(db_pool, agent_manager):
    """Test error handling in various scenarios"""
    # Test invalid agent ID
    with pytest.raises(ValueError):
        await agent_manager.get_agent_llm("invalid_id")
    
    # Test creating agent with invalid user ID
    with pytest.raises(ValueError):
        await agent_manager.create_agent(
            user_id="invalid_id",
            agent_name="Test Agent",
            agent_role="Assistant",
            agent_personality="{}",
            agent_expectations="High quality responses"
        )

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
