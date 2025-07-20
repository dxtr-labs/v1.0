"""
Interactive Email Configuration and Testing Script
This script helps you set up and test email sending functionality.
"""

from simple_email_service import email_service
import getpass

def setup_email_config():
    """Interactive email configuration"""
    print("🔧 Email Configuration Setup")
    print("=" * 50)
    
    print("\nFor Gmail users:")
    print("1. Go to Google Account Settings")
    print("2. Enable 2-Factor Authentication")
    print("3. Go to Security > 2-Step Verification > App passwords")
    print("4. Generate an App password")
    print("5. Use that App password (not your regular password)")
    
    print("\n" + "=" * 50)
    
    # Get email configuration
    sender_email = input("Enter your email address: ").strip()
    if not sender_email:
        print("❌ Email address required")
        return False
    
    print(f"Email: {sender_email}")
    app_password = getpass.getpass("Enter your app password (input hidden): ").strip()
    if not app_password:
        print("❌ App password required")
        return False
    
    # Configure email service
    email_service.configure(sender_email, app_password)
    
    # Test connection
    print("\n🔌 Testing SMTP connection...")
    test_result = email_service.test_connection()
    
    if test_result["success"]:
        print("✅ Email configuration successful!")
        return True
    else:
        print(f"❌ Configuration failed: {test_result['error']}")
        print("\nCommon issues:")
        print("- Make sure 2FA is enabled")
        print("- Use App Password, not regular password")
        print("- Check email address spelling")
        return False

def send_test_email():
    """Send a test email"""
    recipient = input("Enter recipient email address: ").strip()
    if not recipient:
        recipient = "slakshanand1105@gmail.com"
        print(f"Using default: {recipient}")
    
    subject = "Test Email from Automation System"
    body = f"""Hello!

This is a test email from your automation system.

✅ Email configuration is working correctly!
🚀 Your automation engine can now send emails.

Time: {__import__('datetime').datetime.now()}

Best regards,
Automation Engine"""
    
    print(f"\n📧 Sending test email to {recipient}...")
    result = email_service.send_email(recipient, subject, body)
    
    if result["success"]:
        print("✅ Test email sent successfully!")
        print("Check the recipient's inbox (and spam folder)")
        return True
    else:
        print(f"❌ Failed to send email: {result['error']}")
        return False

def main():
    print("🎯 Email System Setup & Test")
    print("=" * 50)
    
    # Step 1: Configure email
    if not setup_email_config():
        print("\n❌ Email configuration failed. Please try again.")
        return
    
    # Step 2: Send test email
    print("\n" + "=" * 50)
    if send_test_email():
        print("\n🎉 Email system is fully operational!")
        print("Your automation workflows can now send real emails.")
    else:
        print("\n❌ Email sending failed. Please check configuration.")

if __name__ == "__main__":
    main()
