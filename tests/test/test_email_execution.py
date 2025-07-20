import asyncio
import sys
import os
import requests
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_complete_email_execution():
    """Test the complete email workflow: generation + execution"""
    
    print("🚀 Testing Complete Email Workflow with Execution")
    print("=" * 60)
    
    from backend.mcp.simple_mcp_llm import MCP_LLM_Orchestrator
    
    orchestrator = MCP_LLM_Orchestrator()
    
    # Test the email generation
    user_message = "service:inhouse Using AI generate a sales pitch for Roomify - one stop place for college students to find roommates and send to slakshanand1105@gmail.com"
    
    print("Step 1: Generating AI workflow...")
    result = await orchestrator.process_user_input("test_user", "test_agent", user_message)
    
    print(f"Status: {result.get('status')}")
    print(f"Message: {result.get('message')}")
    
    if result.get('workflow_json'):
        workflow_json = result['workflow_json']
        print("\n✅ Workflow Generated!")
        print(f"Type: {workflow_json.get('type')}")
        print(f"Recipient: {workflow_json.get('recipient')}")
        print(f"AI Service: {workflow_json.get('ai_service')}")
        
        # Check if workflow has actions
        if 'workflow' in workflow_json and 'actions' in workflow_json['workflow']:
            actions = workflow_json['workflow']['actions']
            print(f"Actions: {len(actions)}")
            
            for i, action in enumerate(actions, 1):
                print(f"  Action {i}: {action.get('node')}")
                if action.get('node') == 'emailSend':
                    params = action.get('parameters', {})
                    print(f"    📧 TO: {params.get('toEmail')}")
                    print(f"    📧 SUBJECT: {params.get('subject')}")
        
        print("\nStep 2: Executing workflow directly...")
        
        # Since we don't have auth, let's execute the workflow manually
        await execute_workflow_manually(workflow_json)
        
    else:
        print("❌ No workflow generated")

async def execute_workflow_manually(workflow_json):
    """Execute the workflow manually by calling the email driver directly"""
    
    try:
        print("🔧 Manual Workflow Execution...")
        
        # Set up email environment
        os.environ['SMTP_HOST'] = 'smtp.gmail.com'  # Try Gmail SMTP
        os.environ['SMTP_PORT'] = '587'
        os.environ['SMTP_USER'] = 'your-email@gmail.com'  # You'll need to set this
        os.environ['SMTP_PASSWORD'] = 'your-app-password'  # You'll need to set this
        
        if 'workflow' in workflow_json and 'actions' in workflow_json['workflow']:
            actions = workflow_json['workflow']['actions']
            
            # Execute each action
            for i, action in enumerate(actions, 1):
                print(f"\nExecuting Action {i}: {action.get('node')}")
                
                if action.get('node') == 'mcpLLM':
                    # AI content generation - already done, skip
                    print("  ✅ AI content generation (already completed)")
                    
                elif action.get('node') == 'emailSend':
                    print("  📧 Executing email sending...")
                    
                    params = action.get('parameters', {})
                    
                    # Replace placeholder with actual AI content
                    email_content = params.get('text', '')
                    if '{ai_generated_content}' in email_content:
                        # Get the AI content from the workflow preview
                        ai_content = get_ai_content_from_workflow(workflow_json)
                        email_content = email_content.replace('{ai_generated_content}', ai_content)
                    
                    # Create a simple email sending function
                    email_result = await send_email_simple(
                        to_email=params.get('toEmail'),
                        subject=params.get('subject'),
                        content=email_content
                    )
                    
                    print(f"  📧 Email Result: {email_result}")
        
    except Exception as e:
        print(f"❌ Workflow execution failed: {e}")
        import traceback
        traceback.print_exc()

def get_ai_content_from_workflow(workflow_json):
    """Extract AI-generated content from workflow preview"""
    
    # For now, return a sample Roomify content
    return """🏠 Find Your Perfect College Roommate with Roomify! 🎓

Dear College Student,

Tired of random roommate assignments? Struggling to find someone compatible? 

Introducing **Roomify** - the ultimate platform designed specifically for college students to find their ideal roommates!

🌟 Why Choose Roomify:
• Smart matching algorithm based on lifestyle preferences
• Verified student profiles for safety and trust  
• Campus-specific communities for your university
• Budget-friendly room sharing options
• 24/7 support for seamless connections

🎁 **Special Launch Offer**: FREE premium membership for first 100 students!

Don't leave your living situation to chance. Join thousands of students who've found their perfect roommate match through Roomify!

Ready to find your ideal roommate? Sign up today!

Happy Room Hunting,
The Roomify Team 🏠✨"""

async def send_email_simple(to_email, subject, content):
    """Simple email sending function with proper error handling"""
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        print(f"    📧 Attempting to send email to {to_email}...")
        print(f"    📧 Subject: {subject}")
        print(f"    📧 Content length: {len(content)} characters")
        
        # For now, just simulate email sending since we don't have real SMTP credentials
        print("    📧 SIMULATING EMAIL SEND (no real SMTP configured)")
        print("    📧 Email content preview:")
        print("    " + "-" * 40)
        print("    " + content[:200] + "..." if len(content) > 200 else "    " + content)
        print("    " + "-" * 40)
        
        return {
            "status": "simulated_success",
            "message": f"Email would be sent to {to_email}",
            "to": to_email,
            "subject": subject,
            "content_length": len(content)
        }
        
        # Uncomment this section when you have real SMTP credentials:
        """
        smtp_host = os.getenv('SMTP_HOST')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_user = os.getenv('SMTP_USER')
        smtp_pass = os.getenv('SMTP_PASSWORD')
        
        if not all([smtp_host, smtp_user, smtp_pass]):
            return {"status": "failed", "error": "SMTP credentials not configured"}
        
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(content, "plain"))
        
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [to_email], msg.as_string())
        
        return {"status": "success", "message": f"Email sent to {to_email}"}
        """
        
    except Exception as e:
        return {"status": "failed", "error": str(e)}

if __name__ == "__main__":
    asyncio.run(test_complete_email_execution())
