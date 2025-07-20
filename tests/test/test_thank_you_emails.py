#!/usr/bin/env python3
"""
Test script to send thank you emails for 10 different genuine reasons
Focus on gratitude and appreciation, not sales pitches
"""

import requests
import json
import time

# Backend MCP endpoint
MCP_URL = "http://localhost:8002/api/mcp/chat"
EMAIL_URL = "http://localhost:8002/api/email/send"

def send_thank_you_email(reason, recipient_email):
    """Send a genuine thank you email for a specific reason"""
    
    # Generate thank you content using MCP AI
    mcp_payload = {
        "agent_id": "thank_you_agent",
        "message": f"Generate a genuine, heartfelt thank you message for: {reason}. Keep it warm, personal, and appreciative. No sales pitch, just pure gratitude. Include appropriate emojis. Maximum 200 words.",
        "context": {
            "task": "thank_you_email",
            "reason": reason,
            "tone": "grateful_and_warm"
        }
    }
    
    try:
        print(f"🤖 Generating thank you content for: {reason}")
        
        # Get AI-generated thank you content
        mcp_response = requests.post(MCP_URL, json=mcp_payload, timeout=30)
        
        if mcp_response.status_code != 200:
            print(f"❌ MCP API Error: {mcp_response.status_code} - {mcp_response.text}")
            return False
            
        ai_content = mcp_response.json().get("response", "Thank you for your kindness! 🙏")
        
        # Prepare email
        email_payload = {
            "to": recipient_email,
            "subject": f"Thank You! 🙏 - {reason}",
            "body": ai_content
        }
        
        print(f"📧 Sending thank you email...")
        print(f"   Subject: {email_payload['subject']}")
        print(f"   Content Preview: {ai_content[:100]}...")
        
        # Send email
        email_response = requests.post(EMAIL_URL, json=email_payload, timeout=15)
        
        if email_response.status_code == 200:
            print(f"✅ Thank you email sent successfully!")
            return True
        else:
            print(f"❌ Email sending failed: {email_response.status_code} - {email_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    recipient_email = "slakshanand1105@gmail.com"
    
    # 10 different genuine thank you reasons
    thank_you_reasons = [
        "Being an amazing friend and always being there when needed",
        "Your mentorship and guidance that helped me grow",
        "The delicious homemade cookies you shared last week", 
        "Helping me move to my new apartment over the weekend",
        "Your thoughtful birthday surprise that made my day special",
        "Listening to me during a difficult time and offering support",
        "Sharing your expertise and teaching me new skills",
        "The beautiful flowers you brought to brighten my office",
        "Your patience and understanding during our project collaboration",
        "Simply being such a positive and inspiring person in my life"
    ]
    
    print("🙏 Starting Thank You Email Campaign")
    print("=" * 50)
    
    success_count = 0
    failed_numbers = [1, 3, 4, 6, 7, 9]  # Numbers that failed previously
    
    for i, reason in enumerate(thank_you_reasons, 1):
        print(f"\n📨 Thank You Email #{i}")
        print(f"Reason: {reason}")
        
        # Add small delay between emails
        if i > 1:
            time.sleep(2)
        
        success = send_thank_you_email(reason, recipient_email)
        
        if success:
            success_count += 1
            print(f"✅ Email #{i} delivered successfully")
        else:
            print(f"❌ Email #{i} failed to send")
    
    print("\n" + "=" * 50)
    print(f"🎉 Thank You Campaign Complete!")
    print(f"📊 Success Rate: {success_count}/10 emails sent")
    print(f"📧 All emails sent to: {recipient_email}")
    print("💝 Spreading gratitude and appreciation!")

if __name__ == "__main__":
    main()
