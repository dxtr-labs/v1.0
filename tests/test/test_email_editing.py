"""
Test the complete email workflow with editing functionality
"""
import requests
import json
import time

def test_email_workflow_with_editing():
    """Test email creation and editing"""
    
    print("🎯 TESTING EMAIL WORKFLOW WITH EDITING")
    print("=" * 50)
    
    BACKEND_URL = "http://localhost:8002"
    
    # Read agent ID
    with open('test_agent_id.txt', 'r') as f:
        agent_id = f.read().strip()
    
    print(f"🤖 Using agent: {agent_id}")
    
    # Step 1: Create initial email workflow
    print(f"\n📧 STEP 1: Creating initial email workflow...")
    initial_request = "draft a sales pitch for selling healthy ramen noodles and send email to slakshanand1105@gmail.com"
    
    response1 = requests.post(
        f"{BACKEND_URL}/api/test/agents/{agent_id}/chat",
        json={"message": initial_request},
        timeout=30
    )
    
    if response1.status_code == 200:
        result1 = response1.json()
        print(f"✅ Initial workflow created")
        print(f"   Status: {result1.get('status')}")
        print(f"   Has JSON: {result1.get('hasWorkflowJson')}")
        print(f"   Response preview: {result1.get('response', '')[:100]}...")
        
        # Check if it mentions DXTR Labs (should be corrected to HOTPOT inc)
        if "DXTR Labs" in result1.get('response', ''):
            print(f"   🎯 Found 'DXTR Labs' - ready for company correction")
        
        # Small delay to ensure workflow is stored
        time.sleep(1)
        
        # Step 2: Edit the company name
        print(f"\n🔄 STEP 2: Editing company name...")
        edit_request = "company name is HOTPOT inc"
        
        response2 = requests.post(
            f"{BACKEND_URL}/api/test/agents/{agent_id}/chat",
            json={"message": edit_request},
            timeout=30
        )
        
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"✅ Edit response received")
            print(f"   Status: {result2.get('status')}")
            print(f"   Has JSON: {result2.get('hasWorkflowJson')}")
            print(f"   Changes applied: {result2.get('changes_applied', 'None')}")
            print(f"   Response preview: {result2.get('response', '')[:150]}...")
            
            # Check if DXTR Labs was replaced with HOTPOT inc
            response_text = result2.get('response', '')
            if "HOTPOT inc" in response_text:
                print(f"   ✅ SUCCESS: Company name updated to HOTPOT inc!")
            elif "DXTR Labs" in response_text:
                print(f"   ❌ FAILED: Still shows DXTR Labs instead of HOTPOT inc")
            else:
                print(f"   ❓ UNCLEAR: Company name status unclear")
                
            # Check the JSON workflow
            workflow_json = result2.get('workflowJson', {})
            if workflow_json:
                email_body = workflow_json.get('steps', [{}])[0].get('parameters', {}).get('body', '')
                if "HOTPOT inc" in email_body:
                    print(f"   ✅ JSON WORKFLOW UPDATED: Email body contains HOTPOT inc")
                else:
                    print(f"   ❌ JSON WORKFLOW NOT UPDATED: Email body still has old company")
        else:
            print(f"❌ Edit request failed: {response2.status_code}")
            print(f"   Error: {response2.text}")
    else:
        print(f"❌ Initial request failed: {response1.status_code}")
        print(f"   Error: {response1.text}")
    
    print(f"\n📊 EXPECTED BEHAVIOR:")
    print(f"   1. Initial email should mention 'DXTR Labs'")
    print(f"   2. Edit request should detect company name change")
    print(f"   3. Updated email should replace 'DXTR Labs' with 'HOTPOT inc'")
    print(f"   4. Both response text and JSON workflow should be updated")

if __name__ == "__main__":
    test_email_workflow_with_editing()
