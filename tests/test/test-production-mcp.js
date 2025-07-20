"""
Test Production Dual MCP LLM Architecture
Tests both Custom MCP LLM (database-stored per agent) and Inhouse AI (driver-based)
"""
import asyncio
import sys
import os
import logging

# Add backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from mcp.production_mcp_llm import ProductionMCPOrchestrator

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_production_architecture():
    """Test the production dual MCP architecture"""
    
    print("🚀 Testing Production Dual MCP LLM Architecture")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = ProductionMCPOrchestrator()
    
    # Test 1: System Status
    print("\n📊 Test 1: System Status")
    status = orchestrator.get_system_status()
    print(f"System: {status['system']}")
    print(f"Status: {status['status']}")
    print(f"Custom MCP LLMs - Cached Agents: {status['architecture']['custom_mcp_llms']['cached_agents']}")
    print(f"Inhouse AI Drivers: {len(status['architecture']['inhouse_ai_drivers']['driver_types'])}")
    print(f"Available Node Templates: {status['architecture']['workflow_nodes']['available_templates']}")
    
    # Test 2: Create Custom MCP LLM for Agent
    print("\n🤖 Test 2: Create Custom MCP LLM for Agent")
    agent_id = "sales_agent_001"
    agent_name = "Sales Automation Agent"
    llm_config = {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000
    }
    personality_traits = {
        "tone": "professional",
        "expertise": "sales_automation",
        "style": "consultative"
    }
    
    success = await orchestrator.create_agent_mcp(agent_id, agent_name, llm_config, personality_traits)
    print(f"✅ Custom MCP LLM created for {agent_name}: {success}")
    
    # Test 3: Process with Custom MCP LLM
    print("\n💬 Test 3: Process with Custom MCP LLM")
    user_input = "I'm interested in automating my sales process. Can you help me understand the pricing?"
    
    response = await orchestrator.process_with_custom_mcp(agent_id, user_input)
    print(f"Success: {response['success']}")
    if response['success']:
        print(f"Agent: {response['agent_name']}")
        print(f"Response: {response['response']}")
    
    # Test 4: Available Node Types
    print("\n📋 Test 4: Available Workflow Node Types")
    node_types = orchestrator.get_available_node_types()
    print("Available node types:")
    for node_type in node_types:
        template = orchestrator.get_node_template(node_type)
        driver = template.get('driver', 'unknown')
        print(f"  - {node_type} (driver: {driver})")
    
    # Test 5: Test Inhouse AI Drivers
    print("\n⚙️ Test 5: Test Inhouse AI Drivers")
    
    # Test email generation
    email_params = {
        "toEmail": "client@example.com",
        "subject": "Sales Follow-up",
        "content": "Thank you for your interest in our automation solutions.",
        "sender_name": "Sales Team"
    }
    
    email_result = await orchestrator.process_with_inhouse_ai("email_send", email_params)
    print(f"Email Send Result: {email_result['success']}")
    if email_result['success']:
        print(f"  Driver Used: {email_result['driver_used']}")
        print(f"  Node Type: {email_result['node_type']}")
    
    # Test data fetch
    data_params = {
        "url": "https://api.example.com/data",
        "method": "GET",
        "headers": {"Authorization": "Bearer token"}
    }
    
    data_result = await orchestrator.process_with_inhouse_ai("data_fetch", data_params)
    print(f"Data Fetch Result: {data_result['success']}")
    if data_result['success']:
        print(f"  Driver Used: {data_result['driver_used']}")
        print(f"  Node Type: {data_result['node_type']}")
    
    # Test 6: Create and Execute Workflow
    print("\n🔄 Test 6: Create and Execute Workflow")
    
    workflow_json = {
        "name": "Sales Follow-up Automation",
        "description": "Automated sales follow-up with data fetch and email",
        "nodes": [
            {
                "id": "fetch_client_data",
                "type": "data_fetch",
                "parameters": {
                    "url": "https://crm.example.com/api/client/{{client_id}}",
                    "method": "GET",
                    "headers": {"Authorization": "Bearer {{api_token}}"}
                }
            },
            {
                "id": "generate_email",
                "type": "ai_content_generation",
                "parameters": {
                    "prompt": "Generate personalized follow-up email based on client data",
                    "content_type": "email",
                    "style": "professional"
                }
            },
            {
                "id": "send_email",
                "type": "email_send",
                "parameters": {
                    "toEmail": "{{client_email}}",
                    "subject": "Following up on your automation needs",
                    "content": "{{generated_content}}",
                    "sender_name": "Sales Team"
                }
            }
        ]
    }
    
    trigger_config = {
        "type": "webhook",
        "endpoint": "/api/triggers/sales-followup",
        "method": "POST"
    }
    
    workflow_id = await orchestrator.create_workflow(agent_id, workflow_json, trigger_config)
    print(f"✅ Workflow created: {workflow_id}")
    
    # Execute the workflow
    input_data = {
        "client_id": "12345",
        "api_token": "sample_token",
        "client_email": "client@example.com"
    }
    
    execution_result = await orchestrator.execute_workflow(workflow_id, input_data)
    print(f"Workflow Execution Success: {execution_result['success']}")
    if execution_result['success']:
        print(f"  Completed Nodes: {len(execution_result['execution_results'])}")
        for i, result in enumerate(execution_result['execution_results']):
            print(f"    Node {i+1}: {result['node_type']} - {result['success']}")
    
    # Test 7: Load Agent MCP from Database
    print("\n💾 Test 7: Load Agent MCP from Database")
    loaded_agent = await orchestrator.get_agent_mcp(agent_id)
    if loaded_agent:
        print(f"✅ Loaded agent: {loaded_agent['agent_name']}")
        print(f"  Memory entries: {len(loaded_agent['memory_context'])}")
        print(f"  Personality: {loaded_agent['personality_traits']}")
    else:
        print("❌ Failed to load agent from database")
    
    print("\n" + "=" * 60)
    print("🎉 Production Dual MCP Architecture Test Complete!")
    
    return {
        "custom_mcp_test": response['success'] if 'response' in locals() else False,
        "inhouse_ai_test": email_result['success'] and data_result['success'],
        "workflow_test": execution_result['success'] if 'execution_result' in locals() else False,
        "database_test": loaded_agent is not None
    }

if __name__ == "__main__":
    asyncio.run(test_production_architecture())
