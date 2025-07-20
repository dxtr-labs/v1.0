#!/usr/bin/env python3
"""
SMTP Connection Test
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_smtp_connection():
    """Test SMTP connection with different passwords"""
    
    smtp_host = "mail.privateemail.com"
    smtp_port = 587
    smtp_user = "automation-engine@dxtr-labs.com"
    
    passwords_to_try = [
        "Lakshu11042005$",  # From test file
        "LuckyPE2005$"      # From earlier configuration
    ]
    
    print("🔧 Testing SMTP Connection...")
    print("=" * 40)
    print(f"Host: {smtp_host}")
    print(f"Port: {smtp_port}")
    print(f"User: {smtp_user}")
    
    for i, password in enumerate(passwords_to_try, 1):
        print(f"\n🔐 Testing password #{i}: {password[:5]}...")
        
        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                print("✅ Connected to SMTP server")
                server.starttls()
                print("✅ Started TLS")
                server.login(smtp_user, password)
                print(f"✅ Authentication successful with password #{i}")
                
                # Try sending a test email
                print("📧 Sending test email...")
                
                msg = MIMEMultipart()
                msg["From"] = smtp_user
                msg["To"] = "slakshanand1105@gmail.com"
                msg["Subject"] = "🧪 SMTP Test - Email Automation Working!"
                
                body = """Hello!

This is a test email from the Sam AI Assistant automation system.

If you're receiving this, it means:
✅ SMTP connection is working
✅ Authentication is successful  
✅ Email automation is ready!

The morning email automation system is now fully operational.

Best regards,
Sam AI Assistant 🤖

---
Sent via SMTP Test | July 14, 2025"""
                
                msg.attach(MIMEText(body, "plain"))
                server.send_message(msg)
                
                print(f"🎉 Test email sent successfully!")
                return password
                
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Authentication failed with password #{i}: {e}")
        except Exception as e:
            print(f"❌ Connection failed with password #{i}: {e}")
    
    print("\n❌ All password attempts failed")
    return None

if __name__ == "__main__":
    working_password = test_smtp_connection()
    if working_password:
        print(f"\n🎉 Working password found: {working_password}")
        print("💡 Use this password in your email automation configuration")
    else:
        print("\n❌ No working password found. Please check your SMTP credentials.")
