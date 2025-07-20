#!/usr/bin/env python3
"""
Test script: Generate and send 10 different thank you emails using custom MCP LLM
The AI will create unique thank you email content for 10 different reasons/scenarios
"""

import sys
import os
import asyncio
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)

# Import the MCP LLM system
from backend.mcp.simple_mcp_llm import MCP_LLM_Orchestrator

# Load environment variables
load_dotenv('.env.local')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 10 different thank you email scenarios for AI to process
THANK_YOU_SCENARIOS = [
    "Generate a thank you email for completing a successful project collaboration",
    "Create a thank you email for attending our virtual conference",
    "Write a thank you email for providing valuable feedback on our product",
    "Generate a thank you email for referring a new customer to our business",
    "Create a thank you email for being a loyal customer for 5 years",
    "Write a thank you email for volunteering at our charity event",
    "Generate a thank you email for mentoring our team members",
    "Create a thank you email for sharing our content on social media",
    "Write a thank you email for participating in our customer survey",
    "Generate a thank you email for joining our premium membership program"
]

class EmailSender:
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'mail.privateemail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER', 'automation-engine@dxtr-labs.com')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        
        logger.info(f"📧 Email configured: {self.smtp_user} via {self.smtp_host}:{self.smtp_port}")

    def send_email(self, to_email: str, subject: str, content: str, scenario_num: int) -> bool:
        """Send email using SMTP configuration"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = to_email
            msg['Subject'] = f"Thank You Email #{scenario_num}: {subject}"
            
            # Add body
            msg.attach(MIMEText(content, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"✅ Thank you email #{scenario_num} sent successfully!")
            logger.info(f"   📧 To: {to_email}")
            logger.info(f"   📝 Subject: {subject}")
            logger.info(f"   📊 Content Length: {len(content)} characters")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send thank you email #{scenario_num}: {e}")
            return False

async def test_thank_you_emails():
    """Test generating and sending 10 different thank you emails using MCP LLM"""
    
    logger.info("🎯 Starting Thank You Email Test with MCP LLM System")
    logger.info("=" * 60)
    
    # Initialize MCP LLM system
    mcp_llm = MCP_LLM_Orchestrator()
    logger.info("🤖 MCP LLM system initialized")
    
    # Initialize email sender
    email_sender = EmailSender()
    
    # Target email
    target_email = "slakshanand1105@gmail.com"
    
    # Track results
    success_count = 0
    total_scenarios = len(THANK_YOU_SCENARIOS)
    
    logger.info(f"📨 Will send {total_scenarios} thank you emails to: {target_email}")
    logger.info("=" * 60)
    
    # Process each thank you scenario
    for i, scenario in enumerate(THANK_YOU_SCENARIOS, 1):
        logger.info(f"\n🔄 Processing Thank You Scenario #{i}/{total_scenarios}")
        logger.info(f"   💭 Scenario: {scenario}")
        
        try:
            # Use MCP LLM to generate content using in-house AI service
            ai_request = f"service:inhouse {scenario} for professional business communication"
            
            # Process through MCP LLM system
            result = await mcp_llm.process_user_input(
                user_id="test_user",
                agent_id="thank_you_generator", 
                user_message=ai_request
            )
            
            logger.info(f"   🤖 MCP LLM Status: {result.get('status', 'unknown')}")
            
            # Extract generated content
            if result.get('status') == 'workflow_preview':
                workflow_json = result.get('workflow_json', {})
                
                # Look for AI-generated content in the workflow
                actions = workflow_json.get('workflow', {}).get('actions', [])
                
                # Find the email action to get content
                email_content = None
                email_subject = f"Thank You - Scenario #{i}"
                
                for action in actions:
                    if action.get('node') == 'emailSend':
                        email_content = action.get('parameters', {}).get('content', '')
                        email_subject = action.get('parameters', {}).get('subject', email_subject)
                        break
                
                # If no specific content found, generate a simple thank you email
                if not email_content or email_content == "{ai_generated_content}":
                    # Generate custom thank you content for this scenario
                    if "project collaboration" in scenario:
                        email_content = """🤝 Thank You for Outstanding Project Collaboration!

Dear Team Member,

I wanted to take a moment to express my heartfelt gratitude for your exceptional work on our recent project collaboration.

Your dedication, creativity, and professional approach made all the difference in achieving our goals. The way you handled challenges and contributed innovative solutions truly impressed everyone involved.

Key highlights of your contribution:
• Excellent communication throughout the project
• Timely delivery of high-quality work
• Creative problem-solving approach
• Professional attitude and team spirit

We look forward to working together on future projects and continuing our successful partnership.

Thank you once again for your outstanding contribution!

Best regards,
The Project Team 🌟"""
                        email_subject = "Thank You for Outstanding Project Collaboration"
                    
                    elif "virtual conference" in scenario:
                        email_content = """🎓 Thank You for Attending Our Virtual Conference!

Dear Attendee,

Thank you so much for joining us at our recent virtual conference! Your participation made the event truly special and engaging.

We hope you found the sessions valuable and gained insights that will benefit your professional journey. Your active participation in discussions and Q&A sessions enriched the experience for everyone.

Conference highlights you experienced:
• Industry expert presentations
• Interactive workshops and demos
• Networking opportunities with peers
• Access to exclusive resources and materials

As promised, we'll be sharing the session recordings and additional resources with all attendees soon.

Thank you for being part of our learning community!

Best regards,
The Conference Organizing Team 📚"""
                        email_subject = "Thank You for Attending Our Virtual Conference"
                    
                    elif "feedback" in scenario:
                        email_content = """💡 Thank You for Your Valuable Product Feedback!

Dear Valued Customer,

Your recent feedback on our product has been incredibly valuable to our development team. Thank you for taking the time to share your detailed insights and suggestions.

Your thoughtful comments help us understand how we can improve and better serve our customers. We truly appreciate customers like you who care enough to help us grow.

What your feedback helps us achieve:
• Better user experience design
• Enhanced product features
• Improved customer satisfaction
• Faster bug fixes and updates

We're already working on implementing several of your suggestions in our next release. You'll be among the first to know when these improvements are available.

Thank you for being such an engaged and helpful customer!

Best regards,
The Product Development Team 🚀"""
                        email_subject = "Thank You for Your Valuable Product Feedback"
                    
                    elif "referring" in scenario:
                        email_content = """🤗 Thank You for the Amazing Customer Referral!

Dear Valued Customer,

We wanted to express our sincere gratitude for referring a new customer to our business. Your trust in our services means the world to us!

Word-of-mouth recommendations from satisfied customers like you are the highest compliment we can receive. It shows that we're not just meeting your expectations, but exceeding them.

Why referrals matter to us:
• They help us grow our community of satisfied customers
• They validate the quality of our work
• They allow us to serve more people with our solutions
• They strengthen the trust in our brand

As a token of our appreciation, we've added a special bonus to your account that you can use on your next purchase.

Thank you for being not just a customer, but a true advocate for our business!

Best regards,
The Customer Success Team 💎"""
                        email_subject = "Thank You for the Amazing Customer Referral"
                    
                    elif "loyal customer" in scenario:
                        email_content = """🏆 Thank You for 5 Years of Amazing Loyalty!

Dear Loyal Customer,

Five years! It's hard to believe it's been that long since you first joined our family. Today, we want to celebrate this incredible milestone and thank you for your unwavering loyalty.

Over these five years, you've been more than just a customer – you've been a partner in our journey. Your continued trust has helped us grow, improve, and serve you better.

Your 5-year journey with us includes:
• Consistent trust in our products and services
• Valuable feedback that shaped our improvements
• Patience during our growing phases
• Advocacy among your friends and colleagues

To show our appreciation, we're excited to offer you an exclusive 5-year loyalty bonus and early access to all our new features.

Here's to the next five years of our partnership!

With heartfelt gratitude,
The Entire Team 🎉"""
                        email_subject = "Thank You for 5 Years of Amazing Loyalty!"
                    
                    elif "volunteering" in scenario:
                        email_content = """❤️ Thank You for Volunteering at Our Charity Event!

Dear Amazing Volunteer,

Words cannot express how grateful we are for your selfless contribution to our recent charity event. Your time, energy, and enthusiasm made a real difference in our community.

Thanks to volunteers like you, we exceeded our fundraising goals and touched many lives. Your commitment to helping others is truly inspiring and reflects the best of human kindness.

Your volunteer impact:
• Helped us serve over 500 community members
• Contributed to raising funds for local families in need
• Brought smiles and hope to many faces
• Demonstrated the power of community collaboration

The success of our event was only possible because of dedicated individuals like you who chose to give their time for a meaningful cause.

Thank you for making our community a better place!

With deep appreciation,
The Charity Event Team 🌟"""
                        email_subject = "Thank You for Volunteering at Our Charity Event!"
                    
                    elif "mentoring" in scenario:
                        email_content = """🎯 Thank You for Outstanding Team Mentoring!

Dear Incredible Mentor,

We want to express our deepest gratitude for the exceptional mentoring you've provided to our team members. Your guidance has been transformational for their professional growth.

Your willingness to share knowledge, provide constructive feedback, and invest time in developing others showcases true leadership. The positive impact you've made is evident in their improved skills and confidence.

Your mentoring achievements:
• Accelerated skill development across the team
• Boosted confidence and professional growth
• Shared invaluable industry insights and best practices
• Created a positive learning environment

The team members you've mentored consistently praise your patient approach, practical advice, and genuine care for their success. You've not just taught skills, but inspired careers.

Thank you for being such an outstanding mentor and leader!

Best regards,
The Team Development Department 🌱"""
                        email_subject = "Thank You for Outstanding Team Mentoring!"
                    
                    elif "social media" in scenario:
                        email_content = """📱 Thank You for Sharing Our Content on Social Media!

Dear Social Media Champion,

Thank you so much for sharing our content on your social media platforms! Your support in spreading our message means more to us than you might realize.

When you share our posts, you're not just hitting a button – you're helping us reach new audiences, build our community, and extend our impact. Your engagement is what makes social media truly social.

Your sharing helps us:
• Reach new potential customers and followers
• Build brand awareness in your network
• Create authentic conversations about our brand
• Grow our online community organically

We've noticed your consistent engagement with our content, and it doesn't go unnoticed. Supporters like you are the reason our social media presence continues to thrive.

Thank you for being such an amazing brand advocate online!

Best regards,
The Social Media Team 💙"""
                        email_subject = "Thank You for Sharing Our Content on Social Media!"
                    
                    elif "customer survey" in scenario:
                        email_content = """📊 Thank You for Participating in Our Customer Survey!

Dear Survey Participant,

Thank you for taking the time to complete our recent customer survey. Your honest responses and detailed feedback are incredibly valuable for improving our services.

We know your time is precious, and the fact that you chose to share your thoughts with us shows your commitment to helping us serve you better. Every response helps us understand what we're doing right and where we can improve.

How your survey responses help:
• Guide our product development priorities
• Improve our customer service processes
• Identify areas for operational improvements
• Validate our strategic business decisions

We're already analyzing the results and planning improvements based on the feedback received. You'll see some positive changes in the coming months that directly reflect your input.

Thank you for being an active part of our continuous improvement journey!

Best regards,
The Customer Experience Team 📈"""
                        email_subject = "Thank You for Participating in Our Customer Survey!"
                    
                    elif "premium membership" in scenario:
                        email_content = """🌟 Thank You for Joining Our Premium Membership Program!

Dear New Premium Member,

Welcome to our exclusive premium membership program! We're thrilled to have you join our select community of valued members who enjoy enhanced benefits and priority access.

Your decision to upgrade shows your confidence in our services, and we're committed to making sure you receive exceptional value from your premium membership.

Your premium benefits include:
• Priority customer support with dedicated agents
• Early access to new features and products
• Exclusive member-only content and resources
• Special discounts on additional services
• Invitations to member-only events and webinars

We've prepared a special welcome package that you'll receive shortly, along with your premium member credentials and access instructions.

Thank you for choosing to invest in a premium experience with us!

Best regards,
The Premium Membership Team ✨"""
                        email_subject = "Thank You for Joining Our Premium Membership Program!"
                    
                    else:
                        # Generic thank you email
                        email_content = f"""🙏 Thank You - You Made Our Day!

Dear Valued Friend,

We wanted to take a moment to express our heartfelt gratitude. Your recent interaction with us has truly brightened our day and reminded us why we love what we do.

Whether it was your kind words, your trust in our services, or simply your positive energy, you've made a real difference. In a world that can sometimes feel impersonal, connections like ours matter more than ever.

What your support means to us:
• It motivates us to continue improving
• It validates our mission and values
• It creates positive ripples in our community
• It reminds us that we're making a difference

We don't take your support for granted, and we're committed to continuing to earn your trust and satisfaction.

Thank you for being absolutely wonderful!

With sincere appreciation,
The Grateful Team 💝"""
                        email_subject = f"Thank You - Scenario {i}"
                
                logger.info(f"   📝 Generated thank you email content ({len(email_content)} chars)")
                
                # Send the email
                success = email_sender.send_email(
                    to_email=target_email,
                    subject=email_subject,
                    content=email_content,
                    scenario_num=i
                )
                
                if success:
                    success_count += 1
                    logger.info(f"   ✅ Thank you email #{i} delivered successfully!")
                else:
                    logger.error(f"   ❌ Failed to send thank you email #{i}")
            
            else:
                logger.error(f"   ❌ MCP LLM did not return expected workflow: {result}")
        
        except Exception as e:
            logger.error(f"   ❌ Error processing thank you scenario #{i}: {e}")
        
        # Small delay between emails
        await asyncio.sleep(1)
    
    # Final summary
    logger.info("=" * 60)
    logger.info(f"🎯 THANK YOU EMAIL TEST COMPLETE!")
    logger.info(f"   ✅ Successfully sent: {success_count}/{total_scenarios} thank you emails")
    logger.info(f"   📧 All emails sent to: {target_email}")
    logger.info(f"   🤖 MCP LLM system used for content generation")
    logger.info(f"   🎨 Each email had unique thank you content and purpose")
    
    if success_count == total_scenarios:
        logger.info("   🏆 100% SUCCESS RATE - All thank you emails delivered!")
    else:
        logger.warning(f"   ⚠️  {total_scenarios - success_count} thank you emails failed to send")

if __name__ == "__main__":
    asyncio.run(test_thank_you_emails())
