import logging
import json
import sys
import os

# Add the backend directory to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(backend_dir)

from mcp.drivers.base_driver import BaseDriver

class MCP_LLM_Driver(BaseDriver):
    """
    Driver for AI content generation using the custom MCP LLM system.
    This driver interfaces with the MCP_LLM_Orchestrator to process user input
    and generate AI responses.
    """
    
    def __init__(self, db_pool, mcp_orchestrator=None):
        super().__init__(db_pool)
        self.mcp_orchestrator = mcp_orchestrator
        logging.info("Initialized MCP_LLM_Driver")
    
    async def execute(self, parameters: dict, input_data: dict, user_id: str, engine_instance=None) -> dict:
        """
        Execute AI content generation using MCP LLM.
        
        Expected parameters:
        - prompt: The user input/prompt to process
        - context: Optional context for the AI
        - max_tokens: Maximum tokens for response (optional)
        - temperature: AI creativity level (optional, 0.0-1.0)
        """
        logging.info(f"MCP_LLM_Driver: Executing AI generation for user {user_id}")
        
        try:
            # 1. Parameter Validation - handle both 'prompt' and 'user_input' parameters
            user_prompt = parameters.get("prompt") or parameters.get("user_input")
            if not user_prompt:
                return {"status": "failed", "error": "Missing required parameter: 'prompt' or 'user_input'"}
            
            context = parameters.get("context", "")
            max_tokens = parameters.get("max_tokens", 1000)
            temperature = parameters.get("temperature", 0.7)
            
            # 2. Get MCP LLM orchestrator instance
            if not self.mcp_orchestrator:
                if engine_instance and hasattr(engine_instance, 'mcp_orchestrator'):
                    self.mcp_orchestrator = engine_instance.mcp_orchestrator
                else:
                    return {"status": "failed", "error": "MCP LLM Orchestrator not available"}
            
            # 3. Prepare the conversation for MCP LLM with AI service selection
            conversation = []
            
            # Add context if provided
            if context:
                conversation.append({
                    "role": "system",
                    "content": context
                })
            
            # Add user prompt
            conversation.append({
                "role": "user", 
                "content": user_prompt
            })
            
            # Check if AI service is specified in parameters
            ai_service = parameters.get("ai_service") or parameters.get("service_selection", "inhouse")
            
            # Modify the user prompt to include service selection to bypass the selection screen
            modified_prompt = f"service:{ai_service} {user_prompt}"
            
            logging.info(f"MCP_LLM_Driver: Processing prompt with {ai_service} service: {user_prompt[:100]}...")
            
            # 4. Call MCP LLM for AI generation using the modified prompt
            ai_response = await self.mcp_orchestrator.process_user_input(
                user_id=user_id,
                agent_id="automation-agent",  # Use a default agent ID for automation
                user_message=modified_prompt  # Use the modified prompt with service selection
            )
            
            if ai_response.get("status") in ["success", "review_needed", "completed"]:
                # Handle success, review_needed, and completed responses
                generated_content = ai_response.get("message", "")
                
                # If there's a workflow_json, include it in the response
                if "workflow_json" in ai_response and ai_response["workflow_json"]:
                    generated_content += f"\n\nGenerated Workflow:\n{ai_response['workflow_json']}"
                
                logging.info(f"MCP_LLM_Driver: AI generation successful, {len(generated_content)} characters generated")
                
                return {
                    "status": "success",
                    "generated_content": generated_content,
                    "original_prompt": user_prompt,
                    "ai_response": ai_response  # Include full response for debugging
                }
            else:
                error_msg = ai_response.get("error", f"Unknown AI generation error. Response: {ai_response}")
                logging.error(f"MCP_LLM_Driver: AI generation failed: {error_msg}")
                logging.error(f"MCP_LLM_Driver: Full AI response: {ai_response}")
                return {"status": "failed", "error": f"AI generation failed: {error_msg}"}
                
        except Exception as e:
            logging.error(f"MCP_LLM_Driver: Unexpected error: {e}", exc_info=True)
            return {"status": "failed", "error": f"AI processing error: {str(e)}"}
