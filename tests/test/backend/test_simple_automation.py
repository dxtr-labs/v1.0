"""
Test the streamlined automation creation system
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

async def test_simple_automation():
    """Test the simple automation creation."""
    try:
        print("🧪 Testing Simple Automation Creation")
        print("=" * 50)
        
        # Initialize database manager
        from db.postgresql_manager import DatabaseManager
        db_manager = DatabaseManager()
        await db_manager.initialize()
        print("✅ Database connected")
        
        # Create test user with unique email
        import time
        unique_email = f"test_{int(time.time())}@example.com"
        user_result = await db_manager.create_user(
            email=unique_email,
            password="password123",
            first_name="Test",
            last_name="User"
        )
        user_id = user_result["user_id"]
        print(f"✅ Created test user: {user_id}")
        
        # Create test agent
        agent_result = await db_manager.create_agent(
            user_id=user_id,
            agent_name="Test Automation Agent",
            agent_role="Email Assistant",
            agent_personality="Helpful and efficient",
            agent_expectations="Create working email automations"
        )
        agent_id = agent_result["agent_id"]
        print(f"✅ Created test agent: {agent_id}")
        
        # Initialize Custom MCP LLM with the new automation system
        from mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine
        engine = CustomMCPLLMIterationEngine(
            agent_id=agent_id,
            db_manager=db_manager
        )
        print("✅ Initialized automation engine")
        
        # Test 1: Simple email automation
        print("\n🔬 Test 1: Simple email with missing parameters")
        print("-" * 40)
        result1 = await engine.process_user_request("Send an email to notify customers")
        print(f"✅ Result: {result1.get('response', 'No response')}")
        print(f"📊 Status: {result1.get('status', 'unknown')}")
        
        # Test 2: Email with some parameters provided
        print("\n🔬 Test 2: Email with recipient provided")
        print("-" * 40)
        result2 = await engine.process_user_request("Send an email to customer@example.com about our new product launch")
        print(f"✅ Result: {result2.get('response', 'No response')}")
        print(f"📊 Status: {result2.get('status', 'unknown')}")
        
        # Test 3: Apology email request
        print("\n🔬 Test 3: Apology email automation")
        print("-" * 40)
        result3 = await engine.process_user_request("Create an apology email for John Doe at john@example.com for missing the product demo")
        print(f"✅ Result: {result3.get('response', 'No response')}")
        print(f"📊 Status: {result3.get('status', 'unknown')}")
        if result3.get('workflow'):
            print(f"🔧 Workflow created with {len(result3['workflow'].get('nodes', []))} nodes")
        
        # Test 4: Regular conversation (non-automation)
        print("\n🔬 Test 4: Regular conversation")
        print("-" * 40)
        result4 = await engine.process_user_request("How are you today?")
        print(f"✅ Result: {result4.get('response', 'No response')}")
        print(f"📊 Status: {result4.get('status', 'unknown')}")
        
        print("\n✅ Simple Automation Creation test completed!")
        
        # Clean up
        await db_manager.close()
        print("🔄 Database connection closed")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_automation())
