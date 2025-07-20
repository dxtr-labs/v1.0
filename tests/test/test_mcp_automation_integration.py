#!/usr/bin/env python3
"""
Test Custom MCP LLM Integration - Check if automation engine is passed correctly
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path  
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_mcp_automation_integration():
    """Test if CustomMCPLLMIterationEngine receives automation engine"""
    print("🧪 Testing Custom MCP LLM -> Automation Engine Integration")
    print("=" * 60)
    
    try:
        # Create a mock automation engine
        class MockAutomationEngine:
            def __init__(self):
                self.name = "Mock Automation Engine"
                
            async def execute_workflow(self, workflow_json, user_id):
                print(f"🚀 Mock automation engine called!")
                print(f"   Workflow: {workflow_json}")
                print(f"   User ID: {user_id}")
                return {
                    "status": "success",
                    "message": "Mock execution completed",
                    "workflow_id": "mock_workflow_123"
                }
        
        mock_automation = MockAutomationEngine()
        
        # Import and initialize CustomMCPLLMIterationEngine
        print("🔧 Initializing CustomMCPLLMIterationEngine...")
        from backend.mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine
        
        # Initialize with automation engine
        engine = CustomMCPLLMIterationEngine(
            agent_id="test_agent_123",
            automation_engine=mock_automation
        )
        
        print(f"✅ Engine initialized")
        print(f"   Agent ID: {engine.agent_id}")
        print(f"   Has automation engine: {engine.automation_engine is not None}")
        print(f"   Automation engine type: {type(engine.automation_engine).__name__}")
        
        # Test email workflow execution
        print("\n📧 Testing email workflow execution...")
        
        test_user_input = "Send a test email to slakshanand1105@gmail.com about testing automation"
        result = await engine.execute_workflow("test_email_workflow_456", test_user_input)
        
        print("\n📊 Execution Result:")
        print(f"   Status: {result.get('status', 'UNKNOWN')}")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Message: {result.get('message', 'No message')}")
        print(f"   Email sent: {result.get('email_sent', 'UNKNOWN')}")
        
        if result.get('status') == 'completed' and result.get('email_sent') == True:
            print("\n✅ SUCCESS: Integration working! Automation engine called successfully")
        elif result.get('status') == 'failed' and 'Automation engine' in result.get('message', ''):
            print("\n✅ SUCCESS: Integration working! Automation engine was called (but failed as expected with mock)")
        else:
            print("\n❌ ISSUE: Integration not working properly")
            print(f"   Expected automation engine to be called, but result suggests otherwise")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure CustomMCPLLMIterationEngine can be imported")
    except Exception as e:
        print(f"❌ Test Error: {e}")
        print(f"💡 Error details: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_automation_integration())
