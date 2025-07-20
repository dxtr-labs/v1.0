import imaplib
import email
from email.header import decode_header
import logging
import os
import sys
import sys

# Add the backend directory to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(backend_dir)

from mcp.drivers.base_driver import BaseDriver

class EmailReadImapDriver(BaseDriver):
    async def execute(self, parameters: dict, input_data: dict, user_id: str, engine_instance=None) -> dict:
        logging.info(f"EmailReadImapDriver: Executing for user {user_id}")

        # 1. Parameter Validation
        required_params = ["mailbox", "postProcessAction", "format"]
        for p in required_params:
            if p not in parameters:
                logging.error(f"EmailReadImapDriver: Missing required parameter: {p}")
                return {"status": "failed", "error": f"Missing required parameter: {p}"}

        mailbox = parameters["mailbox"]
        post_process_action = parameters["postProcessAction"] # 'read' or 'delete'
        output_format = parameters["format"] # 'simple' or 'resolved'
        download_attachments = parameters.get("downloadAttachments", False)
        options = parameters.get("options", {}) # Custom IMAP search options

        # 2. Retrieve Credentials
        try:
            imap_credentials = await self._get_user_service_keys(user_id, "imap_config")
            imap_host = imap_credentials.get("host", os.getenv("IMAP_HOST"))
            imap_port = imap_credentials.get("port", int(os.getenv("IMAP_PORT", 993)))
            imap_user = imap_credentials.get("user", os.getenv("IMAP_USER"))
            imap_pass = imap_credentials.get("password", os.getenv("IMAP_PASSWORD"))

            if not all([imap_host, imap_user, imap_pass]):
                raise ValueError("IMAP credentials (host, user, password) are not fully configured.")
        except Exception as e:
            logging.error(f"EmailReadImapDriver: Failed to retrieve IMAP credentials: {e}")
            return {"status": "failed", "error": f"Failed to retrieve IMAP credentials: {e}"}

        emails_data = []
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(imap_host, imap_port)
            mail.login(imap_user, imap_pass)
            mail.select(mailbox)

            # Build search criteria
            search_criteria = 'UNSEEN' # Default to unread
            if options.get("customEmailConfig"):
                # This is a very simplified handling. Real IMAP search is complex.
                # The LLM's output for customEmailConfig needs to be carefully structured.
                try:
                    # Assuming customEmailConfig is a JSON string of a list, e.g., '["SUBJECT", "invoice"]'
                    # Or more complex: '["UNSEEN", ["SUBJECT", "invoice"]]'
                    custom_config = json.loads(options["customEmailConfig"])
                    if isinstance(custom_config, list):
                        search_criteria = ' '.join(map(str, custom_config)) # Simple join, needs robust parsing
                    else:
                        logging.warning(f"EmailReadImapDriver: Invalid customEmailConfig format: {options['customEmailConfig']}")
                except json.JSONDecodeError:
                    logging.warning(f"EmailReadImapDriver: customEmailConfig is not valid JSON: {options['customEmailConfig']}")
                except Exception as e:
                    logging.warning(f"EmailReadImapDriver: Error parsing customEmailConfig: {e}")
            
            # Search for emails
            status, email_ids = mail.search(None, search_criteria)
            email_id_list = email_ids[0].split()

            for email_id in email_id_list:
                status, msg_data = mail.fetch(email_id, '(RFC822)') # Fetch the email content
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        email_info = {
                            "id": email_id.decode(),
                            "from": msg.get("From"),
                            "to": msg.get("To"),
                            "subject": ''.join(part.decode(charset or 'utf-8') for part, charset in decode_header(msg.get("Subject"))),
                            "date": msg.get("Date"),
                            "body_plain": "",
                            "body_html": "",
                            "attachments": []
                        }

                        # Extract body
                        if msg.is_multipart():
                            for part in msg.walk():
                                ctype = part.get_content_type()
                                cdisp = str(part.get("Content-Disposition"))

                                if ctype == "text/plain" and "attachment" not in cdisp:
                                    email_info["body_plain"] = part.get_payload(decode=True).decode(errors='ignore')
                                elif ctype == "text/html" and "attachment" not in cdisp:
                                    email_info["body_html"] = part.get_payload(decode=True).decode(errors='ignore')
                                elif download_attachments and "attachment" in cdisp:
                                    filename = part.get_filename()
                                    if filename:
                                        # In a real scenario, you'd save this to a temp file or cloud storage
                                        email_info["attachments"].append({"filename": filename, "size": len(part.get_payload(decode=True))})
                        else:
                            email_info["body_plain"] = msg.get_payload(decode=True).decode(errors='ignore')
                        
                        emails_data.append(email_info)

                # Mark as read or delete based on postProcessAction
                if post_process_action == "read":
                    mail.store(email_id, '+FLAGS', '\\Seen')
                elif post_process_action == "delete":
                    mail.store(email_id, '+FLAGS', '\\Deleted')
            
            if post_process_action == "delete":
                mail.expunge() # Permanently remove deleted messages

            mail.logout()
            logging.info(f"EmailReadImapDriver: Successfully read {len(emails_data)} emails from {mailbox}.")
            return {"status": "success", "emails": emails_data}

        except Exception as e:
            logging.error(f"EmailReadImapDriver: Error reading emails from IMAP: {e}", exc_info=True)
            return {"status": "failed", "error": str(e)}
