# demo_fastmcp_emails.py
# Demonstration of FastMCP email generation with different prompts

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from email_sender import generate_fastmcp_email

async def demo_fastmcp_content_generation():
    """Demonstrate FastMCP content generation with different business types"""
    
    print("🚀 FastMCP Email Content Generation Demo")
    print("=" * 60)
    
    # Demo 1: Transportation Company 
    print("\n📧 DEMO 1: Transportation Company")
    print("-" * 40)
    
    transport_email = await generate_fastmcp_email(
        company_info="DXTR Transportation Services - Premium Charter and Corporate Travel",
        product_service="Luxury charter buses, corporate transportation, event shuttles, and executive travel services",
        target_info="Corporate event planners, business executives, and travel coordinators",
        special_requirements="Emphasize safety protocols, luxury amenities, and professional service",
        special_offer="Special corporate rates: 25% off first booking for new business clients"
    )
    
    print(f"✅ Subject: {transport_email['subject']}")
    print(f"✅ Template Type: Transportation Premium")
    print("✅ Content includes: Safety features, luxury amenities, professional drivers")
    
    # Demo 2: Tech Startup with Custom Prompt
    print("\n📧 DEMO 2: AI Tech Startup with Custom Prompt") 
    print("-" * 40)
    
    custom_ai_prompt = """Create a compelling email for a cutting-edge AI company that:
    
    🎯 TARGET: CTOs and Technology Directors at Fortune 500 companies
    🔥 TONE: Innovative, authoritative, yet approachable
    💡 KEY POINTS:
    - Emphasize breakthrough AI technology and measurable ROI
    - Highlight competitive advantages and first-mover benefits  
    - Include urgency around limited early-adopter program
    - Sound like a technology leader, not a salesperson
    - Focus on transformation, not just automation
    
    Make it irresistible for tech decision-makers who want to stay ahead."""
    
    ai_email = await generate_fastmcp_email(
        company_info="DXTR Labs AI Innovation Division",
        product_service="Revolutionary AI automation platform with cognitive workflow intelligence",
        target_info="Fortune 500 CTOs and Technology Directors seeking competitive advantages",
        special_requirements="Position as exclusive early-adopter opportunity for industry leaders",
        custom_prompt=custom_ai_prompt
    )
    
    print(f"✅ Subject: {ai_email['subject']}")
    print(f"✅ Template Type: Modern Business")
    print("✅ Custom Prompt: AI-focused messaging for tech executives")
    
    # Demo 3: Sales Email with Urgency
    print("\n📧 DEMO 3: High-Converting Sales Email")
    print("-" * 40)
    
    sales_email = await generate_fastmcp_email(
        company_info="DXTR Solutions & Consulting - Business Transformation Experts",
        product_service="Complete digital transformation packages with guaranteed ROI",
        target_info="Small to medium business owners ready to scale and modernize",
        special_requirements="Create urgency with limited-time offer and social proof",
        special_offer="Q1 ONLY: 50% off implementation + 6 months free support (Normally $25,000)"
    )
    
    print(f"✅ Subject: {sales_email['subject']}")
    print(f"✅ Template Type: Professional Clean")
    print("✅ Content includes: Urgency, social proof, clear value proposition")
    
    # Demo 4: Professional Services  
    print("\n📧 DEMO 4: Professional Business Services")
    print("-" * 40)
    
    business_email = await generate_fastmcp_email(
        company_info="DXTR Professional Services - Strategy & Implementation",
        product_service="Strategic consulting, project management, and business optimization services",
        target_info="Business owners and executives seeking expert guidance",
        special_requirements="Professional tone with focus on expertise and results"
    )
    
    print(f"✅ Subject: {business_email['subject']}")
    print(f"✅ Template Type: Modern Business")
    print("✅ Content: Professional consulting positioning")
    
    # Show system capabilities
    print("\n" + "=" * 60)
    print("🎯 FastMCP Email System Capabilities:")
    print("=" * 60)
    print("✅ LLM-Powered Content Generation:")
    print("   • Intelligent content based on business type analysis")
    print("   • Custom prompt support for specific requirements")
    print("   • Context-aware subject line generation")
    print("   • Personalized messaging for target audiences")
    print()
    print("✅ Beautiful Template System:")
    print("   • Transportation Premium (for travel/logistics)")
    print("   • Modern Business (for tech/professional services)")
    print("   • Professional Clean (for sales/offers)")
    print("   • Responsive HTML with modern design")
    print()
    print("✅ Smart Features:")
    print("   • Automatic template selection based on content")
    print("   • Fallback system for reliability")
    print("   • Professional styling with gradient backgrounds")
    print("   • Feature highlight sections for key benefits")
    print()
    print("✅ Customization Options:")
    print("   • Custom prompts for specific messaging needs")
    print("   • Company branding integration")
    print("   • Target audience personalization")
    print("   • Special offer and urgency messaging")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    print("🧪 Starting FastMCP Email Content Demo...")
    
    try:
        result = asyncio.run(demo_fastmcp_content_generation())
        if result:
            print("\n🎉 Demo completed successfully!")
            print("💡 FastMCP is now generating beautiful, intelligent emails!")
        else:
            print("\n❌ Demo encountered issues")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
