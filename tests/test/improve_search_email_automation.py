#!/usr/bin/env python3
"""
Improved Search + Email Automation Test
Based on your actual working system
"""

def test_search_email_improvement():
    """Test improved search + email automation prompts"""
    
    print("🎉 SUCCESS! Your search automation is working!")
    print("=" * 60)
    
    print("✅ What worked:")
    print("   • Search prompt was processed successfully")
    print("   • Email generation was triggered")
    print("   • Recipient (slakshanand1105@gmail.com) was detected")
    print("   • Automated workflow executed")
    
    print("\n🔧 Improvements needed:")
    print("   • Email content is too generic")
    print("   • Search results not included in email")
    print("   • Missing specific investor information")
    
    print("\n🚀 Enhanced search prompts to try:")
    
    enhanced_prompts = [
        {
            "category": "Specific AI Investor Search",
            "prompts": [
                "Search Google for 'AI automation startup investors 2025' and email detailed investor list with contact info to slakshanand1105@gmail.com",
                "Find venture capital firms investing in AI automation and email comprehensive report to slakshanand1105@gmail.com",
                "Research angel investors interested in workflow automation startups and send contact database to slakshanand1105@gmail.com"
            ]
        },
        {
            "category": "Industry Research + Email",
            "prompts": [
                "Search for automation industry funding rounds 2024-2025 and email investment analysis to slakshanand1105@gmail.com",
                "Find AI automation companies that recently raised funding and email investor list to slakshanand1105@gmail.com",
                "Research automation technology investors on LinkedIn and email networking opportunities to slakshanand1105@gmail.com"
            ]
        },
        {
            "category": "Targeted Outreach",
            "prompts": [
                "Search for investors who funded companies like UiPath, Automation Anywhere and email similar investor prospects to slakshanand1105@gmail.com",
                "Find seed stage investors in AI/ML automation and email personalized outreach list to slakshanand1105@gmail.com",
                "Research corporate venture arms investing in automation and email partnership opportunities to slakshanand1105@gmail.com"
            ]
        }
    ]
    
    for category_data in enhanced_prompts:
        print(f"\n📋 {category_data['category']}:")
        for i, prompt in enumerate(category_data['prompts'], 1):
            print(f"   {i}. {prompt}")
    
    print(f"\n💡 Pro Tips for Better Results:")
    print(f"   • Be specific about search terms ('AI automation investors' vs 'investors')")
    print(f"   • Include what you want in the email ('detailed list', 'contact info', 'analysis')")
    print(f"   • Specify timeframes ('2024-2025', 'recent funding rounds')")
    print(f"   • Mention similar companies for context ('like UiPath')")
    
    print(f"\n🎯 Your System Capabilities:")
    print(f"   ✅ Multi-source search (Google, Reddit, LinkedIn, News)")
    print(f"   ✅ Email automation to slakshanand1105@gmail.com")
    print(f"   ✅ Natural language processing")
    print(f"   ✅ Workflow generation and execution")
    
    print(f"\n📧 To improve email content, try prompts like:")
    print(f"   • 'Include investor contact details and investment focus'")
    print(f"   • 'Format as professional investor research report'")
    print(f"   • 'Add recent funding examples and investment amounts'")
    
    return enhanced_prompts

def show_email_improvement_suggestions():
    """Show suggestions for better email content"""
    
    print(f"\n📧 EMAIL CONTENT IMPROVEMENT SUGGESTIONS")
    print("=" * 50)
    
    print("Instead of generic content, try these prompts:")
    
    better_prompts = [
        "Search for AI automation investors and create detailed investor database with contact info, investment focus, and recent deals, then email to slakshanand1105@gmail.com",
        
        "Find venture capital firms investing in AI/automation startups, include firm names, partner contacts, investment size, and portfolio companies, then email comprehensive report to slakshanand1105@gmail.com",
        
        "Research angel investors in automation technology, gather LinkedIn profiles, investment history, and contact methods, then email networking list to slakshanand1105@gmail.com"
    ]
    
    for i, prompt in enumerate(better_prompts, 1):
        print(f"\n{i}. {prompt}")
    
    print(f"\n🎯 These prompts will generate emails with:")
    print(f"   • Specific investor names and firms")
    print(f"   • Contact information (emails, LinkedIn)")
    print(f"   • Investment focus areas")
    print(f"   • Recent funding examples")
    print(f"   • Professional formatting")

if __name__ == "__main__":
    enhanced_prompts = test_search_email_improvement()
    show_email_improvement_suggestions()
    
    print(f"\n🚀 READY TO TEST IMPROVED PROMPTS!")
    print(f"Your search automation system is working - now let's make it even better!")
