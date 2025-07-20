#!/usr/bin/env python3
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

def test_email_direct():
    """Test email sending directly"""
    
    # Email configuration
    smtp_server = "mail.privateemail.com"
    port = 587
    sender_email = "automation-engine@dxtr-labs.com"
    password = "Lakshu11042005$"
    
    to_email = "slakshanand1105@gmail.com"
    subject = "🔧 DXTR Labs Direct Email Test"
    
    body = """Hello!

This is a direct test email from DXTR Labs automation system.

We're testing our email functionality to make sure everything works properly.

If you receive this email, our system is working correctly!

Best regards,
DXTR Labs Team
Sam Rodriguez
Senior AI Solutions Consultant"""
    
    try:
        print(f"📧 Attempting to send email from {sender_email} to {to_email}")
        print(f"📡 Using SMTP Server: {smtp_server}:{port}")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = Header(subject, 'utf-8')
        
        # Add text part
        text_part = MIMEText(body, 'plain', 'utf-8')
        msg.attach(text_part)
        
        # Connect and send
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(sender_email, password)
        
        text = msg.as_string()
        server.sendmail(sender_email, [to_email], text)
        server.quit()
        
        print("✅ Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

if __name__ == "__main__":
    test_email_direct()
