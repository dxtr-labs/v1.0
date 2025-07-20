#!/usr/bin/env python3
"""
🔍 TRACE AUTOMATION EXECUTION
Debug exactly where the automation flow is failing
"""

import asyncio
import httpx
import json
import sys
import traceback

# Test configuration
BASE_URL = "http://localhost:8002"
ENDPOINT = "/api/chat/mcpai"
AUTH_TOKEN = "test_session_token_12345"

async def test_automation_execution_trace():
    """Test the complete automation execution flow with detailed tracing"""
    
    print("🔍 AUTOMATION EXECUTION TRACE TEST")
    print("=" * 60)
    
    # Test message that we know triggers automation detection
    message = "Send email to slakshanand1105@gmail.com about our AI trends research"
    
    payload = {
        "message": message,
        "session_id": AUTH_TOKEN,
        "user_id": "test_user",
        "agent_id": "7d80df20-24a0-46b9-8257-e94804d776aa"
    }
    
    print(f"📤 Sending request: {message}")
    print(f"🎯 Target: {ENDPOINT}")
    print()
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{BASE_URL}{ENDPOINT}", json=payload)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"📄 Response Keys: {list(result.keys())}")
                print()
                
                # Check automation fields
                automation_type = result.get("automation_type", "NOT_SET")
                has_workflow = result.get("hasWorkflowJson", False)
                workflow_json = result.get("workflow_json")
                message_content = result.get("message", "")
                
                print(f"🤖 Automation Type: {automation_type}")
                print(f"📋 Has Workflow JSON: {has_workflow}")
                print(f"💬 Message: {message_content[:100]}...")
                print()
                
                if automation_type == "conversational":
                    print("❌ PROBLEM: automation_type is 'conversational' instead of 'email_automation'")
                    print("This means the automation was detected but execution failed")
                elif automation_type == "email_automation":
                    print("✅ SUCCESS: automation_type is 'email_automation'")
                    if has_workflow and workflow_json:
                        print("✅ SUCCESS: Workflow JSON is present")
                        workflow_steps = workflow_json.get("steps", [])
                        print(f"📝 Workflow steps: {len(workflow_steps)}")
                        
                        if workflow_steps:
                            first_step = workflow_steps[0]
                            recipient = first_step.get("parameters", {}).get("to", "")
                            print(f"📧 Email recipient: {recipient}")
                            
                            if recipient == "slakshanand1105@gmail.com":
                                print("✅ SUCCESS: Correct recipient detected")
                            else:
                                print(f"❌ PROBLEM: Wrong recipient '{recipient}' instead of 'slakshanand1105@gmail.com'")
                    else:
                        print("❌ PROBLEM: Missing workflow JSON")
                else:
                    print(f"❌ PROBLEM: Unexpected automation_type: {automation_type}")
                
                print()
                print("📋 FULL RESPONSE:")
                print(json.dumps(result, indent=2))
                
            else:
                print(f"❌ Request failed with status {response.status_code}")
                print(response.text)
                
    except Exception as e:
        print(f"❌ Test error: {e}")
        traceback.print_exc()

async def main():
    """Run the automation execution trace test"""
    await test_automation_execution_trace()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
