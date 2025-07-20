import logging
import json
import os
import sys
import sys

# Add the backend directory to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(backend_dir)

from mcp.drivers.base_driver import BaseDriver

class OpenAI_Driver(BaseDriver):
    """
    Driver for AI content generation using OpenAI's GPT models.
    Supports GPT-3.5, GPT-4, and other OpenAI models.
    """
    
    async def execute(self, parameters: dict, input_data: dict, user_id: str, engine_instance=None) -> dict:
        """
        Execute AI content generation using OpenAI.
        
        Expected parameters:
        - prompt: The user input/prompt to process
        - model: OpenAI model to use (optional, defaults to gpt-3.5-turbo)
        - context: Optional system context
        - max_tokens: Maximum tokens for response (optional)
        - temperature: AI creativity level (optional, 0.0-2.0)
        """
        logging.info(f"OpenAI_Driver: Executing AI generation for user {user_id}")
        
        try:
            # 1. Parameter Validation
            if "prompt" not in parameters:
                return {"status": "failed", "error": "Missing required parameter: prompt"}
            
            user_prompt = parameters["prompt"]
            model = parameters.get("model", "gpt-3.5-turbo")
            context = parameters.get("context", "You are a helpful AI assistant.")
            max_tokens = parameters.get("max_tokens", 1000)
            temperature = parameters.get("temperature", 0.7)
            
            # 2. Get OpenAI API key
            openai_api_key = None
            
            try:
                # Try to get from user's service keys first
                if self.db_pool is not None:
                    user_keys = await self._get_user_service_keys(user_id, "openai_config")
                    openai_api_key = user_keys.get("api_key")
                    logging.info("OpenAI_Driver: Retrieved API key from user database")
            except Exception as db_error:
                logging.warning(f"OpenAI_Driver: Database access failed: {db_error}")
            
            # Fallback to environment variable
            if not openai_api_key:
                openai_api_key = os.getenv("OPENAI_API_KEY")
                logging.info("OpenAI_Driver: Using API key from environment variables")
            
            if not openai_api_key:
                return {"status": "failed", "error": "OpenAI API key not configured"}
            
            # 3. Import OpenAI library (install with: pip install openai)
            try:
                import openai
                openai.api_key = openai_api_key
            except ImportError:
                return {"status": "failed", "error": "OpenAI library not installed. Run: pip install openai"}
            
            # 4. Prepare messages for OpenAI
            messages = [
                {"role": "system", "content": context},
                {"role": "user", "content": user_prompt}
            ]
            
            logging.info(f"OpenAI_Driver: Processing with model {model}, prompt: {user_prompt[:100]}...")
            
            # 5. Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=30
            )
            
            # 6. Extract response
            if response.choices and len(response.choices) > 0:
                generated_content = response.choices[0].message.content
                tokens_used = response.usage.total_tokens if response.usage else 0
                
                logging.info(f"OpenAI_Driver: Generation successful, {len(generated_content)} characters, {tokens_used} tokens")
                
                return {
                    "status": "success",
                    "generated_content": generated_content,
                    "original_prompt": user_prompt,
                    "tokens_used": tokens_used,
                    "model_used": model
                }
            else:
                return {"status": "failed", "error": "No response generated from OpenAI"}
                
        except Exception as e:
            logging.error(f"OpenAI_Driver: Error: {e}", exc_info=True)
            return {"status": "failed", "error": f"OpenAI processing error: {str(e)}"}
