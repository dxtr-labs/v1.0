"""
Debug Automation Detection Test
Test the OpenAI automation detection with detailed logging
"""
import requests
import json

def test_automation_detection_debug():
    """Test automation detection with debug output"""
    
    base_url = "http://localhost:8002"
    
    # Login
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "aitest@example.com", 
        "password": "testpass123"
    })
    
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    
    print("🔍 AUTOMATION DETECTION DEBUG TEST")
    print("=" * 50)
    
    # Very explicit automation request
    test_message = "Send email to slakshanand1105@gmail.com with subject 'Test Email' about TechCorp services"
    
    print(f"📧 Testing message: {test_message}")
    print(f"🎯 Expected: Automation detected, workflow generated")
    
    try:
        response = requests.post(f"{base_url}/api/chat/mcpai",
            json={"message": test_message},
            headers=headers,
            timeout=30
        )
        
        print(f"\n📋 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n📊 Response Analysis:")
            print(f"   Success: {result.get('success', 'unknown')}")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Action Required: {result.get('action_required', 'unknown')}")
            print(f"   Has Workflow JSON: {result.get('hasWorkflowJson', False)}")
            print(f"   Automation Type: {result.get('automation_type', 'none')}")
            print(f"   Workflow ID: {result.get('workflow_id', 'none')}")
            
            # Check for workflow field
            if 'workflow' in result:
                workflow = result['workflow']
                if workflow:
                    print(f"\n✅ WORKFLOW FOUND!")
                    print(f"   Workflow: {json.dumps(workflow, indent=2)}")
                else:
                    print(f"\n⚠️ Workflow field exists but is empty/null")
            else:
                print(f"\n❌ No 'workflow' field in response")
            
            # Full response for debugging
            print(f"\n📋 Full Response Keys: {list(result.keys())}")
            print(f"📝 Message: {result.get('message', 'No message')[:200]}...")
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_email_service_directly():
    """Test the email service directly"""
    print(f"\n📧 TESTING EMAIL SERVICE DIRECTLY")
    print("=" * 40)
    
    # Check if we can import and test the email service
    try:
        import sys
        import os
        sys.path.append('backend')
        
        # Try to import email service
        try:
            from simple_email_service import email_service
            print("✅ Email service imported successfully")
            
            # Test email configuration
            if hasattr(email_service, 'test_email_config'):
                config_result = email_service.test_email_config()
                print(f"📧 Email config test: {config_result}")
            else:
                print("⚠️ No test_email_config method found")
                
        except ImportError as e:
            print(f"❌ Could not import email service: {e}")
            
        # Check environment variables
        smtp_host = os.getenv('SMTP_HOST')
        smtp_port = os.getenv('SMTP_PORT')
        company_email = os.getenv('COMPANY_EMAIL')
        
        print(f"📧 Email Configuration:")
        print(f"   SMTP Host: {smtp_host or 'Not set'}")
        print(f"   SMTP Port: {smtp_port or 'Not set'}")
        print(f"   Company Email: {company_email or 'Not set'}")
        
        if not company_email:
            print("⚠️ COMPANY_EMAIL not configured - emails cannot be sent")
            
    except Exception as e:
        print(f"❌ Error checking email service: {e}")

if __name__ == "__main__":
    test_automation_detection_debug()
    test_email_service_directly()
    
    print(f"\n🎯 DEBUG SUMMARY:")
    print(f"• Check server logs for automation detection responses")
    print(f"• Verify OpenAI API is working for automation detection")
    print(f"• Confirm email credentials are configured")
    print(f"• Test workflow generation logic")
