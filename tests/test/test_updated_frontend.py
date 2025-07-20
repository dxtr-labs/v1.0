#!/usr/bin/env python3
"""
Test the updated frontend email preview detection
"""

import requests
import json

def test_updated_frontend():
    """Test if the updated frontend will now detect email previews"""
    print("🎯 TESTING UPDATED FRONTEND EMAIL PREVIEW DETECTION")
    print("=" * 60)
    
    # Login
    print("🔐 Authenticating...")
    login_response = requests.post("http://localhost:8002/api/auth/login", json={
        "email": "aitest@example.com",
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    print("✅ Authentication successful")
    
    # Test email request
    test_message = """I am ceo and my name is Lakshanand Sugumar. We are proteinramen INC and we sell high protein ramen noodles. this is healthy.
Draft a sales pitch email about our company and send to slakshanand1105@gmail.com"""
    
    print(f"\n📤 Sending email request...")
    
    try:
        response = requests.post("http://localhost:8002/api/chat/mcpai",
            json={"message": test_message},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n🔍 FRONTEND DETECTION SIMULATION:")
            print("=" * 50)
            
            # Simulate the frontend checkForEmailPreview function
            email_content = result.get('email_content')
            recipient = result.get('recipient')
            email_subject = result.get('email_subject')
            
            print(f"✅ data.email_content exists: {'YES' if email_content else 'NO'}")
            print(f"✅ data.recipient exists: {'YES' if recipient else 'NO'}")
            print(f"✅ data.email_subject exists: {'YES' if email_subject else 'NO'}")
            
            if email_content and recipient:
                print(f"\n🎉 FRONTEND LOGIC MATCH:")
                print("✅ Method 8: Check for backend response with email_content + recipient")
                print("✅ This will trigger: showEmailPreview(emailPreviewInfo.preview_data, emailPreviewInfo.automation_result)")
                
                # Show what the frontend will construct
                preview_data = {
                    "to_email": recipient,
                    "subject": email_subject or 'Generated Email',
                    "content": email_content
                }
                
                print(f"\n📧 EMAIL PREVIEW DATA THAT WILL BE SHOWN:")
                print(f"   To: {preview_data['to_email']}")
                print(f"   Subject: {preview_data['subject']}")
                print(f"   Content: {preview_data['content'][:100]}...")
                
                return True
            else:
                print(f"\n❌ FRONTEND CONDITION NOT MET:")
                print(f"   Missing email_content: {'YES' if not email_content else 'NO'}")
                print(f"   Missing recipient: {'YES' if not recipient else 'NO'}")
                return False
                
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_updated_frontend()
    
    if success:
        print(f"\n✅ FRONTEND SHOULD NOW WORK!")
        print(f"📱 The email preview dialog should appear in mcp-enhanced-chat.html")
        print(f"🎯 Try your email request in the browser now!")
    else:
        print(f"\n❌ Frontend still needs fixes")
