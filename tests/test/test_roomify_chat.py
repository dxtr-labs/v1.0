#!/usr/bin/env python3
"""
Test script to debug Roomify email generation through chat interface
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append('backend')

from mcp.automation_engine import mcp_automation_engine

async def test_roomify_chat_interface():
    """Test the Roomify email generation through automation engine"""
    
    print("🧪 Testing Roomify Chat Interface")
    print("=" * 50)
    
    # Test the exact user input from the chat
    user_input = "Use AI to generate a sales email for our product Roomify- Find your roomates for college students and send it to test@example.com. The email should highlight our using our product include a special discount offer, and have a professional tone. Make sure to show me a preview before sending."
    
    print(f"📝 User Input: {user_input}")
    print()
    
    # Test with auto_approve_ai=True (like in chat interface)
    print("🔄 Testing with auto_approve_ai=True (chat interface mode)...")
    result = await mcp_automation_engine.process_automation_request(
        user_input=user_input,
        user_id="test_user",
        auto_approve_ai=True
    )
    
    print("📊 **AUTOMATION ENGINE RESULT:**")
    print(f"Success: {result.get('success')}")
    print(f"Round: {result.get('round')}")
    print(f"Message: {result.get('message')}")
    print()
    
    if 'execution' in result:
        execution = result['execution']
        print("📧 **EXECUTION DETAILS:**")
        print(f"Execution success: {execution.get('success')}")
        print(f"Execution keys: {list(execution.keys())}")
        
        if 'preview_data' in execution:
            preview = execution['preview_data']
            print(f"📬 **PREVIEW DATA:**")
            print(f"To: {preview.get('to_email')}")
            print(f"Subject: {preview.get('subject')}")
            print(f"Template type: {preview.get('template_type')}")
            print(f"Text content length: {len(preview.get('text_content', ''))}")
            print(f"HTML content length: {len(preview.get('html_content', ''))}")
            print()
            print("📄 **TEXT CONTENT PREVIEW:**")
            text_content = preview.get('text_content', '')
            print(text_content[:300] + "..." if len(text_content) > 300 else text_content)
            print()
        else:
            print("❌ No preview_data found in execution result")
            
    if 'workflow' in result:
        workflow = result['workflow']
        print("🔧 **WORKFLOW DETAILS:**")
        print(f"Workflow name: {workflow.get('name')}")
        print(f"Number of nodes: {len(workflow.get('nodes', []))}")
        
        for i, node in enumerate(workflow.get('nodes', [])):
            print(f"  Node {i+1}: {node.get('type')} - {node.get('name')}")
            if node.get('type') == 'emailSend':
                params = node.get('parameters', {})
                print(f"    Subject: {params.get('subject', 'N/A')[:50]}...")
                print(f"    HTML content length: {len(params.get('html', ''))}")
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(test_roomify_chat_interface())
