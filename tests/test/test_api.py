import requests
import json

# Test the specific issue with AI-generated sales pitch
def test_ai_sales_pitch():
    base_url = "http://127.0.0.1:8002"
    
    # Test the exact request that was failing
    test_request = {
        "user_message": "Using AI generate a sales pitch for selling healthy ice creams and send to slakshanand1105@gmail.com",
        "agent_id": "b6befb30-f8c2-470b-a1fa-5326e939dbe3"  # Use actual agent ID from frontend
    }
    
    try:
        print("🧪 Testing AI Sales Pitch Request...")
        print(f"Request: {test_request['user_message']}")
        
        # First test without authentication to see the error
        response = requests.post(f"{base_url}/api/chat/mcpai", 
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ API Response:")
            print(json.dumps(result, indent=2))
        elif response.status_code == 401:
            print("❌ Authentication required - this is expected for API calls")
            print("The issue might be in the frontend processing or MCP LLM logic")
            
            # Let's test the intent analysis directly
            print("\n🔍 Testing intent analysis...")
            test_intent_analysis()
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_intent_analysis():
    """Test the intent analysis function directly"""
    try:
        # Test the intent analysis component
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        from backend.mcp.simple_mcp_llm import MCP_LLM_Orchestrator
        
        orchestrator = MCP_LLM_Orchestrator()
        
        user_message = "Using AI generate a sales pitch for selling healthy ice creams and send to slakshanand1105@gmail.com"
        
        print(f"🔍 Analyzing intent for: {user_message}")
        
        # Test intent analysis
        intent_result = orchestrator.analyze_user_intent(user_message)
        print(f"✅ Intent Analysis Result:")
        print(f"  Primary Intent: {intent_result.get('primary_intent')}")
        print(f"  Confidence: {intent_result.get('confidence')}")
        print(f"  Extracted Emails: {intent_result.get('extracted_emails')}")
        
        # Test full MCP processing 
        print(f"\n🔍 Testing full MCP processing...")
        mcp_result = orchestrator.process_user_input(
            user_id="test-user-id",
            agent_id="test-agent-id", 
            user_message=user_message
        )
        
        print(f"✅ MCP Processing Result:")
        print(f"  Status: {mcp_result.get('status')}")
        print(f"  Message: {mcp_result.get('message', 'No message')}")
        if 'workflow_json' in mcp_result:
            print(f"  Workflow Generated: Yes")
            workflow = mcp_result['workflow_json']
            print(f"    Type: {workflow.get('type')}")
            print(f"    Recipient: {workflow.get('recipient')}")
            print(f"    AI Service: {workflow.get('ai_service')}")
        else:
            print(f"  Workflow Generated: No")
            print(f"  Full Response: {json.dumps(mcp_result, indent=2)}")
        
    except Exception as e:
        print(f"❌ Intent analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_sales_pitch()
