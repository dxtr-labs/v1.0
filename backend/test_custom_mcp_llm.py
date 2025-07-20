"""
Test script for Custom MCP LLM Iteration System
Tests the complete flow: Agent → Workflow → 3 Iterations → Database
"""

import asyncio
import sys
import os
import logging

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from db.postgresql_manager import db_manager
from mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_custom_mcp_llm_system():
    """Test the complete Custom MCP LLM iteration system"""
    
    print("🧪 Testing Custom MCP LLM Iteration System")
    print("=" * 60)
    
    try:
        # Step 1: Initialize database
        await db_manager.initialize()
        print("✅ Database connected")
        
        # Step 2: Create a test user and agent with proper UUIDs
        import uuid
        test_user_id = str(uuid.uuid4())
        
        try:
            # Create a real user for the test
            user = await db_manager.create_user(
                email=f"testuser{test_user_id[:8]}@example.com",
                password="testpass123",
                first_name="Test",
                last_name="User"
            )
            test_user_id = str(user["user_id"])
            print(f"✅ Created test user: {test_user_id}")
        except Exception as e:
            print(f"⚠️ User creation issue: {e}")
            # Use existing user or handle error
            return
        
        # Create test agent with automatic workflow creation
        agent = await db_manager.create_agent(
            user_id=test_user_id,
            agent_name="Test MCP Agent",
            agent_role="Email Automation Assistant",
            agent_personality="Friendly and helpful",
            agent_expectations="Help with email automation"
        )
        
        print(f"Debug: agent result = {agent}")
        
        if not agent:
            print("❌ Agent creation returned None")
            return
        
        agent_id = str(agent["agent_id"])
        print(f"✅ Created test agent: {agent_id}")
        print(f"   Workflow ID: {agent.get('workflow_id', 'NOT FOUND')}")
        
        # Step 3: Verify workflow was created
        workflow = await db_manager.get_workflow_by_agent(agent_id)
        if workflow:
            print(f"✅ Workflow created: {workflow['workflow_id']}")
        else:
            print("❌ No workflow found for agent")
            return
        
        # Step 4: Initialize Custom MCP LLM Iteration Engine
        iteration_engine = CustomMCPLLMIterationEngine(
            agent_id=agent_id,
            session_id="test-session-123"
        )
        
        print(f"✅ Initialized iteration engine for agent {agent_id}")
        
        # Step 5: Test the 3-iteration workflow process
        test_requests = [
            "Send a welcome email to new customers with our company information",
            "How are you today?",
            "Create an automation to send birthday emails to customers"
        ]
        
        for i, test_request in enumerate(test_requests, 1):
            print(f"\n🔬 Test {i}: {test_request}")
            print("-" * 40)
            
            result = await iteration_engine.process_user_request(test_request)
            
            if result.get("success"):
                print(f"✅ Success: {result.get('response')[:100]}...")
                
                if result.get("workflow_generated"):
                    print(f"🔧 Workflow Generated: {result.get('workflow_id')}")
                    print(f"🔄 Iterations: {result.get('iterations', 0)}")
                    print(f"📊 Status: {result.get('automation_status', 'unknown')}")
                
                if result.get("conversation_mode"):
                    print("💬 Conversation mode activated")
                    
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        
        # Step 6: Check final workflow state
        final_workflow = await db_manager.get_workflow_by_agent(agent_id)
        if final_workflow:
            script = final_workflow.get("script", {})
            print(f"\n📋 Final Workflow State:")
            print(f"   Iterations: {script.get('iterations', 0)}")
            print(f"   Nodes: {len(script.get('nodes', []))}")
            print(f"   Status: {script.get('status', 'unknown')}")
        
        print("\n✅ Custom MCP LLM Iteration System test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await db_manager.close()

if __name__ == "__main__":
    asyncio.run(test_custom_mcp_llm_system())
