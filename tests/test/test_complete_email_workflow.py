import asyncio
import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def send_actual_email(to_email: str, subject: str, content: str) -> dict:
    """Send an actual email using SMTP"""
    
    # Email credentials
    smtp_host = "mail.privateemail.com"
    smtp_port = 587
    smtp_user = "suguavaneshwaran@dxtrlabs.com" 
    smtp_pass = "P@ssw0rd2025"
    
    try:
        print(f"📧 Sending email to {to_email}...")
        print(f"📧 Subject: {subject}")
        print(f"📧 Content preview: {content[:100]}...")
        
        # Create message
        msg = MIMEMultipart("alternative")
        msg["From"] = smtp_user
        msg["To"] = to_email
        msg["Subject"] = subject
        
        # Add content
        msg.attach(MIMEText(content, "plain"))
        
        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            
            # Send to both TO and BCC (if any)
            recipients = [to_email]
            
            server.sendmail(smtp_user, recipients, msg.as_string())
            
        print("✅ EMAIL SENT SUCCESSFULLY!")
        return {
            "status": "success",
            "message": f"Email sent successfully to {to_email}",
            "from": smtp_user,
            "to": to_email,
            "subject": subject
        }
        
    except Exception as e:
        print(f"❌ EMAIL FAILED: {e}")
        return {
            "status": "failed", 
            "error": str(e)
        }

async def test_complete_ai_email_workflow():
    """Test the complete AI email workflow from content generation to actual sending"""
    
    print("🤖 Testing Complete AI Email Workflow...")
    print("=" * 60)
    
    from backend.mcp.simple_mcp_llm import MCP_LLM_Orchestrator
    
    orchestrator = MCP_LLM_Orchestrator()
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "CodeMaster IDE",
            "message": "service:inhouse Using AI generate a sales pitch for CodeMaster - a revolutionary IDE for developers and send to slakshanand1105@gmail.com"
        },
        {
            "name": "Roomify Roommate Finder", 
            "message": "service:inhouse Using AI generate a sales pitch for Roomify - one stop place for college students to find roommates and send to slakshanand1105@gmail.com"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. Testing: {scenario['name']}")
        print("-" * 40)
        
        try:
            # Generate AI workflow
            result = await orchestrator.process_user_input("test_user", "test_agent", scenario['message'])
            
            print(f"Status: {result.get('status')}")
            
            if result.get('workflow_preview') and result['workflow_preview'].get('email_preview'):
                email_preview = result['workflow_preview']['email_preview']
                
                # Extract email details
                to_email = email_preview.get('to')
                subject = email_preview.get('subject', 'AI-Generated Content')
                
                # Extract the actual content from the preview
                preview_content = email_preview.get('preview_content', '')
                
                # Parse the content between the --- markers
                content_lines = preview_content.split('\n')
                email_content = []
                in_content_section = False
                
                for line in content_lines:
                    if '---' in line and not in_content_section:
                        in_content_section = True
                        continue
                    elif '---' in line and in_content_section:
                        break
                    elif in_content_section:
                        email_content.append(line)
                
                # Clean up the content
                final_content = '\n'.join(email_content).strip()
                
                # Remove the "Note: Final content will be generated..." line
                if "Note: Final content will be generated" in final_content:
                    final_content = final_content.split("Note: Final content will be generated")[0].strip()
                
                print(f"📧 TO: {to_email}")
                print(f"📧 SUBJECT: {subject}")
                print(f"📧 CONTENT LENGTH: {len(final_content)} characters")
                
                # Ask user if they want to send
                print("\n🤔 Do you want to send this email? (y/n)")
                user_input = input().strip().lower()
                
                if user_input == 'y' or user_input == 'yes':
                    # Send the actual email
                    email_result = send_actual_email(to_email, subject, final_content)
                    
                    if email_result.get('status') == 'success':
                        print(f"✅ EMAIL SENT: {scenario['name']} email sent to {to_email}")
                    else:
                        print(f"❌ EMAIL FAILED: {email_result.get('error')}")
                else:
                    print("⏭️ Email sending skipped")
            else:
                print("❌ No email preview generated")
                
        except Exception as e:
            print(f"❌ Error in scenario {scenario['name']}: {e}")
            import traceback
            traceback.print_exc()
        
        print()

if __name__ == "__main__":
    asyncio.run(test_complete_ai_email_workflow())
