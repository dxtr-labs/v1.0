#!/usr/bin/env python3
"""
Deep Email Delivery Debug - Check what's really happening
"""
import sys
import os
import asyncio
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add backend path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def deep_email_debug():
    """Deep debug of email delivery"""
    print("🔍 DEEP EMAIL DELIVERY DEBUG")
    print("=" * 60)
    
    try:
        from dotenv import load_dotenv
        load_dotenv('.env.local')
        
        # Get credentials
        company_email = os.getenv('COMPANY_EMAIL')
        company_password = os.getenv('COMPANY_EMAIL_PASSWORD')
        smtp_host = os.getenv('SMTP_HOST', 'mail.privateemail.com')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        
        print(f"📧 Email: {company_email}")
        print(f"🏠 SMTP Host: {smtp_host}")
        print(f"🔌 SMTP Port: {smtp_port}")
        print(f"🔐 Password Set: {'Yes' if company_password else 'No'}")
        print()
        
        # Test 1: Raw SMTP connection with detailed logging
        print("🧪 TEST 1: Raw SMTP Connection Test")
        try:
            print(f"Connecting to {smtp_host}:{smtp_port}...")
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.set_debuglevel(1)  # Enable debug output
            print("✅ Connected to SMTP server")
            
            print("Starting TLS...")
            server.starttls()
            print("✅ TLS started")
            
            print(f"Logging in as {company_email}...")
            server.login(company_email, company_password)
            print("✅ Login successful")
            
            # Test 2: Send a simple test email with full tracking
            print("\n🧪 TEST 2: Sending Raw Test Email")
            test_recipient = "slakshanand1105@gmail.com"
            
            msg = MIMEMultipart()
            msg['From'] = company_email
            msg['To'] = test_recipient
            msg['Subject'] = f"URGENT: Email Delivery Test - {os.getpid()}"
            
            body = f"""
This is a CRITICAL email delivery test.

Time: {os.popen('date /t && time /t').read().strip()}
From: {company_email}
To: {test_recipient}
SMTP Host: {smtp_host}
Test ID: EMAIL_DEBUG_{os.getpid()}

If you receive this email, delivery is working!
If not, there's an issue with the SMTP configuration.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            print(f"Sending email from {company_email} to {test_recipient}...")
            text = msg.as_string()
            result = server.sendmail(company_email, [test_recipient], text)
            
            if result:
                print(f"⚠️ SMTP returned errors: {result}")
            else:
                print("✅ SMTP sendmail completed without errors")
            
            server.quit()
            print("✅ SMTP connection closed")
            
        except Exception as smtp_error:
            print(f"❌ SMTP Error: {smtp_error}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 3: Check if emails are being filtered
        print("\n🧪 TEST 3: Email Filtering Check")
        print("📋 Possible reasons emails aren't delivered:")
        print("1. PrivateMail account might be suspended/limited")
        print("2. Gmail is filtering emails as spam")
        print("3. PrivateMail SMTP limits for new accounts")
        print("4. Authentication issues with PrivateMail")
        print("5. Email might be in spam/junk folder")
        
        print("\n🔍 CHECK THESE LOCATIONS:")
        print(f"• Gmail Inbox: https://mail.google.com/")
        print(f"• Gmail Spam: Check spam/junk folder")
        print(f"• Gmail All Mail: Check all mail folder")
        print(f"• Search Gmail for: 'from:{company_email}'")
        
        # Test 4: Alternative email test
        print("\n🧪 TEST 4: Let's try a different approach")
        print("Would you like me to:")
        print("1. Test with a different email service (like Gmail)")
        print("2. Check PrivateMail account status")
        print("3. Use a different recipient email")
        print("4. Test with plain text only (no HTML)")
        
        print(f"\n🎯 IMPORTANT: Check your email now!")
        print(f"Subject: 'URGENT: Email Delivery Test - {os.getpid()}'")
        print(f"From: {company_email}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(deep_email_debug())
