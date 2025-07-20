import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.email_sender import parse_email_automation_request, send_email_directly
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

def test_email_sending():
    # Test the parsing function
    test_message = "send email to slakshanand1105@gmail.com good morning 5:46PM MST"
    print("🧪 Testing email parsing...")
    
    parsed = parse_email_automation_request(test_message)
    print(f"Parsed result: {parsed}")
    
    if parsed["success"]:
        print(f"✅ Email parsed successfully!")
        print(f"To: {parsed['to_email']}")
        print(f"Subject: {parsed['subject']}")
        print(f"Body: {parsed['body']}")
        
        # Check environment variables
        print("\n🔧 Checking email configuration...")
        email_user = os.getenv('EMAIL_USER')
        email_pass = os.getenv('EMAIL_PASS')
        email_host = os.getenv('EMAIL_HOST')
        email_port = os.getenv('EMAIL_PORT')
        
        print(f"EMAIL_USER: {email_user}")
        print(f"EMAIL_HOST: {email_host}")
        print(f"EMAIL_PORT: {email_port}")
        print(f"EMAIL_PASS: {'*' * len(email_pass) if email_pass else 'NOT SET'}")
        
        if not email_pass:
            print("❌ EMAIL_PASS is not set in environment variables!")
            return
        
        print("\n📧 Attempting to send email...")
        try:
            result = send_email_directly(
                parsed["to_email"],
                parsed["subject"],
                parsed["body"]
            )
            print(f"Email send result: {result}")
        except Exception as e:
            print(f"❌ Error sending email: {e}")
    else:
        print(f"❌ Failed to parse email: {parsed.get('error')}")

if __name__ == "__main__":
    test_email_sending()
