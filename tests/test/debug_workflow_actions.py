import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

async def test_ai_workflow_actions():
    """Test that AI workflows are generating proper actions"""
    print("🔧 Testing AI Workflow Action Generation")
    print("=" * 50)
    
    try:
        # Add backend to path
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        # Import MCP orchestrator
        from mcp.simple_mcp_llm import MCP_LLM_Orchestrator
        
        orchestrator = MCP_LLM_Orchestrator()
        
        # Test scenarios
        test_scenarios = [
            {
                "name": "Roomify with inhouse AI",
                "prompt": "service:inhouse Using AI generate a sales pitch for Roomify - college roommate finder and send to test@example.com"
            },
            {
                "name": "Ice cream with AI service selection",
                "prompt": "Using AI generate a sales pitch for healthy ice cream business and send to test@example.com"
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n🧪 Test {i}: {scenario['name']}")
            print("-" * 40)
            print(f"Prompt: {scenario['prompt']}")
            
            # Process the request
            result = await orchestrator.process_user_input(
                user_id=f"test-user-{i}",
                agent_id=f"test-agent-{i}",
                user_message=scenario['prompt']
            )
            
            print(f"📊 Result Status: {result.get('status')}")
            print(f"📝 Message: {result.get('message', 'No message')}")
            
            # Check if workflow was generated
            if 'workflow_json' in result:
                workflow = result['workflow_json']
                print(f"✅ Workflow Generated:")
                print(f"  Type: {workflow.get('type')}")
                print(f"  Recipient: {workflow.get('recipient')}")
                print(f"  AI Service: {workflow.get('ai_service')}")
                
                # Check actions
                actions = workflow.get('actions', [])
                print(f"  Actions Count: {len(actions)}")
                
                for j, action in enumerate(actions):
                    print(f"    Action {j+1}:")
                    print(f"      Type: {action.get('action_type')}")
                    print(f"      Parameters: {list(action.get('parameters', {}).keys())}")
                    
                    # Show email parameters if it's an email action
                    if action.get('action_type') == 'emailSend':
                        params = action.get('parameters', {})
                        print(f"        To: {params.get('toEmail')}")
                        print(f"        Subject: {params.get('subject')}")
                        print(f"        Content: {params.get('text', '')[:50]}...")
                
                # Test workflow execution structure
                if len(actions) >= 2:
                    print(f"  ✅ Complete workflow: AI generation + Email sending")
                elif len(actions) == 1:
                    print(f"  ⚠️ Partial workflow: Only {actions[0].get('action_type')} action")
                else:
                    print(f"  ❌ Empty workflow: No actions generated")
            else:
                print(f"❌ No workflow generated")
                print(f"Full response: {result}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_quick_email_send():
    """Quick test of direct email sending"""
    print(f"\n📧 Quick Email Send Test")
    print("=" * 30)
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        
        # SMTP configuration
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_user = os.getenv("SMTP_USER") 
        smtp_pass = os.getenv("SMTP_PASSWORD")
        
        if not all([smtp_host, smtp_user, smtp_pass]):
            print("❌ SMTP credentials missing")
            return False
        
        # Quick test email
        msg = MIMEText("Test email from multi-topic AI system ✅")
        msg["From"] = smtp_user
        msg["To"] = "slakshanand1105@gmail.com"
        msg["Subject"] = "🧪 Multi-Topic AI Test - System Check"
        
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        
        print("✅ Quick email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Quick email failed: {e}")
        return False

async def main():
    print("🎯 AI Workflow Action Generation Debug")
    print("=" * 60)
    
    # Test 1: Workflow generation
    await test_ai_workflow_actions()
    
    # Test 2: SMTP verification
    email_ok = await test_quick_email_send()
    
    print(f"\n📋 Debug Summary:")
    print(f"✅ SMTP Configuration: {'Working' if email_ok else 'Failed'}")
    print(f"📧 Backend Status: {os.getenv('SMTP_HOST', 'Not configured')}")
    print(f"🤖 AI System: Checking workflow action generation...")

if __name__ == "__main__":
    asyncio.run(main())
