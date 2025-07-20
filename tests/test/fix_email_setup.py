#!/usr/bin/env python3
"""
Email Setup Helper - Fix Email Delivery
"""
import os
from dotenv import load_dotenv

def setup_email_credentials():
    """Help user set up correct email credentials"""
    print("🔧 EMAIL DELIVERY FIX")
    print("=" * 50)
    
    load_dotenv('.env.local')
    current_email = os.getenv('COMPANY_EMAIL')
    
    print(f"❌ Current email failing: {current_email}")
    print()
    print("📋 To fix email delivery, you need:")
    print("1. A REAL Gmail account (like slakshanand1105@gmail.com)")
    print("2. Enable 2-Factor Authentication")
    print("3. Generate an App Password")
    print()
    print("🔗 Gmail App Password Setup:")
    print("1. Go to: https://myaccount.google.com/security")
    print("2. Enable 2-Step Verification")
    print("3. Go to App Passwords")
    print("4. Generate password for 'Mail'")
    print("5. Use that 16-character password (not your regular password)")
    print()
    print("💡 RECOMMENDED SETUP:")
    print("COMPANY_EMAIL=\"slakshanand1105@gmail.com\"")
    print("COMPANY_EMAIL_PASSWORD=\"your-16-character-app-password\"")
    print()
    
    # Check if we should use the recipient email as sender
    print("🤔 Since automation-engine@dxtr-labs.com doesn't exist,")
    print("   should we use slakshanand1105@gmail.com as the sender email?")
    print()
    print("This would mean:")
    print("• FROM: slakshanand1105@gmail.com")  
    print("• TO: slakshanand1105@gmail.com (or any other email)")
    print("• You'll get emails from yourself")
    
    return True

if __name__ == "__main__":
    setup_email_credentials()
