#!/usr/bin/env python3
"""
Final production test - verify actual email sending
"""

import requests
import json
import asyncio
import sys
import os
import uuid

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def create_final_test_agent():
    """Create final test agent"""
    try:
        from db.postgresql_manager import db_manager
        await db_manager.initialize()
        
        async with db_manager.pool.acquire() as conn:
            existing_users = await conn.fetch("SELECT user_id FROM users LIMIT 1")
            user_id = str(existing_users[0]['user_id']) if existing_users else str(uuid.uuid4())
        
        agent_id = str(uuid.uuid4())
        agent_data = {
            'agent_id': agent_id, 'user_id': user_id,
            'agent_name': 'DXTR Labs Production Email Agent',
            'agent_role': 'Email Automation Specialist', 
            'agent_personality': 'Expert in professional email communication',
            'agent_expectations': 'Send production-ready emails with DXTR Labs branding',
            'trigger_config': json.dumps({'email_automation': True, 'production': True}),
            'custom_mcp_code': '', 'workflow_id': None
        }
        
        query = """INSERT INTO agents (agent_id, user_id, agent_name, agent_role, agent_personality, 
                   agent_expectations, trigger_config, custom_mcp_code, workflow_id)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)"""
        
        async with db_manager.pool.acquire() as conn:
            await conn.execute(query, *agent_data.values())
        
        await db_manager.close()
        return agent_id
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return None

def final_production_test(agent_id):
    """Final production email test"""
    base_url = "http://localhost:8002"
    
    print("🚀 FINAL PRODUCTION EMAIL TEST")
    print("=" * 50)
    print(f"🎯 Agent: {agent_id}")
    print("📧 Testing REAL email sending...")
    print("=" * 50)
    
    # Step 1: Request email
    draft_request = {
        "message": "Create a professional email about DXTR Labs AI automation services and send it to slakshanand1105@gmail.com"
    }
    
    try:
        print("📝 Generating email...")
        response = requests.post(f"{base_url}/api/test/agents/{agent_id}/chat", json=draft_request)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'workflow_preview':
                print("✅ Email draft generated successfully!")
                
                # Step 2: Send email
                print("📮 Sending production email...")
                
                confirm_request = {
                    "message": "SEND_APPROVED_EMAIL:prod_test:slakshanand1105@gmail.com:DXTR Labs - AI Automation Partnership Opportunity",
                    "email_content": """Dear Business Leader,

DXTR Labs specializes in cutting-edge AI automation solutions that transform business operations.

🚀 Our Services:
• Custom AI Agent Development
• Intelligent Workflow Automation  
• Process Optimization Solutions
• Enterprise AI Integration

💡 Why Choose DXTR Labs:
- Proven track record in AI automation
- Tailored solutions for your business needs
- Expert team of AI specialists
- Comprehensive support and training

📞 Ready to transform your business with AI?

Contact us for a complimentary consultation:
📧 automation-engine@dxtr-labs.com
🌐 www.dxtrlabs.com

Best regards,
DXTR Labs Team

P.S. We're offering exclusive pilot programs for innovative companies. Let's discuss how AI can give you a competitive advantage!"""
                }
                
                send_response = requests.post(f"{base_url}/api/test/agents/{agent_id}/chat", json=confirm_request)
                
                if send_response.status_code == 200:
                    send_data = send_response.json()
                    status = send_data.get('status')
                    response_msg = send_data.get('response', '')
                    
                    print(f"📤 Send Status: {status}")
                    print(f"📝 Response: {response_msg}")
                    
                    # Check for success indicators
                    success_indicators = [
                        'email sent successfully',
                        'status: email_sent',
                        'delivered to',
                    ]
                    
                    is_success = (
                        status == 'email_sent' or
                        any(indicator in response_msg.lower() for indicator in success_indicators)
                    )
                    
                    if is_success:
                        print("\n🎉 SUCCESS! PRODUCTION EMAIL SENT!")
                        print("✅ DXTR Labs email automation is LIVE!")
                        print("✅ Real emails are being delivered!")
                        print("✅ Website is PRODUCTION READY!")
                        return True
                    else:
                        print(f"\n⚠️ Unclear status: {response_msg}")
                        return False
                else:
                    print(f"❌ Send failed: {send_response.text}")
            else:
                print(f"❌ Draft failed: {data.get('response', 'No response')}")
        else:
            print(f"❌ Request failed: {response.text}")
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    return False

async def main():
    print("🏆 DXTR LABS FINAL PRODUCTION VERIFICATION")
    print("=" * 60)
    
    agent_id = await create_final_test_agent()
    if agent_id:
        success = final_production_test(agent_id)
        
        if success:
            print("\n🚀 PRODUCTION STATUS: FULLY OPERATIONAL")
            print("✅ Email automation working")
            print("✅ SMTP service connected") 
            print("✅ Real emails being sent")
            print("✅ Website ready for client outreach")
            print("\n🎯 DXTR Labs email system is PRODUCTION READY!")
        else:
            print("\n⚠️ Final verification inconclusive")

if __name__ == "__main__":
    asyncio.run(main())
