# You'll need to install the Twilio Python library: pip install twilio
from twilio.rest import Client
import logging
import os
import sys
import sys

# Add the backend directory to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(backend_dir)

from mcp.drivers.base_driver import BaseDriver

class TwilioDriver(BaseDriver):
    async def execute(self, parameters: dict, input_data: dict, user_id: str, engine_instance=None) -> dict:
        logging.info(f"TwilioDriver: Executing for user {user_id}")

        # 1. Parameter Validation
        required_params = ["to", "message"]
        for p in required_params:
            if p not in parameters:
                logging.error(f"TwilioDriver: Missing required parameter: {p}")
                return {"status": "failed", "error": f"Missing required parameter: {p}"}

        # 2. Retrieve Credentials
        try:
            twilio_credentials = await self._get_user_service_keys(user_id, "twilio_config")
            account_sid = twilio_credentials.get("account_sid", os.getenv("TWILIO_ACCOUNT_SID"))
            auth_token = twilio_credentials.get("auth_token", os.getenv("TWILIO_AUTH_TOKEN"))
            from_number = parameters.get("from", twilio_credentials.get("from_number", os.getenv("TWILIO_FROM_NUMBER"))) # Default from .env or user config

            if not all([account_sid, auth_token, from_number]):
                raise ValueError("Twilio credentials (SID, Token, From Number) are not fully configured.")
        except Exception as e:
            logging.error(f"TwilioDriver: Failed to retrieve Twilio credentials: {e}")
            return {"status": "failed", "error": f"Failed to retrieve Twilio credentials: {e}"}

        client = Client(account_sid, auth_token)

        to_number = parameters["to"]
        message_body = parameters["message"]
        to_whatsapp = parameters.get("toWhatsapp", False)

        try:
            if to_whatsapp:
                # Twilio requires 'whatsapp:' prefix for WhatsApp messages
                message = client.messages.create(
                    from_=f"whatsapp:{from_number}",
                    body=message_body,
                    to=f"whatsapp:{to_number}"
                )
            else:
                message = client.messages.create(
                    from_=from_number,
                    body=message_body,
                    to=to_number
                )
            logging.info(f"TwilioDriver: Message sent successfully to {to_number}. SID: {message.sid}")
            return {"status": "success", "message_sid": message.sid, "message_status": message.status}
        except Exception as e:
            logging.error(f"TwilioDriver: Error sending message to {to_number}: {e}", exc_info=True)
            return {"status": "failed", "error": str(e)}
