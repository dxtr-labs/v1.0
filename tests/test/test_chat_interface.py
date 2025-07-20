#!/usr/bin/env python3
"""
Test the chat interface's email generation with FastMCP
This simulates what happens when the chat gets a Roomify email request
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from backend.mcp.automation_engine import MCPAutomationEngine

async def test_chat_roomify_email():
    """Test what the chat interface should generate for Roomify"""
    
    print("=== Testing Chat Interface Roomify Email ===\n")
    
    # Initialize the automation engine (same as chat interface uses)
    engine = MCPAutomationEngine()
    
    # Simulate the exact request from the chat interface
    user_input = "Generate a sales email for our product Roomify- Find your roomates for college students and send it to test@example.com. The email should highlight our using our product include a special discount offer, and have a professional tone."
    
    print(f"🎯 User Request: {user_input}\n")
    
    # Process with AI content (like the chat interface does)
    print("🔄 Processing with FastMCP AI content generation...")
    result = await engine.process_with_ai_content(
        user_input=user_input, 
        recipient_email="test@example.com", 
        use_ai=True
    )
    
    print("🎉 Result:")
    print(f"Success: {result.get('success', False)}")
    print(f"Message: {result.get('message', 'No message')}")
    
    # Check for preview information in the execution section
    execution = result.get('execution', {})
    if 'preview_data' in execution:
        preview = execution['preview_data']
        print(f"\n📧 **ROOMIFY EMAIL PREVIEW WORKING!**")
        print(f"**To:** {preview.get('to_email', 'N/A')}")
        print(f"**Subject:** {preview.get('subject', 'N/A')}")
        
        # Check text content for preview
        text_content = preview.get('text_content', '')
        print(f"**Content Preview:** {text_content[:300]}...")
        
        # Check for Roomify content
        full_content = f"{preview.get('html_content', '')} {text_content}".lower()
        roomify_features = []
        if 'roomify' in full_content:
            roomify_features.append("✅ Contains Roomify-specific content!")
        if 'roommate' in full_content:
            roomify_features.append("✅ Contains roommate matching features!")
        if 'college' in full_content:
            roomify_features.append("✅ Targets college students!")
        if 'discount' in full_content or 'special' in full_content:
            roomify_features.append("✅ Contains discount/special offer!")
        if 'ai' in full_content and 'algorithm' in full_content:
            roomify_features.append("✅ Mentions AI algorithms!")
            
        print("\n" + "\n".join(roomify_features))
        print(f"**Template:** {preview.get('template_type', 'N/A')}")
        
        # Check if we have the special discount
        if '50% off' in text_content and '$15 instead of $30' in text_content:
            print("🎓 ✅ **STUDENT SPECIAL DISCOUNT INCLUDED!**")
            
    elif 'preview_data' in result:
        preview = result['preview_data']
        print(f"\n� **Email Preview Found (top level)**")
        print(f"**Subject:** {preview.get('subject', 'N/A')}")
    else:
        print("❌ No preview_data found in result")
    
    # Check for preview information
    if 'preview_data' in result:
        preview = result['preview_data']
        print(f"\n📧 **Email Preview Generated**")
        print(f"**To:** {preview.get('to_email', 'N/A')}")
        print(f"**Subject:** {preview.get('subject', 'N/A')}")
        
        # Check HTML content
        html_content = preview.get('html_content', '')
        text_content = preview.get('text_content', '')
        
        print(f"**Content Preview:** {text_content[:200]}...")
        
        # Check for Roomify content
        full_content = f"{html_content} {text_content}".lower()
        if 'roomify' in full_content:
            print("✅ Contains Roomify-specific content!")
        if 'roommate' in full_content:
            print("✅ Contains roommate matching features!")
        if 'college' in full_content:
            print("✅ Targets college students!")
        if 'discount' in full_content:
            print("✅ Contains discount offer!")
            
        print(f"**Template:** {preview.get('template_type', 'N/A')}")
    
    elif 'preview' in result:
        preview = result['preview']
        print(f"\n📧 **Email Preview Generated**")
        print(f"**To:** {preview.get('to', 'N/A')}")
        print(f"**Subject:** {preview.get('subject', 'N/A')}")
        print(f"**Content Preview:** {preview.get('content', 'N/A')[:200]}...")
        
        # Check for Roomify content
        content_str = str(preview.get('content', ''))
        if 'Roomify' in content_str:
            print("✅ Contains Roomify-specific content!")
        if 'roommate' in content_str.lower():
            print("✅ Contains roommate matching features!")
        if 'college' in content_str.lower():
            print("✅ Targets college students!")
    
    elif result.get('workflow_json'):
        # Extract email details from workflow
        nodes = result['workflow_json'].get('nodes', [])
        email_node = next((node for node in nodes if node.get('type') == 'emailSend'), None)
        
        if email_node:
            params = email_node.get('parameters', {})
            print(f"\n📧 **Email Preview**")
            print(f"**To:** {params.get('to', 'N/A')}")
            print(f"**Subject:** {params.get('subject', 'N/A')}")
            print(f"\n**Content:**")
            
            # Show HTML content preview
            html_body = params.get('html_body', '')
            if 'Roomify' in html_body:
                print("✅ Contains Roomify-specific content!")
            if 'roommate' in html_body.lower():
                print("✅ Contains roommate matching features!")
            if 'college' in html_body.lower():
                print("✅ Targets college students!")
            
            # Show a preview of the content
            text_body = params.get('body', 'No content')
            print(f"\nText Preview: {text_body[:200]}...")
            
        else:
            print("❌ No email node found in workflow")
    else:
        print("❌ No workflow generated")

if __name__ == "__main__":
    asyncio.run(test_chat_roomify_email())
