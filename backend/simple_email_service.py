import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self):
        # Default configuration - can be overridden
        self.smtp_host = "mail.privateemail.com"  # PrivateMail SMTP
        self.smtp_port = 587
        self.smtp_user = None
        self.smtp_password = None
        self.configured = False
    
    def configure(self, email: str, password: str, host: str = "mail.privateemail.com", port: int = 587):
        """Configure email service with credentials"""
        self.smtp_user = email
        self.smtp_password = password
        self.smtp_host = host
        self.smtp_port = port
        self.configured = True
        print(f"✅ Email service configured for {email}")
    
    def test_connection(self):
        """Test SMTP connection"""
        if not self.configured:
            return {"success": False, "error": "Email service not configured"}
        
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
            return {"success": True, "message": "SMTP connection successful"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: str = None):
        """Send email"""
        if not self.configured:
            print("❌ Email service not configured")
            return {"success": False, "error": "Email service not configured"}
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_user
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
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {to_email}")
            return {
                "success": True,
                "message": f"Email sent to {to_email}",
                "subject": subject
            }
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return {"success": False, "error": str(e)}

# Global email service instance
email_service = EmailService()

def quick_send_email(to_email: str, subject: str, body: str):
    """Quick email sending function"""
    return email_service.send_email(to_email, subject, body)

if __name__ == "__main__":
    print("=== Email Service Test ===")
    print("To configure email service, you need:")
    print("1. Your email address")
    print("2. App password (for Gmail: Settings > Security > 2-Step Verification > App passwords)")
    print("\nExample configuration:")
    print("email_service.configure('your-email@gmail.com', 'your-app-password')")
    print("\nThen test with:")
    print("email_service.send_email('recipient@email.com', 'Subject', 'Body text')")
