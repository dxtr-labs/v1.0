import logging
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_directly(to_email: str, subject: str, body: str, html_body: str = None) -> dict:
    """
    Send real email using SMTP configuration from environment variables.
    """
    try:
        # Get SMTP configuration from environment
        smtp_host = os.getenv('SMTP_HOST', 'mail.privateemail.com')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_user = os.getenv('SMTP_USER', 'automation-engine@dxtr-labs.com')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        if not smtp_password:
            logging.error("SMTP_PASSWORD not found in environment variables")
            return {
                "success": False,
                "error": "SMTP configuration incomplete - missing password"
            }
        
        logging.info(f"🔧 REAL EMAIL: Sending to {to_email} via {smtp_host}:{smtp_port}")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add text body
        text_part = MIMEText(body, 'plain')
        msg.attach(text_part)
        
        # Add HTML body if provided
        if html_body:
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        logging.info(f"✅ REAL EMAIL SENT: Successfully delivered to {to_email}")
        
        return {
            "success": True,
            "message": f"Real email sent to {to_email}",
            "from": smtp_user,
            "to": to_email,
            "subject": subject
        }
        
    except Exception as e:
        logging.error(f"❌ REAL EMAIL FAILED: Error sending to {to_email}: {e}")
        return {
            "success": False,
            "error": f"Failed to send email: {str(e)}",
            "to": to_email
        }

def generate_premium_template(recipient_name: str = "Valued Customer", sender_name: str = "Sam Rodriguez") -> tuple:
    """
    Generate premium email template with HTML and text versions.
    Returns: (html_content, text_content)
    """
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Revolutionary AI Solutions - DXTR Labs</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #DAA520, #D2BD96); padding: 30px; text-align: center; border-radius: 10px; margin-bottom: 30px;">
        <h1 style="color: white; margin: 0; font-size: 28px;">🚀 DXTR Labs</h1>
        <p style="color: white; margin: 10px 0 0 0; font-size: 16px;">Revolutionary AI Solutions</p>
    </div>
    
    <div style="background: #f8f9fa; padding: 25px; border-radius: 10px; margin-bottom: 25px;">
        <h2 style="color: #DAA520; margin: 0 0 15px 0;">Dear {recipient_name},</h2>
        <p>Hi! <strong>{sender_name} from DXTR Labs</strong> here.</p>
    </div>
    
    <div style="background: linear-gradient(135deg, #f0f9ff, #e0f2fe); padding: 30px; border-radius: 15px; margin-bottom: 30px; text-align: center; border: 2px solid #0ea5e9;">
        <h3 style="color: #0c4a6e; margin: 0 0 15px 0;">🚀 Revolutionizing Business Operations</h3>
        <p style="margin: 0; font-size: 16px;">We're transforming companies with our <strong>AI-powered Virtual Workforce</strong> that never sleeps, never makes mistakes, and scales instantly.</p>
    </div>
    
    <div style="margin-bottom: 30px;">
        <h3 style="color: white; margin: 0 0 20px 0; text-align: center; padding: 15px; background: linear-gradient(135deg, #6366f1, #8b5cf6); border-radius: 10px;">⚡ FITNESS APP REVOLUTION</h3>
        
        <div style="background: #fef3c7; border-radius: 10px; padding: 20px; margin-bottom: 15px; border: 2px solid #f59e0b;">
            <h4 style="color: #92400e; margin: 0 0 10px 0;">🏋️ AI-Powered Fitness Transformation</h4>
            <p style="color: #451a03; margin: 0;">Personalized workouts, nutrition coaching, and progress tracking</p>
        </div>
        
        <div style="background: #dcfce7; border-radius: 10px; padding: 20px; margin-bottom: 15px; border: 2px solid #22c55e;">
            <h4 style="color: #166534; margin: 0 0 10px 0;">📱 Smart Features</h4>
            <p style="color: #052e16; margin: 0;">Real-time coaching, community challenges, and achievement tracking</p>
        </div>
        
        <div style="background: #dbeafe; border-radius: 10px; padding: 20px; margin-bottom: 15px; border: 2px solid #2563eb;">
            <h4 style="color: #1e3a8a; margin: 0 0 10px 0;">🎯 Results-Driven</h4>
            <p style="color: #172554; margin: 0;">Proven methodology with measurable fitness improvements</p>
        </div>
    </div>
    
    <div style="background: #DAA520; color: white; padding: 25px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <h3 style="margin: 0 0 15px 0;">🎁 SPECIAL LAUNCH OFFER</h3>
        <p style="margin: 0; font-size: 18px; font-weight: bold;">50% OFF First Month + FREE Premium Features!</p>
    </div>
    
    <div style="text-align: center; margin-bottom: 30px;">
        <a href="#" style="background: linear-gradient(135deg, #DAA520, #D2BD96); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block;">
            🚀 Download Now & Transform Your Fitness!
        </a>
    </div>
    
    <div style="border-top: 2px solid #DAA520; padding-top: 20px; text-align: center; color: #666;">
        <p>Best regards,<br><strong>{sender_name}</strong><br>Senior AI Solutions Consultant<br>DXTR Labs</p>
        <p style="font-size: 12px;">📧 automation@dxtrlabs.com | 📞 +1 (555) 123-DXTR</p>
    </div>
</body>
</html>
"""

    text_content = f"""
🚀 DXTR LABS - Revolutionary AI Solutions

Dear {recipient_name},

Hi! {sender_name} from DXTR Labs here.

🚀 REVOLUTIONIZING FITNESS WITH AI

We're excited to introduce our groundbreaking AI-powered fitness app that's transforming how people achieve their health goals!

🏋️ AI-POWERED FITNESS FEATURES:
• Personalized workout plans tailored to your goals
• AI nutrition coaching with meal recommendations  
• Real-time progress tracking and analytics
• Community challenges and social features
• Smart coaching that adapts to your performance

📱 SMART TECHNOLOGY:
• Real-time form correction using AI
• Adaptive difficulty based on your progress
• Integration with wearables and health apps
• Offline workout capabilities

🎯 PROVEN RESULTS:
• 300% improvement in workout consistency
• 85% of users reach fitness goals within 3 months
• 24/7 AI support and motivation

🎁 SPECIAL LAUNCH OFFER:
50% OFF your first month + FREE Premium Features!

{recipient_name}, are you ready to transform your fitness journey with AI?

🚀 DOWNLOAD NOW and join thousands who've already transformed their lives!

Best regards,
{sender_name}
Senior AI Solutions Consultant
DXTR Labs
📧 automation@dxtrlabs.com
📞 +1 (555) 123-DXTR

🤖 DXTR LABS - Leading the AI Revolution

P.S. This limited-time offer won't last long. Download now and start your transformation today!
"""

    return html_content, text_content
