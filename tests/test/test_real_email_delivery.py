#!/usr/bin/env python3
"""
Test Real Email Sending
This script tests the actual SMTP email delivery to verify emails are being sent.
"""

import sys
import os
import logging
from dotenv import load_dotenv

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)

# Load environment variables
load_dotenv('.env.local')

# Import the real email function
from backend.email_sender import send_email_directly

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_real_email_sending():
    """Test real email sending with SMTP"""
    
    logger.info("🎯 TESTING REAL EMAIL SENDING")
    logger.info("=" * 50)
    
    # Test email details
    to_email = "slakshanand1105@gmail.com"
    subject = "🔦 Test Email from DXTR Labs - Real SMTP"
    body = """🔦 Discover the Amazing BrightBeam Torch Lights! 🔦

Dear Valued Customer,

This is a test email to verify that our SMTP configuration is working correctly.

Our AI-powered automation system is now sending real emails through:
- SMTP Host: mail.privateemail.com
- Port: 587
- From: automation-engine@dxtr-labs.com

If you receive this email, the system is working perfectly!

Best regards,
DXTR Labs Automation Team

🚀 Powered by Custom MCP LLM System"""
    
    logger.info(f"📧 Sending test email to: {to_email}")
    logger.info(f"📝 Subject: {subject}")
    logger.info(f"📊 Content length: {len(body)} characters")
    
    # Send the email
    result = send_email_directly(
        to_email=to_email,
        subject=subject,
        body=body
    )
    
    logger.info("=" * 50)
    if result.get("success"):
        logger.info("🎉 SUCCESS!")
        logger.info("✅ Real email sent successfully!")
        logger.info(f"📧 Delivered to: {result.get('to')}")
        logger.info(f"📤 From: {result.get('from')}")
        logger.info(f"📝 Subject: {result.get('subject')}")
        logger.info("")
        logger.info("🔍 CHECK YOUR EMAIL!")
        logger.info("If you received the test email, the SMTP is working!")
    else:
        logger.error("❌ FAILURE!")
        logger.error(f"💥 Error: {result.get('error')}")
        logger.error("🔧 Check your SMTP configuration in .env.local")
    
    return result.get("success", False)

if __name__ == "__main__":
    success = test_real_email_sending()
    
    if success:
        print("\n🏆 Email delivery test completed successfully!")
        print("📧 Check slakshanand1105@gmail.com for the test email")
    else:
        print("\n❌ Email delivery test failed!")
        print("🔧 Check the error messages above")
