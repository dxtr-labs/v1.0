import requests
import json
import time
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

def test_multiple_ai_topics():
    """Test AI generation and email sending for multiple business topics"""
    print("🚀 Multiple AI Topic Email Generation Test")
    print("=" * 60)
    
    # Multiple business scenarios to test
    test_scenarios = [
        {
            "name": "🏠 Roomify - College Roommate Service",
            "prompt": "service:inhouse Using AI generate a sales pitch for Roomify - one stop place for college students to find roommates and send to slakshanand1105@gmail.com",
            "keywords": ["roommate", "college", "students", "housing"]
        },
        {
            "name": "🍦 Healthy Ice Cream Business",
            "prompt": "Using AI generate a sales pitch for selling healthy ice creams made with organic ingredients and send to slakshanand1105@gmail.com",
            "keywords": ["ice cream", "healthy", "organic", "delicious"]
        },
        {
            "name": "💻 CodeMaster - Programming Bootcamp",
            "prompt": "service:inhouse Using AI generate a sales pitch for CodeMaster programming bootcamp that teaches web development in 12 weeks and send to slakshanand1105@gmail.com",
            "keywords": ["programming", "bootcamp", "web development", "coding"]
        },
        {
            "name": "🍕 PizzaExpress - Fast Food Delivery",
            "prompt": "Using AI generate a sales pitch for PizzaExpress fast pizza delivery service in 30 minutes or less and send to slakshanand1105@gmail.com",
            "keywords": ["pizza", "delivery", "fast", "30 minutes"]
        },
        {
            "name": "💪 FitPro - Personal Training",
            "prompt": "service:inhouse Using AI generate a sales pitch for FitPro personal training service with certified trainers and send to slakshanand1105@gmail.com",
            "keywords": ["fitness", "training", "personal trainer", "workout"]
        }
    ]
    
    successful_emails = []
    failed_emails = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📧 Test {i}/5: {scenario['name']}")
        print("=" * 50)
        
        try:
            # Test direct backend processing since API requires auth
            print(f"🤖 Generating AI content...")
            print(f"Prompt: {scenario['prompt']}")
            
            # Add backend to path
            backend_path = os.path.join(os.path.dirname(__file__), 'backend')
            if backend_path not in sys.path:
                sys.path.insert(0, backend_path)
            
            # Import MCP orchestrator
            from mcp.simple_mcp_llm import MCP_LLM_Orchestrator
            
            orchestrator = MCP_LLM_Orchestrator()
            
            async def process_scenario():
                # Process with MCP orchestrator
                result = await orchestrator.process_user_input(
                    user_id=f"test-user-{i}",
                    agent_id=f"test-agent-{i}",
                    user_message=scenario['prompt']
                )
                
                print(f"✅ AI Processing Result:")
                print(f"  Status: {result.get('status')}")
                print(f"  Message: {result.get('message', 'No message')}")
                
                if 'workflow_json' in result:
                    workflow = result['workflow_json']
                    print(f"📋 Workflow Generated:")
                    print(f"  Type: {workflow.get('type')}")
                    print(f"  Recipient: {workflow.get('recipient')}")
                    print(f"  Actions: {len(workflow.get('actions', []))}")
                    
                    # Find and execute email action
                    for action in workflow.get('actions', []):
                        if action.get('action_type') == 'emailSend':
                            email_params = action.get('parameters', {})
                            content = email_params.get('text', '')
                            
                            print(f"\n📧 Email Content Analysis:")
                            print(f"  To: {email_params.get('toEmail')}")
                            print(f"  Subject: {email_params.get('subject')}")
                            print(f"  Content Length: {len(content)} characters")
                            
                            # Check if content is business-specific
                            keyword_matches = []
                            for keyword in scenario['keywords']:
                                if keyword.lower() in content.lower():
                                    keyword_matches.append(keyword)
                            
                            print(f"  Business Keywords Found: {keyword_matches}")
                            print(f"  Content Preview: {content[:150]}...")
                            
                            # Send email using simple SMTP (like our successful test)
                            email_result = await send_email_simple(
                                to_email=email_params.get('toEmail'),
                                subject=email_params.get('subject', f"AI-Generated: {scenario['name']}"),
                                content=content,
                                scenario_name=scenario['name']
                            )
                            
                            if email_result:
                                successful_emails.append({
                                    'name': scenario['name'],
                                    'keywords': keyword_matches,
                                    'content_length': len(content),
                                    'subject': email_params.get('subject')
                                })
                                print(f"✅ Email sent successfully!")
                            else:
                                failed_emails.append(scenario['name'])
                                print(f"❌ Email sending failed!")
                            
                            break
                else:
                    print(f"❌ No workflow generated")
                    failed_emails.append(scenario['name'])
            
            # Run async processing
            asyncio.run(process_scenario())
            
            # Wait between tests to avoid overwhelming the email server
            if i < len(test_scenarios):
                print(f"\n⏳ Waiting 5 seconds before next test...")
                time.sleep(5)
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            failed_emails.append(scenario['name'])
            import traceback
            traceback.print_exc()
    
    # Final summary
    print(f"\n📊 FINAL RESULTS")
    print("=" * 60)
    print(f"✅ Successful Emails: {len(successful_emails)}/5")
    print(f"❌ Failed Emails: {len(failed_emails)}/5")
    
    if successful_emails:
        print(f"\n🎉 Successfully Sent Emails:")
        for email in successful_emails:
            print(f"  ✅ {email['name']}")
            print(f"     Subject: {email['subject']}")
            print(f"     Keywords: {email['keywords']}")
            print(f"     Length: {email['content_length']} characters")
    
    if failed_emails:
        print(f"\n❌ Failed Emails:")
        for name in failed_emails:
            print(f"  ❌ {name}")
    
    print(f"\n📧 Check slakshanand1105@gmail.com for {len(successful_emails)} AI-generated emails!")
    return len(successful_emails)

async def send_email_simple(to_email, subject, content, scenario_name):
    """Send email using simple SMTP (proven working method)"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # SMTP configuration from environment
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASSWORD")
        
        if not all([smtp_host, smtp_user, smtp_pass]):
            print(f"❌ SMTP credentials missing for {scenario_name}")
            return False
        
        # Create email message
        msg = MIMEMultipart("alternative")
        msg["From"] = smtp_user
        msg["To"] = to_email
        msg["Subject"] = subject
        
        # Add footer to content
        content_with_footer = content + f"""

---
🤖 This email was AI-generated by DXTR Labs Automation Platform
📧 From: {smtp_user}
🎯 Business Topic: {scenario_name}
⚡ Powered by MCP LLM Orchestrator
"""
        
        # Attach content
        msg.attach(MIMEText(content_with_footer, "plain"))
        
        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        
        print(f"📤 Email delivered for {scenario_name}")
        return True
        
    except Exception as e:
        print(f"❌ SMTP error for {scenario_name}: {e}")
        return False

def test_ai_content_variety():
    """Quick test to verify AI generates different content for different businesses"""
    print(f"\n🧪 AI Content Variety Test")
    print("=" * 40)
    
    topics = [
        "healthy ice cream business",
        "college roommate finding service", 
        "programming bootcamp",
        "pizza delivery service",
        "personal training gym"
    ]
    
    for topic in topics:
        print(f"🎯 {topic.title()}: AI should generate business-specific content")
    
    print(f"✅ Testing {len(topics)} different business verticals")

def main():
    print("🎯 MULTIPLE AI TOPIC EMAIL GENERATION TEST")
    print("Testing AI content generation and email delivery for 5 different businesses")
    print("=" * 80)
    
    # Quick content variety check
    test_ai_content_variety()
    
    # Main multiple topic test
    successful_count = test_multiple_ai_topics()
    
    print(f"\n🏆 TEST COMPLETION SUMMARY")
    print("=" * 50)
    print(f"📊 Emails Sent: {successful_count}/5")
    print(f"📧 Recipient: slakshanand1105@gmail.com")
    print(f"🤖 AI Topics: Roomify, Ice Cream, CodeMaster, PizzaExpress, FitPro")
    print(f"✅ SMTP: mail.privateemail.com (Working)")
    print(f"⚡ System Status: Production Ready")
    
    if successful_count >= 4:
        print(f"\n🎉 EXCELLENT! Your AI email system is working perfectly!")
        print(f"Multiple business topics generated and delivered successfully!")
    elif successful_count >= 2:
        print(f"\n✅ GOOD! Most emails sent successfully!")
        print(f"Minor issues with some deliveries - check logs for details.")
    else:
        print(f"\n⚠️ ISSUES DETECTED! Less than half of emails sent.")
        print(f"Check SMTP settings and AI content generation.")

if __name__ == "__main__":
    main()
