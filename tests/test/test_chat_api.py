#!/usr/bin/env python3
"""Test the chat API directly"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from backend.api.chat import ChatRequest, chat_with_mcpai

async def test_chat_api():
    """Test the chat API with a Roomify request"""
    print("=== Testing Chat API for Roomify Email ===")
    
    # Create a chat request
    request = ChatRequest(
        user_input="Generate a sales email for our product Roomify- Find your roomates for college students and send it to test@example.com. The email should highlight our using our product include a special discount offer, and have a professional tone.",
        session_id="test_session_123"
    )
    
    print(f"🎯 Request: {request.user_input}")
    
    try:
        # Call the chat API
        response = await chat_with_mcpai(request)
        
        print(f"\n🎉 **CHAT API RESPONSE:**")
        print(f"Response: {response.response}")
        print(f"Workflow Generated: {response.workflow_generated}")
        print(f"Needs Confirmation: {response.needs_confirmation}")
        print(f"Action Required: {response.action_required}")
        
        if response.preview_data:
            preview = response.preview_data
            print(f"\n📧 **PREVIEW DATA FOUND:**")
            print(f"To: {preview.get('to_email')}")
            print(f"Subject: {preview.get('subject')}")
            print(f"Template: {preview.get('template_type')}")
            
            # Check for Roomify features
            content = preview.get('text_content', '').lower()
            features = []
            if 'roomify' in content:
                features.append("✅ Roomify content")
            if 'roommate' in content:
                features.append("✅ Roommate matching")
            if 'college' in content:
                features.append("✅ College targeting")
            if 'discount' in content or 'special' in content:
                features.append("✅ Special offer")
            if 'ai' in content and 'algorithm' in content:
                features.append("✅ AI algorithms")
                
            print("Features found:", ", ".join(features))
        else:
            print("❌ No preview data found")
            
        if response.execution_details:
            print(f"\n📋 **EXECUTION DETAILS:**")
            exec_details = response.execution_details
            print(f"Keys: {list(exec_details.keys())}")
            
            if 'preview_data' in exec_details:
                preview = exec_details['preview_data']
                print(f"📧 **EXECUTION PREVIEW DATA:**")
                print(f"Subject: {preview.get('subject')}")
                print(f"Template: {preview.get('template_type')}")
                
                # Check for Roomify content
                content = preview.get('text_content', '').lower()
                if 'roomify' in content:
                    print("✅ FOUND ROOMIFY CONTENT IN EXECUTION DETAILS!")
                else:
                    print("❌ No Roomify content in execution details")
            else:
                print("❌ No preview_data in execution_details")
        else:
            print("❌ No execution_details found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chat_api())
