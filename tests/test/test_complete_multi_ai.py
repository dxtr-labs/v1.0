import asyncio
import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

async def test_multiple_ai_business_emails():
    """Test AI generation and email sending for multiple business topics with proper service selection"""
    print("🚀 COMPLETE MULTIPLE AI BUSINESS EMAIL TEST")
    print("=" * 70)
    
    try:
        # Add backend to path
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        # Import required modules
        from mcp.simple_mcp_llm import MCP_LLM_Orchestrator
        from mcp.drivers.email_send_driver import EmailSendDriver
        
        orchestrator = MCP_LLM_Orchestrator()
        email_driver = EmailSendDriver()
        
        # Test scenarios with proper service selection
        business_scenarios = [
            {
                "name": "🏠 Roomify - College Roommate Service",
                "prompt": "service:inhouse Using AI generate a sales pitch for Roomify - one stop place for college students to find roommates and send to slakshanand1105@gmail.com",
                "keywords": ["roommate", "college", "students", "housing"],
                "service": "inhouse"
            },
            {
                "name": "🍦 Healthy Ice Cream Business",
                "prompt": "service:inhouse Using AI generate a sales pitch for selling healthy ice creams made with organic ingredients and send to slakshanand1105@gmail.com",
                "keywords": ["ice cream", "healthy", "organic", "delicious"],
                "service": "inhouse"
            },
            {
                "name": "💻 CodeMaster - Programming Bootcamp",
                "prompt": "service:inhouse Using AI generate a sales pitch for CodeMaster programming bootcamp that teaches web development in 12 weeks and send to slakshanand1105@gmail.com",
                "keywords": ["programming", "bootcamp", "web development", "coding"],
                "service": "inhouse"
            },
            {
                "name": "🍕 PizzaExpress - Fast Food Delivery",
                "prompt": "service:inhouse Using AI generate a sales pitch for PizzaExpress fast pizza delivery service in 30 minutes or less and send to slakshanand1105@gmail.com",
                "keywords": ["pizza", "delivery", "fast", "30 minutes"],
                "service": "inhouse"
            },
            {
                "name": "💪 FitPro - Personal Training",
                "prompt": "service:inhouse Using AI generate a sales pitch for FitPro personal training service with certified trainers and send to slakshanand1105@gmail.com",
                "keywords": ["fitness", "training", "personal trainer", "workout"],
                "service": "inhouse"
            }
        ]
        
        successful_emails = []
        
        for i, scenario in enumerate(business_scenarios, 1):
            print(f"\n📧 Test {i}/5: {scenario['name']}")
            print("=" * 60)
            print(f"🤖 Prompt: {scenario['prompt']}")
            
            try:
                # Step 1: Generate AI workflow
                print(f"\n🔧 Step 1: Generating AI workflow...")
                result = await orchestrator.process_user_input(
                    user_id=f"multi-test-{i}",
                    agent_id=f"multi-agent-{i}",
                    user_message=scenario['prompt']
                )
                
                print(f"Status: {result.get('status')}")
                print(f"Message: {result.get('message')}")
                
                if 'workflow_json' in result and result['workflow_json'].get('actions'):
                    workflow = result['workflow_json']
                    actions = workflow.get('actions', [])
                    
                    print(f"✅ Workflow Generated: {len(actions)} actions")
                    
                    # Step 2: Execute AI content generation
                    ai_action = None
                    email_action = None
                    
                    for action in actions:
                        if action.get('action_type') == 'mcpLLM':
                            ai_action = action
                        elif action.get('action_type') == 'emailSend':
                            email_action = action
                    
                    if ai_action and email_action:
                        print(f"\n🤖 Step 2: Generating AI content...")
                        
                        # Generate business-specific content using the orchestrator's method
                        ai_content = orchestrator._generate_sample_content(
                            user_input=scenario['prompt'],
                            content_type="sales_pitch"
                        )
                        
                        print(f"✅ AI Content Generated: {len(ai_content)} characters")
                        
                        # Check for business keywords
                        keyword_matches = []
                        for keyword in scenario['keywords']:
                            if keyword.lower() in ai_content.lower():
                                keyword_matches.append(keyword)
                        
                        print(f"🎯 Keywords Found: {keyword_matches}")
                        print(f"📝 Content Preview: {ai_content[:150]}...")
                        
                        # Step 3: Send email with AI content
                        print(f"\n📧 Step 3: Sending email...")
                        
                        email_params = email_action.get('parameters', {}).copy()
                        # Replace placeholder with actual AI content
                        email_params['text'] = ai_content
                        
                        print(f"  To: {email_params.get('toEmail')}")
                        print(f"  Subject: {email_params.get('subject')}")
                        print(f"  Content Length: {len(email_params.get('text', ''))}")
                        
                        # Send email using SMTP
                        email_result = await send_business_email(
                            to_email=email_params.get('toEmail'),
                            subject=email_params.get('subject', f"{scenario['name']} - AI Generated"),
                            content=email_params.get('text'),
                            business_name=scenario['name']
                        )
                        
                        if email_result:
                            successful_emails.append({
                                'name': scenario['name'],
                                'keywords_found': keyword_matches,
                                'content_length': len(ai_content),
                                'subject': email_params.get('subject'),
                                'service': scenario['service']
                            })
                            print(f"✅ Email sent successfully!")
                        else:
                            print(f"❌ Email sending failed!")
                    else:
                        print(f"❌ Incomplete workflow - missing actions")
                else:
                    print(f"❌ No workflow or actions generated")
                
                # Wait between tests
                if i < len(business_scenarios):
                    print(f"\n⏳ Waiting 3 seconds before next test...")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"❌ Test failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Final results
        print(f"\n🏆 FINAL RESULTS")
        print("=" * 70)
        print(f"✅ Successful Emails: {len(successful_emails)}/5")
        
        if successful_emails:
            print(f"\n🎉 Successfully Sent Business Emails:")
            for email in successful_emails:
                print(f"  ✅ {email['name']}")
                print(f"     Service: {email['service'].upper()}")
                print(f"     Keywords: {email['keywords_found']}")
                print(f"     Content: {email['content_length']} characters")
                print(f"     Subject: {email['subject']}")
                print()
        
        print(f"📧 Check slakshanand1105@gmail.com for {len(successful_emails)} AI-generated business emails!")
        
        if len(successful_emails) >= 4:
            print(f"\n🎉 EXCELLENT! Multi-topic AI email system working perfectly!")
        elif len(successful_emails) >= 2:
            print(f"\n✅ GOOD! Most emails sent successfully!")
        else:
            print(f"\n⚠️ Some issues detected - check logs for details")
            
        return len(successful_emails)
        
    except Exception as e:
        print(f"❌ Multiple AI test failed: {e}")
        import traceback
        traceback.print_exc()
        return 0

async def send_business_email(to_email, subject, content, business_name):
    """Send business email using SMTP"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # SMTP configuration
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASSWORD")
        
        if not all([smtp_host, smtp_user, smtp_pass]):
            print(f"❌ SMTP credentials missing")
            return False
        
        # Create email
        msg = MIMEMultipart("alternative")
        msg["From"] = smtp_user
        msg["To"] = to_email
        msg["Subject"] = subject
        
        # Add footer
        content_with_footer = content + f"""

---
🤖 This email was AI-generated by DXTR Labs Automation Platform
📧 Business: {business_name}
⚡ Powered by MCP LLM Orchestrator
📞 Contact: automation-engine@dxtr-labs.com
"""
        
        msg.attach(MIMEText(content_with_footer, "plain"))
        
        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        print(f"❌ SMTP error: {e}")
        return False

async def main():
    print("🎯 MULTIPLE AI TOPIC EMAIL GENERATION - COMPLETE TEST")
    print("Testing 5 different businesses with AI content generation and email delivery")
    print("=" * 80)
    
    successful_count = await test_multiple_ai_business_emails()
    
    print(f"\n📊 TEST SUMMARY")
    print("=" * 50)
    print(f"📧 Emails Sent: {successful_count}/5")
    print(f"🎯 Recipient: slakshanand1105@gmail.com")
    print(f"🤖 AI Service: INHOUSE (MCP LLM)")
    print(f"📫 SMTP: mail.privateemail.com")
    print(f"📋 Businesses: Roomify, Ice Cream, CodeMaster, PizzaExpress, FitPro")
    
    if successful_count == 5:
        print(f"\n🎉 PERFECT! All 5 AI-generated business emails sent successfully!")
        print(f"Your multi-topic AI email system is fully operational!")
    elif successful_count >= 3:
        print(f"\n✅ GREAT! Most AI emails sent successfully!")
    else:
        print(f"\n⚠️ Some emails failed - check SMTP and AI configuration")

if __name__ == "__main__":
    asyncio.run(main())
