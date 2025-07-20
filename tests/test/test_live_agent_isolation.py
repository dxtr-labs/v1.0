#!/usr/bin/env python3
"""
Quick test to verify which agent system is being used in the backend
"""

import asyncio
import aiohttp
import json

async def test_agent_isolation():
    """Test if agents are properly isolated"""
    
    print("🧪 TESTING AGENT ISOLATION IN LIVE BACKEND")
    print("=" * 50)
    
    # Test with two different agents using different requests
    test_cases = [
        {
            "agent_id": "agent_1", 
            "message": "find top 10 competitors and email them",
            "expected": "should detect automation request"
        },
        {
            "agent_id": "agent_2",
            "message": "Our company DXTR Labs is a great AI automation platform",
            "expected": "should be conversational"
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}️⃣ Testing Agent {test_case['agent_id']}")
            print(f"   Message: {test_case['message']}")
            print(f"   Expected: {test_case['expected']}")
            
            try:
                # Send request to backend
                url = f"http://localhost:8002/api/test/agents/{test_case['agent_id']}/chat"
                payload = {
                    "message": test_case['message']
                }
                
                print(f"   Sending to: {url}")
                print(f"   Payload: {payload}")
                
                async with session.post(url, json=payload, timeout=10) as response:
                    print(f"   Response status: {response.status}")
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        print(f"   Status: {result.get('status', 'unknown')}")
                        print(f"   Response Type: {result.get('automation_type', 'N/A')}")
                        
                        # Check for instance ID (indicates new system)
                        if 'instance_id' in result:
                            print(f"   ✅ Using NEW isolated system: {result['instance_id']}")
                        else:
                            print(f"   ⚠️ Using OLD shared system")
                            
                        print(f"   Response: {result.get('message', 'No message')[:100]}...")
                        
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Request failed: {response.status}")
                        print(f"   Error: {error_text[:200]}...")
                        
            except Exception as e:
                print(f"   ❌ Error: {e}")
                import traceback
                traceback.print_exc()
                
    print(f"\n📊 Test Complete - Check if responses are properly isolated")

if __name__ == "__main__":
    asyncio.run(test_agent_isolation())
