#!/usr/bin/env python3
"""
Test the complete web search + email workflow through the MCP API
"""
import requests
import json

def test_web_search_workflow():
    """Test the web search automation workflow"""
    
    # Test request - same as what Sam tried
    test_request = "find top 10 ai investors email from web and send that list to slakshanand1105@gmail.com"
    
    print("🚀 Testing Web Search + Email Workflow")
    print(f"📝 Request: {test_request}")
    
    try:
        # Send request to the MCP endpoint
        response = requests.post(
            "http://localhost:8002/api/mcp/chat",
            json={
                "message": test_request,
                "service": "inhouse"  # Use inhouse AI service
            },
            timeout=30
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Request successful!")
            print(f"📋 Response: {json.dumps(result, indent=2)}")
            
            # Check if it's a workflow preview (what we expect)
            if result.get("hasWorkflowPreview"):
                print("🎯 ✅ Web search workflow preview generated successfully!")
                preview = result.get("workflow_preview", {})
                if preview.get("email_preview"):
                    email_preview = preview["email_preview"]
                    print(f"📧 Email Preview:")
                    print(f"   To: {email_preview.get('to', 'N/A')}")
                    print(f"   Subject: {email_preview.get('subject', 'N/A')}")
                    print(f"   Search Results Count: {email_preview.get('search_results_count', 0)}")
                    print("🎉 WEB SEARCH INTEGRATION WORKING!")
                else:
                    print("⚠️ Email preview not found in workflow")
            else:
                print("⚠️ No workflow preview found - might be generic response")
                
        else:
            print(f"❌ Request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_simple_chat():
    """Test a simple chat to verify API is working"""
    print("\n🔧 Testing basic API connectivity...")
    
    try:
        response = requests.post(
            "http://localhost:8002/api/mcp/chat",
            json={
                "message": "Hello, are you working?",
                "service": "inhouse"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Basic API connectivity working")
            return True
        else:
            print(f"❌ Basic API test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Basic API test failed: {e}")
        return False

if __name__ == "__main__":
    # First test basic connectivity
    if test_simple_chat():
        print("\n" + "="*50)
        # Then test the web search workflow
        test_web_search_workflow()
    else:
        print("❌ Skipping web search test due to API connectivity issues")
