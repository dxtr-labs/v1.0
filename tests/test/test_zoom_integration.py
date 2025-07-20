#!/usr/bin/env python3
"""
Test Zoom OAuth integration and meeting creation
"""

import sys
import os
import asyncio
import requests
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_zoom_oauth_endpoint():
    """Test the Zoom OAuth authorization endpoint"""
    print("🔗 Testing Zoom OAuth Authorization Endpoint")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8002/api/oauth/zoom/authorize")
        
        print(f"📤 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ OAuth endpoint working!")
            print(f"🔑 OAuth URL: {result.get('oauth_url', 'N/A')[:100]}...")
            print(f"📝 Message: {result.get('message', 'N/A')}")
            return True
        else:
            print(f"❌ OAuth endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ OAuth test failed: {e}")
        return False

def test_zoom_meeting_request():
    """Test Zoom meeting request through MCP API"""
    print("\n🚀 Testing Zoom Meeting Request via MCP")
    print("=" * 50)
    
    test_request = "setup up a zoom meeting link with potential investors and send the zoom meeting to slakshanand1105@gmail.com"
    print(f"📝 Test Request: {test_request}")
    
    try:
        response = requests.post(
            "http://localhost:8002/api/mcp/chat",
            json={
                "message": test_request,
                "service": "inhouse"
            },
            timeout=30
        )
        
        print(f"📤 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Request successful!")
            
            # Check if it's an OAuth required response
            if result.get("status") == "oauth_required":
                print("🎯 ✅ OAuth flow initiated!")
                
                workflow = result.get("workflow_preview", {})
                oauth_url = result.get("oauth_url", "")
                
                print(f"🔐 OAuth Required: {workflow.get('oauth_required', False)}")
                print(f"🔗 OAuth URL: {oauth_url[:100]}...")
                print(f"📝 Description: {workflow.get('description', 'N/A')}")
                
                # Check if steps are defined
                steps = workflow.get("steps", [])
                print(f"📋 Workflow Steps: {len(steps)}")
                for step in steps:
                    print(f"   {step.get('step')}. {step.get('icon')} {step.get('action')}")
                
                print("🎉 ✅ Zoom OAuth integration working!")
                return True
            else:
                print("⚠️ Expected OAuth response but got different status")
                print(f"📋 Status: {result.get('status', 'N/A')}")
                print(f"📋 Response: {result.get('response', 'N/A')}")
                return False
        else:
            print(f"❌ Request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ MCP test failed: {e}")
        return False

def test_zoom_oauth_detection():
    """Test different Zoom meeting request variations"""
    print("\n🔍 Testing Zoom Request Detection Variations")
    print("=" * 50)
    
    test_variations = [
        "connect with zoom...open zoom oauth and ask to sing in and use that authorization to make email",
        "set up zoom meeting with investors",
        "create zoom link for meeting",
        "schedule zoom call with client"
    ]
    
    success_count = 0
    
    for i, test_request in enumerate(test_variations, 1):
        print(f"\n{i}. Testing: {test_request}")
        
        try:
            response = requests.post(
                "http://localhost:8002/api/mcp/chat",
                json={
                    "message": test_request,
                    "service": "inhouse"
                },
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "oauth_required":
                    print("   ✅ OAuth flow detected")
                    success_count += 1
                else:
                    print(f"   ⚠️ Different response: {result.get('status', 'N/A')}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Detection Results: {success_count}/{len(test_variations)} variations detected correctly")
    return success_count > 0

async def test_zoom_service_direct():
    """Test Zoom service directly"""
    print("\n🔧 Testing Zoom Service Directly")
    print("=" * 50)
    
    try:
        from backend.services.zoom_service import zoom_service
        
        # Test OAuth URL generation
        oauth_url = zoom_service.get_oauth_url("test_state")
        print(f"✅ OAuth URL generated: {len(oauth_url)} characters")
        print(f"🔗 URL Preview: {oauth_url[:100]}...")
        
        # Test meeting info formatting
        mock_meeting_info = {
            'id': '123456789',
            'join_url': 'https://zoom.us/j/123456789',
            'password': 'test123',
            'topic': 'Test Meeting',
            'start_time': '2025-07-19T14:00:00',
            'duration': 30
        }
        
        formatted_info = zoom_service.format_meeting_info_for_email(mock_meeting_info)
        print(f"✅ Meeting info formatted: {len(formatted_info)} characters")
        print(f"📝 Preview: {formatted_info[:150]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct service test failed: {e}")
        return False

async def main():
    """Run all Zoom integration tests"""
    print("🚀 Testing Zoom Integration")
    print("=" * 60)
    
    # Test 1: OAuth endpoint
    oauth_endpoint_ok = test_zoom_oauth_endpoint()
    
    # Test 2: MCP meeting request
    mcp_request_ok = test_zoom_meeting_request()
    
    # Test 3: Detection variations
    detection_ok = test_zoom_oauth_detection()
    
    # Test 4: Direct service
    direct_service_ok = await test_zoom_service_direct()
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS:")
    print(f"   OAuth Endpoint: {'✅ WORKING' if oauth_endpoint_ok else '❌ FAILED'}")
    print(f"   MCP Integration: {'✅ WORKING' if mcp_request_ok else '❌ FAILED'}")
    print(f"   Request Detection: {'✅ WORKING' if detection_ok else '❌ FAILED'}")
    print(f"   Direct Service: {'✅ WORKING' if direct_service_ok else '❌ FAILED'}")
    
    overall_success = oauth_endpoint_ok and mcp_request_ok and detection_ok and direct_service_ok
    
    if overall_success:
        print("\n🎉 SUCCESS: Zoom integration is working!")
        print("\n💡 Sam can now test with:")
        print("   'setup up a zoom meeting link with potential investors and send the zoom meeting to slakshanand1105@gmail.com'")
        print("   'connect with zoom...open zoom oauth and ask to sing in and use that authorization to make email'")
        print("\n🔗 The system will:")
        print("   1. Detect Zoom meeting requests")
        print("   2. Generate OAuth authorization URL")
        print("   3. Guide user through Zoom authorization")
        print("   4. Create meeting and send email invitation")
    else:
        print("\n❌ Some Zoom integration issues remain")

if __name__ == "__main__":
    asyncio.run(main())
