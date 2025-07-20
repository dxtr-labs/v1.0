#!/usr/bin/env python3
"""
Test complete frontend workflow simulation: AI service selection → Content generation → Email sending
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

class EmailSender:
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'mail.privateemail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER', 'automation-engine@dxtr-labs.com')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        
        logger.info(f"📧 Email configured: {self.smtp_user} via {self.smtp_host}:{self.smtp_port}")

    def send_email(self, to_email: str, subject: str, content: str) -> bool:
        """Send email using SMTP configuration"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(content, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent successfully!")
            logger.info(f"   📧 To: {to_email}")
            logger.info(f"   📝 Subject: {subject}")
            logger.info(f"   📊 Content Length: {len(content)} characters")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return False

async def test_complete_workflow():
    """Test the complete frontend workflow simulation"""
    
    logger.info("🧪 Testing Complete Frontend Workflow Simulation")
    logger.info("=" * 60)
    
    # Initialize MCP LLM system
    mcp_llm = MCP_LLM_Orchestrator()
    logger.info("🤖 MCP LLM system initialized")
    
    # Initialize email sender
    email_sender = EmailSender()
    
    # Step 1: User input (like frontend would send)
    user_message = "draft a sales pitch to sell better torch lights using AI and send email to slakshanand1105@gmail.com"
    logger.info(f"📝 User Message: {user_message}")
    
    # Step 2: Process initial request (like frontend API call)
    logger.info("\n🔄 Step 1: Initial Request Processing")
    response1 = await mcp_llm.process_user_input(
        user_id="test_user_frontend",
        agent_id="test_agent_frontend",
        user_message=user_message
    )
    
    logger.info(f"   Status: {response1['status']}")
    logger.info(f"   Message: {response1.get('message', 'No message')[:100]}...")
    
    if response1['status'] == 'ai_service_selection':
        logger.info("   ✅ Correctly triggered AI service selection")
        
        # Step 3: User selects AI service (simulate frontend selection)
        logger.info("\n🔄 Step 2: AI Service Selection")
        service_selection_message = f"service:inhouse {user_message}"
        logger.info(f"   Selected: In-House AI")
        logger.info(f"   New Message: {service_selection_message}")
        
        # Step 4: Process with selected AI service
        response2 = await mcp_llm.process_user_input(
            user_id="test_user_frontend",
            agent_id="test_agent_frontend", 
            user_message=service_selection_message
        )
        
        logger.info(f"   Status: {response2['status']}")
        
        if response2['status'] == 'workflow_preview':
            logger.info("   ✅ Generated workflow preview")
            
            # Extract workflow details
            workflow_json = response2.get('workflow_json', {})
            workflow_actions = workflow_json.get('workflow', {}).get('actions', [])
            
            logger.info(f"   📋 Workflow Actions: {len(workflow_actions)}")
            
            # Step 5: Execute the workflow (simulate what backend would do)
            logger.info("\n🔄 Step 3: Workflow Execution")
            
            ai_generated_content = None
            email_params = None
            
            # Process workflow actions
            for i, action in enumerate(workflow_actions):
                logger.info(f"   Action {i+1}: {action.get('node', 'unknown')}")
                
                if action.get('node') == 'mcpLLM':
                    # Generate AI content
                    user_input = action.get('parameters', {}).get('user_input', '')
                    logger.info(f"      🤖 Generating AI content for: {user_input[:50]}...")
                    
                    # Use the MCP LLM's content generation
                    ai_generated_content = mcp_llm._generate_sample_content(user_input, 'sales_email')
                    logger.info(f"      ✅ Generated {len(ai_generated_content)} chars of content")
                
                elif action.get('node') == 'emailSend':
                    # Extract email parameters
                    params = action.get('parameters', {})
                    email_params = {
                        'to_email': params.get('toEmail', 'slakshanand1105@gmail.com'),
                        'subject': params.get('subject', 'AI-Generated Sales Pitch'),
                        'content': params.get('content', '{ai_generated_content}')
                    }
                    logger.info(f"      📧 Email params extracted")
            
            # Step 6: Send the actual email
            if ai_generated_content and email_params:
                logger.info("\n🔄 Step 4: Email Sending")
                
                # Replace placeholder with actual AI content
                final_content = email_params['content'].replace('{ai_generated_content}', ai_generated_content)
                
                success = email_sender.send_email(
                    to_email=email_params['to_email'],
                    subject=email_params['subject'],
                    content=final_content
                )
                
                if success:
                    logger.info("🎉 COMPLETE SUCCESS: Full workflow executed!")
                    logger.info(f"   📧 Email delivered to: {email_params['to_email']}")
                    logger.info(f"   🎨 AI-generated content length: {len(ai_generated_content)} chars")
                else:
                    logger.error("❌ Email sending failed")
            else:
                logger.error("❌ Missing AI content or email parameters")
        else:
            logger.error(f"❌ Expected workflow_preview, got: {response2['status']}")
    else:
        logger.error(f"❌ Expected ai_service_selection, got: {response1['status']}")
    
    logger.info("=" * 60)
    logger.info("🏁 Complete Workflow Test Finished")

if __name__ == "__main__":
    asyncio.run(test_complete_workflow())
