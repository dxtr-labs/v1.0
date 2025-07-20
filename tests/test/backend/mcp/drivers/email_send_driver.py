import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os
import sys

# Add the backend directory to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(backend_dir)

from mcp.drivers.base_driver import BaseDriver

class EmailSendDriver(BaseDriver):
    async def execute(self, parameters: dict, input_data: dict, user_id: str, engine_instance=None) -> dict:
        logging.info(f"EmailSendDriver: Executing for user {user_id}")
        
        # 1. Flexible Parameter Extraction - Handle various parameter names
        # Email recipient - support multiple parameter names
        to_email = (
            parameters.get("toEmail") or 
            parameters.get("to") or 
            parameters.get("recipient") or 
            parameters.get("email")
        )
        
        # Email subject - support multiple parameter names
        email_subject = (
            parameters.get("subject") or 
            parameters.get("title") or 
            parameters.get("subjectLine") or 
            "AI-Generated Content"
        )
        
        # Email content - support multiple parameter names
        email_text = (
            parameters.get("text") or 
            parameters.get("content") or 
            parameters.get("body") or 
            parameters.get("message") or 
            parameters.get("html") or
            ""
        )
        
        # Additional parameters with flexible naming
        cc = parameters.get("cc", parameters.get("carbonCopy"))
        bcc = parameters.get("bcc", parameters.get("blindCarbonCopy"))
        priority = parameters.get("priority", "normal")
        template_style = parameters.get("template_style", parameters.get("templateStyle", "professional"))
        sender_name = parameters.get("sender_name", parameters.get("senderName", "DXTR Labs"))
        
        logging.info(f"EmailSendDriver: Flexible parameters extracted")
        logging.info(f"EmailSendDriver: TO: {to_email}, CC: {cc}, BCC: {bcc}")
        logging.info(f"EmailSendDriver: SUBJECT: {email_subject}")
        logging.info(f"EmailSendDriver: CONTENT LENGTH: {len(email_text) if email_text else 0}")
        logging.info(f"EmailSendDriver: PRIORITY: {priority}, TEMPLATE: {template_style}")

        # 1.1. Parameter Validation - only require recipient
        if not to_email:
            logging.error(f"EmailSendDriver: Missing required email recipient")
            return {"status": "failed", "error": "Missing required email recipient (toEmail, to, recipient, or email)"}

        # 1.5. Template replacement - substitute placeholders with data from previous nodes
        
        # Replace common placeholders with data from input_data (previous node outputs)
        if input_data:
            # If there's generated content from an AI node, substitute it
            if "generated_content" in input_data:
                email_text = email_text.replace("{ai_generated_content}", input_data["generated_content"])
                email_text = email_text.replace("{{ai_generated_content}}", input_data["generated_content"])
            
            # Replace other common placeholders
            for key, value in input_data.items():
                if isinstance(value, str):
                    email_text = email_text.replace(f"{{{key}}}", value)
                    email_text = email_text.replace(f"{{{{{key}}}}}", value)
                    email_subject = email_subject.replace(f"{{{key}}}", value)
                    email_subject = email_subject.replace(f"{{{{{key}}}}}", value)
        
        # Handle AI content replacement
        if "{ai_generated_content}" in email_text and input_data and "generated_content" in input_data:
            email_text = input_data["generated_content"]
        
        logging.info(f"EmailSendDriver: Template processed, email length: {len(email_text)} characters")

        # 2. Retrieve Credentials for Email Service (e.g., SMTP or SendGrid API Key)
        # Try database first, but fallback to environment variables if DB is unavailable or fails
        email_credentials = {}
        
        try:
            # Only try database if db_pool is available
            if self.db_pool is not None:
                try:
                    email_credentials = await self._get_user_service_keys(user_id, "smtp_config")
                    logging.info("EmailSendDriver: Retrieved credentials from database")
                except Exception as db_error:
                    # If database access fails for any reason, fall back to environment variables
                    logging.warning(f"EmailSendDriver: Database access failed ({db_error}), falling back to environment variables")
                    email_credentials = {}
            else:
                logging.warning("EmailSendDriver: No database pool available, using environment variables only")
        except Exception as e:
            logging.warning(f"EmailSendDriver: Error accessing database: {e}")
            email_credentials = {}
        
        # Fallback to environment variables if not user-specific or if database failed
        smtp_host = email_credentials.get("host", os.getenv("SMTP_HOST"))
        smtp_port = email_credentials.get("port", int(os.getenv("SMTP_PORT", 587)))
        smtp_user = email_credentials.get("user", os.getenv("SMTP_USER"))
        smtp_pass = email_credentials.get("password", os.getenv("SMTP_PASSWORD"))

        logging.info(f"EmailSendDriver: Using SMTP config - Host: {smtp_host}, Port: {smtp_port}, User: {smtp_user}")

        if not all([smtp_host, smtp_user, smtp_pass]):
            missing = []
            if not smtp_host: missing.append("SMTP_HOST")
            if not smtp_user: missing.append("SMTP_USER") 
            if not smtp_pass: missing.append("SMTP_PASSWORD")
            error_msg = f"SMTP credentials are not fully configured. Missing: {', '.join(missing)}"
            logging.error(f"EmailSendDriver: {error_msg}")
            return {"status": "failed", "error": error_msg}

        from_email = parameters.get("fromEmail", parameters.get("from", smtp_user)) # Use user-defined fromEmail or default to SMTP user

        # 3. Construct Email with flexible parameters
        msg = MIMEMultipart("alternative")
        msg["From"] = from_email
        msg["To"] = to_email  # Use flexible parameter
        msg["Subject"] = email_subject  # Use processed subject
        
        # Add CC and BCC if provided
        if cc:
            msg["Cc"] = cc
            logging.info(f"EmailSendDriver: Added CC: {cc}")
        if bcc:
            msg["Bcc"] = bcc
            logging.info(f"EmailSendDriver: Added BCC: {bcc}")
        
        # Add priority header if specified
        if priority.lower() in ["high", "urgent", "1"]:
            msg["X-Priority"] = "1"
            msg["X-MSMail-Priority"] = "High"
        elif priority.lower() in ["low", "3"]:
            msg["X-Priority"] = "3"
            msg["X-MSMail-Priority"] = "Low"

        # Attach email content
        if email_text:  # Use processed text
            msg.attach(MIMEText(email_text, "plain"))
        
        # Check for HTML content in flexible parameters
        html_content = parameters.get("html", parameters.get("htmlContent"))
        if html_content:
            msg.attach(MIMEText(html_content, "html"))

        # 4. Send Email with flexible recipient handling
        try:
            # Build recipient list including CC and BCC
            recipients = [to_email]
            if cc:
                if isinstance(cc, str):
                    recipients.extend([email.strip() for email in cc.split(",")])
                elif isinstance(cc, list):
                    recipients.extend(cc)
            if bcc:
                if isinstance(bcc, str):
                    recipients.extend([email.strip() for email in bcc.split(",")])
                elif isinstance(bcc, list):
                    recipients.extend(bcc)
            
            logging.info(f"EmailSendDriver: Sending to {len(recipients)} recipients: {recipients}")
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls() # Secure the connection
                server.login(smtp_user, smtp_pass)
                server.send_message(msg, to_addrs=recipients)
            
            logging.info(f"EmailSendDriver: Email sent successfully to {to_email} (and {len(recipients)-1} additional recipients)")
            return {
                "status": "success", 
                "message": f"Email sent successfully to {to_email}",
                "recipients": recipients,
                "subject": email_subject,
                "priority": priority,
                "template_style": template_style
            }
        except Exception as e:
            logging.error(f"EmailSendDriver: Error sending email to {to_email}: {e}", exc_info=True)
            return {"status": "failed", "error": str(e)}
    
    async def generate_email_preview(self, parameters: dict, user_id: str) -> dict:
        """Generate a preview of the email without sending it"""
        logging.info(f"EmailSendDriver: Generating email preview for user {user_id}")
        
        # Extract parameters using the same flexible approach
        to_email = (
            parameters.get("toEmail") or 
            parameters.get("to") or 
            parameters.get("recipient") or 
            parameters.get("email")
        )
        
        email_subject = (
            parameters.get("subject") or 
            parameters.get("title") or 
            parameters.get("subjectLine") or 
            "AI-Generated Content"
        )
        
        email_text = (
            parameters.get("text") or 
            parameters.get("content") or 
            parameters.get("body") or 
            parameters.get("message") or 
            parameters.get("html") or
            ""
        )
        
        cc = parameters.get("cc", parameters.get("carbonCopy"))
        bcc = parameters.get("bcc", parameters.get("blindCarbonCopy"))
        priority = parameters.get("priority", "normal")
        template_style = parameters.get("template_style", parameters.get("templateStyle", "professional"))
        sender_name = parameters.get("sender_name", parameters.get("senderName", "DXTR Labs"))
        
        # Get SMTP configuration
        smtp_user = os.getenv('SMTP_USER', os.getenv('COMPANY_EMAIL'))
        smtp_host = os.getenv('SMTP_HOST', 'mail.privateemail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        
        if not smtp_user:
            return {
                "status": "error", 
                "error": "SMTP configuration not found",
                "preview": None
            }
        
        # Generate email preview
        email_preview = {
            "from": f"{sender_name} <{smtp_user}>",
            "to": to_email,
            "cc": cc if cc else None,
            "bcc": bcc if bcc else None,
            "subject": email_subject,
            "body": email_text,
            "priority": priority,
            "template_style": template_style,
            "smtp_server": f"{smtp_host}:{smtp_port}",
            "estimated_size": len(email_text.encode('utf-8')) if email_text else 0,
            "recipients_count": 1 + (len(cc.split(',')) if cc else 0) + (len(bcc.split(',')) if bcc else 0)
        }
        
        # Generate HTML preview for display
        html_preview = f"""
        <div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
            <div style="background: #f8f9fa; padding: 15px; border-bottom: 1px solid #ddd;">
                <h3 style="margin: 0; color: #333;">📧 Email Preview</h3>
            </div>
            <div style="padding: 15px;">
                <div style="margin-bottom: 10px;"><strong>From:</strong> {email_preview['from']}</div>
                <div style="margin-bottom: 10px;"><strong>To:</strong> {to_email}</div>
                {f'<div style="margin-bottom: 10px;"><strong>CC:</strong> {cc}</div>' if cc else ''}
                {f'<div style="margin-bottom: 10px;"><strong>BCC:</strong> {bcc}</div>' if bcc else ''}
                <div style="margin-bottom: 10px;"><strong>Subject:</strong> {email_subject}</div>
                <hr style="margin: 15px 0;">
                <div style="background: #f8f9fa; padding: 15px; border-radius: 4px;">
                    <div style="white-space: pre-wrap;">{email_text}</div>
                </div>
                <hr style="margin: 15px 0;">
                <div style="font-size: 12px; color: #666;">
                    <div>Recipients: {email_preview['recipients_count']}</div>
                    <div>Size: {email_preview['estimated_size']} bytes</div>
                    <div>SMTP: {email_preview['smtp_server']}</div>
                </div>
            </div>
        </div>
        """
        
        return {
            "status": "success",
            "preview": email_preview,
            "html_preview": html_preview,
            "ready_to_send": bool(to_email and email_text),
            "validation": {
                "has_recipient": bool(to_email),
                "has_subject": bool(email_subject),
                "has_content": bool(email_text),
                "valid_email": bool(to_email and '@' in to_email)
            }
        }

    async def send_email_mcp_action(self, parameters: dict) -> dict:
        """Send email with MCP action format"""
        try:
            # Use the existing execute method with dummy user_id
            result = await self.execute(parameters, {}, "mcp_user")
            
            if result.get("status") == "success":
                return {
                    "success": True,
                    "message": result.get("message"),
                    "recipients": result.get("recipients"),
                    "subject": result.get("subject")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Email send failed")
                }
        except Exception as e:
            logging.error(f"EmailSendDriver: MCP action error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

