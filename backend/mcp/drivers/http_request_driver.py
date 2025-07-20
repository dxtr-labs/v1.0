import requests
import logging
import json
import sys
import os

# Add the backend directory to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(backend_dir)

from mcp.drivers.base_driver import BaseDriver

class HttpRequestDriver(BaseDriver):
    async def execute(self, parameters: dict, input_data: dict, user_id: str, engine_instance=None) -> dict:
        logging.info(f"HttpRequestDriver: Executing for user {user_id}")

        # 1. Parameter Validation
        required_params = ["url", "method"]
        for p in required_params:
            if p not in parameters:
                logging.error(f"HttpRequestDriver: Missing required parameter: {p}")
                return {"status": "failed", "error": f"Missing required parameter: {p}"}

        url = parameters["url"]
        method = parameters["method"].upper()
        body = parameters.get("body")
        headers = {h["name"]: h["value"] for h in parameters.get("headers", [])}

        # 2. Construct Request
        request_kwargs = {
            "method": method,
            "url": url,
            "headers": headers
        }

        if body:
            body_type = body.get("type")
            body_data = body.get("data")
            if body_type == "json":
                request_kwargs["json"] = body_data
                if "Content-Type" not in headers:
                    request_kwargs["headers"]["Content-Type"] = "application/json"
            elif body_type == "form":
                request_kwargs["data"] = body_data
                if "Content-Type" not in headers:
                    request_kwargs["headers"]["Content-Type"] = "application/x-www-form-urlencoded"
            # Add other body types (e.g., 'raw', 'binary') as needed

        # 3. Execute Request
        try:
            response = requests.request(**request_kwargs)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            response_content = None
            try:
                response_content = response.json()
            except json.JSONDecodeError:
                response_content = response.text # Fallback to text if not JSON

            logging.info(f"HttpRequestDriver: Request to {url} ({method}) succeeded. Status: {response.status_code}")
            return {
                "status": "success",
                "statusCode": response.status_code,
                "headers": dict(response.headers),
                "body": response_content
            }
        except requests.exceptions.RequestException as e:
            logging.error(f"HttpRequestDriver: Request to {url} ({method}) failed: {e}", exc_info=True)
            return {"status": "failed", "error": str(e)}
        except Exception as e:
            logging.error(f"HttpRequestDriver: An unexpected error occurred: {e}", exc_info=True)
            return {"status": "failed", "error": str(e)}

