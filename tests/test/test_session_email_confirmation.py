#!/usr/bin/env python3
"""
🧪 SESSION-AWARE EMAIL CONFIRMATION TEST
Test email confirmation with proper session state management
"""

import requests
import json
import time

class EmailConfirmationTester:
    def __init__(self):
        self.base_url = "http://localhost:8002"
        self.session_token = None
        self.headers = None
        
    def login(self):
        """Login and establish session"""
        login_response = requests.post(f"{self.base_url}/api/auth/login", json={
            "email": "aitest@example.com",
            "password": "testpass123"
        })
        
        if login_response.status_code == 200:
            self.session_token = login_response.json().get("session_token")
            self.headers = {"Cookie": f"session_token={self.session_token}"}
            print("✅ Login successful")
            return True
        else:
            print("❌ Login failed")
            return False
    
    def send_message(self, message, step_name):
        """Send a message and analyze response"""
        print(f"\n📧 {step_name}")
        print("-" * 50)
        print(f"Message: {message}")
        
        try:
            response = requests.post(f"{self.base_url}/api/chat/mcpai", 
                json={"message": message},
                headers=self.headers,
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Analyze the response
                status = result.get('status', 'unknown')
                email_sent = result.get('email_sent', False)
                done = result.get('done', True)
                action_required = result.get('action_required')
                
                print(f"📊 Response Analysis:")
                print(f"   Status: {status}")
                print(f"   Email Sent: {email_sent}")
                print(f"   Done: {done}")
                print(f"   Action Required: {action_required}")
                
                # Check message content
                message_content = result.get('message', '')
                if 'email ready for review' in message_content.lower():
                    print(f"   ✅ Email preview detected")
                elif 'sent' in message_content.lower() and 'successfully' in message_content.lower():
                    print(f"   🎉 Email sent confirmation detected")
                elif 'perfect' in message_content.lower() and 'sent' in message_content.lower():
                    print(f"   🎉 Email delivery confirmation detected")
                
                # Show preview of message
                preview = message_content[:200].replace('\n', ' ')
                print(f"   📝 Message: {preview}...")
                
                return result
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"   Error: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"❌ Request error: {e}")
            return None

def test_email_confirmation_with_session():
    """Test email confirmation with proper session management"""
    
    print("🚀 SESSION-AWARE EMAIL CONFIRMATION TEST")
    print("=" * 60)
    print("Testing email confirmation with maintained session state")
    
    tester = EmailConfirmationTester()
    
    # Step 1: Login
    if not tester.login():
        return False
    
    # Step 2: Request email (should show preview)
    email_request = "Send an email to slakshanand1105@gmail.com about our TechCorp protein noodles and FastMCP automation services"
    result1 = tester.send_message(email_request, "STEP 1: Email Request")
    
    if not result1:
        print("❌ Step 1 failed")
        return False
    
    # Check if we got a preview
    if result1.get('status') != 'preview_ready':
        print("❌ Expected preview_ready status, got:", result1.get('status'))
        return False
    
    if result1.get('done') != False:
        print("❌ Expected done=False for preview, got:", result1.get('done'))
        return False
    
    print("✅ Step 1 successful: Email preview generated")
    
    # Step 3: Wait a moment (simulating user reading)
    time.sleep(2)
    
    # Step 4: Confirm the email
    confirmation_message = "yes, send it"
    result2 = tester.send_message(confirmation_message, "STEP 2: Email Confirmation")
    
    if not result2:
        print("❌ Step 2 failed")
        return False
    
    # Check if email was sent
    if result2.get('email_sent') == True and result2.get('status') == 'completed':
        print("🎉 SUCCESS: Email confirmation flow worked!")
        print("✅ Email was sent after confirmation")
        return True
    elif 'sent' in result2.get('message', '').lower() and 'successfully' in result2.get('message', '').lower():
        print("🎉 SUCCESS: Email sent (confirmed by message)")
        return True
    else:
        print("❌ FAILED: Email was not sent after confirmation")
        print(f"   Status: {result2.get('status')}")
        print(f"   Email Sent: {result2.get('email_sent')}")
        print(f"   Message: {result2.get('message', '')[:100]}...")
        return False

def main():
    """Run the session-aware test"""
    
    success = test_email_confirmation_with_session()
    
    print(f"\n🎯 FINAL RESULT")
    print("=" * 40)
    
    if success:
        print("✅ EMAIL CONFIRMATION FLOW: WORKING!")
        print("✅ Preview shown before sending")
        print("✅ User confirmation required")
        print("✅ Email sent after confirmation")
        print()
        print("🎉 The system is ready for production!")
        print("📧 Check slakshanand1105@gmail.com for the test email")
    else:
        print("❌ EMAIL CONFIRMATION FLOW: NEEDS DEBUGGING")
        print("🔧 The session state may not be persisting properly")
        print("💡 Try testing in the browser chat interface")
    
    print()
    print("📝 Next Steps:")
    print("   1. Test in the actual browser chat interface")
    print("   2. Verify the email was received")
    print("   3. Test with different confirmation phrases")

if __name__ == "__main__":
    main()
