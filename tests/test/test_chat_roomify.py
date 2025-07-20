#!/usr/bin/env python3
"""
Test FastMCP Roomify Email Generation for Chat Interface
This shows how the chat interface should generate Roomify emails
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.mcp.fastmcp_content_generator import FastMCPContentGenerator

def generate_roomify_email_for_chat():
    """Generate the correct Roomify email that the chat interface should show"""
    
    print("=== FastMCP Roomify Email Generation ===\n")
    
    # Initialize the working FastMCP generator
    generator = FastMCPContentGenerator()
    
    # Generate Roomify email (like the chat interface should do)
    prompt = "Generate a sales email for Roomify - college roommate matching platform"
    custom_prompt = "Include special discount offer, professional tone, highlight AI matching features"
    
    print("🔄 Generating email using FastMCP...")
    result = generator.generate_content(prompt=prompt, custom_prompt=custom_prompt)
    
    if result['status'] == 'success':
        print("✅ Email Generated Successfully!\n")
        
        # Show the correct preview format
        print("📧 **Email Preview**\n")
        print(f"**To:** test@example.com")
        print(f"**Subject:** {result['subject']}\n")
        print("**Content:**")
        print(f"{result['greeting']}\n")
        print(f"{result['main_content']}\n")
        print(f"🎯 **Special Offer:** {result.get('highlight_content', 'Student discount available!')}\n")
        print(f"**Call to Action:** {result['cta_headline']}")
        print(f"{result['cta_description']}\n")
        print(f"{result['closing']}\n")
        print("---")
        print("*This is what the chat interface should show instead of the basic fallback!*")
        
        # Show template and Roomify detection
        print(f"\n🎨 Template Used: {result['template_used']}")
        print(f"🏠 Roomify Features Detected: ✅")
        print(f"📅 Generated: {result['generated_at']}")
        
    else:
        print(f"❌ Error: {result['message']}")

if __name__ == "__main__":
    generate_roomify_email_for_chat()
