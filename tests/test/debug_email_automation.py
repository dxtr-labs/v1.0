#!/usr/bin/env python3
"""
Test script to debug the workflow preview response structure
"""

import asyncio
import json
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine

async def test_email_automation():
    """Test the exact email automation request to see the response structure"""
    
    print("🧪 Testing email automation workflow preview response...")
    
    # Mock agent data
    agent_data = {
        'agent_name': 'BobPop',
        'agent_role': 'PA'
    }
    
    # Create engine instance
    engine = CustomMCPLLMIterationEngine(
        agent_data=agent_data,
        agent_id='test_agent',
        session_id='test_session',
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )
    
    # Add DXTR Labs company info to conversation history (simulating the context)
    company_info = """DXTR Labs – Company Overview
Founded: 2013 (university project) – officially 2014
Headquarters: Sønderborg, Denmark & Menlo Park, California, USA
Industry: EdTech, Education, Smart Toys, IoT

Mission & Vision
DXTR Labs' mission is to "help the world embrace play", focusing on using play as an essential component of child development.

Products
playDXTR: Smart, connected magnetic building blocks with built-in sensors that analyze how children play, providing insights for learning and developmental diagnostics."""
    
    engine.current_conversation['conversation_history'].append({
        "role": "user",
        "content": company_info,
        "timestamp": "2025-07-18T20:30:00",
        "agent_id": "test_agent"
    })
    
    # Test the service selection (simulating "inhouse" selection)
    user_input = "service:inhouse"
    
    print(f"📝 Testing input: {user_input}")
    
    try:
        result = await engine.process_user_request(user_input)
        
        print("\n✅ Response received!")
        print("📊 Response structure:")
        print(json.dumps(result, indent=2, default=str))
        
        # Check if response has the expected structure for editable dialog
        if result.get('status') == 'workflow_preview':
            print("\n🎯 Status: workflow_preview ✅")
            
            if result.get('workflow_preview'):
                print("🎯 Has workflow_preview ✅")
                wp = result['workflow_preview']
                
                if isinstance(wp, dict) and 'email_preview' in wp:
                    print("🎯 Has email_preview structure ✅")
                    ep = wp['email_preview']
                    print(f"   📧 To: {ep.get('to')}")
                    print(f"   📋 Subject: {ep.get('subject')}")
                    print(f"   📝 Content length: {len(ep.get('preview_content', ''))}")
                    print(f"   🤖 AI Service: {ep.get('ai_service')}")
                else:
                    print("❌ workflow_preview is not a dict with email_preview")
                    print(f"   Type: {type(wp)}")
                    print(f"   Keys: {list(wp.keys()) if isinstance(wp, dict) else 'Not a dict'}")
            else:
                print("❌ Missing workflow_preview")
                
            if result.get('workflow_json'):
                print("🎯 Has workflow_json ✅")
            else:
                print("❌ Missing workflow_json")
        else:
            print(f"❌ Wrong status: {result.get('status')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv('.env.local')
    
    asyncio.run(test_email_automation())
