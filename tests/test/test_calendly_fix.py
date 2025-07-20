#!/usr/bin/env python3
"""
Test script to verify the Calendly functionality fix
"""

import asyncio
import json
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from mcp.custom_mcp_llm_iteration import CustomMCPLLMEngine

async def test_calendly_functionality():
    """Test the Calendly link creation functionality"""
    
    print("🧪 Testing Calendly functionality fix...")
    
    # Create a test MCP engine instance
    test_agent_context = {
        'agent_data': {
            'agent_name': 'Sam',
            'agent_role': 'Personal Assistant',
            'agent_id': 'test_agent_123'
        },
        'memory': {},
        'user_id': 'test_user'
    }
    
    # Initialize the engine
    mcp_engine = CustomMCPLLMEngine(
        agent_id='test_agent_123',
        session_id='test_session',
        agent_context=test_agent_context,
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )
    
    # Test the specific user request that was failing
    test_request = "create a calendly link and send to slakshanand1105@gmail.com"
    
    print(f"📝 Testing request: {test_request}")
    print("=" * 60)
    
    try:
        # Process the request
        result = await mcp_engine.process_user_request(test_request)
        
        print("✅ MCP ENGINE RESULT:")
        print(f"Success: {result.get('success')}")
        print(f"Status: {result.get('status')}")
        print(f"Message length: {len(result.get('message', ''))}")
        
        # Check if it's a proper Calendly response
        response_text = result.get('message', '') or result.get('response', '')
        
        print("\n🔍 ANALYZING RESPONSE:")
        print(f"Contains 'calendly': {'calendly' in response_text.lower()}")
        print(f"Contains email address: {'slakshanand1105@gmail.com' in response_text}")
        print(f"Contains 'meeting': {'meeting' in response_text.lower()}")
        print(f"Contains 'schedule': {'schedule' in response_text.lower()}")
        
        # Check workflow details
        if result.get('workflowJson'):
            workflow = result['workflowJson']
            email_params = workflow.get('steps', [{}])[0].get('parameters', {})
            
            print("\n📧 EMAIL DETAILS:")
            print(f"Subject: {email_params.get('subject', 'N/A')}")
            print(f"Recipient: {email_params.get('to', 'N/A')}")
            print(f"Email type: {email_params.get('email_type', 'N/A')}")
            print(f"Content preview: {email_params.get('content', '')[:200]}...")
        
        print("\n" + "=" * 60)
        print("📄 FULL RESPONSE:")
        print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
        
        # Determine if the fix worked
        calendly_indicators = [
            'calendly' in response_text.lower(),
            'meeting' in response_text.lower(),
            'schedule' in response_text.lower(),
            'book' in response_text.lower()
        ]
        
        if any(calendly_indicators) and 'slakshanand1105@gmail.com' in response_text:
            print("\n🎉 SUCCESS: Calendly functionality is working!")
            print("✅ The system now properly generates Calendly meeting invitations instead of generic sales emails.")
            return True
        else:
            print("\n❌ ISSUE: Response doesn't appear to be Calendly-specific")
            return False
            
    except Exception as e:
        print(f"❌ ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_calendly_functionality())
