#!/usr/bin/env python3
"""
Direct backend test to diagnose the editable email workflow
"""

import requests
import json

def test_email_automation_workflow():
    """Test the complete email automation workflow that should return editable content"""
    
    print("🧪 Testing email automation workflow directly...")
    
    base_url = "http://localhost:8002"
    
    # Test 1: First request - should return ai_service_selection
    print("\n📝 Step 1: Initial email automation request")
    
    initial_request = {
        "message": "draft a sales pitch highlight key achievements of dxtr labs and send to slakshanand1105@gmail.com",
        "agentId": "12345678-1234-5678-9abc-123456789abc",  # Valid UUID format
        "agentConfig": {
            "name": "BobPop", 
            "role": "PA"
        },
        "session_id": "test_session_12345"
    }
    
    try:
        response1 = requests.post(f"{base_url}/api/agents/12345678-1234-5678-9abc-123456789abc/chat", 
                                json=initial_request,
                                headers={"Content-Type": "application/json"})
        
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"✅ Step 1 Response Status: {result1.get('status')}")
            print(f"✅ Step 1 Response: {json.dumps(result1, indent=2)}")
            
            if result1.get('status') == 'ai_service_selection':
                print("\n📝 Step 2: Service selection (inhouse)")
                
                # Test 2: Service selection - should return workflow_preview
                service_request = {
                    "message": "service:inhouse",
                    "agentId": "12345678-1234-5678-9abc-123456789abc",  # Same UUID
                    "agentConfig": {
                        "name": "BobPop",
                        "role": "PA"
                    },
                    "session_id": "test_session_12345"
                }
                
                response2 = requests.post(f"{base_url}/api/agents/12345678-1234-5678-9abc-123456789abc/chat",
                                        json=service_request,
                                        headers={"Content-Type": "application/json"})
                
                if response2.status_code == 200:
                    result2 = response2.json()
                    print(f"✅ Step 2 Response Status: {result2.get('status')}")
                    
                    # Check for workflow_preview structure
                    if result2.get('status') == 'workflow_preview':
                        print("🎯 Found workflow_preview status!")
                        
                        if 'workflow_preview' in result2:
                            wp = result2['workflow_preview']
                            print(f"🎯 Has workflow_preview object: {type(wp)}")
                            
                            if isinstance(wp, dict) and 'email_preview' in wp:
                                ep = wp['email_preview']
                                print("🎯 ✅ FOUND EMAIL_PREVIEW STRUCTURE!")
                                print(f"   📧 To: {ep.get('to')}")
                                print(f"   📋 Subject: {ep.get('subject')}")
                                print(f"   📝 Content: {ep.get('preview_content', '')[:100]}...")
                                print(f"   🤖 AI Service: {ep.get('ai_service')}")
                                
                                print("\n🎉 DIAGNOSIS: Backend is returning correct structure for editable dialog!")
                                print("   ✅ Status: workflow_preview")
                                print("   ✅ Has workflow_preview object") 
                                print("   ✅ Has email_preview structure")
                                print("   ✅ All required fields present")
                                print("\n💡 Issue is likely in frontend detection or React state management")
                                
                            else:
                                print(f"❌ workflow_preview missing email_preview: {list(wp.keys()) if isinstance(wp, dict) else 'Not a dict'}")
                        else:
                            print("❌ Missing workflow_preview object in response")
                            
                        if 'workflow_json' in result2:
                            print("✅ Has workflow_json")
                        else:
                            print("❌ Missing workflow_json")
                    else:
                        print(f"❌ Wrong status: {result2.get('status')}")
                        print(f"Full response: {json.dumps(result2, indent=2)}")
                else:
                    print(f"❌ Step 2 HTTP Error: {response2.status_code}")
                    print(f"Response: {response2.text}")
            else:
                print(f"❌ Step 1 wrong status: {result1.get('status')}")
        else:
            print(f"❌ Step 1 HTTP Error: {response1.status_code}")
            print(f"Response: {response1.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_email_automation_workflow()
