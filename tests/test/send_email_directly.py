#!/usr/bin/env python3
"""
Direct email sending test - bypassing preview system
"""

import requests
import json

def send_email_directly():
    """Send email directly using the backend API"""
    base_url = "http://localhost:8002"
    
    print("🚀 DIRECT EMAIL SENDING TEST")
    print("=" * 50)
    
    # Login first
    print("🔐 Logging in...")
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "aitest@example.com", 
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    print("✅ Authentication successful")
    
    # Create email automation directly
    print("\n📧 Creating email automation...")
    
    email_payload = {
        "message": "Send an email to slakshanand1105@gmail.com with subject 'AI Competitors Research Results' and message 'Hello! Here are the top AI agent competitors in the market: 1. OpenAI (ChatGPT, GPT-4) - Leading conversational AI, 2. Anthropic (Claude) - Constitutional AI focused, 3. Google DeepMind (Bard, Gemini) - Search integrated AI, 4. Microsoft (Copilot) - Office productivity AI, 5. Midjourney - AI image generation, 6. Stability AI - Open source models, 7. Cohere - Enterprise AI platform, 8. Hugging Face - AI model hub, 9. Scale AI - Data platform for AI, 10. Character.AI - Conversational characters. These companies are leading the AI automation space with various specializations. Best regards, Your AI Assistant'"
    }
    
    try:
        response = requests.post(f"{base_url}/api/chat/mcpai",
            json=email_payload,
            headers=headers, 
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Email automation created")
            
            # Check if we got workflow
            if result.get('hasWorkflowJson') or result.get('workflow_json'):
                print("📋 Workflow detected")
                
                # Try to confirm the email
                print("\n🔄 Attempting to confirm email send...")
                
                confirm_payload = {
                    "message": "yes"
                }
                
                confirm_response = requests.post(f"{base_url}/api/chat/mcpai",
                    json=confirm_payload,
                    headers=headers,
                    timeout=30
                )
                
                print(f"Confirm Status: {confirm_response.status_code}")
                
                if confirm_response.status_code == 200:
                    confirm_result = confirm_response.json()
                    print("📧 Confirmation response received")
                    
                    # Check if email was actually sent
                    if 'sent' in confirm_result.get('message', '').lower() or confirm_result.get('email_sent'):
                        print("✅ EMAIL SENT SUCCESSFULLY!")
                        print(f"📧 Sent to: slakshanand1105@gmail.com")
                    else:
                        print("⚠️ Email confirmation processed but send status unclear")
                        print(f"Response: {confirm_result.get('message', 'No message')[:200]}")
                else:
                    print(f"❌ Confirmation failed: {confirm_response.status_code}")
                    print(f"Response: {confirm_response.text[:200]}")
            else:
                print("⚠️ No workflow detected in response")
                print(f"Response: {result.get('message', 'No message')[:200]}")
        else:
            print(f"❌ Email creation failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_email_service_directly():
    """Test the email service directly"""
    print("\n🔬 TESTING EMAIL SERVICE DIRECTLY")
    print("=" * 50)
    
    try:
        # Import the email service
        import sys
        sys.path.append('backend')
        from services.email_service import EmailService
        
        email_service = EmailService()
        
        # Test email
        email_data = {
            "to": "slakshanand1105@gmail.com",
            "subject": "AI Competitors Research - Direct Test",
            "message": """Hello!

This is a direct test of the email system. Here are the top 10 AI agent competitors:

1. **OpenAI** - ChatGPT, GPT-4, leading conversational AI
2. **Anthropic** - Claude, constitutional AI approach  
3. **Google DeepMind** - Bard, Gemini, search-integrated AI
4. **Microsoft** - Copilot, Office productivity AI
5. **Midjourney** - AI image generation leader
6. **Stability AI** - Open source AI models
7. **Cohere** - Enterprise AI platform
8. **Hugging Face** - AI model hub and community
9. **Scale AI** - Data platform for AI training
10. **Character.AI** - Conversational AI characters

These companies represent the current competitive landscape in AI automation and agent technologies.

Best regards,
Your AI Research Assistant

---
Sent via TechCorp FastMCP Automation System"""
        }
        
        print(f"📧 Attempting to send email to: {email_data['to']}")
        print(f"📝 Subject: {email_data['subject']}")
        
        result = email_service.send_email(email_data)
        
        if result:
            print("✅ EMAIL SENT SUCCESSFULLY via direct service!")
            print("📧 Check your inbox at slakshanand1105@gmail.com")
        else:
            print("❌ Direct email service failed")
            
    except ImportError as e:
        print(f"⚠️ Cannot import email service: {e}")
    except Exception as e:
        print(f"❌ Direct email test failed: {e}")

if __name__ == "__main__":
    send_email_directly()
    test_email_service_directly()
