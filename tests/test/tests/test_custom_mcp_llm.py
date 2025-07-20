import pytest
import json
import uuid
from unittest.mock import Mock, patch
from typing import Dict, Any

from mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine

@pytest.fixture
def db_manager():
    # Create mock db_manager
    db = Mock()
    db.pool = Mock()
    
    # Set up mock connection
    mock_conn = Mock()
    mock_conn.fetchrow = Mock()
    mock_conn.execute = Mock()
    
    # Set up agent context
    mock_agent_row = {
        "agent_name": "Test Agent",
        "agent_role": "Assistant",
        "agent_personality": json.dumps({"trait": "helpful"}),
        "agent_expectations": "High quality responses",
        "workflow_id": str(uuid.uuid4()),
        "trigger_config": None,
        "custom_mcp_code": None
    }
    mock_conn.fetchrow.return_value = mock_agent_row
    
    # Make acquire return the mock connection
    async def mock_acquire():
        return mock_conn
    db.pool.acquire.return_value = mock_acquire()
    
    return db

@pytest.fixture
def llm_engine(db_manager):
    agent_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    
    return CustomMCPLLMIterationEngine(
        agent_id=agent_id,
        session_id=session_id,
        db_manager=db_manager
    )

@pytest.mark.asyncio
async def test_process_user_request(llm_engine):
    """Test basic request processing"""
    response = await llm_engine.process_user_request("Hello")
    
    assert response is not None
    assert response.get("success") is True
    assert "response" in response

@pytest.mark.asyncio
async def test_automation_intent_analysis(llm_engine):
    """Test automation intent detection"""
    request = "Create an email workflow to send daily reports to test@example.com"
    response = await llm_engine._analyze_automation_intent(request)
    
    assert response is not None
    assert response.get("is_automation") is True
    assert response.get("automation_type") == "content_email"
    assert response.get("confidence", 0.0) > 0.5

@pytest.mark.asyncio
async def test_workflow_building(llm_engine):
    """Test workflow construction"""
    current_workflow = {
        "workflow_id": str(uuid.uuid4()),
        "script": {
            "nodes": [
                {
                    "id": "trigger_node_1",
                    "type": "manual_trigger",
                    "parameters": {
                        "agent_id": llm_engine.agent_id,
                        "trigger_type": "manual"
                    }
                }
            ],
            "edges": []
        }
    }
    
    analysis_result = {
        "proposed_nodes": [
            {
                "id": "email_node_1",
                "type": "email_send",
                "parameters": {
                    "to_email": "test@example.com",
                    "subject": "Daily Report",
                    "body": "Test report content"
                }
            }
        ],
        "workflow_description": "Email sending workflow"
    }
    
    user_input = "Send daily report"
    
    workflow = await llm_engine._build_complete_workflow(
        current_workflow,
        analysis_result,
        user_input
    )
    
    assert workflow is not None
    assert "nodes" in workflow
    assert len(workflow["nodes"]) == 2  # trigger + email node
    assert len(workflow["edges"]) == 1  # connecting the nodes

@pytest.mark.asyncio
async def test_parameter_handling(llm_engine):
    """Test parameter collection and completion"""
    # Test missing parameters detection
    missing_parameters = [
        {
            "name": "to_email",
            "description": "Email address to send to",
            "type": "email",
            "required": True
        }
    ]
    
    partial_workflow = [
        {
            "id": "email_node_1",
            "type": "email_send",
            "parameters": {
                "to_email": "{{to_email}}",
                "subject": "Test Subject",
                "body": "Test Body"
            }
        }
    ]
    
    user_input = "Send to test@example.com"
    
    response = await llm_engine.handle_parameter_collection(
        user_input,
        missing_parameters,
        partial_workflow
    )
    
    assert response.get("success") is True
    assert response.get("status") == "completed"
    assert "workflow" in response

@pytest.mark.asyncio
async def test_ultra_fast_automation(llm_engine):
    """Test the ultra-fast automation path"""
    response = await llm_engine._create_ultra_fast_automation(
        "Quick reply to test@example.com"
    )
    
    assert response is not None
    assert response.get("ultra_fast") is True
    assert response.get("processing_time", "") == "< 1ms"

@pytest.mark.asyncio
async def test_content_topic_extraction(llm_engine):
    """Test content topic extraction"""
    topics = [
        ("Create a sales pitch for ice cream", "sales pitch"),
        ("Write a business proposal", "proposal"),
        ("Generate a financial report", "report"),
        ("Draft a marketing plan", "marketing")
    ]
    
    for input_text, expected_topic in topics:
        topic = llm_engine._extract_content_topic(input_text)
        assert expected_topic in topic.lower()

@pytest.mark.asyncio
async def test_workflow_conversion(llm_engine):
    """Test workflow format conversion for automation engine"""
    workflow_data = {
        "workflow_id": str(uuid.uuid4()),
        "nodes": [
            {
                "id": "node_1",
                "type": "email_send",
                "parameters": {
                    "to_email": "test@example.com",
                    "subject": "Test",
                    "body": "Test"
                }
            }
        ],
        "edges": []
    }
    
    converted = await llm_engine._convert_workflow_for_engine(workflow_data)
    
    assert converted is not None
    assert converted["workflow_id"] == workflow_data["workflow_id"]
    assert len(converted["nodes"]) == len(workflow_data["nodes"])

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
