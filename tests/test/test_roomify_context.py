#!/usr/bin/env python3
"""
Test script for Roomify conversational email generation with proper context usage
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.mcp.conversational_assistant import ConversationalMCPAssistant
from backend.mcp.fastmcp_content_generator import FastMCPContentGenerator

def test_roomify_conversation():
    """Test the conversational flow with Roomify context"""
    print("=== Testing Roomify Conversational Email Generation ===\n")
    
    # Initialize components
    assistant = ConversationalMCPAssistant()
    content_generator = FastMCPContentGenerator()
    
    # Step 1: User requests email for Roomify
    print("👤 User: Generate a sales email for Roomify")
    response_message, response_data = assistant.process_user_input("Generate a sales email for Roomify")
    print(f"🤖 Assistant: {response_message}\n")
    
    # Step 2: User provides company details
    company_details = """Roomify is a college roommate matching platform that uses AI algorithms to connect students with compatible roommates. We help college students find roommates who share their lifestyle, study habits, and interests. Our target audience is college students looking for better living situations."""
    
    print(f"👤 User: {company_details}")
    response_message, response_data = assistant.process_user_input(company_details)
    print(f"🤖 Assistant: {response_message}\n")
    
    # Step 3: Generate email with full context
    if response_data.get('action') == 'generate_email':
        company_name = response_data.get('company_name', 'Roomify')
        company_profile = assistant.company_profiles.get(company_name)
        
        print(f"📊 Company Profile Built:")
        print(f"   Name: {company_profile.name}")
        print(f"   Industry: {company_profile.industry}")
        print(f"   Services: {company_profile.services}")
        print(f"   Description: {company_profile.description}")
        print(f"   Target Audience: {company_profile.target_audience}\n")
        
        # Generate content with Roomify context
        print("🔄 Generating email content with Roomify context...")
        content_prompt = f"Generate a sales email for {company_profile.name} - a college roommate matching platform"
        
        result = content_generator.generate_content(
            prompt=content_prompt,
            custom_prompt=f"Focus on Roomify's AI matching, college students, and finding compatible roommates. Target audience: {company_profile.target_audience}. Services: {', '.join(company_profile.services)}"
        )
        
        if result['status'] == 'success':
            print("✅ Email Generated Successfully!")
            print(f"📧 Subject: {result['subject']}")
            print(f"👋 Greeting: {result['greeting']}")
            print(f"📝 Main Content Preview: {result['main_content'][:200]}...")
            print(f"🎯 CTA: {result['cta_headline']}")
            print(f"✉️ Template Used: {result['template_used']}")
            
            # Show that it's using Roomify-specific content
            content_text = result['main_content'].lower()
            roomify_keywords = ['roomify', 'roommate', 'college', 'students', 'matching']
            found_keywords = [kw for kw in roomify_keywords if kw in content_text]
            print(f"🔍 Roomify Keywords Found: {found_keywords}")
            
        else:
            print(f"❌ Error: {result['message']}")
    
    # Step 4: Provide email recipient details
    print("\n👤 User: Send to marketing@college.edu with our student special offer")
    response_message, response_data = assistant.process_user_input("Send to marketing@college.edu with our student special offer")
    print(f"🤖 Assistant: {response_message}\n")
    
    # Step 5: Check if email generation is ready
    if response_data.get('action') == 'generate_email':
        company_name = response_data.get('company_name', 'Roomify')
        company_profile = assistant.company_profiles.get(company_name)
        
        if company_profile:
            print(f"📊 Final Company Profile:")
            print(f"   Name: {company_profile.name}")
            print(f"   Industry: {company_profile.industry}")
            print(f"   Services: {company_profile.services}")
            print(f"   Target Audience: {company_profile.target_audience}\n")
            
            # Generate final email content
            print("🔄 Generating final email with complete context...")
            content_prompt = f"Generate a sales email for {company_profile.name} - {company_profile.description}"
            
            result = content_generator.generate_content(
                prompt=content_prompt,
                custom_prompt=f"Create engaging content for {company_profile.target_audience} about {', '.join(company_profile.services)}. Include student special offer."
            )
            
            if result['status'] == 'success':
                print("✅ Final Email Generated Successfully!")
                print(f"📧 Subject: {result['subject']}")
                print(f"📝 Content includes Roomify-specific features!")
                
                # Check for Roomify-specific content
                full_content = result.get('main_content', '') + ' ' + result.get('subject', '')
                roomify_indicators = ['roomify', 'roommate', 'college', 'student', 'matching', 'ai']
                found_indicators = [word for word in roomify_indicators if word in full_content.lower()]
                print(f"🎯 Context-Aware Content: {len(found_indicators)}/6 Roomify indicators found: {found_indicators}")
                
            else:
                print(f"❌ Generation failed: {result.get('message', 'Unknown error')}")
        else:
            print("❌ No company profile found")
    else:
        print("ℹ️ Still in conversation mode, not ready to generate email yet")

if __name__ == "__main__":
    test_roomify_conversation()
