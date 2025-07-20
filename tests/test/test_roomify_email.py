# test_roomify_email.py
# Test FastMCP email generation for Roomify

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from email_sender import generate_fastmcp_email, send_fastmcp_email

async def test_roomify_email():
    """Test email generation for Roomify product"""
    
    print("🏠 Testing Roomify Email Generation")
    print("=" * 50)
    
    # Generate Roomify email
    print("📧 Generating Roomify sales email...")
    
    email_data = await generate_fastmcp_email(
        company_info="Roomify - The Ultimate Roommate Finder Platform",
        product_service="AI-powered roommate matching platform for college students",
        target_info="College students looking for compatible roommates",
        special_requirements="Emphasize safety, compatibility matching, and ease of use for students",
        special_offer="STUDENT SPECIAL: 50% off premium matching for first 3 months!"
    )
    
    print("\n" + "="*60)
    print("📧 **EMAIL PREVIEW**")
    print("="*60)
    print(f"**To:** test@example.com")
    print(f"**Subject:** {email_data['subject']}")
    print(f"**Content Type:** HTML + Text")
    print("="*60)
    
    # Show text content preview
    print("\n**TEXT CONTENT PREVIEW:**")
    print("-" * 40)
    print(email_data['text_content'][:500] + "..." if len(email_data['text_content']) > 500 else email_data['text_content'])
    
    print("\n" + "="*60)
    print("✅ **ANALYSIS**")
    print("="*60)
    print(f"• Subject Line: {email_data['subject']}")
    print(f"• Content Length: {len(email_data['text_content'])} characters")
    print(f"• Has HTML Version: {'Yes' if email_data['html_content'] else 'No'}")
    print(f"• Contains 'Roomify': {'Yes' if 'Roomify' in email_data['text_content'] else 'No'}")
    print(f"• Contains 'student': {'Yes' if 'student' in email_data['text_content'].lower() else 'No'}")
    print(f"• Contains discount: {'Yes' if '50%' in email_data['text_content'] else 'No'}")
    
    # Ask for confirmation
    print("\n" + "="*60)
    print("🤔 **SEND CONFIRMATION**")
    print("="*60)
    print("Would you like to send this email?")
    print("• Type 'YES' to send")
    print("• Type 'NO' to cancel")
    print("• Type 'SHOW' to see full HTML content")
    
    return email_data

async def send_roomify_email_with_confirmation():
    """Generate and optionally send Roomify email"""
    
    email_data = await test_roomify_email()
    
    # For demo purposes, let's show the decision process
    print("\n🚀 For this demo, let's proceed with sending...")
    
    try:
        # Actually send the email
        result = await send_fastmcp_email(
            to_email="test@example.com",
            company_info="Roomify - The Ultimate Roommate Finder Platform",
            product_service="AI-powered roommate matching platform for college students",
            target_info="College students looking for compatible roommates",
            special_requirements="Emphasize safety, compatibility matching, and ease of use for students",
            special_offer="STUDENT SPECIAL: 50% off premium matching for first 3 months!"
        )
        
        print("\n✅ **SEND RESULT:**")
        print(f"Success: {result.get('success', False)}")
        print(f"Method: {result.get('method', 'Unknown')}")
        print(f"Message: {result.get('message', 'No message')}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ **SEND ERROR:** {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("🧪 Testing Roomify Email System...")
    
    try:
        result = asyncio.run(send_roomify_email_with_confirmation())
        print(f"\n🏁 Final Result: {'SUCCESS' if result.get('success') else 'FAILED'}")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
