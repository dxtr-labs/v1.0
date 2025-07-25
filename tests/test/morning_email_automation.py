#!/usr/bin/env python3
"""
Production Morning Email Automation Script
Simple script to send daily morning positivity emails through the automation engine
"""
import os
import requests
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set SMTP environment variables (these should match your .env.local)
os.environ['SMTP_HOST'] = 'mail.privateemail.com'
os.environ['SMTP_PORT'] = '587'
os.environ['SMTP_USER'] = 'automation-engine@dxtr-labs.com'
os.environ['SMTP_PASSWORD'] = 'Lakshu11042005$'

# Configuration
BASE_URL = "http://127.0.0.1:8001"
EMAIL_RECIPIENT = "slakshanand1105@gmail.com"
USER_EMAIL = "morningautomation@example.com"
USER_PASSWORD = "automation123"

def get_current_date():
    """Get current date for email content"""
    return datetime.now().strftime("%B %d, %Y")

def authenticate():
    """Authenticate and get session token"""
    print("🔐 Authenticating...")
    
    # Login to get session
    login_data = {
        "email": USER_EMAIL,
        "password": USER_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        result = response.json()
        user_data = result.get('user', {})
        user_id = user_data.get('user_id')
        session_token = result.get('session_token')
        print(f"✅ Authenticated as: {user_data.get('email')}")
        return user_id, session_token
    else:
        print(f"❌ Authentication failed: {response.text}")
        return None, None

def create_morning_email_workflow(user_id, recipient_email):
    """Create workflow JSON for morning email"""
    current_date = get_current_date()
    
    workflow = {
        "workflow_id": f"morning-email-{datetime.now().strftime('%Y%m%d')}",
        "name": "Daily Morning Positivity Email",
        "description": f"Send daily morning positivity email to {recipient_email}",
        "user_id": user_id,
        "trigger": {
            "type": "manual",
            "name": "Manual Trigger",
            "description": "Daily morning email trigger"
        },
        "actions": [
            {
                "action_id": "morning-email-001",
                "node": "emailSend",
                "name": "Send Morning Positivity Email",
                "parameters": {
                    "toEmail": recipient_email,
                    "subject": f"🌅 Good Morning! Your Daily Dose of Positivity - {current_date}",
                    "text": f"""Good morning, beautiful soul! ☀️

"Every morning brings new potential, but only if you get up and seize it!" ✨

✨ YOUR DAILY AFFIRMATIONS ✨
🌟 Today is full of amazing opportunities waiting for me
💪 I have the strength and courage to achieve my dreams  
😊 I choose joy and positivity in everything I do
🚀 Every challenge is a chance for me to grow stronger
💖 I am grateful for this beautiful new day

🌈 Remember, you are amazing just as you are! Today is {current_date}, and it's going to be an incredible day.

The sun is shining just for you, the birds are singing your success song, and the universe is conspiring to make your dreams come true! ✨

Take a deep breath, smile that beautiful smile of yours, and step into this day with confidence. You've got this! 💪

Sending you warm hugs and positive vibes to start your day right! 🤗

Wishing you a day filled with joy, success, and beautiful moments! 🌺

With love and positivity,
Sam - Your Personal Assistant 🤖💖

---
📧 Generated by Sam AI Assistant | {current_date}
🌅 Daily Morning Positivity Automation"""
                }
            }
        ],
        "metadata": {
            "created_by": "Sam AI Assistant",
            "created_date": datetime.now().isoformat(),
            "purpose": "Daily morning motivation and positivity",
            "recipient": recipient_email,
            "execution_mode": "immediate"
        }
    }
    
    return workflow

def execute_workflow(user_id, session_token, workflow):
    """Execute the automation workflow"""
    print("🚀 Executing morning email automation...")
    
    # Automation engine expects workflow to be wrapped in a 'workflow' key
    payload = {
        "workflow_json": {
            "workflow": workflow
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/automations/execute",
        json=payload,
        cookies={"session_token": session_token},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Morning email sent successfully!")
        print(f"📧 Email delivered to: {EMAIL_RECIPIENT}")
        return True
    else:
        print(f"❌ Failed to send email: {response.text}")
        return False

def main():
    """Main execution function"""
    print("🌅 SAM AI ASSISTANT - DAILY MORNING EMAIL AUTOMATION")
    print("=" * 60)
    print(f"📅 Date: {get_current_date()}")
    print(f"📧 Recipient: {EMAIL_RECIPIENT}")
    print("=" * 60)
    
    # Step 1: Authenticate
    user_id, session_token = authenticate()
    if not user_id or not session_token:
        print("❌ Authentication failed. Exiting.")
        return False
    
    # Step 2: Create workflow
    workflow = create_morning_email_workflow(user_id, EMAIL_RECIPIENT)
    
    # Step 3: Execute automation
    success = execute_workflow(user_id, session_token, workflow)
    
    if success:
        print("🎉 SUCCESS! Daily morning email automation completed!")
        print("📱 Please check your email inbox!")
    else:
        print("❌ Morning email automation failed.")
    
    return success

if __name__ == "__main__":
    main()
