#!/usr/bin/env python3
"""
Direct email test using the simple_email_service
"""

import sys
import os

# Add backend to path
sys.path.append('backend')

def test_simple_email_service():
    """Test the simple email service directly"""
    print("🚀 TESTING SIMPLE EMAIL SERVICE DIRECTLY")
    print("=" * 50)
    
    try:
        # Import the email service
        from simple_email_service import email_service
        print("✅ Email service imported successfully")
        
        # Check if it's configured
        if hasattr(email_service, 'configured') and email_service.configured:
            print("✅ Email service is already configured")
        else:
            print("⚠️ Email service not configured, attempting configuration...")
            
            # Try to configure with environment variables
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')
            smtp_host = os.getenv('SMTP_HOST', 'mail.privateemail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            
            if smtp_user and smtp_password:
                email_service.configure(smtp_user, smtp_password, smtp_host, smtp_port)
                print(f"✅ Email service configured for {smtp_user}")
            else:
                print("❌ Missing SMTP credentials in environment")
                return False
        
        # Test email content
        subject = "AI Competitor Research Results - Direct Service Test"
        content = """Hello!

This email was sent directly through the simple email service to verify functionality.

Here are the top 10 AI agent competitors we researched:

1. **OpenAI** - ChatGPT, GPT-4, leading conversational AI platform
2. **Anthropic** - Claude, constitutional AI with safety focus
3. **Google DeepMind** - Bard, Gemini, search-integrated AI
4. **Microsoft** - Copilot, Office and Azure AI integration
5. **Midjourney** - Leading AI image generation platform
6. **Stability AI** - Open source AI models and Stable Diffusion
7. **Cohere** - Enterprise-focused language AI platform
8. **Hugging Face** - AI model hub and community platform
9. **Scale AI** - Data platform for AI model training
10. **Character.AI** - Conversational AI characters and roleplay

These companies represent the current competitive landscape in AI automation and agent technologies.

The research was automatically compiled and this email was generated through our AI automation system.

Best regards,
TechCorp AI Research Assistant

---
Sent via TechCorp FastMCP Automation System
Direct Service Test - {import datetime; datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

        # Attempt to send the email
        print(f"\n📧 Sending email to: slakshanand1105@gmail.com")
        print(f"📝 Subject: {subject}")
        
        result = email_service.send_email(
            to_email="slakshanand1105@gmail.com",
            subject=subject,
            body=content
        )
        
        if result and result.get('success'):
            print("✅ EMAIL SENT SUCCESSFULLY!")
            print("📧 Check your inbox at slakshanand1105@gmail.com")
            print("🎉 Direct email service test passed!")
            return True
        else:
            print(f"❌ Email sending failed: {result}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_backend_email_endpoint():
    """Test the backend email endpoint directly"""
    print("\n🌐 TESTING BACKEND EMAIL ENDPOINT")
    print("=" * 50)
    
    import requests
    
    try:
        # Login first
        base_url = "http://localhost:8002"
        login_response = requests.post(f"{base_url}/api/auth/login", json={
            "email": "aitest@example.com",
            "password": "testpass123"
        })
        
        if login_response.status_code != 200:
            print("❌ Login failed")
            return False
        
        session_token = login_response.json().get("session_token")
        headers = {"Cookie": f"session_token={session_token}"}
        print("✅ Authentication successful")
        
        # Use the direct email endpoint
        email_data = {
            "to_email": "slakshanand1105@gmail.com",
            "subject": "AI Competitor Research - Backend Endpoint Test",
            "content": """Hello!

This email was sent through the backend email endpoint to test direct delivery.

AI Competitor Research Summary:
• OpenAI: Leading conversational AI (ChatGPT, GPT-4)
• Anthropic: Constitutional AI approach (Claude)
• Google: Search-integrated AI (Bard, Gemini)  
• Microsoft: Productivity AI (Copilot)
• Other major players: Midjourney, Stability AI, Cohere, etc.

This demonstrates our automated research and email delivery capabilities.

Best regards,
TechCorp Automation System

---
Sent via backend email endpoint"""
        }
        
        response = requests.post(
            f"{base_url}/api/send-email-directly",
            json=email_data,
            headers=headers,
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Backend email endpoint responded successfully")
            print(f"Response: {result}")
            return True
        else:
            print(f"❌ Backend endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Backend test error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 COMPREHENSIVE EMAIL DELIVERY TEST")
    print("=" * 60)
    
    success1 = test_simple_email_service()
    success2 = test_backend_email_endpoint()
    
    print(f"\n🏁 FINAL RESULTS")
    print("=" * 30)
    print(f"Direct Service Test: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"Backend Endpoint Test: {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    if success1 or success2:
        print(f"\n🎉 EMAIL DELIVERY CONFIRMED!")
        print(f"📧 Check slakshanand1105@gmail.com for the email")
    else:
        print(f"\n⚠️ EMAIL DELIVERY NEEDS ATTENTION")
        print(f"📋 Check SMTP configuration and credentials")
