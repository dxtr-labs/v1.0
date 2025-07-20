#!/usr/bin/env python3
"""
Test email sending functionality with DXTR Labs content
"""

import sys
import os
sys.path.append('backend')

def test_email_sending():
    try:
        # Read the generated HTML content
        with open('dxtr_email_preview.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print("📧 Testing email sending with DXTR Labs content...")
        
        # Import email sender
        from backend.email_sender import send_email_directly
        
        # Convert HTML to simple text for this test
        plain_text = "DXTR Labs - Your trusted partner for innovative architecture solutions. Contact us at info@dxtrlabs.com"
        
        # Test email sending
        result = send_email_directly(
            to_email="slakshanand1105@gmail.com",
            subject="Innovative Architecture Solutions from DXTR Labs",
            body=plain_text  # Using plain text for this test
        )
        
        if result.get("success"):
            print("✅ Email sent successfully!")
            print(f"📬 Delivered to: slakshanand1105@gmail.com")
            print(f"📧 Subject: Innovative Architecture Solutions from DXTR Labs")
            print(f"🎯 Message ID: {result.get('message_id', 'N/A')}")
            return True
        else:
            print(f"❌ Email sending failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"💥 Email test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_email_sending()
