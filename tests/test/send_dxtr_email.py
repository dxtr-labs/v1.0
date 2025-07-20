import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration
smtp_server = 'mail.privateemail.com'
smtp_port = 587
sender_email = 'automation-engine@dxtr-labs.com'
sender_password = 'Lakshu11042005$'
recipient_email = 'slakshanand1105@gmail.com'
subject = 'DXTR Labs Virtual Workforce - Ready to Automate Your Business?'

# Create the message
message = """Dear Slakshan,

Hi! Sam from DXTR Labs here.

We're revolutionizing business operations with our AI-powered Virtual Workforce that never sleeps, never makes mistakes, and can scale instantly.

🚀 DXTR LABS VIRTUAL WORKFORCE ADVANTAGES:

💰 MASSIVE COST SAVINGS: 60-80% reduction compared to traditional hiring
⏰ 24/7 OPERATIONS: Round-the-clock productivity with zero downtime
⚡ INSTANT SCALABILITY: Scale from 1 to 1000 AI agents in minutes
🎯 PERFECT ACCURACY: 99.9% error-free task execution
🚀 RAPID DEPLOYMENT: Go live in just 24 hours

✨ PERFECT FOR YOUR BUSINESS:
• Customer Service: Handle 1000+ customer inquiries simultaneously
• Data Processing: Analyze millions of records in minutes, not months
• Sales & Marketing: Personalized outreach campaigns at unprecedented scale
• Financial Operations: Automated reporting, compliance, and analysis
• HR & Recruitment: Intelligent candidate screening and onboarding

📊 PROVEN RESULTS FROM OUR CLIENTS:
• 300% productivity increase
• 70% cost reduction
• 24/7 guaranteed uptime
• 99.9% accuracy rate

🎁 EXCLUSIVE LAUNCH OFFER:
50% OFF your first 3 months + FREE $10,000 implementation package

Slakshan, ARE YOU READY TO AUTOMATE your business and join the AI revolution?

Over 500+ companies have already transformed their operations with our Virtual Workforce.

🚀 READY TO GET STARTED?
Reply to this email or call +1 (555) DXTR-LAB for your FREE consultation and demo.

Best regards,
Sam Rodriguez
Senior AI Solutions Consultant
DXTR Labs Virtual Workforce Division
📧 sam@dxtrlabs.com
📞 +1 (555) 123-DXTR

🤖 DXTR LABS - Leading the AI Revolution

P.S. This is a limited time offer. Don't miss your chance to be among the first 100 companies to implement our revolutionary Virtual Workforce technology!"""

try:
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    # Add body to email
    msg.attach(MIMEText(message, 'plain'))
    
    # Create SMTP session
    print('📧 Connecting to SMTP server...')
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Enable TLS encryption
    server.login(sender_email, sender_password)
    
    # Send email
    text = msg.as_string()
    server.sendmail(sender_email, recipient_email, text)
    server.quit()
    
    print('✅ DXTR Labs Virtual Workforce email sent successfully!')
    print(f'📧 To: {recipient_email}')
    print(f'📄 Subject: {subject}')
    print('🎯 The beautiful sales email has been delivered!')
    
except Exception as e:
    print(f'❌ Error sending email: {str(e)}')
