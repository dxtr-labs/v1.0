#!/usr/bin/env python3
"""
Direct Investor Outreach Email Automation for Sam
Sends professional emails to all AI investors with Calendly scheduling
"""

import asyncio
import sys
import os

# Add the backend path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.simple_email_service import EmailService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_investor_emails():
    """Send professional investor outreach emails directly"""
    
    # Investor email list from Sam
    investors = [
        {"email": "john.doe@a16z.com", "name": "John Doe", "firm": "Andreessen Horowitz"},
        {"email": "priya.kapoor@sequoiacap.com", "name": "Priya Kapoor", "firm": "Sequoia Capital"},
        {"email": "mike.harrison@greylock.com", "name": "Mike Harrison", "firm": "Greylock Partners"},
        {"email": "investors@lightspeedvp.com", "name": "Investment Team", "firm": "Lightspeed Venture Partners"}
    ]
    
    # Professional email template for investors
    email_subject = "Transforming Work with AI e-Workers – Investment Opportunity"
    
    def generate_email_content(investor_name, firm_name):
        return f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ border-bottom: 2px solid #4CAF50; padding-bottom: 10px; margin-bottom: 20px; }}
        .highlight {{ background-color: #f0f8ff; padding: 15px; border-left: 4px solid #4CAF50; }}
        .time-slots {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
        .cta {{ text-align: center; margin: 20px 0; }}
        .button {{ background-color: #4CAF50; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; display: inline-block; }}
        .signature {{ margin-top: 30px; border-top: 1px solid #eee; padding-top: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🤖 DXTR Labs - AI e-Workers Investment Opportunity</h2>
        </div>
        
        <p>Dear {investor_name},</p>
        
        <p>I hope this email finds you well. I'm <strong>Lakshanand Sugumar</strong>, Founder & CEO of <strong>DXTR Labs</strong>, and I'm reaching out to share an exciting investment opportunity in the future of work automation.</p>
        
        <div class="highlight">
            <h3>🚀 What We're Building</h3>
            <p><strong>DXTR Labs is revolutionizing work with always-available AI e-workers ("DXT Agents")</strong> that replace repetitive human tasks. Unlike existing automation tools, our DXT Agents have:</p>
            <ul>
                <li>✅ <strong>Memory & Personality</strong> - They learn and adapt to user preferences</li>
                <li>✅ <strong>24/7 Availability</strong> - Continuous operation without human intervention</li>
                <li>✅ <strong>Natural Communication</strong> - Users simply chat or speak to assign tasks</li>
                <li>✅ <strong>2000+ Integrated Workflows</strong> - Ready-to-use automation templates</li>
            </ul>
        </div>
        
        <h3>📊 Early Traction</h3>
        <p>We're already seeing incredible results with our early B2B clients:</p>
        <ul>
            <li>🎯 <strong>40+ hours of manual work saved per day</strong> per client</li>
            <li>📈 <strong>100+ companies on our waitlist</strong></li>
            <li>💡 <strong>Targeting the $66B+ automation market</strong></li>
            <li>🔧 <strong>Seamless integration</strong> with existing business tools</li>
        </ul>
        
        <h3>🤝 Let's Connect</h3>
        <p>I'd love to share more about how we're transforming the future of work and explore potential collaboration or investment opportunities with {firm_name}.</p>
        
        <div class="time-slots">
            <h4>📅 Available Time Slots:</h4>
            <ul>
                <li><strong>Monday, July 22</strong> – 10:00 AM to 12:00 PM PT</li>
                <li><strong>Tuesday, July 23</strong> – 3:00 PM to 5:00 PM PT</li>
                <li><strong>Thursday, July 25</strong> – 1:00 PM to 3:00 PM PT</li>
            </ul>
        </div>
        
        <div class="cta">
            <p><strong>Book a time that works best for you:</strong></p>
            <a href="https://calendly.com/dxtrlabs/30min" class="button">📅 Schedule Meeting</a>
        </div>
        
        <p>I'm excited about the potential to work together and would be happy to provide a demo of our AI e-workers in action.</p>
        
        <div class="signature">
            <p>Best regards,</p>
            <p><strong>Lakshanand Sugumar</strong><br>
            Founder & CEO, DXTR Labs<br>
            📧 lakshanand@dxtrlabs.com<br>
            🌐 <a href="https://calendly.com/dxtrlabs/30min">calendly.com/dxtrlabs/30min</a></p>
        </div>
    </div>
</body>
</html>"""
    
    # Initialize email service
    email_service = EmailService()
    
    # Configure email service (using DXTR Labs automation email)
    email_service.configure(
        email="automation-engine@dxtr-labs.com",
        password="AutoFlow2024!",  # The production password
        host="mail.privateemail.com",
        port=587
    )
    
    logger.info("📧 Initialized and configured DXTR Labs email service")
    
    # Send emails to all investors
    success_count = 0
    
    for investor in investors:
        try:
            logger.info(f"📤 Sending email to {investor['name']} at {investor['firm']}...")
            
            # Generate personalized email content
            email_content = generate_email_content(investor['name'], investor['firm'])
            
            # Send the email
            result = email_service.send_email(
                to_email=investor['email'],
                subject=email_subject,
                body=f"Investment opportunity from DXTR Labs - Please see HTML version",
                html_body=email_content
            )
            
            if result and result.get('success'):
                logger.info(f"✅ Email sent successfully to {investor['email']}")
                success_count += 1
            else:
                error_msg = result.get('error', 'Unknown error') if result else 'No response'
                logger.error(f"❌ Failed to send email to {investor['email']}: {error_msg}")
                
        except Exception as e:
            logger.error(f"❌ Error sending to {investor['email']}: {e}")
    
    # Summary
    logger.info(f"\n🎯 INVESTOR OUTREACH COMPLETED!")
    logger.info(f"✅ Successfully sent: {success_count}/{len(investors)} emails")
    logger.info(f"📧 All investors contacted with Calendly scheduling links")
    logger.info(f"🔗 Calendly link: https://calendly.com/dxtrlabs/30min")
    
    return success_count

async def main():
    """Execute investor outreach campaign"""
    logger.info("🚀 DXTR Labs Investor Outreach Campaign")
    logger.info("=" * 50)
    logger.info("📊 Targeting 4 AI investors with professional outreach")
    logger.info("📅 Including Calendly scheduling for meetings")
    logger.info("💼 Professional investment opportunity presentation")
    
    success_count = await send_investor_emails()
    
    if success_count > 0:
        logger.info(f"\n🎉 Campaign successful! {success_count} investor emails sent.")
        logger.info("📬 Check your inbox for delivery confirmations.")
    else:
        logger.error("\n❌ Campaign failed. Please check email configuration.")

if __name__ == "__main__":
    asyncio.run(main())
