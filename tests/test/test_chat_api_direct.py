#!/usr/bin/env python3
"""
Test the chat API directly to see why Roomify content isn't showing
"""

import asyncio
import sys
import os
import json

# Add backend to path
sys.path.append('backend')

from api.chat import chat_with_mcpai
from pydantic import BaseModel
from typing import Dict, Any, Optional

class ChatRequest(BaseModel):
    user_input: Optional[str] = None
    message: Optional[str] = None
    agent_config: Optional[Dict[str, Any]] = None
    agentConfig: Optional[Dict[str, Any]] = None
    agentId: Optional[str] = None
    session_id: Optional[str] = None
    
    def get_user_input(self) -> str:
        return self.user_input or self.message or ""
    
    def get_agent_config(self) -> Dict[str, Any]:
        config = self.agent_config or self.agentConfig or {}
        if self.agentId and 'agent_id' not in config:
            config['agent_id'] = self.agentId
        return config

async def test_chat_api():
    """Test the chat API directly"""
    
    print("🧪 Testing Chat API Directly")
    print("=" * 50)
    
    # Create request matching what frontend sends
    request = ChatRequest(
        user_input="Use AI to generate a sales email for our product Roomify- Find your roomates for college students and send it to test@example.com. The email should highlight our using our product include a special discount offer, and have a professional tone. Make sure to show me a preview before sending.",
        agent_config={
            "name": "Sales Assistant",
            "role": "Email Marketing Specialist",
            "agent_id": "sales_agent_123"
        },
        session_id="test_session"
    )
    
    print(f"📤 Sending request to chat API...")
    print(f"User input: {request.user_input[:100]}...")
    print(f"Agent config: {request.agent_config}")
    print()
    
    try:
        # Call the chat API
        response = await chat_with_mcpai(request)
        
        print("📥 **CHAT API RESPONSE:**")
        print(f"Response type: {type(response)}")
        print(f"Response: {response.response[:200]}...")
        print(f"Workflow generated: {response.workflow_generated}")
        print(f"Needs confirmation: {response.needs_confirmation}")
        print(f"Action required: {response.action_required}")
        print()
        
        if response.preview_data:
            print("📧 **PREVIEW DATA:**")
            preview = response.preview_data
            print(f"To: {preview.get('to_email')}")
            print(f"Subject: {preview.get('subject')}")
            print(f"Template type: {preview.get('template_type')}")
            print(f"Text content length: {len(preview.get('text_content', ''))}")
            print()
            
            print("📄 **PREVIEW TEXT (first 500 chars):**")
            text_content = preview.get('text_content', '')
            print(text_content[:500])
            print()
        else:
            print("❌ No preview data in response")
            
        if response.execution_details:
            print("🔧 **EXECUTION DETAILS:**")
            exec_details = response.execution_details
            print(f"Keys: {list(exec_details.keys())}")
            
    except Exception as e:
        print(f"❌ Chat API error: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(test_chat_api())
