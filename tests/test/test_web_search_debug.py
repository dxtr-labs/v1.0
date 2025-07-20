#!/usr/bin/env python3
"""
🔍 DETAILED WEB SEARCH DEBUG TEST
Debug what's happening in the automation detection
"""

import requests
import json

def test_web_search_debug():
    """Debug web search automation detection"""
    base_url = "http://localhost:8002/api"
    
    print("🔍 WEB SEARCH DEBUG TEST")
    print("=" * 50)
    
    # Authenticate
    login_response = requests.post(f"{base_url}/auth/login", json={
        "email": "aitest@example.com", 
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    print("✅ Authentication successful")
    
    # Test multiple search variations
    search_queries = [
        "search top 10 investors interested in ramen bowl companies",
        "find information about AI startups in healthcare",
        "look up recent trends in automation software",
        "research competitors in the protein noodle market"
    ]
    
    for i, query in enumerate(search_queries, 1):
        print(f"\n{i}️⃣ TESTING: '{query}'")
        print("-" * 60)
        
        try:
            response = requests.post(
                f"{base_url}/chat/mcpai",
                json={"message": query},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Status: {response.status_code}")
                print(f"📋 Full Response Keys: {list(data.keys())}")
                print(f"📋 Success: {data.get('success')}")
                print(f"📋 Status: {data.get('status')}")
                print(f"📋 Automation Type: {data.get('automation_type')}")
                print(f"📋 Has Workflow JSON: {data.get('hasWorkflowJson')}")
                print(f"📋 Has Search Results: {data.get('hasSearchResults')}")
                print(f"📋 Done: {data.get('done')}")
                
                # Show response text
                response_text = data.get('response', '')
                print(f"📝 Response Length: {len(response_text)}")
                print(f"📝 Response Preview: {response_text[:200]}...")
                
                # Check for web search indicators
                if data.get('automation_type') == 'web_search':
                    print("🎯 ✅ WEB SEARCH CORRECTLY DETECTED!")
                elif 'search' in response_text.lower():
                    print("🎯 ⚠️ Response mentions search but type is wrong")
                else:
                    print("🎯 ❌ Web search not detected at all")
                
                # Check workflow JSON if present
                workflow_json = data.get('workflow_json')
                if workflow_json:
                    print(f"📊 Workflow Type: {workflow_json.get('workflow_type')}")
                    print(f"📊 Workflow Status: {workflow_json.get('status')}")
                
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
    
    print("🏁 DEBUG TEST COMPLETE")

if __name__ == "__main__":
    test_web_search_debug()
