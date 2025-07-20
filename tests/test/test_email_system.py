#!/usr/bin/env python3
# Test email functionality with proper debugging

import sys
import os
sys.path.append('.')

from backend.email_sender import send_email_directly
import logging

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_email_delivery():
    """Test email delivery with debugging"""
    
    print("🧪 Testing Email Delivery System")
    print("=" * 50)
    
    # Test email content
    to_email = "slakshanand1105@gmail.com"
    subject = "🔧 Email System Test - Please Check"
    plain_body = """Hello!

This is a test email from the enhanced MCP automation system.

Key Test Information:
✅ Encoding: UTF-8 with special characters: áéíóú, 中文, 🚀
✅ Content: Plain text format
✅ Time: 2025-07-13 04:40 AM
✅ System: Enhanced MCP LLM automation

If you receive this email, the basic email functionality is working.
Please check your spam folder if you don't see it in your inbox.

Best regards,
Automation Test System
    """
    
    html_body = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Email Test</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">🔧 Email System Test</h2>
        
        <p><strong>Hello!</strong></p>
        
        <p>This is a test email from the enhanced MCP automation system.</p>
        
        <div style="background: #e8f4fd; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #2980b9;">Key Test Information:</h3>
            <ul>
                <li>✅ <strong>Encoding:</strong> UTF-8 with special characters: áéíóú, 中文, 🚀</li>
                <li>✅ <strong>Content:</strong> HTML format with styling</li>
                <li>✅ <strong>Time:</strong> 2025-07-13 04:40 AM</li>
                <li>✅ <strong>System:</strong> Enhanced MCP LLM automation</li>
            </ul>
        </div>
        
        <p style="background: #d5f4e6; padding: 10px; border-radius: 5px; border-left: 4px solid #27ae60;">
            <strong>📧 Delivery Test:</strong> If you receive this email, the email functionality is working correctly!
        </p>
        
        <p style="color: #e74c3c;">
            <strong>📁 Important:</strong> Please check your spam folder if you don't see it in your inbox.
        </p>
        
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #ecf0f1;">
        
        <p style="color: #7f8c8d; font-size: 12px;">
            Best regards,<br>
            Automation Test System<br>
            <em>Enhanced MCP LLM Engine</em>
        </p>
    </div>
</body>
</html>
    """
    
    print(f"📧 Sending test email to: {to_email}")
    print(f"📝 Subject: {subject}")
    print(f"🏷️ Content: Plain text + HTML")
    print()
    
    try:
        result = send_email_directly(to_email, subject, plain_body, html_body)
        
        print("📊 Email Send Result:")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        if result.get('error'):
            print(f"   Error: {result['error']}")
            
        if result.get('success'):
            print()
            print("🎉 Email sent successfully!")
            print("🔍 Next steps:")
            print("   1. Check your inbox: slakshanand1105@gmail.com")
            print("   2. Check spam/junk folder")
            print("   3. Look for subject: '🔧 Email System Test - Please Check'")
            print("   4. Email should have both plain text and HTML formatting")
        else:
            print()
            print("❌ Email sending failed!")
            print("🔧 Possible issues:")
            print("   1. SMTP credentials not configured")
            print("   2. Network connectivity issues")
            print("   3. SMTP server settings incorrect")
            
    except Exception as e:
        print(f"💥 Exception occurred: {e}")
        print(f"   Type: {type(e).__name__}")
        import traceback
        print("📋 Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_email_delivery()
