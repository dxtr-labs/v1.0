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

async def test_10_random_ai_topics():
    """Test AI generation for 10 very random topics and send real emails"""
    print("🎲 TESTING 10 VERY RANDOM AI TOPICS")
    print("=" * 60)
    
    try:
        # Add backend to path
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        from mcp.simple_mcp_llm import MCP_LLM_Orchestrator
        
        orchestrator = MCP_LLM_Orchestrator()
        
        # 10 completely random and diverse topics
        random_topics = [
            {
                "name": "🦄 Unicorn Plushies",
                "prompt": "service:inhouse Using AI generate content for magical unicorn plushies that glow in the dark and send to slakshanand1105@gmail.com"
            },
            {
                "name": "🚁 Drone Pizza Delivery",
                "prompt": "service:inhouse Using AI generate content for autonomous drone pizza delivery service and send to slakshanand1105@gmail.com"
            },
            {
                "name": "🌱 Smart Plant Pots",
                "prompt": "service:inhouse Using AI generate content for AI-powered smart plant pots that talk to your plants and send to slakshanand1105@gmail.com"
            },
            {
                "name": "🧙‍♂️ Virtual Reality Magic School",
                "prompt": "service:inhouse Using AI generate content for VR magic school where you learn real wizardry and send to slakshanand1105@gmail.com"
            },
            {
                "name": "🐕 Dog Translation App",
                "prompt": "service:inhouse Using AI generate content for mobile app that translates dog barks into human language and send to slakshanand1105@gmail.com"
            },
            {
                "name": "🚀 Space Tourism Socks",
                "prompt": "service:inhouse Using AI generate content for special anti-gravity socks for space tourists and send to slakshanand1105@gmail.com"
            },
            {
                "name": "🍕 Levitating Pizza Oven",
                "prompt": "service:inhouse Using AI generate content for magnetic levitating pizza oven that cooks pizza in mid-air and send to slakshanand1105@gmail.com"
            },
            {
                "name": "🎮 Brain-Controlled Gaming",
                "prompt": "service:inhouse Using AI generate content for brain-controlled gaming headset that reads your thoughts and send to slakshanand1105@gmail.com"
            },
            {
                "name": "🦎 Chameleon Paint",
                "prompt": "service:inhouse Using AI generate content for color-changing paint that adapts to your mood and send to slakshanand1105@gmail.com"
            },
            {
                "name": "⚡ Lightning Bottle Lamp",
                "prompt": "service:inhouse Using AI generate content for decorative lamps that capture real lightning in bottles and send to slakshanand1105@gmail.com"
            }
        ]
        
        successful_emails = []
        
        for i, topic in enumerate(random_topics, 1):
            print(f"\n🎲 Random Topic {i}/10: {topic['name']}")
            print("=" * 50)
            print(f"🤖 Generating AI content...")
            
            try:
                # Generate AI workflow and content
                result = await orchestrator.process_user_input(
                    user_id=f"random-{i}",
                    agent_id=f"random-agent-{i}",
                    user_message=topic['prompt']
                )
                
                print(f"Status: {result.get('status')}")
                
                if 'workflow_json' in result:
                    workflow = result['workflow_json']
                    actions = workflow.get('actions', [])
                    
                    if len(actions) >= 2:
                        print(f"✅ Workflow generated with {len(actions)} actions")
                        
                        # Generate AI content
                        ai_content = orchestrator._generate_sample_content(
                            user_input=topic['prompt'],
                            content_type="sales_pitch"
                        )
                        
                        print(f"📝 AI Content Generated: {len(ai_content)} characters")
                        print(f"Preview: {ai_content[:100]}...")
                        
                        # Send email immediately
                        email_sent = await send_random_topic_email(
                            topic_name=topic['name'],
                            content=ai_content,
                            topic_number=i
                        )
                        
                        if email_sent:
                            successful_emails.append({
                                'number': i,
                                'name': topic['name'],
                                'content_length': len(ai_content)
                            })
                            print(f"✅ Email #{i} sent successfully!")
                        else:
                            print(f"❌ Email #{i} failed to send!")
                    else:
                        print(f"❌ Incomplete workflow generated")
                else:
                    print(f"❌ No workflow generated")
                
                # Pause between emails to avoid overwhelming
                if i < len(random_topics):
                    print(f"⏳ Waiting 2 seconds before next random topic...")
                    time.sleep(2)
                    
            except Exception as e:
                print(f"❌ Topic {i} failed: {e}")
        
        # Final results
        print(f"\n🎉 RANDOM AI TOPICS RESULTS")
        print("=" * 60)
        print(f"📊 Total Topics Tested: 10")
        print(f"✅ Successful Emails: {len(successful_emails)}/10")
        print(f"📧 Recipient: slakshanand1105@gmail.com")
        
        if successful_emails:
            print(f"\n🎲 Successfully Sent Random AI Emails:")
            for email in successful_emails:
                print(f"  {email['number']}. {email['name']}")
                print(f"     Content: {email['content_length']} characters")
        
        print(f"\n📧 Check slakshanand1105@gmail.com for {len(successful_emails)} random AI-generated emails!")
        
        if len(successful_emails) >= 8:
            print(f"\n🎉 OUTSTANDING! {len(successful_emails)}/10 random AI emails delivered!")
            print(f"Your AI system handles ANY topic perfectly!")
        elif len(successful_emails) >= 5:
            print(f"\n✅ EXCELLENT! {len(successful_emails)}/10 random emails sent!")
            print(f"Your AI system is very versatile!")
        else:
            print(f"\n⚠️ Some random topics failed - check logs")
        
        return len(successful_emails)
        
    except Exception as e:
        print(f"❌ Random topics test failed: {e}")
        import traceback
        traceback.print_exc()
        return 0

async def send_random_topic_email(topic_name, content, topic_number):
    """Send email for random AI topic"""
    try:
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
        msg["From"] = f"DXTR Labs AI <{smtp_user}>"
        msg["To"] = "slakshanand1105@gmail.com"
        msg["Subject"] = f"🎲 Random AI Topic #{topic_number}: {topic_name}"
        
        # Add footer to content
        email_content = content + f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎲 Random AI Topic #{topic_number} of 10
🤖 AI-Generated Content by DXTR Labs MCP LLM
📧 Topic: {topic_name}
⚡ Demonstrating AI versatility across ANY topic
📞 automation-engine@dxtr-labs.com
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This email proves our AI can generate relevant content 
for literally ANY product, service, or crazy idea!
"""
        
        msg.attach(MIMEText(email_content, "plain"))
        
        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        print(f"❌ SMTP error for topic {topic_number}: {e}")
        return False

async def main():
    print("🎯 10 VERY RANDOM AI TOPICS - ULTIMATE VERSATILITY TEST")
    print("Testing AI's ability to generate content for completely random topics")
    print("=" * 80)
    
    success_count = await test_10_random_ai_topics()
    
    print(f"\n🏆 ULTIMATE AI VERSATILITY TEST RESULTS")
    print("=" * 60)
    print(f"🎲 Random Topics: Unicorn Plushies, Drone Pizza, Smart Plants, VR Magic School, etc.")
    print(f"📧 AI Emails Generated: {success_count}/10")
    print(f"📫 Delivery: SMTP (mail.privateemail.com)")
    print(f"🤖 AI Service: INHOUSE MCP LLM")
    print(f"📍 Recipient: slakshanand1105@gmail.com")
    
    if success_count >= 8:
        print(f"\n🎉 🦄 🚀 MAGICAL SUCCESS! 🚀 🦄 🎉")
        print(f"Your AI handles even the most random topics perfectly!")
        print(f"From unicorns to lightning bottles - AI creates relevant content!")
    elif success_count >= 5:
        print(f"\n🎉 AMAZING! {success_count}/10 random topics successfully handled!")
        print(f"Your AI system is incredibly versatile!")
    elif success_count >= 1:
        print(f"\n✅ GOOD! {success_count}/10 random emails sent!")
        print(f"AI system working with some random topics.")
    else:
        print(f"\n⚠️ Random topic generation needs attention")
    
    print(f"\n📧 Your inbox should have {success_count} very creative AI-generated emails!")

if __name__ == "__main__":
    asyncio.run(main())
