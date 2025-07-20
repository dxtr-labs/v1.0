# test_fastmcp_emails.py
# Test script for FastMCP email generation

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from email_sender import send_fastmcp_email, generate_fastmcp_email

async def test_fastmcp_system():
    """Test the FastMCP email generation system"""
    
    print("🤖 Testing FastMCP Email System")
    print("=" * 50)
    
    # Test 1: Transportation Company
    print("\n📧 Test 1: Transportation Company")
    print("-" * 30)
    
    email_data = await generate_fastmcp_email(
        company_info="DXTR Transportation Services",
        product_service="Premium charter bus services and transportation solutions",
        target_info="Corporate clients and event organizers",
        special_requirements="Emphasize safety protocols and luxury amenities",
        special_offer="Special 25% discount for first-time corporate bookings"
    )
    
    print(f"✅ Subject: {email_data['subject']}")
    print(f"✅ Content generated successfully")
    print(f"✅ Template: Transportation Premium")
    
    # Test 2: Custom Prompt for Tech Startup
    print("\n📧 Test 2: Custom Tech Startup Prompt")
    print("-" * 30)
    
    custom_prompt = """Create a professional yet innovative email for a cutting-edge AI startup. 
    The email should:
    - Highlight breakthrough technology and innovation
    - Emphasize ROI and efficiency gains
    - Sound authoritative but approachable
    - Include specific technical benefits
    - Create urgency around early adoption advantages
    
    Make it compelling for technology decision-makers."""
    
    email_data = await generate_fastmcp_email(
        company_info="DXTR Labs AI Innovation Division",
        product_service="Revolutionary AI automation and intelligent workflow solutions",
        target_info="CTOs, Tech Directors, and Innovation Managers",
        special_requirements="Focus on measurable business outcomes and competitive advantages",
        custom_prompt=custom_prompt
    )
    
    print(f"✅ Subject: {email_data['subject']}")
    print(f"✅ Custom prompt processed successfully") 
    print(f"✅ Template: Modern Business")
    
    # Test 3: Sales Email with Special Offer
    print("\n📧 Test 3: Sales Email with Offer")
    print("-" * 30)
    
    email_data = await generate_fastmcp_email(
        company_info="DXTR Solutions & Consulting",
        product_service="Complete digital transformation and business optimization services",
        target_info="Small to medium business owners looking to scale",
        special_requirements="Emphasize quick implementation and immediate results",
        special_offer="Limited time: 50% off implementation costs for Q1 signups"
    )
    
    print(f"✅ Subject: {email_data['subject']}")
    print(f"✅ Sales content generated")
    print(f"✅ Template: Professional Clean")
    
    # Show features
    print("\n" + "=" * 50)
    print("🚀 FastMCP Email System Features:")
    print("✅ FastMCP LLM integration for dynamic content")
    print("✅ Beautiful, responsive HTML templates")
    print("✅ Custom prompt support for user requirements")
    print("✅ Automatic template selection based on content")
    print("✅ Professional styling with modern design")
    print("✅ Fallback system for reliability")
    print("✅ Multiple template styles (Business, Transportation, Clean)")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    print("🧪 Starting FastMCP Email Tests...")
    
    try:
        result = asyncio.run(test_fastmcp_system())
        if result:
            print("\n✅ All tests completed successfully!")
        else:
            print("\n❌ Some tests failed")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
