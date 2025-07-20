# backend/api/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import sys
import os

# Add the backend directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import OpenAI directly here to test
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
    logger.info("✅ OpenAI library loaded successfully")
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("❌ OpenAI library not available - will use fallback responses")

router = APIRouter()

class ChatRequest(BaseModel):
    # Support multiple input formats
    user_input: Optional[str] = None
    message: Optional[str] = None
    
    # Support multiple agent config formats
    agent_config: Optional[Dict[str, Any]] = None
    agentConfig: Optional[Dict[str, Any]] = None
    agentId: Optional[str] = None
    
    session_id: Optional[str] = None
    
    def get_user_input(self) -> str:
        """Get user input from either field"""
        return self.user_input or self.message or ""
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent config from either field, including agentId"""
        config = self.agent_config or self.agentConfig or {}
        if self.agentId and 'agent_id' not in config:
            config['agent_id'] = self.agentId
        return config

class ChatResponse(BaseModel):
    response: str
    workflow_generated: bool = False
    n8n_workflow: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
    needs_confirmation: Optional[bool] = False
    action_required: Optional[str] = None
    ai_enhanced: Optional[bool] = False
    execution_details: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None
    fallback_used: Optional[bool] = False
    preview_data: Optional[Dict[str, Any]] = None

@router.post("/mcpai", response_model=ChatResponse)
async def chat_with_mcpai(request: ChatRequest):
    """
    Enhanced chat endpoint with full MCP LLM integration
    """
    print("=" * 50)
    print("🚀 CHAT REQUEST RECEIVED")
    print(f"Raw request: {request}")
    print("=" * 50)
    
    try:
        agent_config = request.get_agent_config()
        user_input = request.get_user_input()
        session_id = request.session_id or f"session_{agent_config.get('agent_id', 'default')}"
        
        print(f"📝 Parsed - user_input: '{user_input}', agent_config: {agent_config}, session_id: {session_id}")
        
        if not user_input:
            print("❌ ERROR: No user input provided")
            raise HTTPException(status_code=400, detail="User input is required")
        
        # Get agent configuration
        agent_id = agent_config.get("agent_id", "sam_assistant")
        agent_name = agent_config.get("name", "Sam - Personal Assistant")
        
        # Create agent personality based on configuration
        personality = {
            "name": agent_name,
            "role": agent_config.get("role", "General AI Assistant for Automation"),
            "communication_style": "friendly",
            "expertise": ["automation", "workflows", "general assistance", "conversation"],
            "approach": "helpful and knowledgeable"
        }
        
        # LLM configuration with OpenAI
        llm_config = {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        # Process message using Custom MCP LLM iteration system
        try:
            if OPENAI_AVAILABLE:
                # Use the complete Custom MCP LLM iteration system
                print(f"🤖 Calling process_with_custom_mcp_llm for: {user_input[:50]}...")
                result = await process_with_custom_mcp_llm(user_input, agent_config, session_id)
                print(f"🔍 MCP LLM Result Keys: {list(result.keys()) if result else 'None'}")
                print(f"🔍 MCP LLM Success: {result.get('success') if result else 'None'}")
                
                if result.get("success"):
                    print(f"✅ MCP LLM Success - mapping response...")
                    # Map MCP LLM response to frontend expected format
                    has_workflow_json = result.get("hasWorkflowJson", False) or result.get("workflow_generated", False)
                    has_workflow_preview = result.get("hasWorkflowPreview", False)
                    
                    print(f"🔍 hasWorkflowJson: {has_workflow_json}, hasWorkflowPreview: {has_workflow_preview}")
                    print(f"🔍 status from MCP: {result.get('status', 'MISSING')}")
                    
                    # Create enhanced response with all fields frontend expects
                    enhanced_response = ChatResponse(
                        response=result.get("response", "I'm here to help!"),
                        workflow_generated=has_workflow_json,
                        n8n_workflow=result.get("workflowJson") or result.get("workflow_json"),
                        session_id=session_id,
                        agent_id=agent_id,
                        ai_enhanced=True,
                        execution_details=result.get("execution_details"),
                        fallback_used=result.get("fallback_used", False),
                        needs_confirmation=result.get("action_required") is not None,
                        action_required=result.get("action_required")
                    )
                    
                    # Add additional fields that frontend expects directly to response dict
                    response_dict = enhanced_response.dict()
                    response_dict.update({
                        "status": result.get("status", "completed"),
                        "hasWorkflowJson": has_workflow_json,
                        "hasWorkflowPreview": has_workflow_preview,
                        "workflowPreviewContent": result.get("workflowPreviewContent", ""),
                        "done": result.get("done", True),
                        "message": result.get("message", result.get("response", "I'm here to help!")),
                        "workflow_id": result.get("workflow_id"),
                        "automation_type": result.get("automation_type"),
                        "ultra_fast": result.get("ultra_fast", False),
                        "processing_time": result.get("processing_time", ""),
                        "email_sent": result.get("email_sent", False),
                        "execution_status": result.get("execution_status")
                    })
                    
                    print(f"📦 Final response keys: {list(response_dict.keys())}")
                    print(f"📦 Final status: {response_dict.get('status')}")
                    print(f"📦 Final hasWorkflowJson: {response_dict.get('hasWorkflowJson')}")
                    
                    # Return enhanced response using JSONResponse to include custom fields
                    from fastapi.responses import JSONResponse
                    return JSONResponse(content=response_dict)
                else:
                    # Enhanced fallback
                    response = await generate_basic_ai_response(user_input, agent_name, agent_config)
                    
                    return ChatResponse(
                        response=response,
                        workflow_generated=False,
                        session_id=session_id,
                        agent_id=agent_id,
                        fallback_used=True,
                        error_details={"mcp_error": result.get("error")}
                    )
            else:
                # Enhanced fallback with basic AI-like responses
                response = await generate_basic_ai_response(user_input, agent_name, agent_config)
                
                return ChatResponse(
                    response=response,
                    workflow_generated=False,
                    session_id=session_id,
                    agent_id=agent_id,
                    fallback_used=True,
                    error_details={"openai_error": "OpenAI library not available"}
                )
                
        except Exception as ai_error:
            print(f"⚠️ AI processing error: {ai_error}")
            
            # Enhanced fallback with basic AI-like responses
            response = await generate_basic_ai_response(user_input, agent_name, agent_config)
            
            return ChatResponse(
                response=response,
                workflow_generated=False,
                session_id=session_id,
                agent_id=agent_id,
                fallback_used=True,
                error_details={"ai_error": str(ai_error)}
            )
        
    except Exception as e:
        print(f"💥 Chat API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def generate_basic_ai_response(user_input: str, agent_name: str, agent_config: Dict[str, Any]) -> str:
    """Generate basic AI-like responses when MCP LLM is unavailable"""
    
    user_lower = user_input.lower()
    
    # Greeting responses
    if any(word in user_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        return f"Hello! I'm {agent_name}, your AI assistant. How can I help you today?"
    
    # How are you responses
    elif any(phrase in user_lower for phrase in ['how are you', 'how do you do', 'what\'s up']):
        return f"I'm doing great, thank you for asking! I'm {agent_name}, ready to assist you with automation, workflows, or general questions. What would you like to explore today?"
    
    # Name/identity questions
    elif any(word in user_lower for word in ['name', 'who are you', 'what are you']):
        return f"I'm {agent_name}, your {agent_config.get('role', 'AI assistant')}. I can help you with automation workflows, answer questions, and provide assistance with various tasks."
    
    # Capability questions
    elif any(phrase in user_lower for phrase in ['what can you do', 'help me', 'capabilities']):
        return f"I'm {agent_name}, and I can help you with:\n\n• Creating automation workflows\n• Sending emails and notifications\n• Processing data and information\n• General conversation and assistance\n• Connecting different services and tools\n\nWhat would you like to work on?"
    
    # Weather (common AI question)
    elif 'weather' in user_lower:
        return "I don't have access to real-time weather data, but I can help you create automation workflows to get weather information from APIs or send weather-based notifications!"
    
    # Time questions
    elif 'time' in user_lower and any(word in user_lower for word in ['what', 'current', 'now']):
        return "I don't have access to real-time data, but I can help you create workflows that work with time-based triggers and scheduling!"
    
    # Automation related
    elif any(word in user_lower for word in ['automate', 'workflow', 'automation', 'create', 'build']):
        return f"Great! I love helping with automation. I can help you create workflows for email sending, data processing, webhooks, API calls, and much more. What kind of automation are you thinking about?"
    
    # Thank you responses
    elif any(word in user_lower for word in ['thank', 'thanks']):
        return "You're very welcome! I'm here whenever you need assistance with automation or have any questions."
    
    # Default response
    else:
        return f"I'm {agent_name}, your AI assistant for automation and general help. I understand you said: '{user_input}'. While I'm processing that, I can help you with creating workflows, automation, or answer questions. What specific assistance do you need?"

@router.post("/ai-content-confirm", response_model=ChatResponse)
async def confirm_ai_content(request: ChatRequest):
    """Handle AI content generation confirmation - feature removed"""
    return ChatResponse(
        response="AI content generation features have been removed from this system.",
        workflow_generated=False,
        fallback_used=True
    )


async def process_with_openai_direct(user_input: str, agent_name: str, personality: Dict[str, Any]) -> Dict[str, Any]:
    """Direct OpenAI integration for conversational responses"""
    
    try:
        if not OPENAI_AVAILABLE:
            return {"response": f"Hi! I'm {agent_name}, but I'm currently running in basic mode. How can I help you?"}
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {"response": f"Hi! I'm {agent_name}. My AI capabilities are currently limited, but I'm here to help!"}
        
        client = AsyncOpenAI(api_key=api_key)
        
        # Build conversation context
        role = personality.get("role", "AI assistant")
        style = personality.get("communication_style", "friendly")
        expertise = personality.get("expertise", [])
        
        system_prompt = f"""You are {agent_name}, a {role}.

Communication Style: {style}
Expertise Areas: {', '.join(expertise) if expertise else 'General assistance'}

You are an intelligent AI assistant that can:
1. Have natural conversations
2. Help with automation and workflows
3. Provide information and assistance
4. Create automation workflows when requested

Be helpful, knowledgeable, and maintain your {style} personality.
When users ask about automation, workflows, or want to create something automated, 
you should offer to help create workflows for them."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        # Call OpenAI API
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        ai_response = response.choices[0].message.content.strip()
        return {"response": ai_response}
        
    except Exception as e:
        logger.error(f"OpenAI direct processing error: {e}")
        return {"response": f"Hi! I'm {agent_name}. I'm experiencing some technical difficulties, but I'm still here to help you as best I can!"}


async def process_with_custom_mcp_llm(user_input: str, agent_config: Dict[str, Any], session_id: str) -> Dict[str, Any]:
    """
    Complete workflow: Custom MCP LLM → Workflow Creation → Automation Engine → Verification
    """
    
    try:
        from mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine
        
        # Initialize the iteration engine with agent_id
        agent_id = agent_config.get("agent_id", "default")
        iteration_engine = CustomMCPLLMIterationEngine(
            agent_id=agent_id,
            session_id=session_id
        )
        
        # Process with iterative workflow creation
        result = await iteration_engine.process_user_request(user_input)
        
        return result
        
    except Exception as e:
        logger.error(f"Custom MCP LLM processing error: {e}")
        # Fallback to direct OpenAI
        return await process_with_openai_direct(
            user_input, 
            agent_config.get("name", "Assistant"), 
            agent_config
        )
