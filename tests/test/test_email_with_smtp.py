import requests
import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables to test them
load_dotenv('.env.local')

def test_environment_variables():
    """Test that SMTP environment variables are loaded correctly"""
    print("🔍 Testing Environment Variables...")
    
    required_vars = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD"]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var == "SMTP_PASSWORD":
                print(f"✅ {var}: ***{value[-4:]} (password masked)")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not found")
    
    return all(os.getenv(var) for var in required_vars)

def test_complete_email_workflow():
    """Test the complete email workflow with AI content generation"""
    base_url = "http://127.0.0.1:8002"
    
    # Test data for Roomify business
    test_request = {
        "user_message": "service:inhouse Using AI generate a sales pitch for roomify- one stop place for college students to find roommates and send to slakshanand1105@gmail.com",
        "agent_id": "test-agent-123"
    }
    
    print("\n🧪 Testing Complete Email Workflow...")
    print(f"Request: {test_request['user_message']}")
    
    try:
        # Step 1: Generate AI workflow
        print("\n📝 Step 1: Generating AI workflow...")
        response = requests.post(
            f"{base_url}/api/ai/chat/test-agent-123",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Workflow generated successfully!")
            
            # Check if workflow was created
            if "workflow_json" in result:
                workflow = result["workflow_json"]
                print(f"📋 Workflow Details:")
                print(f"  - Type: {workflow.get('type')}")
                print(f"  - Recipient: {workflow.get('recipient')}")
                print(f"  - AI Service: {workflow.get('ai_service')}")
                print(f"  - Actions: {len(workflow.get('actions', []))}")
                
                # Display email content preview
                for i, action in enumerate(workflow.get('actions', [])):
                    if action.get('action_type') == 'emailSend':
                        print(f"\n📧 Email Preview (Action {i+1}):")
                        print(f"  - To: {action.get('parameters', {}).get('toEmail')}")
                        print(f"  - Subject: {action.get('parameters', {}).get('subject', 'AI-Generated Content')}")
                        content = action.get('parameters', {}).get('text', '')
                        print(f"  - Content: {content[:200]}..." if len(content) > 200 else f"  - Content: {content}")
                
                # Step 2: Execute the workflow
                print(f"\n🚀 Step 2: Executing workflow...")
                execution_request = {
                    "workflow_json": workflow,
                    "user_id": "test-user-123"
                }
                
                execution_response = requests.post(
                    f"{base_url}/api/execute-automation-workflow",
                    json=execution_request,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"Execution Status Code: {execution_response.status_code}")
                
                if execution_response.status_code == 200:
                    execution_result = execution_response.json()
                    print("✅ Workflow executed successfully!")
                    print(f"📊 Execution Results:")
                    
                    # Check execution details
                    for i, result in enumerate(execution_result.get("results", [])):
                        print(f"  Action {i+1}: {result.get('status', 'unknown')}")
                        if result.get('status') == 'success':
                            print(f"    ✅ {result.get('message', 'No message')}")
                        elif result.get('status') == 'failed':
                            print(f"    ❌ Error: {result.get('error', 'Unknown error')}")
                    
                    # Check overall status
                    if execution_result.get("status") == "completed":
                        print("\n🎉 EMAIL DELIVERY SUCCESSFUL!")
                        print("Check slakshanand1105@gmail.com for the Roomify sales pitch!")
                    else:
                        print(f"\n⚠️ Workflow Status: {execution_result.get('status')}")
                        print("Email may not have been delivered. Check logs for details.")
                
                else:
                    print(f"❌ Execution failed: {execution_response.text}")
                    
            else:
                print("❌ No workflow generated in response")
                print(f"Response: {json.dumps(result, indent=2)}")
        
        elif response.status_code == 401:
            print("❌ Authentication required - testing with direct backend access...")
            test_direct_backend()
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        import traceback
        traceback.print_exc()

def test_direct_backend():
    """Test direct backend access to the MCP system"""
    try:
        print("\n🔧 Testing Direct Backend Access...")
        
        # Add backend to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        from backend.mcp.simple_mcp_llm import MCP_LLM_Orchestrator
        
        orchestrator = MCP_LLM_Orchestrator()
        
        user_message = "service:inhouse Using AI generate a sales pitch for roomify- one stop place for college students to find roommates and send to slakshanand1105@gmail.com"
        
        print(f"🔍 Processing: {user_message}")
        
        import asyncio
        
        async def run_mcp_test():
            # Process with MCP orchestrator
            result = await orchestrator.process_user_input(
                user_id="test-user-direct",
                agent_id="test-agent-direct",
                user_message=user_message
            )
            
            print(f"✅ Direct Processing Result:")
            print(f"  Status: {result.get('status')}")
            print(f"  Message: {result.get('message', 'No message')}")
            
            if 'workflow_json' in result:
                workflow = result['workflow_json']
                print(f"  📋 Workflow Generated:")
                print(f"    Type: {workflow.get('type')}")
                print(f"    Recipient: {workflow.get('recipient')}")
                print(f"    Actions: {len(workflow.get('actions', []))}")
                
                # Test email driver directly
                print(f"\n📧 Testing Email Driver Directly...")
                from backend.mcp.drivers.email_send_driver import EmailSendDriver
                
                email_driver = EmailSendDriver()
                
                # Find email action in workflow
                for action in workflow.get('actions', []):
                    if action.get('action_type') == 'emailSend':
                        email_params = action.get('parameters', {})
                        
                        print(f"📧 Email Parameters:")
                        print(f"  To: {email_params.get('toEmail')}")
                        print(f"  Subject: {email_params.get('subject')}")
                        content = email_params.get('text', '')
                        print(f"  Content Length: {len(content)} characters")
                        print(f"  Content Preview: {content[:150]}...")
                        
                        # Execute email directly
                        email_result = await email_driver.execute(
                            parameters=email_params,
                            input_data={},
                            user_id="test-user-direct"
                        )
                        
                        print(f"\n📧 Email Delivery Result:")
                        print(f"  Status: {email_result.get('status')}")
                        if email_result.get('status') == 'success':
                            print(f"  ✅ {email_result.get('message')}")
                            print(f"  Recipients: {email_result.get('recipients')}")
                            print(f"  Subject: {email_result.get('subject')}")
                            print(f"\n🎉 EMAIL SUCCESSFULLY SENT!")
                            print(f"Check slakshanand1105@gmail.com for the Roomify sales pitch!")
                        else:
                            print(f"  ❌ Error: {email_result.get('error')}")
                        
                        break
            else:
                print(f"  ❌ No workflow generated")
                print(f"  Full response: {json.dumps(result, indent=2)}")
        
        # Run the async test
        asyncio.run(run_mcp_test())
        
    except Exception as e:
        print(f"❌ Direct backend test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🚀 SMTP Email Configuration Test")
    print("=" * 50)
    
    # Test 1: Environment variables
    env_ok = test_environment_variables()
    
    if not env_ok:
        print("\n❌ Environment variables not configured correctly!")
        print("Please check .env.local file for SMTP settings.")
        return
    
    # Test 2: Complete workflow
    test_complete_email_workflow()

if __name__ == "__main__":
    main()
