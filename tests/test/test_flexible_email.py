#!/usr/bin/env python3
"""
Test script for flexible email parameter system
"""
import requests
import json

# Test the flexible email parameter system
def test_flexible_email():
    print("🧪 Testing Flexible Email Parameter System")
    print("=" * 50)
    
    # Backend URL
    base_url = "http://127.0.0.1:8002"
    
    # Test different email request formats
    test_cases = [
        {
            "name": "Direct Email Request - Standard Parameters",
            "request": "send email to john@example.com with subject 'Meeting Tomorrow' and message 'Hi John, lets meet tomorrow at 3pm'"
        },
        {
            "name": "AI-Generated Sales Pitch",
            "request": "service:inhouse generate sales pitch for healthy ice cream send to sarah@company.com"
        },
        {
            "name": "Marketing Email with CC/BCC",
            "request": "send marketing email to team@startup.com with cc: manager@startup.com and bcc: admin@startup.com about our new product launch"
        },
        {
            "name": "Flexible Parameter Format",
            "request": "email recipient: alex@business.com title: Urgent Update content: Please review the quarterly report by end of day priority: high"
        },
        {
            "name": "AI Content Generation",
            "request": "service:openai create professional email to client@corporation.com about project completion"
        }
    ]
    
    # Test authentication first
    print("🔐 Testing Authentication...")
    try:
        # Try to get current user (this should work if backend is running)
        response = requests.get(f"{base_url}/current-user")
        if response.status_code == 401:
            print("⚠️ Not authenticated - need to login first")
            # For testing, we'll use a mock session
            print("📝 Note: In real usage, user would be authenticated via frontend")
        else:
            print("✅ Authentication check passed")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on port 8002")
        return
    
    print("\n🧪 Testing Email Parameter Extraction...")
    print("-" * 40)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"Request: {test_case['request']}")
        
        try:
            # Test the MCP LLM endpoint
            response = requests.post(f"{base_url}/api/chat/mcpai", 
                json={
                    "user_message": test_case['request'],
                    "agent_id": "test-agent"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Status: {result.get('status')}")
                
                # Check if workflow was generated
                if 'workflow_json' in result:
                    workflow = result['workflow_json']
                    print(f"📧 Email Type: {workflow.get('type')}")
                    print(f"📧 Recipient: {workflow.get('recipient')}")
                    print(f"🤖 AI Service: {workflow.get('ai_service')}")
                    
                    # Check email parameters in actions
                    if 'workflow' in workflow and 'actions' in workflow['workflow']:
                        for action in workflow['workflow']['actions']:
                            if action.get('node') == 'emailSend':
                                params = action.get('parameters', {})
                                print(f"📧 Email Parameters:")
                                for key, value in params.items():
                                    if value:  # Only show non-empty parameters
                                        print(f"   {key}: {value}")
                                break
                
                print(f"💡 Message: {result.get('message', 'No message')}")
                
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)
    
    print("\n🎯 Test Summary:")
    print("The flexible email parameter system should handle:")
    print("✓ Multiple parameter names (toEmail, to, recipient, email)")
    print("✓ Subject variations (subject, title, subjectLine)")
    print("✓ Content variations (content, text, body, message)")
    print("✓ CC/BCC support")
    print("✓ Priority settings")
    print("✓ AI service integration")
    print("✓ Template style options")
    
if __name__ == "__main__":
    test_flexible_email()
