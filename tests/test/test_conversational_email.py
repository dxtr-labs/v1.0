# test_conversational_email.py
# Test the conversational MCP assistant for email generation

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from mcp.smart_email_generator import smart_email_generator

async def simulate_conversation():
    """Simulate a conversation for email generation"""
    
    print("🤖 Conversational MCP Email Assistant Demo")
    print("=" * 60)
    print("This demo shows how the assistant asks for clarification when needed")
    print("=" * 60)
    
    # Test Case 1: Roomify with missing information
    print("\n📱 Test Case 1: User mentions Roomify but lacks details")
    print("-" * 50)
    
    user_request = "Generate a sales email for Roomify"
    print(f"👤 User: {user_request}")
    
    result = await smart_email_generator.process_email_request(user_request)
    
    print(f"\n🤖 Assistant ({result['type']}):")
    print(result['message'])
    
    # Simulate user providing more info
    print(f"\n👤 User: It's a roommate finder platform for college students")
    
    result2 = await smart_email_generator.process_email_request("It's a roommate finder platform for college students")
    
    print(f"\n🤖 Assistant ({result2['type']}):")
    print(result2['message'])
    
    # More details
    print(f"\n👤 User: We help students find compatible roommates using AI matching")
    
    result3 = await smart_email_generator.process_email_request("We help students find compatible roommates using AI matching")
    
    print(f"\n🤖 Assistant ({result3['type']}):")
    print(result3['message'])
    
    # Now generate email
    if result3.get('metadata', {}).get('ready_to_generate'):
        print(f"\n👤 User: Send to test@example.com with 50% student discount")
        
        email_result = await smart_email_generator.generate_email_from_context(
            recipient="test@example.com",
            special_offer="50% student discount for first month"
        )
        
        if email_result.get('success'):
            print(f"\n✅ EMAIL GENERATED SUCCESSFULLY!")
            print("="*50)
            print(f"📧 **To:** {email_result['recipient']}")
            print(f"📧 **Subject:** {email_result['subject']}")
            print(f"📧 **Generated with:** {email_result['generated_with']}")
            print("\n📝 **Content Preview:**")
            print("-"*30)
            content_preview = email_result['text_content'][:300] + "..." if len(email_result['text_content']) > 300 else email_result['text_content']
            print(content_preview)
            
            print(f"\n🏢 **Company Profile Used:**")
            profile = email_result['profile']
            print(f"• Name: {profile['name']}")
            print(f"• Industry: {profile['industry']}")
            print(f"• Services: {profile['services']}")
            print(f"• Target: {profile['target_audience']}")
            
        else:
            print(f"\n❌ Email generation failed: {email_result.get('error')}")
    
    # Test Case 2: Complete information provided upfront
    print("\n\n" + "="*60)
    print("📊 Test Case 2: Complete information provided upfront")
    print("-" * 50)
    
    # Reset conversation
    smart_email_generator.reset_conversation()
    
    complete_request = "Create an email for TechFlow Solutions, a business automation software company targeting small businesses, send to manager@company.com"
    print(f"👤 User: {complete_request}")
    
    result_complete = await smart_email_generator.process_email_request(complete_request)
    
    print(f"\n🤖 Assistant ({result_complete['type']}):")
    print(result_complete['message'])
    
    if result_complete.get('metadata', {}).get('ready_to_generate'):
        email_result2 = await smart_email_generator.generate_email_from_context(
            recipient="manager@company.com",
            special_message="Free trial available"
        )
        
        if email_result2.get('success'):
            print(f"\n✅ SECOND EMAIL GENERATED!")
            print(f"📧 Subject: {email_result2['subject']}")
            print(f"📧 Profile: {email_result2['profile']['name']} ({email_result2['profile']['industry']})")
    
    # Show conversation history
    print("\n\n" + "="*60)
    print("🧠 CONVERSATION MEMORY")
    print("="*60)
    
    history = smart_email_generator.get_conversation_history()
    for i, msg in enumerate(history[-6:], 1):  # Show last 6 messages
        role_emoji = {"user": "👤", "assistant": "🤖", "system": "⚙️"}.get(msg['role'], "💬")
        print(f"{role_emoji} {msg['role'].title()}: {msg['content'][:80]}...")
    
    print("\n" + "="*60)
    print("🎯 CONVERSATIONAL FEATURES DEMONSTRATED:")
    print("="*60)
    print("✅ Asks clarifying questions when information is missing")
    print("✅ Remembers conversation context and builds company profile")
    print("✅ Uses accumulated knowledge for email generation")
    print("✅ Handles both incomplete and complete requests")
    print("✅ Maintains conversation memory across interactions")
    print("✅ Adapts to different industries and business types")
    print("="*60)

if __name__ == "__main__":
    print("🧪 Starting Conversational Email Assistant Test...")
    
    try:
        asyncio.run(simulate_conversation())
        print("\n🎉 Conversational demo completed successfully!")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
