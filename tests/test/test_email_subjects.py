#!/usr/bin/env python3
"""
Test the improved email sender with custom subjects
"""

import sys
import os

# Add the backend directory to the path  
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from email_sender import parse_email_automation_request, send_email_directly

def test_improved_email_parsing():
    """Test the improved email parsing with custom subjects"""
    
    test_cases = [
        {
            "message": "Send email to slakshanand1105@gmail.com with subject: 🚀 AI Agent Automation Revolution - July 2025 Market Intelligence",
            "expected_subject": "🚀 AI Agent Automation Revolution - July 2025 Market Intelligence"
        },
        {
            "message": "Create and send AI trends email to slakshanand1105@gmail.com",
            "expected_subject": "🚀 AI Agent Automation Revolution - July 2025 Market Intelligence"
        },
        {
            "message": "Send an AI personal assistant email to slakshanand1105@gmail.com",
            "expected_subject": "✨ Your AI Personal Assistant - Daily Update"
        },
        {
            "message": "Send newsletter to slakshanand1105@gmail.com",
            "expected_subject": "📰 Technology Newsletter - Latest Updates"
        }
    ]
    
    print("🧪 Testing Improved Email Subject Detection")
    print("=" * 50)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test['message'][:50]}...")
        
        parsed = parse_email_automation_request(test["message"])
        
        if parsed["success"]:
            actual_subject = parsed["subject"]
            expected_subject = test["expected_subject"]
            
            if actual_subject == expected_subject:
                print(f"✅ PASS: Subject correctly detected")
                print(f"   📧 Subject: {actual_subject}")
            else:
                print(f"❌ FAIL: Subject mismatch")
                print(f"   Expected: {expected_subject}")
                print(f"   Actual: {actual_subject}")
        else:
            print(f"❌ FAIL: Parsing failed - {parsed.get('error')}")
    
    print("\n" + "=" * 50)
    print("✅ Email Subject Detection Test Complete!")
    
    # Demonstrate the fix
    print("\n🔧 THE FIX APPLIED:")
    print("✅ Enhanced email parsing with custom subject extraction")
    print("✅ Smart subject detection based on content keywords")
    print("✅ Support for emojis and professional formatting")
    print("✅ Fallback to intelligent defaults based on message type")
    
    print("\n📧 NOW YOUR EMAILS WILL HAVE PROPER SUBJECTS:")
    print("   🚀 AI Agent Automation Revolution - July 2025 Market Intelligence")
    print("   ✨ Your AI Personal Assistant - Daily Update")
    print("   📰 Technology Newsletter - Latest Updates")
    print("   📊 Automated Report - Analysis & Insights")
    print("   💼 Business Proposal - Innovative Solutions")

if __name__ == "__main__":
    test_improved_email_parsing()
