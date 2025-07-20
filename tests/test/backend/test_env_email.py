"""
Load Email Configuration from .env and Test
"""

import os
from dotenv import load_dotenv
from simple_email_service import email_service

def load_email_from_env():
    """Load email configuration from .env file"""
    
    # Load environment variables from .env file
    load_dotenv()
    
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    
    print(f"🔧 Loading email config from .env:")
    print(f"SMTP Host: {smtp_host}")
    print(f"SMTP Port: {smtp_port}")
    print(f"SMTP User: {smtp_user}")
    print(f"SMTP Password: {'*' * len(smtp_password) if smtp_password else 'Not found'}")
    
    if not smtp_user or not smtp_password:
        print("❌ SMTP credentials not found in .env file")
        return False
    
    if smtp_password == "your_smtp_password":
        print("❌ SMTP password is still placeholder value")
        print("Please update SMTP_PASSWORD in .env file with actual password")
        return False
    
    # Configure email service
    email_service.configure(smtp_user, smtp_password, smtp_host, smtp_port)
    
    # Test connection
    print("\n🔌 Testing SMTP connection...")
    test_result = email_service.test_connection()
    
    if test_result["success"]:
        print("✅ Email configuration successful!")
        return True
    else:
        print(f"❌ SMTP connection failed: {test_result['error']}")
        return False

def send_test_email_to_user():
    """Send test email to the user"""
    recipient = "slakshanand1105@gmail.com"
    subject = "🎉 Email System Working!"
    body = """Hello!

Great news! Your automation system's email functionality is now working correctly.

✅ Email service configured successfully
✅ SMTP connection established
✅ Test email delivered

Your automation workflows can now send real emails!

Time: {datetime}

Best regards,
Your Automation Engine""".format(datetime=__import__('datetime').datetime.now())
    
    print(f"\n📧 Sending test email to {recipient}...")
    result = email_service.send_email(recipient, subject, body)
    
    if result["success"]:
        print("✅ Test email sent successfully!")
        print("🎯 Check your inbox (and spam folder)")
        return True
    else:
        print(f"❌ Failed to send email: {result['error']}")
        return False

if __name__ == "__main__":
    print("🎯 Email Configuration from .env")
    print("=" * 50)
    
    if load_email_from_env():
        print("\n" + "=" * 50)
        if send_test_email_to_user():
            print("\n🎉 Email system fully operational!")
            print("Your automation engine can now send emails to slakshanand1105@gmail.com")
        else:
            print("\n❌ Email sending failed")
    else:
        print("\n❌ Email configuration failed")
        print("Please check your .env file and SMTP credentials")
