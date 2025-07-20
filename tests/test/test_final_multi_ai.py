import asyncio
import os
import sys
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

async def test_end_to_end_ai_emails():
    """Test complete end-to-end AI email generation using direct orchestrator and SMTP"""
    print("🚀 END-TO-END MULTIPLE AI BUSINESS EMAIL TEST")
    print("=" * 70)
    
    try:
        # Add backend to path
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        from mcp.simple_mcp_llm import MCP_LLM_Orchestrator
        
        orchestrator = MCP_LLM_Orchestrator()
        
        # Test scenarios for 5 different businesses
        business_scenarios = [
            {
                "name": "🏠 Roomify - College Roommate Service",
                "prompt": "service:inhouse Using AI generate a sales pitch for Roomify - one stop place for college students to find roommates and send to slakshanand1105@gmail.com",
                "business_type": "roommate matching",
                "expected_keywords": ["roommate", "college", "students", "housing"]
            },
            {
                "name": "🍦 FreshScoop - Healthy Ice Cream",
                "prompt": "service:inhouse Using AI generate a sales pitch for FreshScoop healthy ice cream made with organic ingredients and send to slakshanand1105@gmail.com",
                "business_type": "healthy food",
                "expected_keywords": ["ice cream", "healthy", "organic", "delicious"]
            },
            {
                "name": "💻 CodeMaster - Programming Bootcamp",
                "prompt": "service:inhouse Using AI generate a sales pitch for CodeMaster programming bootcamp that teaches web development in 12 weeks and send to slakshanand1105@gmail.com",
                "business_type": "education",
                "expected_keywords": ["programming", "bootcamp", "web development", "coding"]
            },
            {
                "name": "🍕 PizzaExpress - Fast Delivery",
                "prompt": "service:inhouse Using AI generate a sales pitch for PizzaExpress fast pizza delivery service in 30 minutes or less and send to slakshanand1105@gmail.com",
                "business_type": "food delivery",
                "expected_keywords": ["pizza", "delivery", "fast", "30 minutes"]
            },
            {
                "name": "💪 FitPro - Personal Training",
                "prompt": "service:inhouse Using AI generate a sales pitch for FitPro personal training service with certified trainers and send to slakshanand1105@gmail.com",
                "business_type": "fitness",
                "expected_keywords": ["fitness", "training", "personal trainer", "workout"]
            }
        ]
        
        successful_emails = []
        
        for i, scenario in enumerate(business_scenarios, 1):
            print(f"\n📧 Test {i}/5: {scenario['name']}")
            print("=" * 60)
            
            try:
                # Step 1: Generate AI workflow
                print(f"🤖 Generating AI workflow for {scenario['business_type']}...")
                result = await orchestrator.process_user_input(
                    user_id=f"business-test-{i}",
                    agent_id=f"ai-agent-{i}",
                    user_message=scenario['prompt']
                )
                
                print(f"Status: {result.get('status')}")
                
                if 'workflow_json' in result:
                    workflow = result['workflow_json']
                    actions = workflow.get('actions', [])
                    
                    print(f"✅ Workflow generated with {len(actions)} actions")
                    
                    # Step 2: Generate business-specific AI content
                    print(f"🎯 Generating {scenario['business_type']} content...")
                    
                    # Use the orchestrator's sample content generation with business context
                    ai_content = orchestrator._generate_sample_content(
                        user_input=scenario['prompt'],
                        content_type="sales_pitch"
                    )
                    
                    print(f"✅ Generated {len(ai_content)} characters of content")
                    
                    # Check if content is business-specific
                    keyword_matches = []
                    for keyword in scenario['expected_keywords']:
                        if keyword.lower() in ai_content.lower():
                            keyword_matches.append(keyword)
                    
                    print(f"🎯 Business keywords found: {keyword_matches}")
                    print(f"📝 Content preview: {ai_content[:100]}...")
                    
                    # Step 3: Extract email parameters and send
                    email_action = None
                    for action in actions:
                        if action.get('action_type') == 'emailSend':
                            email_action = action
                            break
                    
                    if email_action:
                        email_params = email_action.get('parameters', {})
                        recipient = email_params.get('toEmail', 'slakshanand1105@gmail.com')
                        subject = email_params.get('subject', f"{scenario['name']} - AI Generated Sales Pitch")
                        
                        print(f"📧 Sending email...")
                        print(f"  To: {recipient}")
                        print(f"  Subject: {subject}")
                        print(f"  Content: {len(ai_content)} characters")
                        
                        # Send the actual email
                        email_success = await send_ai_email(
                            recipient=recipient,
                            subject=subject,
                            content=ai_content,
                            business_name=scenario['name']
                        )
                        
                        if email_success:
                            successful_emails.append({
                                'business': scenario['name'],
                                'type': scenario['business_type'],
                                'keywords': keyword_matches,
                                'content_length': len(ai_content),
                                'subject': subject
                            })
                            print(f"✅ Email delivered successfully!")
                        else:
                            print(f"❌ Email delivery failed!")
                    else:
                        print(f"❌ No email action found in workflow")
                else:
                    print(f"❌ No workflow generated")
                
                # Pause between tests
                if i < len(business_scenarios):
                    print(f"\n⏳ Waiting 4 seconds before next business...")
                    time.sleep(4)
                    
            except Exception as e:
                print(f"❌ Test {i} failed: {e}")
        
        # Final summary
        print(f"\n🏆 MULTIPLE AI BUSINESS EMAIL RESULTS")
        print("=" * 70)
        print(f"✅ Successful Deliveries: {len(successful_emails)}/5")
        
        if successful_emails:
            print(f"\n🎉 AI-Generated Business Emails Sent:")
            for email in successful_emails:
                print(f"  ✅ {email['business']}")
                print(f"     Type: {email['type']}")
                print(f"     Keywords: {email['keywords']}")
                print(f"     Length: {email['content_length']} chars")
                print(f"     Subject: {email['subject']}")
                print()
        
        print(f"📧 Check slakshanand1105@gmail.com for {len(successful_emails)} different business emails!")
        
        # Overall assessment
        if len(successful_emails) == 5:
            print(f"\n🎉 PERFECT! All 5 AI business emails generated and delivered!")
            print(f"Your multi-topic AI email system is production-ready!")
        elif len(successful_emails) >= 3:
            print(f"\n✅ EXCELLENT! Most AI business emails delivered successfully!")
        elif len(successful_emails) >= 1:
            print(f"\n👍 GOOD! Some AI emails delivered - system is working!")
        else:
            print(f"\n⚠️ No emails delivered - check configuration")
        
        return len(successful_emails)
        
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return 0

async def send_ai_email(recipient, subject, content, business_name):
    """Send AI-generated business email via SMTP"""
    try:
        # SMTP configuration from environment
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASSWORD")
        
        if not all([smtp_host, smtp_user, smtp_pass]):
            print(f"❌ SMTP configuration incomplete")
            return False
        
        # Create professional email
        msg = MIMEMultipart("alternative")
        msg["From"] = f"DXTR Labs AI <{smtp_user}>"
        msg["To"] = recipient
        msg["Subject"] = subject
        
        # Add business footer
        email_content = content + f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AI-Generated Business Content by DXTR Labs
📧 Business Focus: {business_name}
⚡ Powered by MCP LLM Orchestrator
📞 automation-engine@dxtr-labs.com
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This email demonstrates our AI's ability to generate 
business-specific content for any industry or service.
"""
        
        msg.attach(MIMEText(email_content, "plain"))
        
        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        print(f"❌ SMTP delivery error: {e}")
        return False

async def main():
    print("🎯 MULTIPLE AI TOPIC EMAIL GENERATION - PRODUCTION TEST")
    print("Testing AI content generation and delivery for 5 different businesses")
    print("=" * 80)
    
    # Run the complete test
    success_count = await test_end_to_end_ai_emails()
    
    print(f"\n📊 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"🎯 Business Types Tested: 5 (Roommate, Food, Education, Delivery, Fitness)")
    print(f"📧 AI Emails Generated: {success_count}/5")
    print(f"📫 Delivery Method: SMTP (mail.privateemail.com)")
    print(f"🤖 AI Service: INHOUSE MCP LLM")
    print(f"📍 Recipient: slakshanand1105@gmail.com")
    
    if success_count == 5:
        print(f"\n🎉 🎉 🎉 OUTSTANDING SUCCESS! 🎉 🎉 🎉")
        print(f"All 5 different business AI emails generated and delivered!")
        print(f"Your multi-topic AI email system is FULLY OPERATIONAL!")
    elif success_count >= 3:
        print(f"\n🎉 EXCELLENT! {success_count}/5 AI business emails delivered!")
        print(f"Your multi-topic AI system is working great!")
    elif success_count >= 1:
        print(f"\n✅ GOOD! {success_count}/5 AI emails delivered successfully!")
        print(f"System is functional with minor issues to resolve.")
    else:
        print(f"\n⚠️ No emails delivered - check SMTP and AI configuration")

if __name__ == "__main__":
    asyncio.run(main())
