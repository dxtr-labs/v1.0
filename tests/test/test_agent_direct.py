import asyncio
import sys
import os
from pathlib import Path

# Add backend to path  
backend_path = Path(__file__).parent / 'backend'
sys.path.append(str(backend_path))

from core.agent_processor import AgentProcessor
from dotenv import load_dotenv

# Load environment
load_dotenv(Path(__file__).parent / '.env.local')

async def test_agent_response():
    """Test the agent response system directly"""
    print("🧪 Testing Agent Response System...")
    
    # Mock database pool and automation engine
    class MockDB:
        async def acquire(self):
            return self
        
        async def fetchrow(self, query, *args):
            # Mock agent data
            if "SELECT agent_id" in query:
                return {
                    'agent_id': 'test-agent',
                    'agent_name': 'testbot',
                    'agent_role': 'Personal Assistant', 
                    'agent_personality': {},
                    'agent_expectations': 'Be helpful and informative about DXTR Labs',
                    'custom_mcp_code': '',
                    'trigger_config': {},
                    'operation_mode': 'chat',
                    'created_at': None,
                    'updated_at': None
                }
            # Mock memory data
            return {
                'memory_data': {
                    'conversation_history': [],
                    'context': {'user_preferences': {}}
                },
                'updated_at': '2025-07-16'
            }
        
        async def execute(self, query, *args):
            pass
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, *args):
            pass
    
    class MockAutomationEngine:
        pass
    
    # Create processor
    processor = AgentProcessor(MockDB(), MockAutomationEngine())
    
    # Test the exact message that should trigger OpenAI
    test_message = "Hello, can you tell me about DXTR Labs?"
    
    print(f"📝 Testing message: '{test_message}'")
    
    try:
        result = await processor.process_with_agent(
            agent_id="test-agent",
            user_input=test_message,
            user_id="test-user"
        )
        
        print(f"✅ Result received: {result}")
        print(f"📊 Status: {result.get('status')}")
        print(f"💬 Message: {result.get('message', 'No message')[:200]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"📜 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_agent_response())
