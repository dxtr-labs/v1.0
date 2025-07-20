"""
Simple test for automation creation with complete parameters
"""

import asyncio
import logging
import os
import sys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_complete_automation():
    """Test automation creation with all parameters provided."""
    try:
        print("🧪 Testing Complete Automation Creation")
        print("=" * 50)
        
        # Initialize database manager
        from db.postgresql_manager import DatabaseManager
        db_manager = DatabaseManager()
        await db_manager.initialize()
        print("✅ Database connected")
        
        # Create test user
        import time
        unique_email = f"autotest_{int(time.time())}@example.com"
        user_result = await db_manager.create_user(
            email=unique_email,
            password="password123",
            first_name="Auto",
            last_name="Test"
        )
        user_id = user_result["user_id"]
        print(f"✅ Created test user: {user_id}")
        
        # Create test agent
        agent_result = await db_manager.create_agent(
            user_id=user_id,
            agent_name="Email Automation Agent",
            agent_role="Email Assistant",
            agent_personality="Professional and efficient",
            agent_expectations="Create working email automations quickly"
        )
        agent_id = agent_result["agent_id"]
        print(f"✅ Created test agent: {agent_id}")
        
        # Initialize Custom MCP LLM
        from mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine
        engine = CustomMCPLLMIterationEngine(
            agent_id=agent_id,
            db_manager=db_manager
        )
        print("✅ Initialized automation engine")
        
        # Test 1: Complete email automation
        print("\n🔬 Test 1: Complete email automation")
        print("-" * 40)
        # Test better parameter extraction
        result1 = await engine._create_simple_automation(
            'Send email to customer@example.com with subject "Welcome!" and message "Thank you for joining us!"'
        )
        print(f"✅ Status: {result1.get('status', 'unknown')}")
        print(f"📝 Response: {result1.get('response', 'No response')[:100]}...")
        if result1.get('workflow'):
            workflow = result1['workflow']
            print(f"🔧 Workflow ID: {workflow.get('id', 'N/A')}")
            print(f"📊 Nodes: {len(workflow.get('nodes', []))}")
            if workflow.get('nodes'):
                node = workflow['nodes'][0]
                print(f"📧 Email to: {node['parameters'].get('toEmail', 'N/A')}")
                print(f"📝 Subject: {node['parameters'].get('subject', 'N/A')}")
        
        # Test 2: Test the automation detection
        print("\n🔬 Test 2: Automation detection test")
        print("-" * 40)
        
        # Should detect as automation
        auto_test = engine._is_automation_request("Send email to notify customers")
        print(f"✅ 'Send email to notify customers' -> Automation: {auto_test}")
        
        # Should NOT detect as automation
        conv_test = engine._is_automation_request("How are you today?")
        print(f"✅ 'How are you today?' -> Automation: {conv_test}")
        
        conv_test2 = engine._is_automation_request("Hello, nice to meet you!")
        print(f"✅ 'Hello, nice to meet you!' -> Automation: {conv_test2}")
        
        print("\n✅ Complete Automation test finished!")
        
        # Clean up
        await db_manager.close()
        print("🔄 Database connection closed")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_automation())
