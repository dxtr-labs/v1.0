import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.mcp.simple_mcp_llm import MCP_LLM_Orchestrator

async def test_send_actual_email():
    """Test sending an actual email with the AI content"""
    
    orchestrator = MCP_LLM_Orchestrator()
    
    print("📧 Testing Actual Email Sending...")
    print("=" * 50)
    
    # Test sending CodeMaster email
    test_message = "service:inhouse Using AI generate a sales pitch for CodeMaster - a revolutionary IDE for developers and send to slakshanand1105@gmail.com"
    
    print(f"Request: {test_message}")
    print()
    
    try:
        result = await orchestrator.process_user_input("test_user", "test_agent", test_message)
        
        print(f"Status: {result.get('status', 'Unknown')}")
        print(f"Message: {result.get('message', 'No message')}")
        
        if result.get('workflow_preview'):
            preview = result['workflow_preview']
            print(f"\n✅ WORKFLOW DETAILS:")
            print(f"   Title: {preview.get('title', 'Unknown')}")
            print(f"   Description: {preview.get('description', 'Unknown')}")
            print(f"   Steps: {len(preview.get('steps', []))}")
            print(f"   Estimated Credits: {preview.get('estimated_credits', 'Unknown')}")
            print(f"   Recipient: {preview.get('recipient', 'Unknown')}")
            
            if preview.get('email_preview'):
                email = preview['email_preview']
                print(f"\n📧 EMAIL DETAILS:")
                print(f"   TO: {email.get('to', 'Unknown')}")
                print(f"   SUBJECT: {email.get('subject', 'Unknown')}")
                print(f"   CONTENT TYPE: {email.get('content_type', 'Unknown')}")
                print(f"   AI SERVICE: {email.get('ai_service', 'Unknown')}")
        
        # Check if workflow_json exists for actual execution
        if result.get('workflow_json'):
            workflow_json = result['workflow_json']
            print(f"\n🔧 WORKFLOW JSON:")
            print(f"   Type: {workflow_json.get('type', 'Unknown')}")
            
            # Check both possible action locations
            actions = workflow_json.get('actions', [])
            workflow_actions = workflow_json.get('workflow', {}).get('actions', [])
            
            if actions:
                print(f"   Actions (direct): {len(actions)}")
                for i, action in enumerate(actions, 1):
                    print(f"     Action {i}: {action.get('node', 'Unknown')} - {action.get('parameters', {}).get('toEmail', 'No email')}")
            
            if workflow_actions:
                print(f"   Actions (nested): {len(workflow_actions)}")
                for i, action in enumerate(workflow_actions, 1):
                    print(f"     Action {i}: {action.get('node', 'Unknown')} - {action.get('parameters', {}).get('toEmail', 'No email')}")
                    if action.get('node') == 'emailSend':
                        params = action.get('parameters', {})
                        print(f"       📧 Email To: {params.get('toEmail', 'Unknown')}")
                        print(f"       📧 Subject: {params.get('subject', 'Unknown')}")
                        print(f"       📧 Content: {params.get('text', 'Unknown')[:100]}...")
            
            print(f"   Recipient: {workflow_json.get('recipient', 'Unknown')}")
            print(f"   AI Service: {workflow_json.get('ai_service', 'Unknown')}")
        else:
            print(f"\n❌ No workflow_json found")
        
        print(f"\n📊 Full Result Keys: {list(result.keys())}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_send_actual_email())
