#!/usr/bin/env python3
"""
Complete Automated Email Workflow - Bypasses Frontend Issues
This script will:
1. Use your custom MCP LLM system
2. Generate AI content for torch lights sales pitch
3. Send email to slakshanand1105@gmail.com
4. Show the complete workflow working
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

class CompleteEmailWorkflow:
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'mail.privateemail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER', 'automation-engine@dxtr-labs.com')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        
        self.mcp_llm = MCP_LLM_Orchestrator()
        
        logger.info(f"🔧 Email System: {self.smtp_user} via {self.smtp_host}:{self.smtp_port}")
        logger.info(f"🤖 MCP LLM: Initialized and ready")

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
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Email sending failed: {e}")
            return False

    async def execute_complete_workflow(self, user_request: str, target_email: str):
        """Execute the complete AI → Email workflow"""
        
        logger.info("🚀 EXECUTING COMPLETE AUTOMATED WORKFLOW")
        logger.info("=" * 70)
        logger.info(f"📝 Request: {user_request}")
        logger.info(f"📧 Target: {target_email}")
        logger.info("")
        
        # Step 1: Process initial request
        logger.info("🔄 STEP 1: Processing User Request")
        response1 = await self.mcp_llm.process_user_input(
            user_id="automated_user",
            agent_id="automated_agent",
            user_message=user_request
        )
        
        logger.info(f"   Status: {response1['status']}")
        
        if response1['status'] == 'ai_service_selection':
            logger.info("   ✅ AI service selection triggered")
            
            # Step 2: Automatically select in-house AI service
            logger.info("\n🔄 STEP 2: Auto-Selecting In-House AI Service")
            service_request = f"service:inhouse {user_request}"
            
            response2 = await self.mcp_llm.process_user_input(
                user_id="automated_user",
                agent_id="automated_agent",
                user_message=service_request
            )
            
            logger.info(f"   Status: {response2['status']}")
            
            if response2['status'] == 'workflow_preview':
                logger.info("   ✅ Workflow preview generated")
                
                # Step 3: Extract and execute workflow
                logger.info("\n🔄 STEP 3: Executing Workflow")
                workflow_json = response2.get('workflow_json', {})
                actions = workflow_json.get('workflow', {}).get('actions', [])
                
                ai_content = None
                email_params = None
                
                # Process each action
                for i, action in enumerate(actions):
                    action_type = action.get('node', 'unknown')
                    logger.info(f"   Action {i+1}: {action_type}")
                    
                    if action_type == 'mcpLLM':
                        # Generate AI content
                        user_input = action.get('parameters', {}).get('user_input', user_request)
                        logger.info(f"      🤖 Generating AI content...")
                        
                        ai_content = self.mcp_llm._generate_sample_content(user_input, 'sales_email')
                        logger.info(f"      ✅ Generated {len(ai_content)} characters")
                        
                    elif action_type == 'emailSend':
                        # Extract email parameters
                        params = action.get('parameters', {})
                        email_params = {
                            'to_email': params.get('toEmail', target_email),
                            'subject': params.get('subject', '🔦 BrightBeam Torch Lights - Illuminate Your Path!'),
                            'content': params.get('content', '{ai_generated_content}')
                        }
                        logger.info(f"      📧 Email parameters prepared")
                
                # Step 4: Send the email
                if ai_content and email_params:
                    logger.info("\n🔄 STEP 4: Sending Email")
                    
                    # Replace placeholder with actual content
                    final_content = email_params['content'].replace('{ai_generated_content}', ai_content)
                    
                    logger.info(f"   📧 To: {email_params['to_email']}")
                    logger.info(f"   📝 Subject: {email_params['subject']}")
                    logger.info(f"   📊 Content: {len(final_content)} characters")
                    logger.info(f"   🎨 Content Preview:")
                    logger.info(f"      {final_content[:200]}...")
                    
                    # Send the email
                    success = self.send_email(
                        to_email=email_params['to_email'],
                        subject=email_params['subject'],
                        content=final_content
                    )
                    
                    if success:
                        logger.info("\n🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
                        logger.info("✅ AI-generated sales pitch email sent!")
                        logger.info(f"✅ Delivered to: {email_params['to_email']}")
                        logger.info(f"✅ Using: Custom MCP LLM + SMTP delivery")
                        return True
                    else:
                        logger.error("❌ Email delivery failed")
                        return False
                else:
                    logger.error("❌ Missing AI content or email parameters")
                    return False
            else:
                logger.error(f"❌ Expected workflow_preview, got: {response2['status']}")
                return False
        else:
            logger.error(f"❌ Expected ai_service_selection, got: {response1['status']}")
            return False
        
        return False

async def main():
    """Run the complete automated workflow"""
    
    logger.info("🎯 COMPLETE AUTOMATED EMAIL WORKFLOW")
    logger.info("This will generate and send the torch lights sales pitch email")
    logger.info("using your custom MCP LLM system and SMTP configuration.")
    logger.info("")
    
    # Initialize workflow
    workflow = CompleteEmailWorkflow()
    
    # Execute the complete workflow
    user_request = "draft a sales pitch to sell better torch lights using AI and send email to slakshanand1105@gmail.com"
    target_email = "slakshanand1105@gmail.com"
    
    success = await workflow.execute_complete_workflow(user_request, target_email)
    
    logger.info("=" * 70)
    if success:
        logger.info("🏆 MISSION ACCOMPLISHED!")
        logger.info("📧 Your torch lights sales pitch email has been sent!")
        logger.info("🎨 Generated using your custom MCP LLM system")
        logger.info("🚀 Delivered via your SMTP configuration")
    else:
        logger.info("❌ Workflow execution failed")
    logger.info("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
