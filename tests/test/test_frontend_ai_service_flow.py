#!/usr/bin/env python3
"""
Test what the frontend should send when user selects an AI service
This simulates the complete frontend interaction
"""

import json
import requests
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_frontend_ai_service_selection():
    """Test the complete frontend workflow with AI service selection"""
    
    logger.info("🧪 Testing Frontend AI Service Selection Flow")
    logger.info("=" * 60)
    
    # Backend URL
    backend_url = "http://127.0.0.1:8002"
    
    # Step 1: Initial request (what frontend currently does)
    logger.info("🔄 Step 1: Initial Request")
    initial_payload = {
        "message": "draft a sales pitch to sell better torch lights using AI and send email to slakshanand1105@gmail.com",
        "agentId": "test_agent",
        "agentConfig": {
            "name": "Test Agent",
            "role": "Sales Assistant"
        },
        "session_id": "test_session"
    }
    
    # For testing, we'll use a test user header instead of session token
    headers = {
        "Content-Type": "application/json",
        "x-user-id": "test_user_123"  # This bypasses authentication for testing
    }
    
    try:
        response1 = requests.post(
            f"{backend_url}/api/chat/mcpai",
            json=initial_payload,
            headers=headers,
            timeout=30
        )
        
        logger.info(f"   Status Code: {response1.status_code}")
        
        if response1.status_code == 200:
            result1 = response1.json()
            logger.info(f"   Response Status: {result1.get('status', 'unknown')}")
            logger.info(f"   Action Required: {result1.get('action_required', 'none')}")
            
            if result1.get('status') == 'ai_service_selection':
                logger.info("   ✅ Successfully got AI service selection")
                
                # Step 2: User selects AI service (what frontend SHOULD do next)
                logger.info("\n🔄 Step 2: AI Service Selection")
                logger.info("   User selects: In-House AI")
                
                # Frontend should send the original message with service prefix
                service_selection_payload = {
                    "message": f"service:inhouse {initial_payload['message']}",
                    "agentId": initial_payload["agentId"],
                    "agentConfig": initial_payload["agentConfig"],
                    "session_id": initial_payload["session_id"]
                }
                
                response2 = requests.post(
                    f"{backend_url}/api/chat/mcpai",
                    json=service_selection_payload,
                    headers=headers,
                    timeout=30
                )
                
                logger.info(f"   Status Code: {response2.status_code}")
                
                if response2.status_code == 200:
                    result2 = response2.json()
                    logger.info(f"   Response Status: {result2.get('status', 'unknown')}")
                    
                    if result2.get('status') == 'workflow_preview':
                        logger.info("   ✅ Successfully got workflow preview")
                        logger.info(f"   Workflow Actions: {len(result2.get('workflow_json', {}).get('workflow', {}).get('actions', []))}")
                        
                        # Step 3: Confirm workflow (what frontend should do next)
                        logger.info("\n🔄 Step 3: Workflow Confirmation")
                        
                        confirm_payload = {
                            "agentId": initial_payload["agentId"],
                            "confirmed": True,
                            "workflow_json": result2.get('workflow_json'),
                            "original_message": initial_payload["message"]
                        }
                        
                        response3 = requests.post(
                            f"{backend_url}/api/chat/mcpai/confirm",
                            json=confirm_payload,
                            headers=headers,
                            timeout=30
                        )
                        
                        logger.info(f"   Status Code: {response3.status_code}")
                        
                        if response3.status_code == 200:
                            result3 = response3.json()
                            logger.info(f"   Success: {result3.get('success', False)}")
                            logger.info(f"   Response: {result3.get('response', 'No response')[:100]}...")
                            logger.info("   🎉 COMPLETE WORKFLOW SUCCESS!")
                        else:
                            logger.error(f"   ❌ Confirmation failed: {response3.text}")
                    else:
                        logger.error(f"   ❌ Expected workflow_preview, got: {result2.get('status')}")
                        logger.error(f"   Response: {json.dumps(result2, indent=2)}")
                else:
                    logger.error(f"   ❌ AI service selection failed: {response2.text}")
            else:
                logger.error(f"   ❌ Expected ai_service_selection, got: {result1.get('status')}")
                logger.error(f"   Response: {json.dumps(result1, indent=2)}")
        else:
            logger.error(f"   ❌ Initial request failed: {response1.text}")
    
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
    
    logger.info("=" * 60)
    logger.info("🏁 Frontend AI Service Selection Test Complete")

if __name__ == "__main__":
    test_frontend_ai_service_selection()
