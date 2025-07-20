"""
Debug Backend Automation Processing
Test what's happening between automation detection and workflow generation
"""
import requests
import json
import time

def debug_automation_processing():
    """Debug the automation processing pipeline"""
    
    base_url = "http://localhost:8002"
    
    # Login
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "aitest@example.com",
        "password": "testpass123"
    })
    
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    
    print("🔍 DEBUGGING AUTOMATION PROCESSING PIPELINE")
    print("=" * 60)
    
    # Set up context first
    print("📋 Setting up context...")
    context_msg = "My company is TechCorp and I'm the CEO"
    requests.post(f"{base_url}/api/chat/mcpai", json={"message": context_msg}, headers=headers)
    
    # Test with the simplest possible automation request
    simple_requests = [
        "Send email to slakshanand1105@gmail.com",
        "Email slakshanand1105@gmail.com about our company",
        "Create email for slakshanand1105@gmail.com"
    ]
    
    for i, request in enumerate(simple_requests, 1):
        print(f"\n🧪 Simple Test {i}: {request}")
        
        try:
            response = requests.post(f"{base_url}/api/chat/mcpai",
                json={"message": request},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract key information
                automation_type = result.get('automation_type', 'unknown')
                has_workflow = result.get('hasWorkflowJson', False)
                action_required = result.get('action_required', 'unknown')
                status = result.get('status', 'unknown')
                
                print(f"   📊 Backend Response:")
                print(f"      Automation Type: {automation_type}")
                print(f"      Has Workflow: {has_workflow}")
                print(f"      Action Required: {action_required}")
                print(f"      Status: {status}")
                
                # Check if there's any workflow data
                if 'workflow' in result:
                    print(f"      Workflow Field Present: {bool(result['workflow'])}")
                    if result['workflow']:
                        print(f"      Workflow Content: {result['workflow']}")
                
                # Look for automation keywords in response
                response_text = result.get('message', '').lower()
                automation_keywords = ['workflow', 'automation', 'email', 'send', 'create']
                found_keywords = [kw for kw in automation_keywords if kw in response_text]
                
                if found_keywords:
                    print(f"      Automation Keywords Found: {found_keywords}")
                
                # Check the specific response message
                print(f"      Response: {result.get('message', 'No message')[:100]}...")
                
                # If automation_type is 'conversational', that's our bug
                if automation_type == 'conversational':
                    print(f"   🚨 BUG FOUND: Should be 'email_automation' but got 'conversational'")
                elif automation_type == 'email_automation':
                    print(f"   ✅ Correct automation type detected!")
                    
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        time.sleep(2)
    
    return None

def test_direct_email_service():
    """Test the email service directly"""
    print(f"\n📧 TESTING EMAIL SERVICE DIRECTLY")
    print("=" * 40)
    
    try:
        # Test the email service components
        import sys
        import os
        sys.path.append('backend')
        
        # Try to import and test email service
        try:
            from backend.simple_email_service import email_service
            print("✅ Email service module found")
            
            # Check if we can create a test email
            test_email_data = {
                "recipient": "slakshanand1105@gmail.com",
                "subject": "Test Email from TechCorp",
                "content": "Hello! This is a test email from TechCorp's automation system."
            }
            
            print(f"📧 Test email data prepared:")
            print(f"   To: {test_email_data['recipient']}")
            print(f"   Subject: {test_email_data['subject']}")
            print(f"   Content: {test_email_data['content'][:50]}...")
            
            # Check if email service has a send method
            if hasattr(email_service, 'send_email'):
                print("✅ send_email method found")
                # We won't actually send here, just check the method exists
            else:
                print("⚠️ send_email method not found")
                
        except ImportError as e:
            print(f"❌ Could not import email service: {e}")
            
    except Exception as e:
        print(f"❌ Error testing email service: {e}")

if __name__ == "__main__":
    debug_automation_processing()
    test_direct_email_service()
    
    print(f"\n🎯 DEBUGGING SUMMARY:")
    print(f"We know OpenAI correctly detects automation, but backend returns 'conversational'")
    print(f"This suggests the issue is in the backend logic between detection and execution")
    print(f"The _detect_automation_intent method works, but _execute_automation_with_context might not be called")
    print(f"Or there's an error in the automation execution that falls back to conversational mode")
