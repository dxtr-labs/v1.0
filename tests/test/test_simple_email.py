#!/usr/bin/env python3

# Clean simple test of email functionality
import asyncio
import sys
import os

async def test_email_simple():
    """Test email sending with minimal setup"""
    print("🧪 Simple Email Test")
    print("=" * 30)
    
    # Add backend to path
    backend_path = os.path.join(os.path.dirname(__file__), "backend")
    sys.path.insert(0, backend_path)
    
    try:
        # Load environment
        from dotenv import load_dotenv
        load_dotenv(os.path.join(backend_path, '.env.local'))
        print("✅ Environment loaded")
        
        # Test automation engine
        print("1️⃣ Testing automation engine...")
        from mcp.simple_automation_engine import AutomationEngine
        automation_engine = AutomationEngine()
        print("✅ AutomationEngine created")
        
        # Create simple email workflow
        print("2️⃣ Creating email workflow...")
        workflow_json = {
            "name": "Simple Email Test",
            "actions": [
                {
                    "action_type": "email",
                    "parameters": {
                        "to": "slakshanand1105@gmail.com",
                        "subject": "Simple Test Email",
                        "body": "This is a simple test email to verify the automation engine works.",
                        "from": "automation-engine@dxtr-labs.com"
                    }
                }
            ]
        }
        
        print("3️⃣ Executing workflow...")
        result = await automation_engine.execute_workflow(workflow_json)
        
        print("📊 Result:")
        print(f"  Status: {result.get('status', 'unknown')}")
        print(f"  Actions successful: {result.get('actions_successful', 0)}/{result.get('actions_executed', 0)}")
        print(f"  Message: {result.get('message', 'No message')}")
        
        # Check detailed results
        detailed_results = result.get('detailed_results', [])
        if detailed_results:
            for i, action_result in enumerate(detailed_results):
                action_status = action_result.get('result', {}).get('status', 'unknown')
                action_message = action_result.get('result', {}).get('message', 'No message')
                print(f"  Action {i+1}: {action_status} - {action_message}")
        
        if result.get('status') == 'completed' and result.get('actions_successful', 0) > 0:
            print("🎉 SUCCESS: Email sent!")
            return True
        else:
            print("❌ FAILED: Email not sent")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_email_simple())
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
