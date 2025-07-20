#!/usr/bin/env python3

# Simple direct test without going through the API
import asyncio
import sys
import os

async def test_email_direct():
    """Test email sending directly"""
    print("🧪 Direct Email Test")
    print("=" * 30)
    
    # Add backend to path
    backend_path = os.path.join(os.path.dirname(__file__), "backend")
    sys.path.insert(0, backend_path)
    
    try:
        # Test if we can import the automation engine
        print("1️⃣ Testing imports...")
        from mcp.automation_engine import AutomationEngine
        print("✅ AutomationEngine imported")
        
        # Create automation engine
        print("2️⃣ Creating automation engine...")
        automation_engine = AutomationEngine()
        print("✅ AutomationEngine created")
        
        # Test email workflow
        print("3️⃣ Testing email workflow...")
        workflow_json = {
            "workflow": {
                "trigger": {
                    "node": "immediate",
                    "parameters": {
                        "trigger_type": "manual",
                        "user_input": "send email to slakshanand1105@gmail.com"
                    }
                },
                "actions": [
                    {
                        "node": "emailSend",
                        "parameters": {
                            "to": "slakshanand1105@gmail.com",
                            "subject": "Test Email from Direct Test",
                            "body": "This is a test email sent directly through the automation engine.",
                            "from": "automation-engine@dxtr-labs.com"
                        }
                    }
                ],
                "logic": []
            }
        }
        
        result = await automation_engine.execute_workflow(workflow_json, "test_user")
        
        print("📊 Execution result:")
        print(f"  Status: {result.get('status')}")
        print(f"  Success: {result.get('success', False)}")
        print(f"  Message: {result.get('message', 'No message')}")
        
        if result.get('status') == 'success':
            print("🎉 SUCCESS: Email should be sent!")
        else:
            print("❌ FAILED: Email not sent")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    return all_present

async def test_email_driver_direct():
    """Test email driver directly with SMTP credentials"""
    print("\n📧 Direct Email Driver Test")
    print("=" * 40)
    
    try:
        # Add backend to Python path
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        # Import email driver
        from mcp.drivers.email_send_driver import EmailSendDriver
        
        # Create driver instance
        email_driver = EmailSendDriver()
        
        # Test parameters
        email_params = {
            "toEmail": "slakshanand1105@gmail.com",
            "subject": "🏠 Test Email: Roomify Sales Pitch",
            "text": """
🏠 Find Your Perfect College Roommate with Roomify! 🎓

Hey there, future college superstar! 

Are you tired of scrolling through endless social media posts hoping to find that perfect roommate? Look no further! Roomify is here to revolutionize your college housing experience.

🌟 Why Choose Roomify?
✅ Smart Matching Algorithm - We pair you with compatible roommates based on lifestyle, study habits, and interests
✅ Verified Student Profiles - All users are verified college students, ensuring safety and authenticity
✅ Campus-Specific Search - Find roommates within your specific college or university
✅ Budget-Friendly Options - Filter by budget to find affordable housing solutions
✅ 24/7 Support - Our team is always here to help you navigate your housing journey

🎯 Special Features:
• Personality compatibility tests
• Shared interest matching
• Study schedule alignment
• Cleanliness preference matching
• Social activity level compatibility

🚀 Ready to find your perfect roommate? 
Join thousands of students who have already found their ideal living situation through Roomify!

Download the Roomify app today and start your journey to the perfect college living experience!

Best regards,
The Roomify Team
Your One-Stop Place for College Roommate Solutions
"""
        }
        
        print(f"📮 Sending test email...")
        print(f"  To: {email_params['toEmail']}")
        print(f"  Subject: {email_params['subject']}")
        print(f"  Content Length: {len(email_params['text'])} characters")
        
        # Execute email sending
        result = await email_driver.execute(
            parameters=email_params,
            input_data={},
            user_id="test-user-direct"
        )
        
        print(f"\n📊 Email Result:")
        print(f"  Status: {result.get('status')}")
        
        if result.get('status') == 'success':
            print(f"  ✅ Success: {result.get('message')}")
            print(f"  Recipients: {result.get('recipients')}")
            print(f"  Subject: {result.get('subject')}")
            print(f"\n🎉 EMAIL SUCCESSFULLY DELIVERED!")
            print(f"Check slakshanand1105@gmail.com for the Roomify sales pitch!")
            return True
        else:
            print(f"  ❌ Failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Email driver test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🚀 Complete Email Delivery Test")
    print("=" * 50)
    
    # Test 1: SMTP credentials
    smtp_ok = test_smtp_credentials()
    
    if not smtp_ok:
        print("\n❌ SMTP credentials not configured correctly!")
        return
    
    # Test 2: Direct email sending
    email_ok = await test_email_driver_direct()
    
    if email_ok:
        print("\n✅ ALL TESTS PASSED!")
        print("Your email system is now fully functional with SMTP configuration.")
    else:
        print("\n❌ Email delivery failed. Check SMTP settings and credentials.")

if __name__ == "__main__":
    asyncio.run(main())
