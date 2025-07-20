#!/usr/bin/env python3
"""
Quick test for the fixed OpenAI integration
"""

import requests

def test_fixed_integration():
    print("🧪 Testing Fixed OpenAI Integration...")
    
    # Login
    response = requests.post('http://127.0.0.1:8002/api/auth/login', 
                           headers={'Content-Type': 'application/json'},
                           json={'email': 'test@dxtrlabs.com', 'password': 'testpass123'}, 
                           timeout=10)

    if response.status_code == 200:
        result = response.json()
        session_token = result.get('session_token')
        print(f'✅ Logged in successfully')
        
        # Test different messages
        test_messages = [
            "Hello! Tell me about your company",
            "What makes DXTR Labs special?",
            "How can you help me with automation?",
            "What are digital employees?"
        ]
        
        for message in test_messages:
            print(f"\n📤 Testing: '{message}'")
            
            test_response = requests.post('http://127.0.0.1:8002/api/chat/mcpai',
                                        headers={'Content-Type': 'application/json', 'Cookie': f'session_token={session_token}'},
                                        json={'message': message},
                                        timeout=30)
            
            if test_response.status_code == 200:
                result = test_response.json()
                response_message = result.get('message', '')
                
                print(f"✅ Status: {result.get('status')}")
                print(f"📏 Length: {len(response_message)} chars")
                print(f"🏢 Contains DXTR: {'DXTR' in response_message}")
                print(f"📝 Response: {response_message[:150]}...")
                
                # Check if it's the old generic response
                if "I don't have custom programming yet" in response_message:
                    print("⚠️ Still getting generic response!")
                else:
                    print("✅ Getting personalized response!")
                    
            else:
                print(f"❌ Error: {test_response.text}")
            
            print("-" * 50)
    else:
        print(f"❌ Login failed: {response.text}")

if __name__ == "__main__":
    test_fixed_integration()
