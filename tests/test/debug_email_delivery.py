#!/usr/bin/env python3
"""
Quick Email Delivery Debug Test
Tests the actual email sending functionality to see where it's failing
"""
import sys
import os
import asyncio
import logging

# Add backend path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_email_delivery():
    """Test email delivery with the exact same flow as the frontend"""
    print("🚀 DEBUGGING EMAIL DELIVERY")
    print("=" * 50)
    
    try:
        # Import email systems
        from backend.simple_email_service import email_service
        from backend.mcp.drivers.email_send_driver import EmailSendDriver
        import os
        from dotenv import load_dotenv
        
        # Load environment
        load_dotenv('.env.local')
        
        # Check environment variables
        company_email = os.getenv('COMPANY_EMAIL')
        company_password = os.getenv('COMPANY_EMAIL_PASSWORD')
        
        print(f"📧 COMPANY_EMAIL: {company_email}")
        print(f"🔐 PASSWORD SET: {'Yes' if company_password else 'No'}")
        print()
        
        # Test 1: Configure email service  
        print("🧪 TEST 1: Configuring Email Service (PrivateMail)")
        if company_email and company_password:
            # Use PrivateMail SMTP settings
            email_service.configure(company_email, company_password, "mail.privateemail.com", 587)
            print("✅ Email service configured for PrivateMail")
        else:
            print("❌ Email credentials missing!")
            return
        
        # Test 2: Test SMTP connection
        print("\n🧪 TEST 2: Testing SMTP Connection")
        connection_result = email_service.test_connection()
        print(f"Connection Result: {connection_result}")
        
        if not connection_result.get('success'):
            print("❌ SMTP connection failed!")
            print(f"Error: {connection_result.get('error')}")
            return
        
        # Test 3: Direct email service test
        print("\n🧪 TEST 3: Direct Email Service Test")
        test_email = "slakshanand1105@gmail.com"
        direct_result = email_service.send_email(
            to_email=test_email,
            subject="Test Email from Automation System",
            body="This is a test email to verify delivery works."
        )
        print(f"Direct Email Result: {direct_result}")
        
        # Test 4: Email driver test (what the frontend uses)
        print("\n🧪 TEST 4: Email Driver Test (Frontend Path)")
        email_driver = EmailSendDriver(db_pool=None)  # Pass None for db_pool in testing
        
        driver_parameters = {
            "toEmail": test_email,
            "subject": "Driver Test Email",
            "text": "This email was sent via the EmailSendDriver (same as frontend uses)"
        }
        
        driver_result = await email_driver.execute(
            parameters=driver_parameters,
            input_data={},
            user_id="debug_user"
        )
        
        print(f"Driver Result: {driver_result}")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 SUMMARY:")
        if connection_result.get('success'):
            print("✅ SMTP Connection: Working")
        else:
            print("❌ SMTP Connection: Failed")
            
        if direct_result.get('success'):
            print("✅ Direct Email: Sent")
        else:
            print("❌ Direct Email: Failed")
            
        if driver_result.get('success', True):  # Driver might not return success key
            print("✅ Driver Email: Processed")
        else:
            print("❌ Driver Email: Failed")
            
        print(f"\n🎯 Check your inbox at {test_email} for test emails!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_email_delivery())
