import logging
import json
import os
import sys
import sys

# Add the backend directory to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(backend_dir)

from mcp.drivers.base_driver import BaseDriver

class Claude_Driver(BaseDriver):
    """
    Driver for AI content generation using Anthropic's Claude models.
    Supports Claude 3 (Haiku, Sonnet, Opus) and other Anthropic models.
    """
    
    async def execute(self, parameters: dict, input_data: dict, user_id: str, engine_instance=None) -> dict:
        """
        Execute AI content generation using Claude.
        
        Expected parameters:
        - prompt: The user input/prompt to process
        - model: Claude model to use (optional, defaults to claude-3-sonnet-20240229)
        - context: Optional system context
        - max_tokens: Maximum tokens for response (optional)
        - temperature: AI creativity level (optional, 0.0-1.0)
        """
        logging.info(f"Claude_Driver: Executing AI generation for user {user_id}")
        
        try:
            # 1. Parameter Validation
            if "prompt" not in parameters:
                return {"status": "failed", "error": "Missing required parameter: prompt"}
            
            user_prompt = parameters["prompt"]
            model = parameters.get("model", "claude-3-sonnet-20240229")
            context = parameters.get("context", "You are a helpful AI assistant.")
            max_tokens = parameters.get("max_tokens", 1000)
            temperature = parameters.get("temperature", 0.7)
            
            # 2. Get Anthropic API key
            anthropic_api_key = None
            
            try:
                # Try to get from user's service keys first
                if self.db_pool is not None:
                    user_keys = await self._get_user_service_keys(user_id, "anthropic_config")
                    anthropic_api_key = user_keys.get("api_key")
                    logging.info("Claude_Driver: Retrieved API key from user database")
            except Exception as db_error:
                logging.warning(f"Claude_Driver: Database access failed: {db_error}")
            
            # Fallback to environment variable
            if not anthropic_api_key:
                anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
                logging.info("Claude_Driver: Using API key from environment variables")
            
            if not anthropic_api_key:
                return {"status": "failed", "error": "Anthropic API key not configured"}
            
            # 3. Import Anthropic library (install with: pip install anthropic)
            try:
                import anthropic
                client = anthropic.AsyncAnthropic(api_key=anthropic_api_key)
            except ImportError:
                return {"status": "failed", "error": "Anthropic library not installed. Run: pip install anthropic"}
            
            logging.info(f"Claude_Driver: Processing with model {model}, prompt: {user_prompt[:100]}...")
            
            # 4. Call Claude API
            response = await client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=context,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # 5. Extract response
            if response.content and len(response.content) > 0:
                generated_content = response.content[0].text
                tokens_used = response.usage.input_tokens + response.usage.output_tokens if response.usage else 0
                
                logging.info(f"Claude_Driver: Generation successful, {len(generated_content)} characters, {tokens_used} tokens")
                
                return {
                    "status": "success",
                    "generated_content": generated_content,
                    "original_prompt": user_prompt,
                    "tokens_used": tokens_used,
                    "model_used": model
                }
            else:
                return {"status": "failed", "error": "No response generated from Claude"}
                
        except Exception as e:
            logging.error(f"Claude_Driver: Error: {e}", exc_info=True)
            return {"status": "failed", "error": f"Claude processing error: {str(e)}"}
