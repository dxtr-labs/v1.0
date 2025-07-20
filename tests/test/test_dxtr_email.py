#!/usr/bin/env python3
"""
Test script to verify DXTR Labs AI content generation and email sending
"""

import sys
import os
sys.path.append('backend')

async def test_dxtr_email():
    try:
        from backend.mcp.ai_content_generator import ai_content_generator
        
        # Test content generation
        print("🧪 Testing DXTR Labs AI content generation...")
        
        user_input = "generate cold email for DXTR Labs architecture company to sell services and send to slakshanand1105@gmail.com"
        recipient_email = "slakshanand1105@gmail.com"
        
        print(f"📥 Input: {user_input}")
        print(f"📧 Recipient: {recipient_email}")
        
        # Test content type detection
        content_type = ai_content_generator.detect_content_type(user_input)
        print(f"🎯 Detected content type: {content_type}")
        
        # Test confirmation prompt
        confirmation_prompt = ai_content_generator.create_confirmation_prompt(user_input, recipient_email)
        print(f"🤔 Confirmation prompt: {confirmation_prompt}")
        
        # Test content generation
        print("\n🚀 Generating AI content...")
        result = ai_content_generator.generate_content(user_input, recipient_email)
        
        if result.get("success"):
            print("✅ AI content generation successful!")
            print(f"📧 Subject: {result.get('subject')}")
            print(f"🎨 Content type: {result.get('content_type')}")
            print(f"📝 Template source: {result.get('template_source')}")
            
            # Save the HTML content to a file for inspection
            html_content = result.get('html_content', '')
            if html_content:
                with open('dxtr_email_preview.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print("💾 HTML content saved to dxtr_email_preview.html")
            
            return True
        else:
            print(f"❌ AI content generation failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_dxtr_email())
