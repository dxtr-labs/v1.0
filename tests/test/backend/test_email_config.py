import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_email_config():
    """Test email sending with Gmail configuration"""
    
    # Gmail SMTP configuration
    smtp_host = "smtp.gmail.com"
    smtp_port = 587
    
    # For testing, let's use a simple configuration
    print("🔧 Email Configuration Test")
    print(f"SMTP Host: {smtp_host}")
    print(f"SMTP Port: {smtp_port}")
    
    # Check if we have email credentials
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    if not smtp_user or not smtp_password:
        print("❌ Missing email configuration")
        print("Please set SMTP_USER and SMTP_PASSWORD environment variables")
        return False
    
    try:
        # Test SMTP connection
        print(f"🔌 Testing connection to {smtp_host}...")
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            print("✅ SMTP connection successful!")
            return True
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        return False

def send_test_email(to_email: str):
    """Send a test email"""
    smtp_host = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    if not smtp_user or not smtp_password:
        return {"success": False, "error": "Email credentials not configured"}
    
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = "Test Email from Automation System"
        
        body = """
Hello!

This is a test email from your automation system.

If you received this, the email configuration is working correctly!

Best regards,
Automation Engine
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        print(f"✅ Test email sent to {to_email}")
        return {"success": True, "message": "Test email sent successfully"}
        
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("=== Email Configuration Test ===")
    
    # Test configuration
    if test_email_config():
        # Send test email
        test_email = "slakshanand1105@gmail.com"
        print(f"\n📧 Sending test email to {test_email}...")
        result = send_test_email(test_email)
        print(f"Result: {result}")
    else:
        print("\n❌ Please configure email settings first")
        print("1. Set environment variables:")
        print("   $env:SMTP_USER='your-email@gmail.com'")
        print("   $env:SMTP_PASSWORD='your-app-password'")
        print("2. For Gmail, enable 2FA and create App Password")
