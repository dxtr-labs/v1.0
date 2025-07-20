#!/usr/bin/env python3
"""
AI + Email Workflow Demo
Demonstrates different types of AI processing with email delivery
"""
import os
import sys
import requests
import json
import time

# Set SMTP environment variables
os.environ['SMTP_HOST'] = 'mail.privateemail.com'
os.environ['SMTP_PORT'] = '587'
os.environ['SMTP_USER'] = 'automation-engine@dxtr-labs.com'
os.environ['SMTP_PASSWORD'] = 'Lakshu11042005$'

BASE_URL = "http://127.0.0.1:8002"

def authenticate_user():
    """Quick authentication"""
    login_data = {"email": "aitest@example.com", "password": "testpass123"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        result = response.json()
        user_id = result.get('user', {}).get('user_id')
        session_token = result.get('session_token')
        return response.cookies, user_id, session_token
    return None, None, None

def create_workflow(user_id, prompt, recipient):
    """Create AI + Email workflow"""
    return {
        "workflow": {
            "workflow_id": f"demo-{int(time.time())}",
            "name": "AI Demo Workflow",
            "description": f"Demo AI processing for: {prompt[:50]}...",
            "user_id": user_id,
            "trigger": {"type": "manual", "name": "Demo Trigger"},
            "actions": [
                {
                    "action_id": "ai-001",
                    "node": "mcpLLM",
                    "name": "AI Processing",
                    "parameters": {
                        "prompt": prompt,
                        "context": "You are Sam, an AI assistant at DXTR Labs. Provide helpful, professional responses.",
                        "max_tokens": 1000,
                        "temperature": 0.7
                    }
                },
                {
                    "action_id": "email-001",
                    "node": "emailSend",
                    "name": "Email Delivery",
                    "parameters": {
                        "toEmail": recipient,
                        "subject": f"🤖 AI Demo - {prompt[:30]}...",
                        "text": f"""DXTR Labs AI + Email Automation Demo

Original Request: {prompt}

AI Response:
{"{ai_generated_content}"}

---
This email was generated and sent automatically by DXTR Labs' AI + Email automation system.

Demo completed on 2025-07-14
Powered by Sam AI Assistant"""
                    }
                }
            ]
        }
    }

def execute_workflow(cookies, session_token, workflow_json):
    """Execute workflow"""
    if session_token:
        cookies.set('session_token', session_token)
    
    response = requests.post(
        f"{BASE_URL}/api/automations/execute",
        json={"workflow_json": workflow_json},
        cookies=cookies,
        headers={"Content-Type": "application/json"}
    )
    return response.status_code == 200

def main():
    print("🚀 DXTR Labs AI + Email Automation Demo")
    print("=" * 50)
    
    # Authenticate
    cookies, user_id, session_token = authenticate_user()
    if not user_id:
        print("❌ Authentication failed")
        return
    
    print(f"✅ Authenticated as user: {user_id}")
    
    # Demo scenarios
    scenarios = [
        {
            "name": "Sales Pitch Demo",
            "prompt": "Create a sales pitch for DXTR Labs intelligent automation solutions",
            "description": "AI generates professional sales content"
        },
        {
            "name": "Automation Workflow Demo", 
            "prompt": "Help me create an automation workflow for email processing",
            "description": "AI suggests workflow automation"
        },
        {
            "name": "General AI Demo",
            "prompt": "Write a professional greeting for new customers",
            "description": "AI generates general business content"
        }
    ]
    
    recipient = input("\n📧 Enter recipient email: ").strip() or "slakshanand1105@gmail.com"
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🧪 Demo {i}: {scenario['name']}")
        print(f"📝 Prompt: {scenario['prompt']}")
        print(f"💡 Expected: {scenario['description']}")
        
        # Create and execute workflow
        workflow = create_workflow(user_id, scenario['prompt'], recipient)
        success = execute_workflow(cookies, session_token, workflow)
        
        if success:
            print(f"✅ Demo {i} executed successfully!")
            print(f"📧 AI-generated email sent to {recipient}")
        else:
            print(f"❌ Demo {i} failed")
        
        print("-" * 30)
    
    print(f"\n🎉 Demo Complete!")
    print(f"📱 Check {recipient} for 3 demo emails")
    print(f"🚀 DXTR Labs AI + Email automation is ready for production!")

if __name__ == "__main__":
    main()
