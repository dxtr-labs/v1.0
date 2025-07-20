#!/usr/bin/env python3
"""
Test the specific AI service selection flow that's causing the loop
"""

import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8002"

async def test_ai_service_flow():
    """Test the specific flow that's causing the loop"""
    print('🔍 Testing AI Service Selection Flow')
    print('=' * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Step 1: Send the initial AI request (should trigger service selection)
        print('\n📝 Step 1: Testing initial AI request...')
        initial_message = "using ai generate a sales pitch to sell healthy ice cream products and send those in email to slakshanand1105@gmail.com"
        
        data = {
            "message": initial_message,
            "agentId": "test-agent",
            "agentConfig": {
                "name": "Test Agent",
                "role": "assistant",
                "personality": {},
                "llm_config": {}
            }
        }
        
        try:
            async with session.post(f"{BASE_URL}/api/chat/mcpai", json=data) as response:
                print(f"Response status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"Response status: {result.get('status')}")
                    
                    if result.get('status') == 'ai_service_selection':
                        print("✅ Step 1 SUCCESS: AI service selection triggered")
                        
                        # Step 2: Select a service and send the formatted message
                        print('\n📝 Step 2: Testing service selection...')
                        
                        service_message = f"service:inhouse {initial_message}"
                        print(f"Sending formatted message: {service_message}")
                        
                        service_data = {
                            "message": service_message,
                            "agentId": "test-agent",
                            "agentConfig": {
                                "name": "Test Agent",
                                "role": "assistant",
                                "personality": {},
                                "llm_config": {}
                            }
                        }
                        
                        async with session.post(f"{BASE_URL}/api/chat/mcpai", json=service_data) as service_response:
                            print(f"Service selection response status: {service_response.status}")
                            
                            if service_response.status == 200:
                                service_result = await service_response.json()
                                print(f"Service response status: {service_result.get('status')}")
                                print(f"Service response keys: {list(service_result.keys())}")
                                
                                if service_result.get('status') == 'workflow_preview':
                                    print("✅ Step 2 SUCCESS: Workflow preview generated")
                                    
                                    # Check workflow preview structure
                                    workflow_preview = service_result.get('workflow_preview', {})
                                    print(f"Workflow preview keys: {list(workflow_preview.keys())}")
                                    print(f"Title: {workflow_preview.get('title')}")
                                    print(f"Steps: {len(workflow_preview.get('steps', []))}")
                                    
                                else:
                                    print(f"❌ Step 2 FAILED: Expected workflow_preview, got {service_result.get('status')}")
                                    print(f"Full response: {json.dumps(service_result, indent=2)}")
                            elif service_response.status == 401:
                                print("⚠️ Authentication required for service selection")
                            else:
                                print(f"❌ Service selection failed: {service_response.status}")
                                response_text = await service_response.text()
                                print(f"Error response: {response_text}")
                    else:
                        print(f"❌ Step 1 FAILED: Expected ai_service_selection, got {result.get('status')}")
                elif response.status == 401:
                    print("⚠️ Authentication required for initial request")
                else:
                    print(f"❌ Initial request failed: {response.status}")
                    response_text = await response.text()
                    print(f"Error response: {response_text}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    await test_ai_service_flow()

if __name__ == "__main__":
    asyncio.run(main())
