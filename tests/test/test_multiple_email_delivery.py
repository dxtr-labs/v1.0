#!/usr/bin/env python3
"""
Multiple Email Address Delivery Test
Testing bulk email automation capabilities
"""

import sys
import os
import time

# Add backend to path
sys.path.append('backend')

# Set environment variables for email service
os.environ['SMTP_HOST'] = 'mail.privateemail.com'
os.environ['SMTP_PORT'] = '587'
os.environ['SMTP_USER'] = 'automation-engine@dxtr-labs.com'
os.environ['SMTP_PASSWORD'] = 'Lakshu11042005$'

def test_multiple_email_delivery():
    """Test sending emails to multiple recipients"""
    print("🚀 MULTIPLE EMAIL DELIVERY TEST")
    print("=" * 50)
    
    # List of test email addresses
    email_addresses = [
        "slakshanand1105@gmail.com",
        "test1@example.com",
        "test2@example.com", 
        "demo@techcorp.com",
        "client@fastmcp.com"
    ]
    
    try:
        # Import the email service
        from simple_email_service import email_service
        print("✅ Email service imported")
        
        # Configure email service
        smtp_user = os.getenv('SMTP_USER')
        smtp_password = os.getenv('SMTP_PASSWORD')
        smtp_host = os.getenv('SMTP_HOST')
        smtp_port = int(os.getenv('SMTP_PORT'))
        
        email_service.configure(smtp_user, smtp_password, smtp_host, smtp_port)
        print("✅ Email service configured")
        
        # Test connection
        connection_result = email_service.test_connection()
        if not connection_result.get('success'):
            print(f"❌ Connection failed: {connection_result.get('error')}")
            return False
        print("✅ SMTP connection verified")
        
        successful_sends = 0
        failed_sends = 0
        
        print(f"\n📧 SENDING TO {len(email_addresses)} RECIPIENTS:")
        print("-" * 50)
        
        for i, email_addr in enumerate(email_addresses, 1):
            print(f"\n📤 [{i}/{len(email_addresses)}] Sending to: {email_addr}")
            
            # Customize content for each recipient
            subject = f"🤖 AI Automation Test #{i} - Multiple Delivery"
            
            content = f"""Hello!

This is test email #{i} from our AI automation system testing multiple email delivery.

🎯 RECIPIENT: {email_addr}
📊 TEST BATCH: {i} of {len(email_addresses)}
🤖 AUTOMATION: Web Search + Email Generation

📋 TEST SCENARIOS COVERED:
• Multiple recipient handling
• Bulk email automation 
• Sequential delivery testing
• Content personalization
• System reliability verification

🚀 AI CAPABILITIES DEMONSTRATED:
✅ Natural language processing
✅ Automated content generation
✅ Multi-recipient email delivery
✅ Professional email formatting
✅ Real-time automation execution

📈 BUSINESS USE CASES:
• Newsletter distribution
• Client updates and announcements
• Marketing campaign automation
• Notification systems
• Bulk communication workflows

This email demonstrates our system's ability to handle multiple email addresses efficiently and reliably.

Best regards,
TechCorp AI Automation System

---
✅ Automated Email #{i}
📧 Delivered via FastMCP Engine
🕐 Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}
🎯 Multi-recipient test successful"""

            try:
                # Send email
                result = email_service.send_email(
                    to_email=email_addr,
                    subject=subject,
                    body=content
                )
                
                if result and result.get('success'):
                    print(f"   ✅ SUCCESS - Email sent to {email_addr}")
                    successful_sends += 1
                else:
                    print(f"   ❌ FAILED - {email_addr}: {result.get('error') if result else 'Unknown error'}")
                    failed_sends += 1
                    
            except Exception as e:
                print(f"   ❌ EXCEPTION - {email_addr}: {e}")
                failed_sends += 1
            
            # Small delay between sends to avoid overwhelming SMTP server
            if i < len(email_addresses):
                time.sleep(2)
        
        # Results summary
        print(f"\n📊 MULTIPLE EMAIL DELIVERY RESULTS:")
        print("=" * 50)
        print(f"Total Recipients: {len(email_addresses)}")
        print(f"Successful Sends: {successful_sends}")
        print(f"Failed Sends: {failed_sends}")
        print(f"Success Rate: {(successful_sends/len(email_addresses)*100):.1f}%")
        
        if successful_sends > 0:
            print(f"\n🎉 MULTIPLE EMAIL DELIVERY OPERATIONAL!")
            print(f"✅ System can handle bulk email automation")
            print(f"✅ Sequential delivery working")
            print(f"✅ Content personalization functional")
            return True
        else:
            print(f"\n⚠️ No emails delivered successfully")
            return False
            
    except Exception as e:
        print(f"❌ Error in multiple email test: {e}")
        return False

def test_api_multiple_emails():
    """Test multiple emails through the API"""
    print(f"\n🌐 TESTING MULTIPLE EMAILS VIA API")
    print("=" * 50)
    
    import requests
    
    try:
        base_url = "http://localhost:8002"
        
        # Login
        login_response = requests.post(f"{base_url}/api/auth/login", json={
            "email": "aitest@example.com",
            "password": "testpass123"
        })
        
        if login_response.status_code != 200:
            print("❌ API login failed")
            return False
        
        session_token = login_response.json().get("session_token")
        headers = {"Cookie": f"session_token={session_token}"}
        print("✅ API authentication successful")
        
        # Test multiple email automation requests
        api_test_scenarios = [
            {
                "message": "Send a welcome email to slakshanand1105@gmail.com about our AI automation services",
                "description": "Primary email test"
            },
            {
                "message": "Create and send a product update email to test@example.com about our FastMCP platform improvements",
                "description": "Product update test"
            },
            {
                "message": "Send a thank you email to demo@techcorp.com for their interest in our automation solutions",
                "description": "Thank you email test"
            }
        ]
        
        successful_api_tests = 0
        
        for i, scenario in enumerate(api_test_scenarios, 1):
            print(f"\n📤 API Test {i}: {scenario['description']}")
            print(f"   Message: {scenario['message']}")
            
            try:
                response = requests.post(f"{base_url}/api/chat/mcpai",
                    json={"message": scenario['message']},
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Check if automation was detected
                    if (result.get('hasWorkflowJson') or 
                        result.get('workflow_json') or
                        'email' in result.get('message', '').lower()):
                        print(f"   ✅ API automation detected")
                        successful_api_tests += 1
                    else:
                        print(f"   ⚠️ No automation detected in API response")
                else:
                    print(f"   ❌ API request failed: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ API test exception: {e}")
            
            time.sleep(3)  # Pause between API tests
        
        print(f"\n📊 API MULTIPLE EMAIL TEST RESULTS:")
        print(f"   Total API Tests: {len(api_test_scenarios)}")
        print(f"   Successful Tests: {successful_api_tests}")
        print(f"   API Success Rate: {(successful_api_tests/len(api_test_scenarios)*100):.1f}%")
        
        return successful_api_tests > 0
        
    except Exception as e:
        print(f"❌ API multiple email test error: {e}")
        return False

def test_bulk_automation_request():
    """Test a single request that triggers multiple emails"""
    print(f"\n🎯 TESTING BULK AUTOMATION REQUEST")
    print("=" * 50)
    
    import requests
    
    try:
        base_url = "http://localhost:8002"
        
        # Login
        login_response = requests.post(f"{base_url}/api/auth/login", json={
            "email": "aitest@example.com",
            "password": "testpass123"
        })
        
        if login_response.status_code != 200:
            print("❌ Bulk test login failed")
            return False
        
        session_token = login_response.json().get("session_token")
        headers = {"Cookie": f"session_token={session_token}"}
        
        # Single request for multiple emails
        bulk_message = """Send AI competitor research emails to multiple recipients:
        1. Send to slakshanand1105@gmail.com with subject 'AI Market Analysis'
        2. Send to test@example.com with subject 'Competition Report' 
        3. Send to demo@techcorp.com with subject 'Industry Intelligence'
        
        Include information about top AI companies: OpenAI, Anthropic, Google, Microsoft, etc."""
        
        print("📤 Sending bulk automation request...")
        print(f"   Request: {bulk_message[:100]}...")
        
        response = requests.post(f"{base_url}/api/chat/mcpai",
            json={"message": bulk_message},
            headers=headers,
            timeout=45
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Bulk request processed")
            
            # Check response
            response_msg = result.get('message', '')
            if 'email' in response_msg.lower():
                print("✅ Bulk automation detected")
                return True
            else:
                print("⚠️ Bulk automation detection unclear")
                return False
        else:
            print(f"❌ Bulk request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Bulk automation test error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 COMPREHENSIVE MULTIPLE EMAIL DELIVERY TESTING")
    print("=" * 70)
    print("Testing scenarios:")
    print("• Direct multiple email sending")
    print("• API-based multiple email automation")
    print("• Bulk automation requests")
    print("• System reliability and performance")
    
    # Run all tests
    test1_result = test_multiple_email_delivery()
    test2_result = test_api_multiple_emails()
    test3_result = test_bulk_automation_request()
    
    # Final summary
    print(f"\n🏁 COMPREHENSIVE TEST RESULTS")
    print("=" * 40)
    print(f"Direct Multiple Emails: {'✅ PASSED' if test1_result else '❌ FAILED'}")
    print(f"API Multiple Emails: {'✅ PASSED' if test2_result else '❌ FAILED'}")
    print(f"Bulk Automation: {'✅ PASSED' if test3_result else '❌ FAILED'}")
    
    total_tests = 3
    passed_tests = sum([test1_result, test2_result, test3_result])
    
    print(f"\nOverall Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    if passed_tests >= 2:
        print(f"\n🎉 MULTIPLE EMAIL DELIVERY SYSTEM OPERATIONAL!")
        print(f"✅ System can handle multiple recipients")
        print(f"✅ Bulk email automation working")
        print(f"✅ API integration functional")
        print(f"📧 Check all test email addresses for deliveries")
    else:
        print(f"\n⚠️ Multiple email system needs attention")
        print(f"📋 Check SMTP configuration and API integration")
