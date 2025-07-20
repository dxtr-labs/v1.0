import requests
import json
import asyncio

def test_real_email_sending():
    """Test the actual email sending using the correct MCP endpoint"""
    
    base_url = "http://127.0.0.1:8002"
    
    # You'll need to get a real session token and agent ID from the frontend
    # For now, let's try with the agent ID you mentioned
    agent_id = "b6befb30-f8c2-470b-a1fa-5326e939dbe3"
    
    test_request = {
        "message": "service:inhouse Using AI generate a sales pitch for CodeMaster - a revolutionary IDE for developers and send to slakshanand1105@gmail.com"
    }
    
    # Test headers (you'll need a real auth token)
    headers = {
        "Content-Type": "application/json",
        # "Authorization": "Bearer YOUR_TOKEN_HERE",  # You'll need to add this
        # Or session cookie if using sessions
    }
    
    try:
        print("🧪 Testing Real Email Sending...")
        print(f"Request: {test_request['message']}")
        print(f"Agent ID: {agent_id}")
        
        # Use the correct MCP endpoint
        response = requests.post(
            f"{base_url}/api/ai/chat/{agent_id}", 
            json=test_request,
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Response:")
            print(json.dumps(result, indent=2))
            
            if result.get('workflow_json'):
                print("\n🔧 WORKFLOW DETECTED!")
                workflow = result['workflow_json']
                if 'workflow' in workflow and 'actions' in workflow['workflow']:
                    actions = workflow['workflow']['actions']
                    print(f"📧 Found {len(actions)} actions:")
                    for i, action in enumerate(actions, 1):
                        print(f"  Action {i}: {action.get('node', 'Unknown')}")
                        if action.get('node') == 'emailSend':
                            params = action.get('parameters', {})
                            print(f"    📧 TO: {params.get('toEmail', 'Unknown')}")
                            print(f"    📧 SUBJECT: {params.get('subject', 'Unknown')}")
        
        elif response.status_code == 401:
            print("❌ Authentication required")
            print("You need to:")
            print("1. Login to the frontend first")
            print("2. Get your session token/cookie")
            print("3. Add it to the request headers")
            print("\nFor now, let's try the direct MCP test...")
            
            # Fallback to direct MCP test
            test_direct_mcp()
            
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        test_direct_mcp()

def test_direct_mcp():
    """Test MCP directly without going through the API"""
    print("\n" + "="*50)
    print("🔧 Testing Direct MCP Execution...")
    
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
    
    from backend.mcp.simple_mcp_llm import MCP_LLM_Orchestrator
    
    async def run_mcp_test():
        orchestrator = MCP_LLM_Orchestrator()
        
        user_message = "service:inhouse Using AI generate a sales pitch for CodeMaster - a revolutionary IDE for developers and send to slakshanand1105@gmail.com"
        
        result = await orchestrator.process_user_input("test_user", "test_agent", user_message)
        
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message')}")
        
        # Check if we can execute the workflow directly
        if result.get('workflow_json'):
            workflow_json = result['workflow_json']
            print("\n🚀 EXECUTING WORKFLOW DIRECTLY...")
            
            # Try to execute the email action directly
            if 'workflow' in workflow_json and 'actions' in workflow_json['workflow']:
                actions = workflow_json['workflow']['actions']
                
                for action in actions:
                    if action.get('node') == 'emailSend':
                        print(f"📧 Executing email action...")
                        
                        # Import and execute the email driver directly
                        from backend.mcp.drivers.email_send_driver import EmailSendDriver
                        
                        email_driver = EmailSendDriver()
                        email_params = action.get('parameters', {})
                        
                        # Set environment variables for email sending
                        os.environ['SMTP_HOST'] = 'mail.privateemail.com'
                        os.environ['SMTP_USER'] = 'suguavaneshwaran@dxtrlabs.com'
                        os.environ['SMTP_PASSWORD'] = 'P@ssw0rd2025'
                        
                        print(f"Email TO: {email_params.get('toEmail')}")
                        print(f"Email SUBJECT: {email_params.get('subject')}")
                        
                        try:
                            # Execute the email sending
                            email_result = await email_driver.execute(
                                parameters=email_params,
                                input_data={},
                                user_id="test_user"
                            )
                            
                            print(f"📧 EMAIL RESULT: {email_result}")
                            
                            if email_result.get('status') == 'success':
                                print("✅ EMAIL SENT SUCCESSFULLY!")
                            else:
                                print(f"❌ EMAIL FAILED: {email_result.get('error')}")
                                
                        except Exception as e:
                            print(f"❌ Email execution failed: {e}")
                            import traceback
                            traceback.print_exc()
    
    # Run the async test
    asyncio.run(run_mcp_test())

if __name__ == "__main__":
    test_real_email_sending()
