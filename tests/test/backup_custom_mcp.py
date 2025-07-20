"""
Custom MCP LLM Iteration Engine
Handles workflow creation and refinement through multiple iterations with OpenAI
Integrated with Automation Script Builder for 100% working JSON scripts
"""

import os
import re
import gc
import sys
import json
import uuid
import time
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables from .env.local
env_path = Path(__file__).parent.parent.parent / '.env.local'
load_dotenv(dotenv_path=env_path)

# Set up logging
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.append(str(SCRIPT_DIR.parent))

# Get email credentials from environment
COMPANY_EMAIL = os.getenv('COMPANY_EMAIL')
COMPANY_EMAIL_PASSWORD = os.getenv('COMPANY_EMAIL_PASSWORD')

if not COMPANY_EMAIL or not COMPANY_EMAIL_PASSWORD:
    logger.warning("Email credentials not found in .env.local - email features will be limited")

# Simple automation templates
from simple_email_service import email_service

# Import HTTP driver
sys.path.append(str(SCRIPT_DIR.parent / 'drivers'))
try:
    from http_request_driver import http_driver
except ImportError:
    logger.warning("HTTP driver not available - some features will be limited")
    http_driver = None

from db.postgresql_manager import db_manager

# Essential OpenAI support for intent detection
HAS_OPENAI = False
try:
    import openai
    from openai import AsyncOpenAI
    HAS_OPENAI = True
    logger.info("✅ OpenAI package loaded successfully - full AI capabilities available")
except ImportError:
    logger.error("❌ OpenAI package not available - automation intent detection will be limited")
    logger.error("Run: pip install openai")

class CustomMCPLLMIterationEngine:
    """
    Enhanced Custom MCP LLM Engine that:
    1. Uses Smart Automation Engine to create 100% working workflows
    2. Understands driver capabilities and requirements
    3. Asks for missing information interactively
    4. Generates validated JSON automation scripts
    5. Integrates with automation engine for execution
    """
    
    def __init__(self, agent_id: str, session_id: str = None, db_manager=None, openai_api_key: str = None, automation_engine=None, agent_context: Dict = None):
        self.agent_id = agent_id
        self.session_id = session_id or f"session_{agent_id}"
        self.max_iterations = 3
        self.current_iteration = 0
        self.db_manager = db_manager
        self.automation_engine = automation_engine  # Store automation engine reference
        
        # Store agent context for enhanced content generation
        self.agent_context = agent_context or {}
        self.agent_data = self.agent_context.get('agent_data', {})
        self.agent_memory = self.agent_context.get('memory', {})
        self.user_id = self.agent_context.get('user_id')
        
        # Extract agent expectations for content generation protocols
        self.agent_expectations = self.agent_data.get('agent_expectations', '')
        self.agent_personality = self.agent_data.get('agent_personality', {})
        
        logger.error(f"🤖 MCP Engine initialized with agent context: {self.agent_data.get('agent_name', 'Unknown')} | Expectations: {bool(self.agent_expectations)}")
        
        # Get OpenAI API key
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            self.logger = logging.getLogger(__name__)
            self.logger.warning("OpenAI API key not found - some features may be limited")
        
        # Initialize simple automation templates
        self.automation_templates = {
            "simple_email": {
                "name": "Send Email",
                "params": ["toEmail", "subject", "text"],
                "template": {
                    "id": "{workflow_id}",
                    "name": "Email Automation", 
                    "steps": [{
                        "id": "email_1",
                        "driver": "email_send",
                        "params": {
                            "to": "{toEmail}",
                            "toEmail": "{toEmail}",
                            "subject": "{subject}", 
                            "text": "{text}",
                            "message": "{text}",
                            "template_style": "professional"
                        }
                    }]
                }
            },
            "apology_email": {
                "name": "AI Apology Email",
                "params": ["customer_email", "customer_name", "event_name"],
                "template": {
                    "id": "{workflow_id}",
                    "name": "Apology Email",
                    "steps": [{
                        "id": "ai_1", 
                        "driver": "openai",
                        "params": {
                            "prompt": "Write a professional apology for {customer_name} for missing {event_name}",
                            "context": "Professional apology email writer"
                        }
                    }, {
                        "id": "email_1",
                        "driver": "email_send", 
                        "params": {
                            "to": "{customer_email}",
                            "toEmail": "{customer_email}",
                            "subject": "Apologies - {event_name}",
                            "text": "{{ai_1.output}}",
                            "message": "{{ai_1.output}}"
                        }
                    }]
                }
            },
            "fetch_summarize_email": {
                "name": "Fetch Data & Email Summary",
                "params": ["website_url", "recipient_email", "summary_topic"],
                "template": {
                    "id": "{workflow_id}",
                    "name": "Website Data Summary Email",
                    "steps": [{
                        "id": "fetch_1",
                        "driver": "http_request",
                        "params": {
                            "url": "{website_url}",
                            "method": "GET"
                        }
                    }, {
                        "id": "ai_summarize_1",
                        "driver": "openai",
                        "params": {
                            "prompt": "Analyze and summarize this website data focusing on {summary_topic}. Data: {{fetch_1.output}}. Create a clear, professional summary.",
                            "context": "You are a data analyst creating professional summaries of web content",
                            "temperature": 0.3
                        }
                    }, {
                        "id": "email_1",
                        "driver": "email_send",
                        "params": {
                            "to": "{recipient_email}",
                            "toEmail": "{recipient_email}",
                            "subject": "Website Summary Report - {summary_topic}",
                            "text": "Here's your requested website summary:\\n\\n{{ai_summarize_1.output}}",
                            "message": "Here's your requested website summary:\\n\\n{{ai_summarize_1.output}}",
                            "template_style": "professional"
                        }
                    }]
                }
            }
        }
        
        # Track conversation state for parameter collection
        self.pending_template = None
        self.pending_params = None
        self.pending_missing_params = None
        
        # NEW: Track workflow parameter collection state
        self.pending_workflow_params = None
        self.pending_partial_workflow = None
        self.workflow_collection_active = False
        
        # Ultra-aggressive performance optimization to eliminate ALL lag
        self.conversation_history = []
        self.max_history = 2  # Drastically reduced from 5 to 2 for maximum speed
        self._cache = {}  # Add caching for repeated operations
        self._last_cleanup = datetime.now()
        self._response_cache = {}  # Cache responses to avoid repeated processing
        self._processing_lock = False  # Prevent concurrent processing that causes lag
        
    async def _fetch_agent_details(self) -> Optional[Dict[str, Any]]:
        """
        Fetch agent details from the database
        """
        try:
            if not self.db_manager:
                logger.error("No database manager available")
                return None
                
            agent_query = "SELECT * FROM agents WHERE agent_id = $1"
            agent_result = await self.db_manager.fetch_one(agent_query, self.agent_id)
            
            if not agent_result:
                logger.error(f"No agent found with ID: {self.agent_id}")
                return None
                
            return {
                "name": agent_result.get("name", "AI Assistant"),
                "role": agent_result.get("role", "General Assistant"),
                "personality": json.loads(agent_result.get("personality", "{}")),
                "preferences": json.loads(agent_result.get("preferences", "{}")),
                "agent_id": agent_result.get("agent_id"),
                "created_at": agent_result.get("created_at")
            }
            
        except Exception as e:
            logger.error(f"❌ Error fetching agent details: {e}")
            return None

    async def _fetch_agent_workflow(self) -> Optional[Dict[str, Any]]:
        """
        Fetch agent's current workflow from the database
        Returns:
            Optional[Dict[str, Any]]: Workflow data or None if not found/error
            The workflow will have the structure:
            {
                "workflow_id": str,
                "agent_id": str,
                "script": {
                    "id": str,
                    "name": str,
                    "description": str,
                    "nodes": List[Dict],
                    "edges": List[Dict]
                },
                "created_at": datetime,
                "updated_at": datetime
            }
        """
        try:
            if not self.db_manager:
                logger.error("❌ No database manager available for workflow fetch")
                return self._create_empty_workflow()
                
            workflow_query = """
                SELECT workflow_id, agent_id, script, created_at, updated_at 
                FROM workflows 
                WHERE agent_id = $1 
                ORDER BY created_at DESC 
                LIMIT 1
            """
            
            try:
                workflow_result = await self.db_manager.fetch_one(workflow_query, self.agent_id)
                logger.info(f"🔍 Fetched workflow for agent {self.agent_id}")
            except Exception as db_error:
                logger.error(f"❌ Database error fetching workflow: {db_error}")
                return self._create_empty_workflow()
            
            if not workflow_result:
                logger.info(f"ℹ️ No existing workflow found for agent {self.agent_id}, creating new")
                return self._create_empty_workflow()
            
            try:
                script_data = json.loads(workflow_result.get("script", "{}"))
                if not isinstance(script_data, dict):
                    logger.error("❌ Invalid script data format")
                    return self._create_empty_workflow()
                    
                # Validate required fields
                required_fields = ["id", "name", "nodes", "edges"]
                if not all(field in script_data for field in required_fields):
                    logger.error("❌ Missing required fields in workflow script")
                    return self._create_empty_workflow()
                    
                workflow = {
                    "workflow_id": workflow_result.get("workflow_id"),
                    "agent_id": workflow_result.get("agent_id"),
                    "script": script_data,
                    "created_at": workflow_result.get("created_at"),
                    "updated_at": workflow_result.get("updated_at")
                }
                
                logger.info(f"✅ Successfully loaded workflow with {len(script_data.get('nodes', []))} nodes")
                return workflow
                
            except json.JSONDecodeError as json_error:
                logger.error(f"❌ Invalid JSON in workflow script: {json_error}")
                return self._create_empty_workflow()
            
        except Exception as e:
            logger.error(f"❌ Error fetching agent workflow: {e}")
            return self._create_empty_workflow()
            
    def _create_empty_workflow(self) -> Dict[str, Any]:
        """Create a new empty workflow with proper structure"""
        workflow_id = str(uuid.uuid4())
        return {
            "workflow_id": workflow_id,
            "agent_id": self.agent_id,
            "script": {
                "id": workflow_id,
                "name": "New Workflow",
                "description": "Generated workflow",
                "nodes": [],
                "edges": [],
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "status": "new"
            }
        }
    
    def add_to_memory(self, user_input: str, assistant_response: str):
        """Ultra-lightweight memory with maximum performance"""
        # Ensure conversation history is initialized as a list
        if not isinstance(self.conversation_history, list):
            self.conversation_history = []
            
        # Skip memory entirely if response is too similar (prevent duplicates)
        if len(self.conversation_history) > 0:
            last = self.conversation_history[-1]
            if isinstance(last, dict):
                last_response = last.get("assistant", "")
                if isinstance(assistant_response, str) and assistant_response[:30] == last_response[:30]:
                    return  # Skip completely
        
        # Ultra-aggressive cleanup every 60 seconds
        if (datetime.now() - self._last_cleanup).total_seconds() > 60:
            self._ultra_cleanup()
        
        # Store only essential data with extreme truncation
        self.conversation_history.append({
            "user": str(user_input)[:50],      # Heavily reduced from 200
            "assistant": str(assistant_response)[:100]  # Heavily reduced from 300
        })
        
        # Keep only last 2 exchanges (ultra-minimal)
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def _ultra_cleanup(self):
        """Ultra-aggressive cleanup to eliminate any possible lag"""
        # Clear everything aggressively
        self._cache.clear()
        self._response_cache.clear()
        
        # Clear conversation history if it gets too large
        if len(self.conversation_history) > 1:
            self.conversation_history = self.conversation_history[-1:]
        
        # Force immediate garbage collection
        import gc
        gc.collect()
        
        self._last_cleanup = datetime.now()
        logger.info("🧹 ULTRA cleanup completed - maximum performance mode")
    
    def get_conversation_context(self) -> str:
        """Ultra-minimal context to prevent any lag"""
        if not self.conversation_history:
            return ""
        
        # Return only the most recent exchange, heavily truncated
        if self.conversation_history:
            last = self.conversation_history[-1]
            return f"Last: {last['user'][:20]}...{last['assistant'][:30]}..."
        
        return ""
    
    def check_conversation_continuity(self, user_input: str) -> Optional[str]:
        """Check if user is referring to previous conversation"""
        continuation_patterns = [
            r'\b(that|this|it|the previous|last|earlier)\b',
            r'\b(continue|keep going|proceed|next)\b', 
            r'\b(same|similar|like before)\b',
            r'\b(what about|how about)\b'
        ]
        
        for pattern in continuation_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return self.get_conversation_context()
        
        return None
    
    def _validate_email_credentials(self) -> bool:
        """
        Validate that email credentials are properly configured
        """
        if not COMPANY_EMAIL or not COMPANY_EMAIL_PASSWORD:
            logger.error("Email credentials not found in .env.local")
            return False
            
        # Basic validation of email format
        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        if not re.match(email_pattern, COMPANY_EMAIL):
            logger.error(f"Invalid email format: {COMPANY_EMAIL}")
            return False
            
        return True

    async def process_user_request(self, user_input: str, request_data: dict = None) -> Dict[str, Any]:
        """
        🚀 ENHANCED PROCESSING: OpenAI-powered intent detection with smart automation routing
        This is the core method that determines whether a request is automation or conversational
        """
        logger.error(f"🎯 CRITICAL DEBUG: Processing user request: {user_input[:100]}...")
        logger.error(f"🎯 CRITICAL DEBUG: HAS_OPENAI = {HAS_OPENAI}")
        logger.error(f"🎯 CRITICAL DEBUG: self.openai_api_key = {bool(self.openai_api_key)} (length: {len(self.openai_api_key) if self.openai_api_key else 0})")
        
        # Handle special actions for approved emails
        if user_input.startswith("SEND_APPROVED_EMAIL:"):
            parts = user_input.split(":", 3)
            if len(parts) >= 4:
                workflow_id = parts[1]
                recipient = parts[2] 
                subject = parts[3]
                
                # Get email content from request data if available
                email_content = request_data.get("email_content", "") if request_data else ""
                
                logger.error(f"🎯 PROCESSING APPROVED EMAIL SEND: {workflow_id} -> {recipient}")
                return await self.send_approved_email(workflow_id, user_input, recipient, email_content, subject)
        
        # Validate email credentials if this is an email-related request
        if "email" in user_input.lower():
            if not self._validate_email_credentials():
                return {
                    "success": False,
                    "response": "⚠️ Email credentials not properly configured in .env.local. Please check your configuration.",
                    "status": "error",
                    "error": "invalid_credentials"
                }
                
        # Immediate processing lock check to prevent concurrent requests
        if self._processing_lock:
            return {
                "success": True,
                "response": "Processing your previous request. Please wait a moment.",
                "processing_time": "< 1ms (locked)"
            }
        
        self._processing_lock = True
        start_time = datetime.now()
        
        try:
            # Ultra-fast input validation with immediate return
            user_input = user_input.strip()
            if len(user_input) < 2:
                return self._instant_response("Please provide more details about what you'd like to automate.")
            
            # 🧠 STEP 1: CONTEXT EXTRACTION - Extract ALL useful information for memory
            logger.error(f"🧠 STEP 1: EXTRACTING CONTEXT from: {user_input[:50]}...")
            context_extraction = await self._extract_context_information(user_input)
            if context_extraction:
                await self._store_context_in_memory(context_extraction, user_input)
                logger.error(f"� CONTEXT STORED: {list(context_extraction.keys())}")
            
            # �🔄 EMAIL EDITING DETECTION - Check if user is modifying an existing email workflow  
            logger.error(f"🔄 CHECKING FOR EMAIL EDITING: {user_input[:50]}...")
            email_edit_result = await self._detect_email_editing_intent(user_input)
            if email_edit_result:
                logger.error(f"📝 EMAIL EDITING DETECTED - updating existing workflow")
                return email_edit_result
            
            # 🤖 STEP 2: AUTOMATION DETECTION - Determine if there's an automation task
            logger.error(f"🤖 STEP 2: AUTOMATION DETECTION for: {user_input[:50]}...")
            logger.error(f"🤖 AUTOMATION CHECK: HAS_OPENAI = {HAS_OPENAI}, api_key = {bool(self.openai_api_key)}")
            
            if HAS_OPENAI and self.openai_api_key:
                logger.error(f"🤖 Using OpenAI for automation detection...")
                automation_result = await self._detect_automation_intent(user_input, context_extraction)
                logger.error(f"🤖 Automation detection result: {automation_result}")
                
                if automation_result and automation_result.get("has_automation_task"):
                    logger.error(f"🎯 AUTOMATION TASK DETECTED: {automation_result.get('automation_type')}")
                    # Execute automation with enriched context
                    result = await self._execute_automation_with_context(user_input, automation_result, context_extraction)
                    if result:
                        return result
                else:
                    logger.error(f"💬 NO AUTOMATION TASK - providing helpful conversational response")
                    # Provide conversational response but context is already stored
                    return await self._create_contextual_conversational_response(user_input, context_extraction)
            else:
                logger.error(f"⚠️ OpenAI NOT AVAILABLE - HAS_OPENAI={HAS_OPENAI}, api_key={bool(self.openai_api_key)}")
            
            # Fallback: Enhanced pattern-based detection for automation
            logger.warning("⚠️ OpenAI not available - using enhanced pattern detection")
            enhanced_intent = await self._enhanced_pattern_detection(user_input)
            
            if enhanced_intent.get("is_automation"):
                logger.error(f"🔧 Pattern detection found automation: {enhanced_intent.get('automation_type')}")
                result = await self._execute_smart_automation(user_input, enhanced_intent)
                if result:
                    return result
            
            # If nothing else worked, provide helpful fallback instantly
            logger.error("🚨 CRITICAL: All intent detection failed - using conversational fallback")
            return await self._create_helpful_conversational_response(user_input)
            
        except Exception as e:
            logger.error(f"❌ Enhanced processing error: {e}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            
            # CRITICAL FIX: Instead of generic fallback, try OpenAI conversational response even during errors
            logger.error("🔄 EXCEPTION RECOVERY: Attempting OpenAI conversational response as fallback...")
            try:
                if HAS_OPENAI and self.openai_api_key:
                    recovery_response = await self._generate_ai_conversational_response(
                        user_input, 
                        self.agent_data.get('agent_name', 'AI Assistant'),
                        self.agent_data.get('agent_role', 'Personal Assistant'),
                        [],
                        {}
                    )
                    if recovery_response:
                        logger.error(f"✅ RECOVERY SUCCESS: OpenAI provided response during exception: {recovery_response[:100]}...")
                        return {
                            "success": True,
                            "status": "conversational",
                            "message": recovery_response,
                            "response": recovery_response,
                            "agent_context": {
                                "response_type": "exception_recovery",
                                "recovered_from_error": True
                            },
                            "hasWorkflowJson": False,
                            "hasWorkflowPreview": False,
                            "done": True
                        }
            except Exception as recovery_error:
                logger.error(f"❌ RECOVERY FAILED: {recovery_error}")
            
            # Only use generic fallback as absolute last resort
            logger.error("⚠️ LAST RESORT: Using generic fallback - OpenAI recovery failed")
            return self._instant_response("I'm having some technical difficulties. Could you please rephrase your message so I can better assist you?")
        
        finally:
            self._processing_lock = False
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"⚡ Enhanced processing: {processing_time:.3f}s")
    
    async def _openai_intent_detection(self, user_input: str) -> Dict[str, Any]:
        """
        🤖 OpenAI-powered intent detection - the core intelligence for routing requests
        """
        try:
            if not HAS_OPENAI or not self.openai_api_key:
                return {"is_automation": False, "reason": "no_openai"}
            
            client = AsyncOpenAI(api_key=self.openai_api_key)
            
            # Enhanced system prompt for intent detection
            system_prompt = """You are an expert automation intent classifier. Analyze user messages and determine if they want to create an automation or just have a conversation.

AUTOMATION INDICATORS:
- Email automation: "send email", "draft email", "email someone", "compose email"
- Content creation: "write", "draft", "create", "generate", "compose" + sending
- Data fetching: "fetch", "get data", "scrape", "retrieve from website"
- Workflow creation: "automate", "create workflow", "build automation"
- Scheduling: "schedule", "recurring", "daily", "weekly"

CONVERSATIONAL INDICATORS:
- Questions: "how are you", "what can you do", "help me understand"
- Greetings: "hi", "hello", "hey", "good morning"
- General chat: casual conversation without action requests

OUTPUT FORMAT (JSON only):
{
  "is_automation": true/false,
  "automation_type": "email_automation|content_creation|data_fetching|workflow|scheduling|none",
  "confidence": 0.0-1.0,
  "detected_email": "email@example.com or null",
  "content_type": "sales_pitch|report|proposal|email|none",
  "action_verbs": ["send", "create", "write"],
  "reasoning": "brief explanation of classification"
}"""

            user_prompt = f"Classify this user message:\n\n'{user_input}'"
            
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            logger.error(f"🤖 OpenAI Intent Response: {content}")
            
            # Parse JSON response
            try:
                import json
                result = json.loads(content)
                logger.error(f"✅ Intent Detection Result: automation={result.get('is_automation')}, type={result.get('automation_type')}")
                return result
            except json.JSONDecodeError:
                logger.error(f"❌ Failed to parse OpenAI JSON response: {content}")
                return {"is_automation": False, "reason": "parse_error"}
                
        except Exception as e:
            logger.error(f"❌ OpenAI intent detection error: {e}")
            return {"is_automation": False, "reason": "openai_error"}
    
    async def _execute_smart_automation(self, user_input: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        🚀 Execute automation based on detected intent - the core automation router
        """
        try:
            automation_type = intent.get("automation_type")
            logger.error(f"🎯 Executing smart automation: {automation_type}")
            
            if automation_type in ["email_automation", "content_creation"]:
                return await self._create_contextual_automation(user_input, intent)
            elif automation_type == "data_fetching":
                return await self._create_data_automation(user_input, intent)
            elif automation_type in ["workflow", "scheduling"]:
                return await self._create_advanced_workflow(user_input, intent)
            else:
                # Fallback to contextual automation
                return await self._create_contextual_automation(user_input, intent)
                
        except Exception as e:
            logger.error(f"❌ Smart automation execution error: {e}")
            return None
    
    async def _create_helpful_conversational_response(self, user_input: str) -> Dict[str, Any]:
        """
        Create enhanced conversational responses using agent context, memory, and AI
        """
        logger.error(f"🎯 CONVERSATIONAL RESPONSE DEBUG: Starting for '{user_input[:50]}...'")
        
        user_lower = user_input.lower()
        
        # Get agent context for personalized responses
        agent_name = self.agent_data.get('agent_name', 'AI Assistant')
        agent_role = self.agent_data.get('agent_role', 'Personal Assistant')
        
        logger.error(f"🎯 CONVERSATIONAL DEBUG: Agent = {agent_name}, Role = {agent_role}")
        
        # Check conversation history for context
        previous_interactions = self.agent_memory.get('conversation_history', [])
        user_context = self.agent_memory.get('context', {})
        user_preferences = user_context.get('user_preferences', {})
        
        logger.error(f"🎯 CONVERSATIONAL DEBUG: OpenAI available = {HAS_OPENAI}, API key = {bool(self.openai_api_key)}")
        
        # Try to generate AI-powered conversational response first
        logger.error(f"🎯 CONVERSATIONAL DEBUG: Attempting OpenAI response generation...")
        ai_response = await self._generate_ai_conversational_response(user_input, agent_name, agent_role, previous_interactions, user_preferences)
        logger.error(f"🎯 CONVERSATIONAL DEBUG: AI response = {bool(ai_response)}, content = {ai_response[:100] if ai_response else 'None'}")
        
        if ai_response:
            logger.error(f"✅ USING OPENAI CONVERSATIONAL RESPONSE: {ai_response[:100]}...")
            # Store user input patterns for learning
            await self._update_user_preferences(user_input, 'conversational')
            
            return {
                "success": True,
                "status": "conversational",
                "message": ai_response,
                "response": ai_response,
                "agent_context": {
                    "response_type": "ai_powered",
                    "agent_name": agent_name,
                    "personalized": True
                },
                "hasWorkflowJson": False,
                "hasWorkflowPreview": False,
                "done": True
            }
        
        # If OpenAI fails, try enhanced pattern-based response before minimal fallback
        logger.error(f"⚠️ OpenAI conversational response failed - trying enhanced fallback")
        
        # Enhanced fallback that still tries to be helpful and engaging
        enhanced_fallback = await self._create_enhanced_fallback_response(user_input, agent_name, agent_role, previous_interactions)
        
        if enhanced_fallback:
            await self._update_user_preferences(user_input, 'conversational')
            return {
                "success": True,
                "status": "conversational",
                "message": enhanced_fallback,
                "response": enhanced_fallback,
                "agent_context": {
                    "response_type": "enhanced_fallback",
                    "agent_name": agent_name,
                    "personalized": True
                },
                "hasWorkflowJson": False,
                "hasWorkflowPreview": False,
                "done": True
            }
        
        # Absolute minimal fallback - only if everything else fails
        logger.error(f"🚨 Using minimal fallback - all enhanced responses failed")
        
        simple_response = f"Hello! I'm {agent_name}, your {agent_role} from DXTR Labs. How can I help you with automation today?"
        
        await self._update_user_preferences(user_input, 'conversational')
        
        return {
            "success": True,
            "status": "conversational",
            "message": simple_response,
            "response": simple_response,
            "agent_context": {
                "response_type": "minimal_fallback",
                "agent_name": agent_name,
                "personalized": False,
                "needs_retry": True
            },
            "hasWorkflowJson": False,
            "hasWorkflowPreview": False,
            "done": True
        }
        response = ""
        
        # Personalized greetings with memory
        if any(greeting in user_lower for greeting in ["hi", "hello", "hey", "good morning", "good afternoon", "how are you"]):
            if previous_interactions:
                recent_automation_types = [interaction.get('automation_type') for interaction in previous_interactions[-3:] if interaction.get('automation_type')]
                last_interaction = previous_interactions[-1] if previous_interactions else None
                
                if 'email_preview' in recent_automation_types:
                    response = f"Hello again! I see we've been working on email automation recently. Ready to create more emails or try a different automation? I'm {agent_name}, your {agent_role}, and I'm here to make your work easier!"
                elif last_interaction and last_interaction.get('user_input'):
                    last_topic = last_interaction.get('user_input', '')[:30]
                    response = f"Welcome back! I remember we were discussing {last_topic}... I'm {agent_name}, your {agent_role}. Ready to continue or start something new?"
                else:
                    response = f"Welcome back! I'm {agent_name}, your {agent_role}. Based on our previous conversations, I'm here to help with your automation needs. What would you like to work on today?"
            else:
                response = f"Hi there! I'm {agent_name}, your {agent_role}. I specialize in creating smart automations that save you time and boost productivity! What would you like to automate today?"
        
        elif any(word in user_lower for word in ["help", "what can you do", "capabilities", "features"]):
            capabilities = [
                "Email Automation: Send emails, draft content, create sales pitches, automated responses",
                "Data Fetching: Extract information from websites, APIs, and databases",
                "Workflow Creation: Build custom automation workflows with multiple steps", 
                "Scheduling: Set up recurring tasks and time-based automations",
                "AI Content Generation: Create personalized content for any purpose",
                "Smart Conversations: Context-aware responses that remember your preferences"
            ]
            
            examples = [
                "Send email to john@example.com with a sales pitch for our new product",
                "Draft a professional follow-up email for my client meeting", 
                "Create a welcome email sequence for new customers",
                "Build a workflow to fetch data from our website daily"
            ]
            
            if previous_interactions:
                recent_requests = [interaction.get('user_input', '') for interaction in previous_interactions[-2:] if interaction.get('user_input')]
                if recent_requests:
                    examples.insert(0, f"Smart Suggestion: Based on your recent activity, you might like: Create a follow-up email for our conversation about {recent_requests[-1][:30]}...")
            
            response = f"""Here's what I can do for you:

{chr(10).join([f"• {cap}" for cap in capabilities])}

Example Requests:
{chr(10).join([f"✓ {ex}" for ex in examples])}

I remember our conversations and learn your preferences to provide better assistance over time! What would you like to create?"""
        
        elif any(word in user_lower for word in ["thank you", "thanks", "appreciate"]):
            if user_preferences.get('frequent_user'):
                response = f"You're very welcome! It's always a pleasure working with you. I've learned a lot about your preferences and I'm here whenever you need automation magic! What's next on your list?"
            else:
                response = f"You're absolutely welcome! I'm {agent_name} and I'm here to help make your work easier. Feel free to ask me anything about automation - I love solving problems!"
        
        elif any(word in user_lower for word in ["good", "great", "awesome", "excellent", "perfect"]):
            response = f"That's wonderful to hear! I'm glad I could help. I'm always learning and improving to serve you better. Is there anything else you'd like to automate or explore?"
        
        elif any(word in user_lower for word in ["bye", "goodbye", "see you", "later"]):
            if previous_interactions:
                response = f"Goodbye for now! I'll remember our conversation and your preferences for next time. Feel free to come back whenever you need automation help - I'm always here!"
            else:
                response = f"Goodbye! It was great meeting you. Come back anytime you need automation assistance - I'll be here to help!"
        
        # Questions about the assistant itself
        elif any(phrase in user_lower for phrase in ["who are you", "what are you", "tell me about yourself"]):
            total_interactions = len(previous_interactions)
            if total_interactions > 5:
                response = f"I'm {agent_name}, your dedicated {agent_role}! We've had {total_interactions} interactions together, and I've been learning your preferences to provide better assistance. I specialize in automation and workflow creation, and I love helping people save time through smart technology!"
            else:
                response = f"I'm {agent_name}, your {agent_role}! I'm an AI-powered automation specialist who helps create workflows, send emails, fetch data, and build custom solutions. I remember our conversations and learn your preferences to provide increasingly personalized assistance!"
        
        # Default helpful response with context
        else:
            context_hint = ""
            if previous_interactions:
                recent_automation_types = [interaction.get('automation_type') for interaction in previous_interactions[-3:] if interaction.get('automation_type')]
                if recent_automation_types:
                    context_hint = f" I notice you've been working with {', '.join(set(recent_automation_types))} recently."
            
            response = f"I understand you're interested in \"{user_input}\".{context_hint} While I specialize in automation and workflow creation, I'm here to help however I can! \n\nQuick Ideas:\n• Turn this into an automated workflow\n• Create an email about this topic\n• Set up data fetching related to this\n• Build a custom solution\n\nWhat would you like me to help you automate or create?"
        
        # Store this interaction for learning
        await self._update_user_preferences(user_input, 'conversational')
        
        return {
            "success": True,
            "status": "conversational", 
            "message": response,
            "response": response,
            "agent_context": {
                "response_type": "enhanced_template",
                "agent_name": agent_name,
                "personalized": bool(previous_interactions),
                "context_used": bool(user_preferences)
            },
            "hasWorkflowJson": False,
            "hasWorkflowPreview": False,
            "done": True
        }

    async def _generate_ai_conversational_response(self, user_input: str, agent_name: str, agent_role: str, previous_interactions: list, user_preferences: dict) -> str:
        """Generate AI-powered conversational response using OpenAI"""
        logger.error(f"🤖 AI RESPONSE DEBUG: Starting generation for '{user_input[:30]}...'")
        
        try:
            if not HAS_OPENAI:
                logger.error(f"🤖 AI RESPONSE DEBUG: OpenAI package not available - HAS_OPENAI={HAS_OPENAI}")
                return None
                
            if not self.openai_api_key:
                logger.error(f"🤖 AI RESPONSE DEBUG: No OpenAI API key - self.openai_api_key={bool(self.openai_api_key)}")
                return None
                
            logger.error(f"🤖 AI RESPONSE DEBUG: All requirements met, attempting OpenAI call...")
            logger.error(f"🤖 AI RESPONSE DEBUG: API Key length: {len(self.openai_api_key) if self.openai_api_key else 0}")
            logger.error(f"🤖 AI RESPONSE DEBUG: API Key preview: {self.openai_api_key[:20]}...")
            
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.openai_api_key)
            logger.error(f"🤖 AI RESPONSE DEBUG: OpenAI client created successfully")
            
            # Build context from memory
            context_parts = []
            if previous_interactions:
                recent_history = previous_interactions[-3:]
                context_parts.append(f"Recent conversation context: {recent_history}")
            
            if user_preferences:
                prefs_str = ", ".join([f"{k}: {v}" for k, v in user_preferences.items()])
                context_parts.append(f"User preferences: {prefs_str}")
            
            if self.agent_expectations:
                context_parts.append(f"Agent expectations: {self.agent_expectations}")
            
            context_section = "\n".join(context_parts) if context_parts else ""
            
            prompt = f"""You are {agent_name}, a {agent_role} representing DXTR Labs.

DXTR Labs Company Context:
- We create AI-powered digital employees that automate real business tasks
- Unlike basic chatbots, our agents combine conversation with real action
- We specialize in email automation, data processing, and workflow creation
- Our digital employees work 24/7 and learn user preferences

Your personality should be:
- Friendly and conversational (avoid corporate descriptions)
- Enthusiastic about helping with automation
- Focus on what you can DO for the user, not just company facts
- Be natural and engaging, like a helpful colleague
- When greeting users, be welcoming but focus on how you can help

{context_section}

User message: "{user_input}"

Provide a natural, conversational response that:
- Greets the user warmly if it's a greeting
- Asks how you can help with their automation needs
- Shows enthusiasm for digital employee solutions
- Stays conversational, not corporate-sounding
- Offers to help with specific automation tasks
- Avoids just listing company facts unless directly asked

Keep the response friendly, helpful, and focused on the user's needs."""
            
            logger.error(f"🤖 AI RESPONSE DEBUG: Making OpenAI API call...")
            
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are {agent_name}, a {agent_role} from DXTR Labs. You're a helpful digital employee who loves automation and making people's work easier. Be conversational, friendly, and focus on how you can help users with their automation needs. Avoid just reciting company facts - instead, be engaging and offer specific help."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            ai_response = response.choices[0].message.content.strip()
            logger.error(f"🤖 AI RESPONSE DEBUG: ✅ SUCCESS! Generated {len(ai_response)} chars for: {user_input[:50]}...")
            logger.error(f"🤖 AI RESPONSE DEBUG: Response preview: {ai_response[:100]}...")
            return ai_response
            
        except Exception as e:
            logger.error(f"🤖 AI RESPONSE DEBUG: ❌ FAILED! Error: {e}")
            logger.error(f"🤖 AI RESPONSE DEBUG: Error type: {type(e).__name__}")
            import traceback
            logger.error(f"🤖 AI RESPONSE DEBUG: Full traceback: {traceback.format_exc()}")
            return None
    
    async def _update_user_preferences(self, user_input: str, interaction_type: str):
        """Update user preferences based on interaction patterns"""
        try:
            # This is already handled in the agent_processor memory update
            # But we can add specific preference learning here
            user_lower = user_input.lower()
            
            preferences_updates = {}
            
            # Track company information sharing
            if any(phrase in user_lower for phrase in ["company name", "what we sell", "what makes us special", "dxtr labs"]):
                logger.error(f"🏢 Company information detected and storing: {user_input[:100]}...")
                preferences_updates['company_details_shared'] = True
                preferences_updates['company_context_timestamp'] = datetime.now().isoformat()
                
                # Extract specific company details
                if "dxtr labs" in user_lower:
                    preferences_updates['company_name'] = "DXTR Labs"
                if "ai-powered digital employees" in user_lower or "digital employees" in user_lower:
                    preferences_updates['business_type'] = "AI-powered digital employees"
                if "24/7" in user_input or "24 7" in user_input:
                    preferences_updates['key_feature'] = "24/7 automation"
                if "fraction of the cost" in user_lower or "cost" in user_lower:
                    preferences_updates['value_prop'] = "cost_effective"
            
            # Track automation preferences
            if 'email' in user_lower:
                preferences_updates['prefers_email_automation'] = True
                preferences_updates['last_email_request'] = datetime.now().isoformat()
            
            if any(word in user_lower for word in ['data', 'fetch', 'scrape']):
                preferences_updates['interested_in_data'] = True
            
            if any(word in user_lower for word in ['schedule', 'recurring', 'daily']):
                preferences_updates['likes_scheduling'] = True
            
            # Track interaction frequency
            total_interactions = len(self.agent_memory.get('conversation_history', []))
            if total_interactions > 10:
                preferences_updates['frequent_user'] = True
            
            # Store preferences (this will be saved by the agent processor)
            current_context = self.agent_memory.get('context', {})
            current_prefs = current_context.get('user_preferences', {})
            current_prefs.update(preferences_updates)
            
            if preferences_updates:
                logger.error(f"🧠 User preferences updated with: {preferences_updates}")
            
        except Exception as e:
            logger.warning(f"Preference update failed: {e}")

    def _instant_response(self, message: str) -> dict:
        """Generate an instant response for quick interactions"""
        agent_name = self.agent_context.get('agent_data', {}).get('agent_name', 'Assistant')
        agent_role = self.agent_context.get('agent_data', {}).get('agent_role', 'Digital Assistant')
        
        return {
            "success": True,
            "status": "conversational",
            "message": message,
            "response": message,
            "agent_context": {
                "response_type": "instant",
                "agent_name": agent_name,
                "agent_role": agent_role,
                "personalized": False
            },
            "hasWorkflowJson": False,
            "hasWorkflowPreview": False,
            "done": True
        }
    
    async def _create_enhanced_fallback_response(self, user_input: str, agent_name: str, agent_role: str, previous_interactions: list) -> str:
        """Create enhanced fallback responses when OpenAI is not available"""
        try:
            user_lower = user_input.lower()
            
            # Enhanced pattern-based responses that are still engaging
            if any(greeting in user_lower for greeting in ["hi", "hello", "hey", "good morning", "good afternoon"]):
                if previous_interactions:
                    return f"Welcome back! I'm {agent_name}, your {agent_role} from DXTR Labs. Ready to continue where we left off or start something new? I can help with email automation, content creation, and workflow building!"
                else:
                    return f"Hello! I'm {agent_name}, your {agent_role} from DXTR Labs. I specialize in automation that actually gets things done - like sending emails, generating content, and building smart workflows. What can I automate for you today?"
            
            elif any(word in user_lower for word in ["help", "what can you do", "capabilities"]):
                return f"Great question! As your {agent_role}, I can help you with:\n\n• Email automation - Send personalized emails, follow-ups, and campaigns\n• Content creation - Generate sales pitches, reports, and professional communications\n• Data workflows - Fetch information and process it automatically\n• Smart scheduling - Set up recurring tasks and notifications\n\nWhat type of automation interests you most?"
            
            elif any(word in user_lower for word in ["email", "send", "message", "write"]):
                return f"Perfect! Email automation is one of my specialties. I can help you draft professional emails, send them to specific recipients, or even set up automated email sequences. Who would you like to send an email to, or what kind of email content do you need?"
            
            elif any(word in user_lower for word in ["automation", "automate", "workflow", "process"]):
                return f"Excellent! I love building automations that save time and boost productivity. I can create workflows for email sending, data processing, content generation, and much more. What specific task would you like to automate?"
            
            elif "thank" in user_lower:
                return f"You're very welcome! I'm always here to help with your automation needs. Is there anything else I can help you automate or any other workflows you'd like to explore?"
            
            else:
                # Generic but still helpful fallback
                return f"I'm {agent_name}, your {agent_role} from DXTR Labs! I'm here to help automate your work - whether that's sending emails, creating content, building workflows, or processing data. What would you like to work on together?"
                
        except Exception as e:
            logger.error(f"Enhanced fallback error: {e}")
            return None

    async def _detect_email_editing_intent(self, user_input: str) -> Optional[Dict[str, Any]]:
        """
        🔄 Detect if user is editing/clarifying an existing email workflow
        """
        try:
            user_lower = user_input.lower()
            
            # Check if we have recent email workflow in memory
            recent_interactions = self.agent_memory.get('conversation_history', [])
            last_workflow = None
            
            # Look for recent email workflow in conversation
            for interaction in reversed(recent_interactions[-5:]):  # Check last 5 interactions
                if isinstance(interaction, dict) and interaction.get('workflow_status') == 'preview_ready':
                    last_workflow = interaction
                    break
            
            # Also check if there's a pending workflow in session
            if hasattr(self, 'pending_workflow_params') and self.pending_workflow_params:
                last_workflow = self.pending_workflow_params
            
            if not last_workflow:
                logger.error(f"🔄 No recent email workflow found for editing")
                return None
            
            # Detect editing patterns
            editing_patterns = [
                # Company/sender corrections
                r'\b(company|company name|our company|sender|from)\s+(is|name is|should be|change to)\s+([A-Za-z0-9\s]+)',
                r'\b(company|organization|business)[\s:]+(.*?)(?:\s|$)',
                
                # Subject line changes
                r'\b(subject|title|heading|subject line)\s+(is|should be|change to|make it)\s+(.*)',
                
                # Recipient changes
                r'\b(send to|recipient|email|to)\s+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
                
                # Content modifications
                r'\b(change|update|modify|edit|fix|correct)\b',
                r'\b(make it more|add|include|mention)\b',
                
                # Direct corrections without keywords
                r'^[A-Za-z0-9\s]+ (is|inc|corp|llc|ltd)$',  # "HOTPOT inc", "Company Name LLC"
            ]
            
            detected_changes = {}
            
            for pattern in editing_patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    if 'company' in pattern or 'sender' in pattern:
                        # Extract company name
                        if len(match.groups()) >= 3:
                            detected_changes['company_name'] = match.group(3).strip()
                        elif len(match.groups()) >= 2:
                            detected_changes['company_name'] = match.group(2).strip()
                    elif 'subject' in pattern:
                        if len(match.groups()) >= 3:
                            detected_changes['subject'] = match.group(3).strip()
                    elif 'send to' in pattern or 'recipient' in pattern:
                        if len(match.groups()) >= 2:
                            detected_changes['recipient'] = match.group(2).strip()
            
            # Special case: Simple company name corrections like "company name is HOTPOT inc"
            if not detected_changes and re.match(r'^[A-Za-z0-9\s]+(inc|corp|llc|ltd|company)\.?$', user_input.strip(), re.IGNORECASE):
                detected_changes['company_name'] = user_input.strip()
            
            # Another pattern: "HOTPOT inc" by itself
            if not detected_changes and len(user_input.split()) <= 3 and any(keyword in user_lower for keyword in ['inc', 'corp', 'llc', 'ltd', 'company']):
                detected_changes['company_name'] = user_input.strip()
            
            if not detected_changes:
                logger.error(f"🔄 No editing patterns detected in: {user_input}")
                return None
            
            logger.error(f"🔄 EMAIL EDITING DETECTED: {detected_changes}")
            
            # Update the existing email workflow
            return await self._update_email_workflow(last_workflow, detected_changes, user_input)
            
        except Exception as e:
            logger.error(f"❌ Email editing detection error: {e}")
            return None
    
    async def _update_email_workflow(self, original_workflow: Dict, changes: Dict, user_input: str) -> Dict[str, Any]:
        """
        🔄 Update existing email workflow with user changes
        """
        try:
            logger.error(f"🔄 UPDATING EMAIL WORKFLOW with changes: {changes}")
            
            # Get the original email data
            original_preview = original_workflow.get('workflowPreview', {})
            original_json = original_workflow.get('workflowJson', {})
            
            recipient = original_preview.get('recipient') or changes.get('recipient')
            original_subject = original_preview.get('subject', '')
            original_body = original_preview.get('body', '')
            
            # Apply changes
            if 'company_name' in changes:
                company_name = changes['company_name']
                logger.error(f"🔄 Updating company name to: {company_name}")
                
                # Regenerate email content with the correct company
                updated_content = await self._regenerate_email_with_company(
                    user_input, recipient, company_name, original_subject, original_body
                )
                
                if updated_content:
                    subject = updated_content.get('subject', original_subject)
                    body = updated_content.get('body', original_body)
                else:
                    # Fallback: simple find/replace
                    subject = original_subject.replace('DXTR Labs', company_name)
                    body = original_body.replace('DXTR Labs', company_name)
            else:
                subject = changes.get('subject', original_subject)
                body = original_body
            
            # Update the workflow JSON
            updated_workflow_json = {
                "workflow_id": original_json.get("workflow_id", str(uuid.uuid4())),
                "name": f"Email Automation - {subject}",
                "description": f"Send email to {recipient}",
                "steps": [
                    {
                        "step_id": 1,
                        "action": "email_send",
                        "driver": "email",
                        "parameters": {
                            "to": recipient,
                            "subject": subject,
                            "body": body,
                            "from": COMPANY_EMAIL
                        }
                    }
                ],
                "metadata": {
                    "created_by": "mcp_llm_engine",
                    "automation_type": "email_automation",
                    "content_type": "sales_pitch",
                    "user_input": user_input,
                    "updated": True,
                    "changes_applied": changes
                }
            }
            
            logger.error(f"✅ EMAIL WORKFLOW UPDATED with company: {changes.get('company_name', 'N/A')}")
            
            # Return updated workflow
            return {
                "success": True,
                "status": "preview_ready",
                "message": f"I've updated the email with your changes. Would you like me to send it?",
                "response": f"📧 **Updated Email Preview**\n\n**To:** {recipient}\n**Subject:** {subject}\n\n**Body:**\n{body}\n\nWould you like me to send this updated email?",
                "workflowJson": updated_workflow_json,
                "workflowPreview": {
                    "recipient": recipient,
                    "subject": subject,
                    "body": body,
                    "action": "email_send"
                },
                "hasWorkflowJson": True,
                "hasWorkflowPreview": True,
                "done": False,
                "workflow_status": "preview_ready",
                "changes_applied": changes
            }
            
        except Exception as e:
            logger.error(f"❌ Email workflow update error: {e}")
            return None
    
    async def _regenerate_email_with_company(self, original_request: str, recipient: str, company_name: str, original_subject: str, original_body: str) -> Dict[str, Any]:
        """
        🔄 Regenerate email content with correct company information
        """
        try:
            if not HAS_OPENAI or not self.openai_api_key:
                return None
            
            client = AsyncOpenAI(api_key=self.openai_api_key)
            
            system_prompt = f"""You are updating an email with corrected company information.

CONTEXT:
- Original request: {original_request}
- Correct company name: {company_name}
- Recipient: {recipient}
- Keep the same email purpose and content style

TASK: Update the email to use the correct company name throughout, maintaining the same tone and message.

OUTPUT FORMAT (JSON only):
{{
  "subject": "Updated subject line with correct company",
  "body": "Updated email body with correct company name throughout"
}}"""

            user_prompt = f"""Update this email to use "{company_name}" instead of "DXTR Labs":

Original Subject: {original_subject}
Original Body: {original_body}

Keep the same message and tone, just update the company references."""
            
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            logger.error(f"🔄 REGENERATED EMAIL CONTENT: {content[:100]}...")
            
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                logger.error(f"❌ Failed to parse regenerated email JSON")
                return None
                
        except Exception as e:
            logger.error(f"❌ Email regeneration error: {e}")
            return None

    def store_workflow_in_memory(self, workflow_result: Dict[str, Any], user_input: str):
        """Store the latest workflow in agent memory for editing detection"""
        try:
            if not workflow_result or not workflow_result.get('workflowJson'):
                return
            
            # Store in agent memory for persistence
            if not hasattr(self, 'agent_memory') or not self.agent_memory:
                self.agent_memory = {}
            
            if 'conversation_history' not in self.agent_memory:
                self.agent_memory['conversation_history'] = []
            
            # Store the workflow with timestamp
            workflow_memory = {
                'timestamp': datetime.now().isoformat(),
                'user_input': user_input,
                'workflow_status': workflow_result.get('status'),
                'workflowJson': workflow_result.get('workflowJson'),
                'workflowPreview': workflow_result.get('workflowPreview'),
                'type': 'email_workflow'
            }
            
            self.agent_memory['conversation_history'].append(workflow_memory)
            
            # Keep only last 10 items in memory
            if len(self.agent_memory['conversation_history']) > 10:
                self.agent_memory['conversation_history'] = self.agent_memory['conversation_history'][-10:]
            
            # Also store as the "current workflow" for quick access
            self.agent_memory['current_workflow'] = workflow_memory
            self.pending_workflow_params = workflow_memory
            
            logger.error(f"💾 WORKFLOW STORED IN MEMORY for editing: {workflow_result.get('workflowJson', {}).get('workflow_id', 'unknown')}")
            
        except Exception as e:
            logger.error(f"❌ Failed to store workflow in memory: {e}")

    async def _build_enhanced_email_workflow(self, user_input: str, recipient_email: str, content_type: str) -> Dict[str, Any]:
        """
        🚀 Build a complete email automation workflow with JSON script
        """
        try:
            logger.error(f"🎯 BUILDING EMAIL WORKFLOW: {user_input[:50]}... -> {recipient_email}")
            
            # Use OpenAI to generate the email content and subject
            email_content_result = await self._generate_email_content(user_input, recipient_email, content_type)
            
            if not email_content_result:
                logger.error(f"❌ Failed to generate email content")
                return None
            
            subject = email_content_result.get("subject", "Automated Email")
            body = email_content_result.get("body", "")
            
            # Build the automation JSON workflow
            workflow_json = {
                "workflow_id": str(uuid.uuid4()),
                "name": f"Email Automation - {subject}",
                "description": f"Send email to {recipient_email}",
                "steps": [
                    {
                        "step_id": 1,
                        "action": "email_send",
                        "driver": "email",
                        "parameters": {
                            "to": recipient_email,
                            "subject": subject,
                            "body": body,
                            "from": COMPANY_EMAIL
                        }
                    }
                ],
                "metadata": {
                    "created_by": "mcp_llm_engine",
                    "automation_type": "email_automation",
                    "content_type": content_type,
                    "user_input": user_input
                }
            }
            
            logger.error(f"✅ EMAIL WORKFLOW JSON BUILT: {len(str(workflow_json))} chars")
            
            # Create the response
            workflow_result = {
                "success": True,
                "status": "preview_ready",
                "message": f"I've created an email automation for {recipient_email}. Would you like me to send it?",
                "response": f"📧 **Email Preview**\n\n**To:** {recipient_email}\n**Subject:** {subject}\n\n**Body:**\n{body}\n\nWould you like me to send this email?",
                "workflowJson": workflow_json,
                "workflowPreview": {
                    "recipient": recipient_email,
                    "subject": subject,
                    "body": body,
                    "action": "email_send"
                },
                "hasWorkflowJson": True,
                "hasWorkflowPreview": True,
                "done": False,  # Waiting for user confirmation
                "workflow_status": "preview_ready"
            }
            
            # 💾 STORE WORKFLOW IN MEMORY FOR EDITING
            self.store_workflow_in_memory(workflow_result, user_input)
            
            return workflow_result
            
        except Exception as e:
            logger.error(f"❌ Enhanced email workflow building error: {e}")
            return None
    
    async def _generate_email_content(self, user_input: str, recipient_email: str, content_type: str) -> Dict[str, Any]:
        """
        Generate email subject and body using OpenAI based on user request
        """
        try:
            if not HAS_OPENAI or not self.openai_api_key:
                # Fallback content generation
                return {
                    "subject": "Email from DXTR Labs",
                    "body": f"Hello,\n\nThis is an automated email based on your request: {user_input}\n\nBest regards,\nDXTR Labs Team"
                }
            
            client = AsyncOpenAI(api_key=self.openai_api_key)
            
            # Enhanced system prompt for email generation
            system_prompt = f"""You are an expert email content generator for DXTR Labs. Generate professional email content based on user requests.

CONTEXT:
- Company: DXTR Labs (AI-powered digital employees and automation)
- Content Type: {content_type}
- Recipient: {recipient_email}

REQUIREMENTS:
- Professional and engaging tone
- Clear subject line (under 60 characters)
- Well-structured body content
- Include DXTR Labs branding when appropriate
- Match the user's intent and content type

OUTPUT FORMAT (JSON only):
{{
  "subject": "Clear, engaging subject line",
  "body": "Professional email body with proper formatting\\n\\nInclude line breaks and structure as needed"
}}"""

            user_prompt = f"Generate email content for this request:\n\n'{user_input}'\n\nRecipient: {recipient_email}"
            
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            logger.error(f"🎯 EMAIL CONTENT GENERATED: {content[:100]}...")
            
            # Parse JSON response
            try:
                result = json.loads(content)
                logger.error(f"✅ EMAIL CONTENT PARSED: subject='{result.get('subject')}', body length={len(result.get('body', ''))}")
                return result
            except json.JSONDecodeError:
                logger.error(f"❌ Failed to parse email content JSON: {content}")
                # Extract content manually if JSON parsing fails
                lines = content.split('\n')
                subject = "Email from DXTR Labs"
                body = content
                
                for line in lines:
                    if 'subject' in line.lower() and ':' in line:
                        subject = line.split(':', 1)[1].strip().strip('"')
                        break
                
                return {"subject": subject, "body": body}
                
        except Exception as e:
            logger.error(f"❌ Email content generation error: {e}")
            return {
                "subject": "Email from DXTR Labs",
                "body": f"Hello,\n\nThis is regarding: {user_input}\n\nBest regards,\nDXTR Labs Team"
            }
    
    async def _create_email_automation_with_context(self, user_input: str, automation_result: Dict[str, Any], enriched_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create email automation with enriched context"""
        try:
            if not HAS_OPENAI or not self.openai_api_key:
                return await self._create_helpful_conversational_response(user_input)
            
            client = AsyncOpenAI(api_key=self.openai_api_key)
            
            # Build context string for AI
            context_str = self._build_context_string_for_ai(enriched_context)
            
            system_prompt = f"""You are an AI email automation specialist. Create personalized email automation workflows using available context.

AVAILABLE CONTEXT: {context_str}

STRICT JSON OUTPUT STRUCTURE:
{{
  "workflow_type": "email_automation",
  "status": "automation_ready", 
  "workflow_id": "email_auto_{int(time.time())}",
  "steps": [
    {{
      "action": "send_email",
      "parameters": {{
        "to": "recipient@email.com",
        "subject": "Personalized subject using context",
        "content": "Email content with company name, products, and context",
        "from_name": "{self.agent_data.get('agent_name', 'AI Assistant')}",
        "sender_email": "noreply@dxtrlabs.com",
        "email_type": "business|personal|promotional"
      }}
    }
  ],
  "estimated_execution_time": "2 minutes",
  "requires_approval": true,
  "automation_summary": "Brief description of the email automation"
}}

PERSONALIZATION RULES:
- Use company name naturally in email content
- Reference specific products/services mentioned
- Include relevant context from conversation
- Make subject line compelling and personalized
- Keep professional tone unless specified otherwise"""

            # Extract recipient from automation result
            recipient = automation_result.get("target_recipient", "")
            if not recipient:
                # Try to extract from user input
                import re
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, user_input)
                recipient = emails[0] if emails else "recipient@email.com"

            user_prompt = f"""Create email automation for: "{user_input}"

Target recipient: {recipient}
Specific action: {automation_result.get('specific_action', 'Send email')}

Use ALL available context to create a highly personalized email."""

            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            content = response.choices[0].message.content.strip()
            logger.error(f"📧 EMAIL AUTOMATION RESPONSE: {content}")
            
            try:
                workflow_json = json.loads(content)
                
                # Store the workflow
                workflow_id = workflow_json.get("workflow_id", f"email_auto_{int(time.time())}")
                self._store_workflow_in_memory(workflow_id, workflow_json, user_input)
                
                return {
                    "success": True,
                    "status": "automation_ready",
                    "message": f"✅ Email automation created: {workflow_json.get('automation_summary', 'Email automation')}",
                    "response": f"I've created a personalized email automation using your context. {workflow_json.get('automation_summary', 'Ready to send!')}",
                    "workflow_json": workflow_json,
                    "hasWorkflowJson": True,
                    "hasWorkflowPreview": True,
                    "workflow_preview": self._create_workflow_preview(workflow_json),
                    "done": True
                }
                
            except json.JSONDecodeError:
                logger.error(f"❌ Failed to parse email automation JSON")
                return await self._create_helpful_conversational_response(user_input)
                
        except Exception as e:
            logger.error(f"❌ Email automation with context error: {e}")
            return await self._create_helpful_conversational_response(user_input)
    
    async def _create_data_automation_with_context(self, user_input: str, automation_result: Dict[str, Any], enriched_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create data fetching automation with context"""
        try:
            context_str = self._build_context_string_for_ai(enriched_context)
            
            # Basic data automation structure
            workflow_json = {
                "workflow_type": "data_automation",
                "status": "automation_ready", 
                "workflow_id": f"data_auto_{int(time.time())}",
                "steps": [
                    {
                        "action": "fetch_data",
                        "parameters": {
                            "source": "web_scraping",
                            "query": user_input,
                            "context": context_str
                        }
                    }
                ],
                "estimated_execution_time": "5 minutes",
                "requires_approval": True,
                "automation_summary": f"Data fetching automation: {automation_result.get('specific_action', 'Fetch data')}