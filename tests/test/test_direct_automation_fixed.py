#!/usr/bin/env python3
"""
🔍 DIRECT AUTOMATION TEST
Test the automation execution directly without HTTP layer
"""

import asyncio
import sys
import os
import traceback

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_direct_automation():
    """Test automation execution directly"""
    
    print("🔍 DIRECT AUTOMATION TEST")
    print("=" * 60)
    
    try:
        # Import the engine
        from mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine
        
        # Initialize the engine
        engine = CustomMCPLLMIterationEngine({
            'agent_name': 'Test Agent',
            'agent_id': 'test_agent',
            'company': 'DXTR Labs'
        })
        
        # Test message that should trigger automation
        message = "Send email to slakshanand1105@gmail.com about our AI trends research"
        
        print(f"📤 Processing message: {message}")
        print()
        
        # Process the request
        result = await engine.process_user_request(message)
        
        print("📋 RESULT:")
        print(f"Type: {type(result)}")
        print(f"Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict):
            automation_type = result.get("automation_type", "NOT_SET")
            has_workflow = result.get("hasWorkflowJson", False)
            message_content = result.get("message", "")
            
            print(f"🤖 Automation Type: {automation_type}")
            print(f"📋 Has Workflow JSON: {has_workflow}")
            print(f"💬 Message: {message_content[:100]}...")
            
            if automation_type == "conversational":
                print("❌ PROBLEM: automation_type is 'conversational' - check logs for execution failure")
            elif automation_type == "email_automation":
                print("✅ SUCCESS: automation_type is 'email_automation'")
                if has_workflow:
                    print("✅ SUCCESS: Workflow JSON is present")
                else:
                    print("❌ PROBLEM: Missing workflow JSON")
            else:
                print(f"❌ PROBLEM: Unexpected automation_type: {automation_type}")
        
        print()
        print("📝 FULL RESULT:")
        print(result)
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        traceback.print_exc()

async def main():
    """Run the direct automation test"""
    await test_direct_automation()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
