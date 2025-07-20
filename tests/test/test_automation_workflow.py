"""
Test the fixed automation workflow building
This should now create JSON workflows instead of just conversational responses
"""
import requests
import json

def test_automation_workflow_building():
    """Test that automation intent now builds JSON workflows"""
    
    print("🎯 TESTING AUTOMATION WORKFLOW BUILDING")
    print("=" * 50)
    
    BACKEND_URL = "http://localhost:8002"
    
    # Read the agent ID
    try:
        with open('test_agent_id.txt', 'r') as f:
            agent_id = f.read().strip()
        print(f"🤖 Using agent: {agent_id}")
    except:
        print("❌ Could not read agent ID")
        return
    
    # Test automation requests that should build JSON workflows
    automation_requests = [
        "draft a sales pitch for selling healthy ramen noodles and send email to slakshanand1105@gmail.com",
        "send an email to test@example.com about our DXTR Labs services",
        "create an email automation for slakshanand1105@gmail.com with a welcome message",
        "write and send a follow-up email to slakshanand1105@gmail.com"
    ]
    
    for i, request in enumerate(automation_requests, 1):
        print(f"\n🎯 Test {i}/4: '{request}'")
        
        try:
            # Test the NO-AUTH endpoint
            chat_response = requests.post(
                f"{BACKEND_URL}/api/test/agents/{agent_id}/chat",
                json={"message": request},
                timeout=45  # Give more time for workflow building
            )
            
            print(f"    📊 Status Code: {chat_response.status_code}")
            
            if chat_response.status_code == 200:
                result = chat_response.json()
                
                # Extract key fields
                response_text = result.get('response', '')
                success = result.get('success', False)
                status = result.get('status', 'unknown')
                workflow_status = result.get('workflow_status', 'unknown')
                has_workflow_json = result.get('hasWorkflowJson', False)
                has_workflow_preview = result.get('hasWorkflowPreview', False)
                workflow_json = result.get('workflowJson', {})
                workflow_preview = result.get('workflowPreview', {})
                
                print(f"    📤 Request: {request}")
                print(f"    📥 Response ({len(response_text)} chars): {response_text[:150]}...")
                print(f"    📊 Status: {status}")
                print(f"    🔄 Workflow Status: {workflow_status}")
                print(f"    ✅ Success: {success}")
                print(f"    📝 Has JSON: {has_workflow_json}")
                print(f"    👁  Has Preview: {has_workflow_preview}")
                
                # Analyze the results
                if has_workflow_json and workflow_json:
                    print(f"    ✅ SUCCESS: JSON WORKFLOW CREATED!")
                    print(f"        📋 Workflow ID: {workflow_json.get('workflow_id', 'N/A')}")
                    print(f"        📧 Email To: {workflow_json.get('steps', [{}])[0].get('parameters', {}).get('to', 'N/A')}")
                    print(f"        📬 Subject: {workflow_json.get('steps', [{}])[0].get('parameters', {}).get('subject', 'N/A')}")
                    print(f"        🔧 Action: {workflow_json.get('steps', [{}])[0].get('action', 'N/A')}")
                    
                elif has_workflow_preview and workflow_preview:
                    print(f"    ✅ PARTIAL SUCCESS: WORKFLOW PREVIEW CREATED!")
                    print(f"        📧 Recipient: {workflow_preview.get('recipient', 'N/A')}")
                    print(f"        📬 Subject: {workflow_preview.get('subject', 'N/A')}")
                    
                elif status == "conversational":
                    print(f"    ❌ STILL CONVERSATIONAL: Not building automation workflows!")
                    print(f"    ❌ System is still in chat mode instead of automation mode")
                    
                else:
                    print(f"    ❓ UNCLEAR: Mixed results - need investigation")
                
            else:
                print(f"    ❌ Request failed: {chat_response.status_code}")
                try:
                    error_detail = chat_response.json()
                    print(f"    ❌ Error: {json.dumps(error_detail, indent=2)}")
                except:
                    print(f"    ❌ Error: {chat_response.text}")
                
        except Exception as e:
            print(f"    ❌ Request error: {e}")
    
    print(f"\n📊 SUMMARY:")
    print(f"🎯 EXPECTED RESULTS:")
    print(f"   ✅ hasWorkflowJson: true")
    print(f"   ✅ workflowJson: {{workflow_id, steps, parameters}}")
    print(f"   ✅ status: 'preview_ready' (not 'conversational')")
    print(f"   ✅ Email parameters extracted (to, subject, body)")
    
    print(f"\n❌ FAILURE INDICATORS:")
    print(f"   ❌ status: 'conversational' (means still chatting, not automating)")
    print(f"   ❌ hasWorkflowJson: false (means no automation built)")
    print(f"   ❌ Long conversational responses without JSON workflows")

if __name__ == "__main__":
    test_automation_workflow_building()
