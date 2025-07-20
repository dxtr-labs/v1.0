#!/usr/bin/env python3
"""
Create a test agent directly and test email workflow
"""

import asyncio
import sys
import os
import uuid
import requests
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def create_test_agent():
    """Create a test agent directly in the database"""
    
    try:
        from db.postgresql_manager import db_manager
        
        # Initialize database connection
        await db_manager.initialize()
        
        # First, check if any users exist and create one if needed
        async with db_manager.pool.acquire() as conn:
            # Check for existing users
            existing_users = await conn.fetch("SELECT user_id FROM users LIMIT 1")
            
            if existing_users:
                user_id = str(existing_users[0]['user_id'])
                print(f"📊 Using existing user: {user_id}")
            else:
                # Create a test user
                user_id = str(uuid.uuid4())
                await conn.execute(
                    "INSERT INTO users (user_id, email, password_hash) VALUES ($1, $2, $3)",
                    user_id,
                    "test@dxtrlabs.com",
                    "test_hash"
                )
                print(f"👤 Created test user: {user_id}")
        
        # Generate agent ID
        agent_id = str(uuid.uuid4())
        
        # Create agent data with enhanced MCP and HR capabilities
        agent_data = {
            'agent_id': agent_id,
            'user_id': user_id,
            'agent_name': 'DXTR Labs HR Automation Specialist',
            'agent_role': 'HR Manager & Automation Expert', 
            'agent_personality': 'Professional HR specialist with deep knowledge of DXTR Labs platform, MCP protocol, and automation workflows. Expert in employee communication, onboarding, and HR processes.',
            'agent_expectations': 'Execute complex HR automation workflows using MCP protocol. Handle employee communications, recruitment outreach, onboarding sequences, and HR data processing. Always provide structured workflow previews before execution.',
            'trigger_config': json.dumps({
                'email_automation': True,
                'mcp_enabled': True,
                'hr_workflows': True,
                'structured_responses': True,
                'workflow_preview_required': True
            }),
            'custom_mcp_code': '''
# MCP HR Automation Protocol
class HRWorkflowEngine:
    def __init__(self):
        self.capabilities = ["email_automation", "employee_onboarding", "recruitment", "hr_communication"]
        self.company_info = {
            "name": "DXTR Labs",
            "mission": "Building AI agents to replace human workers",
            "platform": "DXT Agents for universal AI automation"
        }
    
    def generate_hr_workflow(self, request_type, recipient, context):
        return {
            "workflow_type": request_type,
            "recipient": recipient,
            "company_branding": self.company_info,
            "personalization": context
        }
''',
            'workflow_id': None
        }
        
        # Insert agent into database
        query = """
        INSERT INTO agents (agent_id, user_id, agent_name, agent_role, agent_personality, 
                           agent_expectations, trigger_config, custom_mcp_code, workflow_id)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """
        
        async with db_manager.pool.acquire() as conn:
            await conn.execute(
                query,
                agent_data['agent_id'],
                agent_data['user_id'],
                agent_data['agent_name'],
                agent_data['agent_role'],
                agent_data['agent_personality'],
                agent_data['agent_expectations'],
                agent_data['trigger_config'],
                agent_data['custom_mcp_code'],
                agent_data['workflow_id']
            )
        
        print(f"✅ Created test agent: {agent_id}")
        print(f"📝 Agent Name: {agent_data['agent_name']}")
        
        # Close database connection
        await db_manager.close()
        
        return agent_id
        
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        return None

def test_email_workflow(agent_id):
    """Test the email workflow with the created agent"""
    
    base_url = "http://localhost:8002"
    
    print(f"\n🧪 Testing Email Workflow with Agent: {agent_id}")
    print("=" * 50)
    
    # Step 1: Request HR automation workflow
    print("📝 Step 1: Requesting HR automation workflow...")
    
    draft_request = {
        "message": "As HR Manager, I need to send a professional recruitment email to a potential candidate at slakshanand1105@gmail.com about joining DXTR Labs. Highlight our AI automation platform, the exciting opportunity to work with cutting-edge DXT Agents, and our mission to revolutionize work with AI. Please create a workflow preview for me to review before sending."
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/test/agents/{agent_id}/chat",
            json=draft_request,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📤 Draft Request Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response Status: {data.get('status')}")
            print(f"🔄 Has Workflow Preview: {data.get('hasWorkflowPreview', False)}")
            print(f"🔍 Workflow Preview Data: {data.get('workflowPreview')}")
            print(f"🔍 Debug Info Keys: {data.get('debug_info', {}).get('response_keys', [])}")
            
            # Look for workflow preview in the debug data or other fields
            workflow_preview_found = (
                data.get('workflowPreview') or 
                data.get('workflow_preview') or
                data.get('hasWorkflowPreview', False)
            )
            
            if workflow_preview_found and data.get('status') == 'workflow_preview':
                print("🎉 Workflow preview mode detected - proceeding with email confirmation...")
                
                # Use HR-specific content
                recipient = "slakshanand1105@gmail.com"
                subject = "Exciting AI Engineering Opportunity at DXTR Labs - Join Our Revolutionary Platform"
                content = """Dear Talented Professional,

I hope this message finds you well. I'm reaching out from DXTR Labs, where we're building the future of work through AI automation.

🚀 About DXTR Labs:
We're developing a revolutionary platform that replaces human workers with intelligent, always-available AI agents called "DXT Agents." Our mission is to make AI agents universally accessible, allowing anyone to automate tasks as easily as texting a friend.

🎯 The Opportunity:
We're looking for exceptional talent to join our team as we build:
• DXT Agents with memory and personality
• Custom automation engine inspired by advanced workflow systems
• FastMCP LLM Protocol for multi-step conversational planning
• Next.js frontend with intuitive chat interfaces
• FastAPI backend with PostgreSQL integration

💡 Why DXTR Labs:
• Work on cutting-edge AI technology
• Shape the future of human-AI collaboration  
• Join a mission to make AI automation universal
• Opportunity to work with 2000+ automation templates
• Growing platform with 100+ users already on waitlist

🔮 Our Vision:
From email automation and scheduling to voice/call integration and plug-in marketplaces - we're building the complete AI workforce solution.

📞 Next Steps:
I'd love to discuss how your expertise could contribute to our revolutionary platform. Are you available for a conversation about this exciting opportunity?

Best regards,
DXTR Labs HR Team
automation-engine@dxtr-labs.com

P.S. We're moving fast in the AI automation space - let's connect soon to explore this opportunity!"""
                
                print(f"📧 Email Subject: {subject}")
                print(f"📧 Email Subject: {subject}")
                print(f"📧 Email Content Preview: {content[:150]}...")
                
                # Step 2: Confirm and send email
                print("\n📮 Step 2: Confirming and sending email...")
                
                # Test email confirmation
                confirm_request = {
                    "message": f"SEND_APPROVED_EMAIL:workflow_123:{recipient}:{subject}",
                    "email_content": content
                }
                
                print(f"📤 Sending confirmation request:")
                print(f"  Message: {confirm_request['message']}")
                print(f"  Email Content: {confirm_request['email_content'][:50]}...")
                
                confirm_response = requests.post(
                    f"{base_url}/api/test/agents/{agent_id}/chat",
                    json=confirm_request,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"📤 Confirm Request Status: {confirm_response.status_code}")
                
                if confirm_response.status_code == 200:
                    confirm_data = confirm_response.json()
                    print(f"✅ Final Status: {confirm_data.get('status')}")
                    print(f"📧 Email Sent: {confirm_data.get('email_sent', False)}")
                    print(f"🎯 Message: {confirm_data.get('message', 'No message')}")
                    
                    if confirm_data.get('email_sent'):
                        print("\n🎉 SUCCESS: Complete email automation workflow working!")
                        print(f"📬 Recipient: {confirm_data.get('recipient')}")
                        print(f"📝 Subject: {confirm_data.get('subject')}")
                        return True
                    else:
                        print("❌ Email was not sent")
                        print(f"📝 Response: {confirm_data.get('response')}")
                else:
                    print(f"❌ Confirm Request Failed: {confirm_response.text}")
            else:
                print("❌ No workflow preview in response")
                print(f"📝 Response: {data.get('response', 'No response')}")
        else:
            print(f"❌ Draft Request Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Test Error: {e}")
    
    return False

async def main():
    """Main test function"""
    print("🚀 Starting Complete Email Automation Test")
    print("=" * 50)
    
    # Create test agent
    agent_id = await create_test_agent()
    
    if agent_id:
        # Test email workflow
        success = test_email_workflow(agent_id)
        
        if success:
            print("\n✅ ALL TESTS PASSED: Email automation is working end-to-end!")
        else:
            print("\n❌ TEST FAILED: Issues found in email automation workflow")
    else:
        print("❌ Could not create test agent - cannot proceed with test")

if __name__ == "__main__":
    asyncio.run(main())
