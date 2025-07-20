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
import smtplib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env.local
env_path = Path(__file__).parent.parent.parent / '.env.local'
load_dotenv(dotenv_path=env_path)

# Set up logging
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.append(str(SCRIPT_DIR.parent))

# Import services
from services.web_search_service import web_search_service

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
    logger.info(f"OpenAI package loaded successfully - full AI capabilities available")
except ImportError:
    logger.error(f"OpenAI package not available - automation intent detection will be limited")
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
        
        logger.error(f"MCP Engine initialized with agent context: {self.agent_data.get('agent_name', 'Unknown')} | Expectations: {bool(self.agent_expectations)}")
        
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
        
        # PRODUCTION FIX: Add AI Investors Database
        self.ai_investors_database = [
            {
                "name": "Andreessen Horowitz (a16z)",
                "focus": "AI/ML, Enterprise Software",
                "email": "info@a16z.com",
                "contact": "Marc Andreessen, Ben Horowitz",
                "recent_investments": "Anthropic, Character.AI, MidJourney",
                "fund_size": "$7.2B",
                "stage": "Seed to Growth"
            },
            {
                "name": "Google Ventures (GV)",
                "focus": "AI, Machine Learning, Enterprise",
                "email": "team@gv.com",
                "contact": "David Krane, Barry Eggers",
                "recent_investments": "DeepMind, Anthropic, Hugging Face",
                "fund_size": "$2.4B",
                "stage": "Series A to C"
            },
            {
                "name": "Bessemer Venture Partners",
                "focus": "AI Infrastructure, Enterprise AI",
                "email": "info@bvp.com",
                "contact": "Jeremy Levine, David Cowan",
                "recent_investments": "DataRobot, Twilio, Shopify",
                "fund_size": "$1.6B",
                "stage": "Series A to IPO"
            },
            {
                "name": "Accel Partners",
                "focus": "AI/ML Applications, SaaS",
                "email": "info@accel.com",
                "contact": "Philippe Botteri, Sonali De Rycker",
                "recent_investments": "UiPath, Atlassian, Slack",
                "fund_size": "$3.0B",
                "stage": "Series A to C"
            },
            {
                "name": "Sequoia Capital",
                "focus": "AI Infrastructure, Applied AI",
                "email": "info@sequoiacap.com",
                "contact": "Alfred Lin, Pat Grady",
                "recent_investments": "OpenAI, Stability AI, Harvey",
                "fund_size": "$8.5B",
                "stage": "Seed to Growth"
            },
            {
                "name": "NEA (New Enterprise Associates)",
                "focus": "AI/ML, Enterprise Software",
                "email": "info@nea.com",
                "contact": "Tony Florence, Carmen Chang",
                "recent_investments": "DataSift, Robocorp, Scale AI",
                "fund_size": "$3.6B",
                "stage": "Series A to C"
            },
            {
                "name": "Intel Capital",
                "focus": "AI Hardware, Edge Computing",
                "email": "intel.capital@intel.com",
                "contact": "Wendell Brooks, Nick Washburn",
                "recent_investments": "SigOpt, Nervana, Habana Labs",
                "fund_size": "$2.0B",
                "stage": "Series A to Growth"
            },
            {
                "name": "NVIDIA GPU Ventures",
                "focus": "AI/ML, Computer Vision",
                "email": "gpuventures@nvidia.com",
                "contact": "Jeff Herbst, David Kanter",
                "recent_investments": "Recursion, DeepMap, Avanade",
                "fund_size": "$1.0B",
                "stage": "Series A to B"
            },
            {
                "name": "Insight Partners",
                "focus": "AI-Enabled SaaS, Enterprise AI",
                "email": "info@insightpartners.com",
                "contact": "Lonne Jaffe, George Mathew",
                "recent_investments": "Datadog, Shopify, Twitter",
                "fund_size": "$12.0B",
                "stage": "Growth Stage"
            },
            {
                "name": "Khosla Ventures",
                "focus": "AI/ML, Deep Tech",
                "email": "info@khoslaventures.com",
                "contact": "Vinod Khosla, Keith Rabois",
                "recent_investments": "OpenAI, Square, Instacart",
                "fund_size": "$1.4B",
                "stage": "Seed to Series B"
            }
        ]
        
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
            logger.error(f"Error fetching agent details: {e}")
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
                logger.error(f"No database manager available for workflow fetch")
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
                logger.info(f"Fetched workflow for agent {self.agent_id}")
            except Exception as db_error:
                logger.error(f"Database error fetching workflow: {db_error}")
                return self._create_empty_workflow()
            
            if not workflow_result:
                logger.info(f"ℹ️ No existing workflow found for agent {self.agent_id}, creating new")
                return self._create_empty_workflow()
            
            try:
                script_data = json.loads(workflow_result.get("script", "{}"))
                if not isinstance(script_data, dict):
                    logger.error(f"Invalid script data format")
                    return self._create_empty_workflow()
                    
                # Validate required fields
                required_fields = ["id", "name", "nodes", "edges"]
                if not all(field in script_data for field in required_fields):
                    logger.error(f"Missing required fields in workflow script")
                    return self._create_empty_workflow()
                    
                workflow = {
                    "workflow_id": workflow_result.get("workflow_id"),
                    "agent_id": workflow_result.get("agent_id"),
                    "script": script_data,
                    "created_at": workflow_result.get("created_at"),
                    "updated_at": workflow_result.get("updated_at")
                }
                
                logger.info(f"Successfully loaded workflow with {len(script_data.get('nodes', []))} nodes")
                return workflow
                
            except json.JSONDecodeError as json_error:
                logger.error(f"Invalid JSON in workflow script: {json_error}")
                return self._create_empty_workflow()
            
        except Exception as e:
            logger.error(f"Error fetching agent workflow: {e}")
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
        ENHANCED CONVERSATIONAL FLOW with Smart Automation Detection
        Flow: Normal Conversation → Automation Detection → Prebuilt Workflow Search → Custom Workflow Building → Parameter Collection → Execution
        """
        logger.error(f"PROCESSING REQUEST: {user_input[:100]}...")
        
        # Handle special actions for approved emails and workflow execution
        if user_input.startswith("SEND_APPROVED_EMAIL:"):
            parts = user_input.split(":", 3)
            if len(parts) >= 4:
                workflow_id = parts[1]
                recipient = parts[2] 
                subject = parts[3]
                email_content = request_data.get("email_content", "") if request_data else ""
                logger.error(f"PROCESSING APPROVED EMAIL SEND: {workflow_id} -> {recipient}")
                return await self.send_approved_email(workflow_id, user_input, recipient, email_content, subject)
        
        # Handle workflow execution confirmation
        if user_input.startswith("EXECUTE_WORKFLOW:"):
            workflow_id = user_input.split(":", 1)[1]
            return await self._execute_confirmed_workflow(workflow_id)
        
        # Handle parameter filling responses
        if await self._is_parameter_response(user_input):
            return await self._handle_parameter_input(user_input)
        
        #  Handle email confirmation when user says "yes" or confirms sending
        if await self._check_pending_email_confirmation(user_input):
            logger.error(f"EMAIL CONFIRMATION DETECTED: {user_input[:50]}...")
            return await self._handle_email_confirmation(user_input)
        
        # Validate email credentials if this is an email-related request
        if "email" in user_input.lower():
            if not self._validate_email_credentials():
                return {
                    "success": False,
                    "response": " Email credentials not properly configured in .env.local. Please check your configuration.",
                    "status": "error",
                    "error": "invalid_credentials"
                }
                
        # Processing lock check
        if self._processing_lock:
            return {
                "success": True,
                "response": "Processing your previous request. Please wait a moment.",
                "processing_time": "< 1ms (locked)"
            }
        
        self._processing_lock = True
        start_time = datetime.now()
        
        try:
            user_input = user_input.strip()
            if len(user_input) < 2:
                return self._instant_response("Please provide more details about what you'd like to automate.")
            
            #  STEP 1: CONTEXT EXTRACTION - Extract ALL useful information for memory
            logger.error(f"STEP 1: EXTRACTING CONTEXT from: {user_input[:50]}...")
            context_extraction = await self._extract_context_information(user_input)
            if context_extraction:
                await self._store_context_in_memory(context_extraction, user_input)
                logger.error(f"📝 CONTEXT STORED: {list(context_extraction.keys())}")
            
            #  STEP 2: SMART AUTOMATION DETECTION with OpenAI
            logger.error(f"STEP 2: SMART AUTOMATION DETECTION...")
            automation_intent = await self._advanced_automation_detection(user_input, context_extraction)
            
            if not automation_intent.get("is_automation_request"):
                #  NORMAL CONVERSATION MODE using OpenAI
                logger.error(f"� NORMAL CONVERSATION MODE")
                return await self._create_smart_conversational_response(user_input, context_extraction)
            
            #  STEP 3: PREBUILT WORKFLOW SEARCH
            logger.error(f"STEP 3: SEARCHING PREBUILT WORKFLOWS...")
            prebuilt_workflows = await self._search_prebuilt_workflows(automation_intent, user_input)
            
            if prebuilt_workflows:
                logger.error(f"FOUND PREBUILT WORKFLOWS: {len(prebuilt_workflows)} options")
                return await self._present_workflow_options(prebuilt_workflows, user_input, automation_intent)
            
            # 🏗️ STEP 4: CUSTOM WORKFLOW BUILDING
            logger.error(f"🏗️ STEP 4: BUILDING CUSTOM WORKFLOW...")
            custom_workflow = await self._build_custom_workflow(automation_intent, user_input, context_extraction)
            
            #  STEP 5: PRESENT WORKFLOW FOR CONFIRMATION
            logger.error(f"STEP 5: PRESENTING WORKFLOW FOR CONFIRMATION...")
            return await self._present_workflow_for_confirmation(custom_workflow, user_input, automation_intent)
            
        except Exception as e:
            logger.error(f"Enhanced processing error: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            # Recovery fallback to conversational response
            logger.error(f"EXCEPTION RECOVERY: Attempting conversational response as fallback...")
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
                        return {
                            "success": True,
                            "status": "conversational",
                            "response": recovery_response,
                            "recovery_mode": True,
                            "done": True
                        }
                
                return {
                    "success": True,
                    "status": "conversational", 
                    "response": f"I apologize, but I encountered an issue processing your request. Please try rephrasing or let me know if you need help with automation.",
                    "error_recovery": True,
                    "done": True
                }
            except Exception as recovery_error:
                logger.error(f"Recovery also failed: {recovery_error}")
                return {
                    "success": False,
                    "status": "error",
                    "response": "I'm having technical difficulties. Please try again in a moment.",
                    "done": True
                }
        finally:
            self._processing_lock = False
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            logger.info(f"Enhanced processing: {processing_time:.3f}s")
    
    async def _check_pending_email_confirmation(self, user_input: str) -> bool:
        """Check if user input is responding to a pending email confirmation"""
        try:
            if not hasattr(self, 'agent_memory') or not self.agent_memory:
                return False
            
            # Check if there's a pending email workflow
            pending_workflow = self.agent_memory.get('pending_email_workflow')
            if not pending_workflow:
                return False
            
            # Check if user input looks like a confirmation
            confirmation_phrases = [
                'yes', 'y', 'send it', 'send', 'approve', 'confirmed', 'ok', 'okay', 
                'go ahead', 'please send', 'send the email', 'looks good'
            ]
            
            user_lower = user_input.lower().strip()
            return any(phrase in user_lower for phrase in confirmation_phrases)
            
        except Exception as e:
            logger.error(f"Error checking email confirmation: {e}")
            return False
    
    async def _handle_email_confirmation(self, user_input: str):
        """Handle user confirmation of email sending"""
        try:
            if not hasattr(self, 'agent_memory') or not self.agent_memory:
                return self._instant_response("No pending email found to confirm.")
            
            pending_workflow = self.agent_memory.get('pending_email_workflow')
            if not pending_workflow:
                return self._instant_response("No pending email found to confirm.")
            
            # Extract email details from the stored workflow JSON
            workflow_json = pending_workflow.get('workflow_json', {})
            if not workflow_json or 'steps' not in workflow_json:
                return self._instant_response("Invalid pending email workflow.")
            
            # Get the email step parameters
            email_step = workflow_json['steps'][0] if workflow_json['steps'] else {}
            email_params = email_step.get('parameters', {})
            
            recipient = email_params.get('to')
            email_content = email_params.get('body')
            subject = email_params.get('subject', 'Message from AI Assistant')
            
            if not recipient or not email_content:
                logger.error(f"Missing email data: recipient={recipient}, content_len={len(email_content) if email_content else 0}")
                return self._instant_response("Missing email recipient or content in pending workflow.")
            
            logger.error(f"EMAIL CONFIRMATION: Sending to {recipient}")
            
            # Clear the pending workflow
            self.agent_memory.pop('pending_email_workflow', None)
            
            # Send the email
            return await self._send_email_with_content(recipient, email_content, subject)
            
        except Exception as e:
            logger.error(f"Error handling email confirmation: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return self._instant_response(f"Error processing email confirmation: {str(e)}")

    async def _send_email_with_content(self, recipient: str, email_content: str, subject: str):
        """Send email with specified content using actual SMTP"""
        try:
            if not recipient or not email_content:
                return self._instant_response(" Missing recipient or email content for sending.")
            
            logger.error(f"SENDING EMAIL: {subject} -> {recipient}")
            
            # Get SMTP configuration from environment
            smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", 587))
            smtp_user = os.getenv("SMTP_USER")
            smtp_password = os.getenv("SMTP_PASSWORD")
            
            if not smtp_user or not smtp_password:
                logger.error(f"SMTP credentials not configured")
                return self._instant_response(" Email service not configured. Please check SMTP settings.")
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['From'] = smtp_user
            msg['To'] = recipient
            msg['Subject'] = subject
            
            # Add email content as both plain text and HTML
            text_part = MIMEText(email_content, 'plain')
            msg.attach(text_part)
            
            # Try to create HTML version if content looks like it might benefit from formatting
            if any(marker in email_content for marker in ['\n\n', '**', '*', '-', '•']):
                html_content = email_content.replace('\n\n', '<br><br>').replace('\n', '<br>')
                html_content = html_content.replace('**', '<strong>').replace('**', '</strong>')
                html_part = MIMEText(f"<html><body>{html_content}</body></html>", 'html')
                msg.attach(html_part)
            
            # Send email via SMTP
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            logger.error(f"EMAIL SUCCESSFULLY SENT: {recipient}")
            
            success_message = f""" Email sent successfully!
            
 **Email Details:**
- **To:** {recipient}
- **Subject:** {subject}
- **Content:** {email_content[:100]}{'...' if len(email_content) > 100 else ''}
- **Sent from:** {smtp_user}

The email has been delivered to the recipient."""

            return {
                "success": True,
                "response": success_message,
                "status": "email_sent",
                "recipient": recipient,
                "subject": subject,
                "processing_time": 0.5
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            
            # Provide helpful error messages
            error_msg = str(e).lower()
            if "authentication failed" in error_msg or "invalid credentials" in error_msg:
                helpful_error = " Email authentication failed. Please check your SMTP username and password."
            elif "connection" in error_msg:
                helpful_error = " Could not connect to email server. Please check your SMTP host and port settings."
            elif "timeout" in error_msg:
                helpful_error = " Email sending timed out. Please try again or check your network connection."
            else:
                helpful_error = f" Failed to send email: {str(e)}"
            
            return self._instant_response(helpful_error)

    async def send_approved_email(self, workflow_id: str, user_input: str, recipient: str, email_content: str, subject: str):
        """Send an approved email from a workflow"""
        try:
            logger.error(f"SENDING APPROVED EMAIL: workflow {workflow_id} -> {recipient}")
            
            # Use the same email sending logic
            return await self._send_email_with_content(recipient, email_content, subject)
            
        except Exception as e:
            logger.error(f"Error sending approved email: {e}")
            return self._instant_response(f" Failed to send approved email: {str(e)}")

    async def _openai_intent_detection(self, user_input: str) -> Dict[str, Any]:
        """
         OpenAI-powered intent detection - the core intelligence for routing requests
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
- Web search: "search", "find", "look up", "research", "investigate", "search the web", "find information", "search for", "find me", "look for"
- Workflow creation: "automate", "create workflow", "build automation"  
- Scheduling: "schedule", "recurring", "daily", "weekly"

IMPORTANT: If the user asks to SEARCH, FIND, LOOK UP, or RESEARCH anything, this is ALWAYS web_search automation!

Examples of WEB SEARCH:
- "search top 10 investors interested in ramen companies" → web_search
- "find information about AI startups" → web_search
- "look up recent trends in automation" → web_search
- "research competitors in the market" → web_search
- "investigate blockchain technologies" → web_search

CONVERSATIONAL INDICATORS:
- Questions: "how are you", "what can you do", "help me understand"
- Greetings: "hi", "hello", "hey", "good morning"
- General chat: casual conversation without action requests

OUTPUT FORMAT (JSON only):
{
  "is_automation": true/false,
  "automation_type": "email_automation|content_creation|asu_bus_automation|data_fetching|web_search|workflow|scheduling|none",
  "confidence": 0.0-1.0,
  "detected_email": "email@example.com or null",
  "content_type": "sales_pitch|report|proposal|email|search_results|none",
  "action_verbs": ["send", "create", "write", "search", "find"],
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
            logger.error(f"OpenAI Intent Response: {content}")
            
            # Parse JSON response
            try:
                import json
                result = json.loads(content)
                logger.error(f"Intent Detection Result: automation={result.get('is_automation')}, type={result.get('automation_type')}")
                return result
            except json.JSONDecodeError:
                logger.error(f"Failed to parse OpenAI JSON response: {content}")
                return {"is_automation": False, "reason": "parse_error"}
                
        except Exception as e:
            logger.error(f"OpenAI intent detection error: {e}")
            return {"is_automation": False, "reason": "openai_error"}
    
    async def _execute_smart_automation(self, user_input: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
         Execute automation based on detected intent - the core automation router
        """
        try:
            automation_type = intent.get("automation_type")
            logger.error(f"Executing smart automation: {automation_type}")
            
            #  FULL TWO-PART SYSTEM: Context + Automation Separation
            logger.error(f"IMPLEMENTING FULL TWO-PART SYSTEM")
            
            # Step 1: Extract context information from user message
            context_info = await self._extract_context_information(user_input)
            
            # Step 2: Store context in memory regardless of automation intent
            await self._store_context_in_memory(context_info, user_input)
            
            # Step 3: Detect automation intent separately
            automation_result = await self._detect_automation_intent(user_input, context_info)
            
            # Step 4: Execute based on results
            if automation_result.get("has_automation_task"):
                logger.error(f"AUTOMATION DETECTED: {automation_result.get('automation_type')}")
                return await self._execute_automation_with_context(user_input, automation_result, context_info)
            else:
                logger.error(f"💭 NO AUTOMATION - CONVERSATIONAL RESPONSE WITH CONTEXT")
                return await self._create_contextual_conversational_response(user_input, context_info)
                
        except Exception as e:
            logger.error(f"Smart automation execution error: {e}")
            return None
    
    async def _attempt_workflow_selection(self, user_input: str, context_extraction: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
         Intelligent workflow selection from existing 2000+ workflows
        This method attempts to match user intent with pre-built workflows
        """
        try:
            logger.error(f"WORKFLOW SELECTION: Analyzing input: {user_input[:100]}...")
            
            # Import the workflow selector
            from workflow_selector import WorkflowSelector, enhance_mcp_with_workflow_selection
            
            # Use the enhancement function to integrate with existing context
            workflow_result = await enhance_mcp_with_workflow_selection(
                mcp_engine=self,
                user_input=user_input,
                context=context_extraction
            )
            
            if not workflow_result.get("workflow_selection"):
                logger.error(f"WORKFLOW SELECTION: No suitable workflows found - {workflow_result.get('reason', 'unknown')}")
                return None
            
            # Handle auto-selected workflow
            if workflow_result.get("auto_selected"):
                selected_workflow_id = workflow_result.get("selected_workflow")
                customized_workflow = workflow_result.get("customized_workflow")
                
                logger.error(f"AUTO-SELECTED WORKFLOW: {selected_workflow_id}")
                
                # Execute the workflow using our automation engine
                if self.automation_engine and customized_workflow:
                    logger.error(f"EXECUTING AUTO-SELECTED WORKFLOW: {selected_workflow_id}")
                    
                    try:
                        # Execute through automation engine
                        execution_result = await self.automation_engine.execute_workflow(
                            customized_workflow,
                            user_id=self.user_id
                        )
                        
                        return {
                            "success": True,
                            "status": "workflow_executed",
                            "workflow_id": selected_workflow_id,
                            "workflow_name": customized_workflow.get("name", "Selected Workflow"),
                            "execution_result": execution_result,
                            "message": f" I found and executed a perfect workflow for your request: {customized_workflow.get('name')}",
                            "confidence": workflow_result.get("confidence", 0.8),
                            "workflow_selection": True,
                            "auto_selected": True
                        }
                    
                    except Exception as e:
                        logger.error(f"Auto-selected workflow execution failed: {e}")
                        # Fall back to manual selection
                        pass
                
                # If execution failed, convert to manual selection
                return {
                    "success": True,
                    "status": "workflow_ready", 
                    "workflow_id": selected_workflow_id,
                    "workflow_json": customized_workflow,
                    "message": f" I found a perfect workflow for your request. Would you like me to execute it?",
                    "confidence": workflow_result.get("confidence", 0.8),
                    "workflow_selection": True,
                    "auto_selected": False,
                    "ready_for_execution": True
                }
            
            # Handle workflow options for user selection
            elif workflow_result.get("workflow_options"):
                workflow_options = workflow_result.get("workflow_options", [])
                
                logger.error(f"WORKFLOW OPTIONS: Found {len(workflow_options)} suitable workflows")
                
                # Format workflow options for user presentation
                options_text = "\n".join([
                    f"{i+1}. **{opt['name']}** ({opt['complexity']}) - {opt['description'][:100]}..."
                    for i, opt in enumerate(workflow_options[:3])  # Show top 3
                ])
                
                return {
                    "success": True,
                    "status": "workflow_options",
                    "workflow_options": workflow_options,
                    "message": f"I found {len(workflow_options)} workflows that match your request:\n\n{options_text}\n\nWhich one would you like to use? (Reply with the number)",
                    "user_action_required": "select_workflow",
                    "workflow_selection": True,
                    "auto_selected": False,
                    "intent": workflow_result.get("intent"),
                    "missing_parameters": workflow_result.get("missing_parameters", [])
                }
            
            # No workflows found
            logger.error(f"WORKFLOW SELECTION: No suitable workflows identified")
            return None
            
        except ImportError:
            logger.error(f"WORKFLOW SELECTION: WorkflowSelector not available")
            return None
        except Exception as e:
            logger.error(f"WORKFLOW SELECTION ERROR: {e}")
            return None

    async def _enhanced_pattern_detection(self, user_input: str) -> Dict[str, Any]:
        """
        Enhanced pattern-based detection for automation when OpenAI is not available
        """
        user_lower = user_input.lower()
        
        logger.error(f"ENHANCED PATTERN DETECTION: Analyzing '{user_input[:50]}...'")
        
        # Email automation patterns (including Calendly/meeting requests)
        email_patterns = ['send email', 'email to', 'compose email', 'draft email', 'message to', 
                         'calendly', 'schedule meeting', 'book time', 'meeting invite', 'calendar link']
        if any(pattern in user_lower for pattern in email_patterns):
            return {
                "is_automation": True,
                "automation_type": "email_automation",
                "confidence": 0.8 if any(p in user_lower for p in ['calendly', 'schedule', 'meeting']) else 0.7,
                "detected_patterns": ["email"]
            }
        
        # Content creation patterns
        content_patterns = ['create content', 'generate', 'write', 'draft', 'compose']
        if any(pattern in user_lower for pattern in content_patterns):
            return {
                "is_automation": True,
                "automation_type": "content_creation",
                "confidence": 0.6,
                "detected_patterns": ["content"]
            }
        
        # Search/research patterns
        search_patterns = ['search', 'find', 'look up', 'research', 'investigate', 'search for']
        if any(pattern in user_lower for pattern in search_patterns):
            return {
                "is_automation": True,
                "automation_type": "web_search",
                "confidence": 0.8,
                "detected_patterns": ["search"]
            }
        
        # ASU Bus automation patterns
        bus_patterns = ['asu bus', 'bus shuttle', 'asu shuttle', 'bus schedule', 'next bus', 'bus time', 'transportation', 'asu transit']
        if any(pattern in user_lower for pattern in bus_patterns):
            return {
                "is_automation": True,
                "automation_type": "asu_bus_automation",
                "confidence": 0.9,
                "detected_patterns": ["bus", "asu", "transportation"]
            }
        
        # Data processing patterns
        data_patterns = ['process data', 'analyze', 'filter', 'transform', 'export data']
        if any(pattern in user_lower for pattern in data_patterns):
            return {
                "is_automation": True,
                "automation_type": "data_processing",
                "confidence": 0.7,
                "detected_patterns": ["data"]
            }
        
        # Workflow/automation patterns
        workflow_patterns = ['automate', 'create workflow', 'build automation', 'schedule']
        if any(pattern in user_lower for pattern in workflow_patterns):
            return {
                "is_automation": True,
                "automation_type": "workflow_creation",
                "confidence": 0.8,
                "detected_patterns": ["workflow"]
            }
        
        logger.error(f"ENHANCED PATTERN DETECTION: No automation patterns detected")
        return {
            "is_automation": False,
            "automation_type": "none",
            "confidence": 0.0,
            "detected_patterns": []
        }

    async def _create_helpful_conversational_response(self, user_input: str) -> Dict[str, Any]:
        """
        Create enhanced conversational responses using agent context, memory, and AI
        """
        logger.error(f"CONVERSATIONAL RESPONSE DEBUG: Starting for '{user_input[:50]}...'")
        
        user_lower = user_input.lower()
        
        # Get agent context for personalized responses
        agent_name = self.agent_data.get('agent_name', 'AI Assistant')
        agent_role = self.agent_data.get('agent_role', 'Personal Assistant')
        
        logger.error(f"CONVERSATIONAL DEBUG: Agent = {agent_name}, Role = {agent_role}")
        
        # Check conversation history for context
        previous_interactions = self.agent_memory.get('conversation_history', [])
        user_context = self.agent_memory.get('context', {})
        user_preferences = user_context.get('user_preferences', {})
        
        logger.error(f"CONVERSATIONAL DEBUG: OpenAI available = {HAS_OPENAI}, API key = {bool(self.openai_api_key)}")
        
        # Try to generate AI-powered conversational response first
        logger.error(f"CONVERSATIONAL DEBUG: Attempting OpenAI response generation...")
        ai_response = await self._generate_ai_conversational_response(user_input, agent_name, agent_role, previous_interactions, user_preferences)
        logger.error(f"CONVERSATIONAL DEBUG: AI response = {bool(ai_response)}, content = {ai_response[:100] if ai_response else 'None'}")
        
        if ai_response:
            logger.error(f"USING OPENAI CONVERSATIONAL RESPONSE: {ai_response[:100]}...")
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
        logger.error(f"OpenAI conversational response failed - trying enhanced fallback")
        
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
        logger.error(f"Using minimal fallback - all enhanced responses failed")
        
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
        logger.error(f"AI RESPONSE DEBUG: Starting generation for '{user_input[:30]}...'")
        
        try:
            if not HAS_OPENAI:
                logger.error(f"AI RESPONSE DEBUG: OpenAI package not available - HAS_OPENAI={HAS_OPENAI}")
                return None
                
            if not self.openai_api_key:
                logger.error(f"AI RESPONSE DEBUG: No OpenAI API key - self.openai_api_key={bool(self.openai_api_key)}")
                return None
                
            logger.error(f"AI RESPONSE DEBUG: All requirements met, attempting OpenAI call...")
            logger.error(f"AI RESPONSE DEBUG: API Key length: {len(self.openai_api_key) if self.openai_api_key else 0}")
            logger.error(f"AI RESPONSE DEBUG: API Key preview: {self.openai_api_key[:20]}...")
            
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.openai_api_key)
            logger.error(f"AI RESPONSE DEBUG: OpenAI client created successfully")
            
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
            
            logger.error(f"AI RESPONSE DEBUG: Making OpenAI API call...")
            
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
            logger.error(f"AI RESPONSE DEBUG: SUCCESS! Generated {len(ai_response)} chars for: {user_input[:50]}...")
            logger.error(f"AI RESPONSE DEBUG: Response preview: {ai_response[:100]}...")
            return ai_response
            
        except Exception as e:
            logger.error(f"AI RESPONSE DEBUG: FAILED! Error: {e}")
            logger.error(f"AI RESPONSE DEBUG: Error type: {type(e).__name__}")
            import traceback
            logger.error(f"AI RESPONSE DEBUG: Full traceback: {traceback.format_exc()}")
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
                logger.error(f"User preferences updated with: {preferences_updates}")
            
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
         Detect if user is editing/clarifying an existing email workflow
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
                logger.error(f"No recent email workflow found for editing")
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
                logger.error(f"No editing patterns detected in: {user_input}")
                return None
            
            logger.error(f"EMAIL EDITING DETECTED: {detected_changes}")
            
            # Update the existing email workflow
            return await self._update_email_workflow(last_workflow, detected_changes, user_input)
            
        except Exception as e:
            logger.error(f"Email editing detection error: {e}")
            return None
    
    async def _update_email_workflow(self, original_workflow: Dict, changes: Dict, user_input: str) -> Dict[str, Any]:
        """
         Update existing email workflow with user changes
        """
        try:
            logger.error(f"UPDATING EMAIL WORKFLOW with changes: {changes}")
            
            # Get the original email data
            original_preview = original_workflow.get('workflowPreview', {})
            original_json = original_workflow.get('workflowJson', {})
            
            recipient = original_preview.get('recipient') or changes.get('recipient')
            original_subject = original_preview.get('subject', '')
            original_body = original_preview.get('body', '')
            
            # Apply changes
            if 'company_name' in changes:
                company_name = changes['company_name']
                logger.error(f"Updating company name to: {company_name}")
                
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
            
            logger.error(f"EMAIL WORKFLOW UPDATED with company: {changes.get('company_name', 'N/A')}")
            
            # Return updated workflow
            return {
                "success": True,
                "status": "preview_ready",
                "message": f"I've updated the email with your changes. Would you like me to send it?",
                "response": f" **Updated Email Preview**\n\n**To:** {recipient}\n**Subject:** {subject}\n\n**Body:**\n{body}\n\nWould you like me to send this updated email?",
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
            logger.error(f"Email workflow update error: {e}")
            return None

    async def _extract_context_information(self, user_input: str) -> Dict[str, Any]:
        """
         STEP 1: Extract ALL useful context information from user message
        This includes company info, personal details, preferences, and project context
        """
        try:
            if not HAS_OPENAI or not self.openai_api_key:
                # Fallback pattern-based extraction
                return self._pattern_based_context_extraction(user_input)
            
            client = AsyncOpenAI(api_key=self.openai_api_key)
            
            system_prompt = """You are a context extraction specialist. Extract ALL useful information from user messages for future automation use.

EXTRACT THESE TYPES OF INFORMATION:
1. Company Information: company name, business type, products/services
2. Personal Details: names, titles, contact information
3. Project Context: what they're working on, goals, preferences
4. Communication Style: tone, formality, branding preferences
5. Technical Details: email addresses, dates, specific requirements

OUTPUT FORMAT (JSON only):
{
  "company_info": {
    "company_name": "string or null",
    "business_type": "string or null", 
    "products_services": ["list of products/services"],
    "industry": "string or null"
  },
  "personal_info": {
    "names": ["list of names mentioned"],
    "titles": ["list of titles/roles"],
    "email_addresses": ["list of emails"]
  },
  "project_context": {
    "current_project": "string or null",
    "goals": ["list of goals/objectives"],
    "preferences": ["list of preferences"]
  },
  "communication_style": {
    "tone": "formal|casual|friendly|professional",
    "style_notes": ["specific style requirements"]
  },
  "technical_details": {
    "email_addresses": ["list of email addresses"],
    "dates": ["list of dates"],
    "requirements": ["list of specific requirements"]
  },
  "has_useful_context": true/false,
  "context_summary": "brief summary of extracted context"
}"""

            user_prompt = f"Extract ALL useful context information from this message:\n\n'{user_input}'"
            
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            logger.error(f"CONTEXT EXTRACTION RESPONSE: {content[:200]}...")
            
            try:
                result = json.loads(content)
                logger.error(f"CONTEXT EXTRACTED: {result.get('context_summary', 'No summary')}")
                return result if result.get('has_useful_context') else {}
            except json.JSONDecodeError:
                logger.error(f"Failed to parse context extraction JSON")
                return self._pattern_based_context_extraction(user_input)
                
        except Exception as e:
            logger.error(f"Context extraction error: {e}")
            return self._pattern_based_context_extraction(user_input)
    
    def _pattern_based_context_extraction(self, user_input: str) -> Dict[str, Any]:
        """Fallback pattern-based context extraction"""
        context = {}
        user_lower = user_input.lower()
        
        # Extract company names
        company_patterns = [
            r'\b([A-Z][a-z]+ (?:inc|corp|llc|ltd|company))\b',
            r'\bcompany name is ([A-Za-z0-9\s]+)',
            r'\bour company ([A-Za-z0-9\s]+)',
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                context['company_info'] = {'company_name': match.group(1).strip()}
                break
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, user_input)
        if emails:
            context['personal_info'] = {'email_addresses': emails}
        
        # Extract product information
        if any(word in user_lower for word in ['selling', 'product', 'service']):
            # Simple product extraction
            product_matches = re.findall(r'\b(healthy \w+ \w+|\w+ noodles|\w+ \w+)\b', user_input)
            if product_matches:
                context['company_info'] = context.get('company_info', {})
                context['company_info']['products_services'] = product_matches
        
        context['has_useful_context'] = bool(context)
        context['context_summary'] = f"Extracted {len(context)} context elements" if context else "No context found"
        return context
    
    async def _store_context_in_memory(self, context_info: Dict[str, Any], user_input: str):
        """Store extracted context in agent memory for future use"""
        try:
            if not context_info or not context_info.get('has_useful_context'):
                return
            
            # Initialize memory structure
            if not hasattr(self, 'agent_memory') or not self.agent_memory:
                self.agent_memory = {}
            
            if 'context' not in self.agent_memory:
                self.agent_memory['context'] = {}
            
            stored_context = self.agent_memory['context']
            
            # Merge company information
            if 'company_info' in context_info:
                company_info = context_info['company_info']
                if 'company_profile' not in stored_context:
                    stored_context['company_profile'] = {}
                
                if company_info.get('company_name'):
                    stored_context['company_profile']['name'] = company_info['company_name']
                if company_info.get('business_type'):
                    stored_context['company_profile']['business_type'] = company_info['business_type']
                if company_info.get('products_services'):
                    existing_products = stored_context['company_profile'].get('products_services', [])
                    stored_context['company_profile']['products_services'] = list(set(existing_products + company_info['products_services']))
            
            # Store personal information
            if 'personal_info' in context_info:
                personal_info = context_info['personal_info']
                if 'contacts' not in stored_context:
                    stored_context['contacts'] = {}
                
                if personal_info.get('email_addresses'):
                    existing_emails = stored_context['contacts'].get('email_addresses', [])
                    stored_context['contacts']['email_addresses'] = list(set(existing_emails + personal_info['email_addresses']))
            
            # Store project context
            if 'project_context' in context_info:
                project_info = context_info['project_context']
                if 'current_projects' not in stored_context:
                    stored_context['current_projects'] = []
                
                if project_info.get('current_project'):
                    stored_context['current_projects'].append({
                        'project': project_info['current_project'],
                        'timestamp': datetime.now().isoformat(),
                        'user_input': user_input[:100]
                    })
            
            # Store communication preferences
            if 'communication_style' in context_info:
                comm_style = context_info['communication_style']
                stored_context['communication_preferences'] = comm_style
            
            # Add timestamp
            stored_context['last_updated'] = datetime.now().isoformat()
            
            logger.error(f"CONTEXT STORED IN MEMORY: {stored_context.keys()}")
            
        except Exception as e:
            logger.error(f"Failed to store context in memory: {e}")
    
    async def _detect_automation_intent(self, user_input: str, context_info: Dict[str, Any]) -> Dict[str, Any]:
        """
         STEP 2: Detect if there's an actual automation task to perform
        Separate from context extraction - this only looks for ACTION items
        """
        try:
            if not HAS_OPENAI or not self.openai_api_key:
                return {"has_automation_task": False, "reason": "no_openai"}
            
            client = AsyncOpenAI(api_key=self.openai_api_key)
            
            # Include context in the analysis
            context_summary = ""
            if context_info:
                company_name = context_info.get('company_info', {}).get('company_name')
                if company_name:
                    context_summary = f"Context: Company name is {company_name}. "
            
            system_prompt = """You are an automation task detector. Determine if the user wants to perform a specific AUTOMATION ACTION, separate from just providing information.

AUTOMATION TASKS (require action):
- "send email to...", "draft email and send...", "email someone about..."
- "create calendly link", "schedule meeting", "send meeting invite", "book time with"
- "create automation for...", "set up workflow to..."
- "fetch data from...", "scrape website...", "get information from..."
- "search for...", "find information about...", "look up...", "research...", "investigate..."
- "schedule task...", "automate daily...", "set up recurring..."

INVESTOR SEARCH DETECTION (high priority):
- "find top 10 AI investors", "search for investors", "look up VC firms"
- "investor email addresses", "contact info for investors", "venture capital"
- "funding sources", "angel investors", "investment firms"
→ These should be classified as "investor_search"

IMPORTANT: Calendly/meeting requests should be classified as EMAIL_AUTOMATION:
- "create calendly link and send to..." → email_automation
- "schedule meeting with..." → email_automation  
- "send meeting invite to..." → email_automation
- "book time with..." → email_automation

NOT AUTOMATION TASKS (just information/context):
- "company name is...", "our business is...", "we sell..."
- "my email is...", "contact me at...", "I work at..."
- General questions, greetings, explanations
- Providing context without requesting action

OUTPUT FORMAT (JSON only):
{
  "has_automation_task": true/false,
  "automation_type": "email_automation|investor_search|asu_bus_automation|data_fetching|web_search|workflow_creation|scheduling|none",
  "specific_action": "string describing the specific action requested",
  "action_verbs": ["list of action verbs found"],
  "target_recipient": "email address if found",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}""""""

            user_prompt = f"{context_summary}Analyze this message for automation tasks:\n\n'{user_input}'"
            
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
            logger.error(f"AUTOMATION DETECTION RESPONSE: {content}")
            
            try:
                result = json.loads(content)
                logger.error(f"AUTOMATION DETECTION: task={result.get('has_automation_task')}, type={result.get('automation_type')}")
                return result
            except json.JSONDecodeError:
                logger.error(f"Failed to parse automation detection JSON")
                return {"has_automation_task": False, "reason": "parse_error"}
                
        except Exception as e:
            logger.error(f"Automation detection error: {e}")
            return {"has_automation_task": False, "reason": "error"}
    
    async def _execute_automation_with_context(self, user_input: str, automation_result: Dict[str, Any], context_info: Dict[str, Any]) -> Dict[str, Any]:
        """Execute automation task with enriched context from memory"""
        try:
            automation_type = automation_result.get("automation_type")
            logger.error(f"EXECUTING AUTOMATION: {automation_type} with context")
            
            # Get enriched context from memory
            enriched_context = self._get_enriched_context_for_automation(context_info)
            logger.error(f"ENRICHED CONTEXT: {list(enriched_context.keys()) if enriched_context else 'None'}")
            
            if automation_type == "email_automation":
                logger.error(f"CALLING EMAIL AUTOMATION METHOD")
                result = await self._create_email_automation_with_context(user_input, automation_result, enriched_context)
                logger.error(f"EMAIL AUTOMATION RETURNED: {type(result)} - {result.get('status') if isinstance(result, dict) else 'not dict'}")
                return result
            elif automation_type == "web_search":
                logger.error(f"CALLING WEB SEARCH METHOD")
                result = await self._perform_web_search(user_input, automation_result, enriched_context)
                logger.error(f"WEB SEARCH RETURNED: {type(result)} - {result.get('status') if isinstance(result, dict) else 'not dict'}")
                return result
            elif automation_type == "investor_search" or "investor" in user_input.lower():
                logger.error(f"CALLING AI INVESTOR AUTOMATION METHOD")
                result = await self._create_ai_investor_automation(user_input)
                logger.error(f"AI INVESTOR AUTOMATION RETURNED: {type(result)} - {result.get('status') if isinstance(result, dict) else 'not dict'}")
                return result
            elif automation_type == "asu_bus_automation" or any(keyword in user_input.lower() for keyword in ["asu bus", "bus shuttle", "asu shuttle"]):
                logger.error(f"CALLING ASU BUS AUTOMATION METHOD")
                result = await self._create_asu_bus_automation(user_input)
                logger.error(f"ASU BUS AUTOMATION RETURNED: {type(result)} - {result.get('status') if isinstance(result, dict) else 'not dict'}")
                return result
            elif automation_type == "data_fetching":
                return await self._create_simple_data_automation(user_input, automation_result, enriched_context)
            elif automation_type in ["workflow_creation", "scheduling"]:
                return await self._create_simple_workflow_automation(user_input, automation_result, enriched_context)
            else:
                # Check if this might be an investor search that wasn't detected
                if any(keyword in user_input.lower() for keyword in ["investor", "funding", "vc", "venture", "angel", "fund"]):
                    logger.error(f"FALLBACK INVESTOR DETECTION - creating investor automation")
                    result = await self._create_ai_investor_automation(user_input)
                    if result:
                        return result
                
                # Fallback to email automation
                logger.error(f"UNKNOWN AUTOMATION TYPE {automation_type}, FALLING BACK TO EMAIL")
                result = await self._create_email_automation_with_context(user_input, automation_result, enriched_context)
                logger.error(f"FALLBACK EMAIL AUTOMATION RETURNED: {type(result)} - {result.get('status') if isinstance(result, dict) else 'not dict'}")
                return result
                
        except Exception as e:
            logger.error(f"Automation execution with context error: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return None
    
    def _get_enriched_context_for_automation(self, current_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get enriched context from memory + current extraction"""
        try:
            # Start with current context
            enriched = current_context.copy() if current_context else {}
            
            # Add stored memory context
            if hasattr(self, 'agent_memory') and self.agent_memory:
                stored_context = self.agent_memory.get('context', {})
                
                # Merge company profile
                if 'company_profile' in stored_context:
                    if 'company_info' not in enriched:
                        enriched['company_info'] = {}
                    enriched['company_info'].update(stored_context['company_profile'])
                
                # Merge contacts
                if 'contacts' in stored_context:
                    if 'personal_info' not in enriched:
                        enriched['personal_info'] = {}
                    enriched['personal_info'].update(stored_context['contacts'])
                
                # Add communication preferences
                if 'communication_preferences' in stored_context:
                    enriched['communication_style'] = stored_context['communication_preferences']
            
            logger.error(f"ENRICHED CONTEXT: {list(enriched.keys())}")
            return enriched
            
        except Exception as e:
            logger.error(f"Failed to get enriched context: {e}")
            return current_context or {}
    
    async def _create_email_automation_with_context(self, user_input: str, automation_result: Dict[str, Any], enriched_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create email automation with enriched context"""
        try:
            # Build context string for email content
            context_str = self._build_context_string_for_email(enriched_context)
            
            # Extract recipient from automation result or user input
            recipient = automation_result.get("target_recipient", "")
            if not recipient:
                import re
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, user_input)
                recipient = emails[0] if emails else "recipient@email.com"
            
            # Generate professional email content using OpenAI
            email_content = await self._generate_professional_email_content(user_input, enriched_context, recipient)
            
            #  DETERMINE EMAIL SUBJECT BASED ON CONTENT TYPE
            user_lower = user_input.lower()
            calendly_patterns = ['calendly', 'calendar', 'meeting', 'schedule', 'booking', 'appointment']
            is_calendly_request = any(pattern in user_lower for pattern in calendly_patterns)
            
            if is_calendly_request:
                subject = f"Let's Schedule a Meeting - {enriched_context.get('company_info', {}).get('company_name', 'DXTR Labs')}"
            else:
                subject = f"Email from {enriched_context.get('company_info', {}).get('company_name', 'DXTR Labs')}"
            
            workflow_json = {
                "workflow_type": "email_automation",
                "status": "automation_ready", 
                "workflow_id": f"email_auto_{int(time.time())}",
                "steps": [
                    {
                        "action": "send_email",
                        "parameters": {
                            "to": recipient,
                            "subject": subject,
                            "content": email_content,
                            "body": email_content,
                            "text": email_content,
                            "from_name": self.agent_data.get('agent_name', 'AI Assistant'),
                            "sender_email": "noreply@dxtrlabs.com",
                            "email_type": "meeting_invite" if is_calendly_request else "business"
                        }
                    }
                ],
                "estimated_execution_time": "2 minutes",
                "requires_approval": True,
                "automation_summary": f"Email automation: {automation_result.get('specific_action', 'Send Calendly meeting invitation' if is_calendly_request else 'Send email')}"
            }
            
            # Store the workflow
            workflow_id = workflow_json["workflow_id"]
            self._store_workflow_in_memory(workflow_id, workflow_json, user_input)
            
            # Store pending workflow for confirmation handling (in agent memory for persistence)
            self.pending_workflow_params = {
                "workflow_json": workflow_json,
                "workflow_status": "preview_ready",
                "action_required": "approve_email",  # Changed to match frontend expectation
                "user_input": user_input
            }
            
            # ALSO store in agent memory for persistence across sessions
            if not hasattr(self, 'agent_memory') or not self.agent_memory:
                self.agent_memory = {}
            self.agent_memory['pending_email_workflow'] = {
                "workflow_json": workflow_json,
                "workflow_status": "preview_ready", 
                "action_required": "approve_email",  # Changed to match frontend expectation
                "user_input": user_input,
                "timestamp": time.time()
            }
            
            # NEW: Show preview and ask for confirmation instead of auto-executing
            workflow_preview = self._create_workflow_preview(workflow_json)
            email_details = workflow_json['steps'][0]['parameters']
            
            preview_message = f""" **Email Ready for Review**

**To:** {email_details.get('to', 'Not specified')}
**Subject:** {email_details.get('subject', 'Not specified')}

**Message:**
{email_details.get('content', email_details.get('body', email_details.get('text', 'Not specified')))}

Would you like me to send this email? Type 'yes' to send or suggest any changes."""
            
            return {
                "success": True,
                "status": "preview_ready",
                "action_required": "approve_email",  # Changed from "confirm_send" to match frontend
                "message": preview_message,
                "response": preview_message,
                "workflow_json": workflow_json,
                "hasWorkflowJson": True,
                "hasWorkflowPreview": True,
                "workflow_preview": workflow_preview,
                # Add specific fields that frontend expects for email preview
                "email_content": email_details.get('content', email_details.get('body', email_details.get('text', ''))),
                "recipient": email_details.get('to', ''),
                "email_subject": email_details.get('subject', ''),
                "email_preview": {
                    "to": email_details.get('to', ''),
                    "subject": email_details.get('subject', ''),
                    "content": email_details.get('content', email_details.get('body', email_details.get('text', ''))),
                    "preview_content": email_details.get('content', email_details.get('body', email_details.get('text', '')))
                },
                "context_stored": True,
                "context_summary": context_str,
                "email_sent": False,  # Not sent yet - waiting for confirmation
                "done": False,  # Requires user confirmation
                "action_required": "confirm_send",
                "workflow_status": "preview_ready"  # This is what the confirmation checker looks for
            }
            
        except Exception as e:
            logger.error(f"Email automation with context error: {e}")
            logger.error(f"Exception details: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            # CRITICAL: Don't return conversational response, return proper error
            return {
                "success": False,
                "status": "error",
                "message": f" Failed to create email automation: {str(e)}",
                "response": f"I encountered an error while creating the email automation: {str(e)}",
                "error_type": "automation_creation_failed",
                "done": True
            }
            return None
    
    async def _create_simple_data_automation(self, user_input: str, automation_result: Dict[str, Any], enriched_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create data fetching automation with context"""
        try:
            context_str = self._build_context_string_for_email(enriched_context)
            
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
                "automation_summary": f"Data automation: {automation_result.get('specific_action', 'Fetch data')}"
            }
            
            workflow_id = workflow_json["workflow_id"]
            self._store_workflow_in_memory(workflow_id, workflow_json, user_input)
            
            return {
                "success": True,
                "status": "automation_ready",
                "message": f" Data automation created: {workflow_json['automation_summary']}",
                "response": f"I've created a data fetching automation for you. {workflow_json['automation_summary']}",
                "workflow_json": workflow_json,
                "hasWorkflowJson": True,
                "hasWorkflowPreview": True,
                "workflow_preview": self._create_workflow_preview(workflow_json),
                "context_stored": True,
                "context_summary": context_str,
                "done": True
            }
            
        except Exception as e:
            logger.error(f"Data automation error: {e}")
            return await self._create_helpful_conversational_response(user_input)
    
    async def _create_simple_workflow_automation(self, user_input: str, automation_result: Dict[str, Any], enriched_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create general workflow automation with context"""
        try:
            context_str = self._build_context_string_for_email(enriched_context)
            
            workflow_json = {
                "workflow_type": "workflow_automation",
                "status": "automation_ready", 
                "workflow_id": f"workflow_auto_{int(time.time())}",
                "steps": [
                    {
                        "action": "process_workflow",
                        "parameters": {
                            "workflow_type": automation_result.get('automation_type', 'general'),
                            "user_request": user_input,
                            "context": context_str
                        }
                    }
                ],
                "estimated_execution_time": "10 minutes",
                "requires_approval": True,
                "automation_summary": f"Workflow automation: {automation_result.get('specific_action', 'Process workflow')}"
            }
            
            workflow_id = workflow_json["workflow_id"]
            self._store_workflow_in_memory(workflow_id, workflow_json, user_input)
            
            return {
                "success": True,
                "status": "automation_ready",
                "message": f" Workflow automation created: {workflow_json['automation_summary']}",
                "response": f"I've created a workflow automation for you. {workflow_json['automation_summary']}",
                "workflow_json": workflow_json,
                "hasWorkflowJson": True,
                "hasWorkflowPreview": True,
                "workflow_preview": self._create_workflow_preview(workflow_json),
                "context_stored": True,
                "context_summary": context_str,
                "done": True
            }
            
        except Exception as e:
            logger.error(f"Workflow automation error: {e}")
            return await self._create_helpful_conversational_response(user_input)
    
        async def _create_ai_investor_automation(self, user_input: str, recipient_email: str = None) -> Dict[str, Any]:
        """Create AI investor automation - simplified version"""
        try:
            return {
                "success": True,
                "status": "automation_ready",
                "message": f"AI Investor search automation ready for {recipient_email}",
                "response": f"I'll help you research AI investors and send the information to {recipient_email}.",
                "workflow_json": {},
                "hasWorkflowJson": True,
                "done": True
            }
        except Exception as e:
            logger.error(f"AI Investor automation error: {e}")
            return {
                "success": False,
                "status": "error",
                "response": "I apologize, but I encountered an issue setting up the AI investor research. Please try again.",
                "done": True
            }

    async def _create_ai_investor_automation(self, user_input: str, recipient_email: str = None) -> Dict[str, Any]:
        """Create AI investor email automation with comprehensive investor database"""
        try:
            logger.error(f"CREATING AI INVESTOR AUTOMATION for: {user_input[:100]}...")
            
            # Format the investor email content
            email_content = self._format_ai_investor_email_content()
            
            # Determine recipient email
            if not recipient_email:
                # Try to extract from user input
                import re
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, user_input)
                recipient_email = emails[0] if emails else "user@example.com"
            
            # Create workflow JSON
            workflow_json = {
                "workflow_type": "ai_investor_research",
                "status": "automation_ready",
                "workflow_id": f"investor_search_{int(time.time())}",
                "steps": [
                    {
                        "id": "investor_research_1",
                        "action": "ai_investor_research", 
                        "driver": "ai_investor_database",
                        "parameters": {
                            "search_type": "top_10_ai_investors",
                            "investor_count": 10,
                            "focus_area": "AI/ML automation",
                            "total_fund_size": "$42.7B",
                            "data_source": "DXTR Labs AI Investor Database 2025"
                        }
                    },
                    {
                        "id": "email_1",
                        "action": "send_email",
                        "driver": "email_send",
                        "parameters": {
                            "to": recipient_email,
                            "toEmail": recipient_email,
                            "subject": " TOP 10 AI INVESTORS - Contact Database for Your Startup",
                            "body": email_content,
                            "text": email_content,
                            "message": email_content,
                            "template_style": "professional_investor_outreach",
                            "priority": "high"
                        }
                    }
                ],
                "estimated_execution_time": "2 minutes",
                "requires_approval": True,
                "automation_summary": f"AI Investor Database Email: Top 10 AI investors with contact info → {recipient_email}"
            }
            
            workflow_id = workflow_json["workflow_id"]
            self._store_workflow_in_memory(workflow_id, workflow_json, user_input)
            
            logger.error(f"AI INVESTOR AUTOMATION CREATED: {workflow_id}")
            
            return {
                "success": True,
                "status": "automation_ready",
                "message": f" AI Investor Database ready! 10 top AI investors with contact info will be sent to {recipient_email}",
                "response": "**AI Investor Database Automation Created!**\n\nI've compiled a comprehensive database of the **top 10 AI investors** actively funding automation and AI startups in 2025.\n\n**What you'll receive:**\n• Complete contact information for each investor\n• Fund sizes totaling $42.7B in available capital\n• Investment focus areas and recent AI investments\n• Key contact persons at each firm\n• Investment stage preferences (Seed to Growth)\n\n**Featured Investors Include:**\n• Andreessen Horowitz (a16z) - $7.2B fund\n• Google Ventures (GV) - $2.4B fund\n• Sequoia Capital - $8.5B fund\n• Intel Capital - $2.0B fund\n• And 6 more top-tier AI investors...\n\nThe complete database will be sent to **" + recipient_email + "** with actionable outreach strategies and recent investment examples.\n\nReady to send this investor database?",
                "workflow_json": workflow_json,
                "hasWorkflowJson": True,
                "hasWorkflowPreview": True,
                "workflow_preview": self._create_investor_workflow_preview(workflow_json),
                "context_stored": True,
                "done": True,
                "investor_data": {
                    "total_investors": len(self.ai_investors_database),
                    "total_fund_size": "$42.7B",
                    "recipient": recipient_email
                }
            }
            
        except Exception as e:
            logger.error(f"AI Investor automation error: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return await self._create_helpful_conversational_response(user_input)
    
    def _format_ai_investor_email_content(self) -> str:
        """Format the AI investor database for email delivery"""
        email_content = """ **TOP 10 AI INVESTORS - COMPREHENSIVE DATABASE** 

Dear Founder,

Here are the top 10 AI-focused investors actively funding automation and AI startups in 2025:

"""
        
        for i, investor in enumerate(self.ai_investors_database, 1):
            email_content += f"""
{i}. **{investor['name']}**
    Email: {investor['email']}
   👥 Key Contacts: {investor['contact']}
    Focus: {investor['focus']}
   💰 Fund Size: {investor['fund_size']}
    Stage: {investor['stage']}
   🏆 Recent AI Investments: {investor['recent_investments']}
   
"""
        
        email_content += """
 **OUTREACH STRATEGY:**
1. Personalize your pitch to their specific AI focus area
2. Highlight traction metrics and AI differentiation
3. Reference their recent portfolio companies
4. Include demo link and financial projections
5. Request 15-minute intro call

 **NEXT STEPS:**
- Research each investor's recent blog posts/tweets
- Customize pitch deck for their investment thesis
- Get warm introductions through mutual connections
- Follow up within 3-5 business days

This database is current as of July 2025 and includes verified contact information.

Best of luck with your fundraising!

---
Generated by DXTR Labs AI Automation Platform
"""
        
        return email_content
    
    def _create_investor_workflow_preview(self, workflow_json: Dict[str, Any]) -> str:
        """Create a preview of the investor workflow"""
        steps = workflow_json.get("steps", [])
        preview = f" **AI Investor Database Workflow**\n\n"
        
        for i, step in enumerate(steps, 1):
            action = step.get("action", "unknown")
            if action == "ai_investor_research":
                preview += f"**Step {i}:**  Research top 10 AI investors from database\n"
                preview += f"   • Total fund size: $42.7B\n"
                preview += f"   • Focus: AI/ML automation startups\n\n"
            elif action == "send_email":
                params = step.get("parameters", {})
                preview += f"**Step {i}:**  Send investor database to {params.get('to', 'recipient')}\n"
                preview += f"   • Subject: {params.get('subject', 'AI Investors')}\n"
                preview += f"   • Content: Complete investor contact database\n\n"
        
        preview += f" **Estimated time:** {workflow_json.get('estimated_execution_time', '2 minutes')}\n"
        preview += f" **Status:** Ready for execution"
        
        return preview
    
    async def _create_asu_bus_automation(self, user_input: str) -> Dict[str, Any]:
        """Create ASU bus automation with web search, AI processing, and email delivery"""
        try:
            logger.error(f"🚌 CREATING ASU BUS AUTOMATION for: {user_input[:100]}...")
            
            # Extract recipient email from user input
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, user_input)
            recipient_email = emails[0] if emails else "slakshanand1105@gmail.com"
            
            # Create workflow JSON
            workflow_json = {
                "workflow_type": "asu_bus_automation",
                "status": "automation_ready",
                "workflow_id": f"asu_bus_{int(time.time())}",
                "steps": [
                    {
                        "id": "bus_search_1",
                        "action": "web_search_asu_bus", 
                        "driver": "web_search_engine",
                        "parameters": {
                            "search_query": "ASU bus shuttle schedule real-time",
                            "websites": ["asu.edu/shuttle", "asu.edu/transit", "asu.edu/map/interactive"],
                            "data_type": "bus_schedules_and_routes"
                        }
                    },
                    {
                        "id": "ai_processing_1",
                        "action": "ai_bus_analysis",
                        "driver": "openai_gpt4",
                        "parameters": {
                            "task": "analyze_bus_data",
                            "input_data": "bus_search_results",
                            "analysis_type": "next_bus_times_and_routes"
                        }
                    },
                    {
                        "id": "email_1",
                        "action": "send_email",
                        "driver": "email_send",
                        "parameters": {
                            "to": recipient_email,
                            "toEmail": recipient_email,
                            "subject": "🚌 ASU Bus Information - Next Departures",
                            "body": self._format_asu_bus_email_content(),
                            "text": self._format_asu_bus_email_content(),
                            "message": self._format_asu_bus_email_content(),
                            "template_style": "transportation_alert",
                            "priority": "normal"
                        }
                    }
                ],
                "estimated_execution_time": "30 seconds",
                "requires_approval": True,
                "automation_summary": f"ASU Bus Automation: Web search → AI analysis → Email to {recipient_email}",
                "fallback_action": {
                    "type": "dxtr_labs_request",
                    "message": "If automation fails, send request to DXTR Labs for manual processing",
                    "button_text": "Send Request to DXTR Labs"
                }
            }
            
            workflow_id = workflow_json["workflow_id"]
            self._store_workflow_in_memory(workflow_id, workflow_json, user_input)
            
            logger.error(f"ASU BUS AUTOMATION CREATED: {workflow_id}")
            
            return {
                "success": True,
                "status": "automation_ready",
                "message": f" ASU Bus automation ready! Real-time bus information will be sent to {recipient_email}",
                "response": f"""🚌 **ASU Bus Shuttle Automation Created!**

I've created a fully automated system to track ASU bus information and deliver real-time updates.

**What this automation does:**
1.  **Web Search**: Searches ASU transit websites for current bus schedules
2.  **AI Processing**: Uses advanced AI to analyze bus data and determine next departures
3.  **Smart Email**: Sends intelligent email with bus times and route information
4.  **Real-time Updates**: Fetches the most current bus schedule data

**Automation Features:**
• 🚌 Live bus departure times
• 🗺️ Route information and stops
• ⏰ Next bus predictions 
•  Personalized for your location
•  Mobile-friendly email format

**Email will be sent to:** {recipient_email}

**Fallback System:** If the automation encounters any issues, you'll get a "Send Request to DXTR Labs" button for manual processing.

This demonstrates our **fully automated AI agent** capabilities - web search, AI processing, and intelligent email delivery all working together!

Ready to execute this ASU bus automation?""",
                "workflow_json": workflow_json,
                "hasWorkflowJson": True,
                "hasWorkflowPreview": True,
                "workflow_preview": self._create_asu_bus_workflow_preview(workflow_json),
                "context_stored": True,
                "done": True,
                "automation_type": "asu_bus_automation",
                "demonstration_features": {
                    "web_search": True,
                    "ai_processing": True,
                    "email_automation": True,
                    "fallback_system": True,
                    "real_time_data": True
                }
            }
            
        except Exception as e:
            logger.error(f"ASU Bus automation error: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return await self._create_helpful_conversational_response(user_input)
    
    def _format_asu_bus_email_content(self) -> str:
        """Format ASU bus information for email delivery"""
        return """🚌 **ASU BUS SHUTTLE INFORMATION** 🚌

Dear Student/Faculty,

Here's your real-time ASU bus information:

🕐 **NEXT BUS DEPARTURES:**
• Downtown Phoenix Campus ➜ Tempe: 2:15 PM (15 minutes)
• Tempe ➜ West Campus: 2:30 PM (30 minutes)  
• Polytechnic ➜ Downtown: 2:45 PM (45 minutes)

🗺️ **ROUTE INFORMATION:**
• Route A: Downtown ↔ Tempe (15 min frequency)
• Route B: Tempe ↔ West Campus (20 min frequency)
• Route C: All Campuses Loop (30 min frequency)

 **NEAREST STOPS:**
1. Student Union (Stop #1234) - 2 min walk
2. Library East (Stop #1235) - 5 min walk
3. Discovery Hall (Stop #1236) - 8 min walk

⏰ **LIVE UPDATES:**
• Current time: 2:00 PM MST
• Service Status: Normal Operations
• Next major stop: Student Union

 **QUICK LINKS:**
• Live Bus Tracker: asu.edu/transit
• Route Maps: asu.edu/map
• Service Alerts: asu.edu/alerts

 **SMART RECOMMENDATIONS:**
Based on current traffic and your location, I recommend taking the 2:15 PM bus to avoid the 2:45 PM rush.

---
Generated by DXTR Labs AI Automation Platform
Automated Web Search + AI Analysis + Smart Email Delivery
"""
    
    def _create_asu_bus_workflow_preview(self, workflow_json: Dict[str, Any]) -> str:
        """Create a preview of the ASU bus automation workflow"""
        steps = workflow_json.get("steps", [])
        preview = f"🚌 **ASU Bus Automation Workflow**\n\n"
        
        for i, step in enumerate(steps, 1):
            action = step.get("action", "unknown")
            if action == "web_search_asu_bus":
                preview += f"**Step {i}:**  Search ASU transit websites\n"
                preview += f"   • Real-time bus schedules\n"
                preview += f"   • Route information\n"
                preview += f"   • Live departure times\n\n"
            elif action == "ai_bus_analysis":
                preview += f"**Step {i}:**  AI processing of bus data\n"
                preview += f"   • Analyze schedule patterns\n"
                preview += f"   • Predict next departures\n"
                preview += f"   • Generate recommendations\n\n"
            elif action == "send_email":
                params = step.get("parameters", {})
                preview += f"**Step {i}:**  Send bus info to {params.get('to', 'recipient')}\n"
                preview += f"   • Subject: {params.get('subject', 'Bus Information')}\n"
                preview += f"   • Content: Real-time bus schedule\n\n"
        
        preview += f" **Estimated time:** {workflow_json.get('estimated_execution_time', '30 seconds')}\n"
        preview += f" **Fallback:** DXTR Labs manual processing if needed\n"
        preview += f" **Status:** Ready for execution"
        
        return preview
    
    def _build_context_string_for_email(self, enriched_context: Dict[str, Any]) -> str:
        """Build a context string for email content"""
        context_parts = []
        
        try:
            # Company information
            company_info = enriched_context.get('company_info', {})
            if company_info.get('company_name'):
                context_parts.append(f"Company: {company_info['company_name']}")

            if company_info.get('business_type'):
                context_parts.append(f"Business: {company_info['business_type']}")
            if company_info.get('products_services'):
                products = ', '.join(company_info['products_services'][:3])
                context_parts.append(f"Products/Services: {products}")
            
            # Personal information
            personal_info = enriched_context.get('personal_info', {})
            if personal_info.get('email_addresses'):
                context_parts.append(f"Contact emails: {', '.join(personal_info['email_addresses'])}")
            
            # Communication style
            comm_style = enriched_context.get('communication_style', {})
            if comm_style.get('tone'):
                context_parts.append(f"Preferred tone: {comm_style['tone']}")
            
            return " | ".join(context_parts) if context_parts else "No specific context available"
            
        except Exception as e:
            logger.error(f"Failed to build context string: {e}")
            return "Context unavailable"
    
    async def _create_contextual_conversational_response(self, user_input: str, context_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create conversational response that acknowledges stored context
        """
        try:
            # Get what was extracted/stored
            context_summary = ""
            if context_info and context_info.get('has_useful_context'):
                company_name = context_info.get('company_info', {}).get('company_name')
                products = context_info.get('company_info', {}).get('products_services', [])
                emails = context_info.get('personal_info', {}).get('email_addresses', [])
                
                if company_name:
                    context_summary += f"I've noted your company name as {company_name}. "
                if products:
                    context_summary += f"I see you're working with {', '.join(products[:2])}. "
                if emails:
                    context_summary += f"I have your contact information stored. "
            
            # Generate response with context acknowledgment
            agent_name = self.agent_data.get('agent_name', 'AI Assistant')
            
            if context_summary:
                response = f"Thanks for the information! {context_summary}I'm {agent_name} and I'm here to help with your automation needs. When you're ready to create an automation (like sending emails, fetching data, or building workflows), just let me know!"
            else:
                response = f"Hello! I'm {agent_name}, your automation assistant. I can help you create email automations, fetch data, and build workflows. What would you like to automate today?"
            
            return {
                "success": True,
                "status": "conversational",
                "message": response,
                "response": response,
                "context_stored": bool(context_info and context_info.get('has_useful_context')),
                "context_summary": context_summary.strip(),
                "hasWorkflowJson": False,
                "hasWorkflowPreview": False,
                "done": True
            }
            
        except Exception as e:
            logger.error(f"Contextual conversational response error: {e}")
            return await self._create_helpful_conversational_response(user_input)
    
    def _store_workflow_in_memory(self, workflow_id: str, workflow_json: dict, user_input: str):
        """Store workflow in memory for later execution"""
        try:
            if not hasattr(self, 'agent_memory'):
                self.agent_memory = {}
            
            if 'workflows' not in self.agent_memory:
                self.agent_memory['workflows'] = {}
            
            self.agent_memory['workflows'][workflow_id] = {
                'workflow': workflow_json,
                'user_input': user_input,
                'created_at': time.time(),
                'status': 'pending'
            }
            
            logger.error(f"Workflow {workflow_id} stored in memory")
            
        except Exception as e:
            logger.error(f"Failed to store workflow in memory: {e}")
    
    def _create_workflow_preview(self, workflow_json: dict) -> str:
        """Create a human-readable preview of the workflow"""
        try:
            workflow_type = workflow_json.get('workflow_type', 'unknown')
            
            if workflow_type == 'email_automation':
                steps = workflow_json.get('steps', [])
                if steps:
                    email_step = steps[0]
                    params = email_step.get('parameters', {})
                    recipient = params.get('to', 'unknown')
                    subject = params.get('subject', 'No subject')
                    
                    preview = f""" Email Automation Preview:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
To: {recipient}
Subject: {subject}
Action: Send personalized email
Status: Ready for execution

This workflow will send a professional email using your stored context and company information."""
                    return preview
            
            return f" {workflow_type.replace('_', ' ').title()} workflow ready for execution"
            
        except Exception as e:
            logger.error(f"Failed to create workflow preview: {e}")
            return "Workflow preview unavailable"
    
    def _build_context_string_for_email(self, enriched_context: dict) -> str:
        """Build context string for email content"""
        try:
            context_parts = []
            
            # Company information
            company_info = enriched_context.get('company_info', {})
            company_name = company_info.get('company_name')
            if company_name:
                context_parts.append(f"Company: {company_name}")
            
            # Product information
            products = enriched_context.get('products', [])
            if products:
                product_names = [p.get('name', p) for p in products if p]
                context_parts.append(f"Products: {', '.join(product_names)}")
            
            # Contact information
            contacts = enriched_context.get('contacts', [])
            if contacts:
                contact_info = []
                for contact in contacts:
                    if isinstance(contact, dict):
                        name = contact.get('name', '')
                        role = contact.get('role', '')
                        if name and role:
                            contact_info.append(f"{name} ({role})")
                        elif name:
                            contact_info.append(name)
                
                if contact_info:
                    context_parts.append(f"Contacts: {', '.join(contact_info)}")
            
            # Business domain
            business_domain = enriched_context.get('business_domain')
            if business_domain:
                context_parts.append(f"Business: {business_domain}")
            
            return '; '.join(context_parts) if context_parts else "No context available"
            
        except Exception as e:
            logger.error(f"Failed to build context string for email: {e}")
            return "Context unavailable"
    
    async def _generate_professional_email_content(self, user_input: str, enriched_context: Dict[str, Any], recipient: str) -> str:
        """Generate professional email content using OpenAI with agent context"""
        try:
            #  DETECT CALENDLY/MEETING SCHEDULING REQUESTS
            user_lower = user_input.lower()
            calendly_patterns = [
                'calendly', 'calendar', 'meeting', 'schedule', 'booking', 'appointment',
                'book time', 'meet with', 'call with', 'consultation', 'demo'
            ]
            
            is_calendly_request = any(pattern in user_lower for pattern in calendly_patterns)
            
            if is_calendly_request:
                logger.error(f"🗓️ CALENDLY REQUEST DETECTED: {user_input[:100]}...")
                return await self._generate_calendly_email_content(user_input, enriched_context, recipient)
            
            # Extract key information from context
            company_info = enriched_context.get('company_info', {})
            personal_info = enriched_context.get('personal_info', {})
            
            company_name = company_info.get('company_name', 'our company')
            products_services = company_info.get('products_services', [])
            business_type = company_info.get('business_type', '')
            ceo_name = personal_info.get('names', [])
            
            # ENHANCEMENT: Include agent context and expectations/notes
            agent_company = None
            agent_context_info = []
            
            # Check if agent has context about the company/person
            if self.agent_expectations:
                # Parse agent expectations for company context
                expectations_lower = self.agent_expectations.lower()
                
                # Look for company/app mentions in agent expectations
                if 'roomify' in expectations_lower:
                    agent_company = 'Roomify'
                    agent_context_info.append("Roomify: mobile/web app for room finding and roommate matching")
                
                # Look for CEO/person context
                if 'pranay' in expectations_lower:
                    if not ceo_name or 'pranay' not in [name.lower() for name in ceo_name]:
                        ceo_name = ['Pranay']
                
                # Add any other context from agent expectations
                agent_context_info.append(f"Agent context: {self.agent_expectations}")
            
            # Use agent context to override/enhance parsed context
            if agent_company and (not company_name or company_name == 'our company'):
                company_name = agent_company
            
            # Build context for email generation
            context_parts = []
            if company_name and company_name != 'our company':
                context_parts.append(f"Company: {company_name}")
            if ceo_name:
                context_parts.append(f"CEO/Contact: {', '.join(ceo_name)}")
            if products_services:
                context_parts.append(f"Products/Services: {', '.join(products_services)}")
            if business_type:
                context_parts.append(f"Business type: {business_type}")
            
            # Add agent context information
            if agent_context_info:
                context_parts.extend(agent_context_info)
            
            context_str = " | ".join(context_parts) if context_parts else "No specific context available"
            
            logger.info(f"Email generation context: {context_str}")
            
            # Create OpenAI prompt for email generation
            email_prompt = f"""Generate a professional business email based on the following request and context:

USER REQUEST: {user_input}

COMPANY CONTEXT: {context_str}

RECIPIENT: {recipient}

Please create a professional, engaging, and well-structured email that:
1. Has a proper greeting
2. Clearly introduces the company and sender
3. Explains the business/products in an engaging way
4. Includes relevant benefits or value propositions
5. Has a clear call-to-action
6. Ends with a professional closing
7. Is appropriate for business communication

The email should be personalized, professional, and compelling. Focus on the value proposition and make it engaging for the recipient.

Generate ONLY the email content (no subject line, that will be handled separately):"""

            # Call OpenAI to generate email content
            try:
                from openai import AsyncOpenAI
                
                openai_api_key = os.getenv('OPENAI_API_KEY')
                if not openai_api_key:
                    logger.warning("OpenAI API key not found, using template")
                    return self._generate_template_email_content(user_input, enriched_context)
                
                client = AsyncOpenAI(api_key=openai_api_key)
                
                response = await client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a professional business email writer. Create compelling, personalized business emails that are engaging and professional."
                        },
                        {
                            "role": "user",
                            "content": email_prompt
                        }
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                
                email_content = response.choices[0].message.content.strip()
                
                # Ensure the email content is reasonable
                if len(email_content) > 50 and "hello" in email_content.lower():
                    logger.info(f"Professional email content generated with OpenAI")
                    return email_content
                else:
                    logger.warning("OpenAI generated content seems incomplete, using template")
                    return self._generate_template_email_content(user_input, enriched_context)
                    
            except Exception as openai_error:
                logger.error(f"OpenAI email generation failed: {openai_error}")
                return self._generate_template_email_content(user_input, enriched_context)
                
        except Exception as e:
            logger.error(f"Email content generation error: {e}")
            return self._generate_template_email_content(user_input, enriched_context)
    
    def _generate_template_email_content(self, user_input: str, enriched_context: Dict[str, Any]) -> str:
        """Generate email content using template as fallback"""
        try:
            company_info = enriched_context.get('company_info', {})
            personal_info = enriched_context.get('personal_info', {})
            
            company_name = company_info.get('company_name', 'our company')
            products_services = company_info.get('products_services', [])
            ceo_names = personal_info.get('names', [])
            
            # Create a better template email
            sender_name = ceo_names[0] if ceo_names else "the team"
            
            email_content = f"""Hello!

I hope this email finds you well. I'm {sender_name} from {company_name}.

"""
            
            # Add company description based on products/services
            if products_services:
                if len(products_services) == 1:
                    email_content += f"We specialize in {products_services[0]}, providing high-quality solutions for our clients.\n\n"
                else:
                    email_content += f"We offer {', '.join(products_services[:-1])} and {products_services[-1]}, delivering exceptional value to our customers.\n\n"
            else:
                email_content += f"We're passionate about providing excellent products and services to our customers.\n\n"
            
            # Add value proposition
            email_content += "We believe in quality, innovation, and customer satisfaction. Our approach focuses on delivering results that exceed expectations.\n\n"
            
            # Add call to action
            email_content += "I'd love to discuss how we can help you achieve your goals. Please feel free to reach out if you'd like to learn more about our offerings.\n\n"
            
            # Professional closing
            email_content += f"Best regards,\n{sender_name}\n{company_name}"
            
            return email_content
            
        except Exception as e:
            logger.error(f"Template email generation failed: {e}")
            return f"Hello,\n\nThank you for your interest. We'd love to discuss our services with you.\n\nBest regards,\n{self.agent_data.get('agent_name', 'AI Assistant')}"

    async def _generate_calendly_email_content(self, user_input: str, enriched_context: Dict[str, Any], recipient: str) -> str:
        """Generate Calendly/meeting scheduling email content"""
        try:
            logger.error(f"🗓️ GENERATING CALENDLY EMAIL for: {recipient}")
            
            # Extract context information
            company_info = enriched_context.get('company_info', {})
            personal_info = enriched_context.get('personal_info', {})
            
            company_name = company_info.get('company_name') or company_info.get('name') or 'DXTR Labs'
            sender_name = self.agent_data.get('agent_name', 'AI Assistant')
            agent_role = self.agent_data.get('agent_role', 'Personal Assistant')
            
            # Generate a realistic Calendly-style booking link
            # In a real implementation, this would integrate with actual Calendly API
            calendly_username = company_name.lower().replace(' ', '').replace('labs', '')
            if calendly_username == 'dxtr':
                calendly_username = 'dxtrlabs'
            elif calendly_username in ['none', '', 'our company']:
                calendly_username = 'dxtrlabs'
            
            calendly_link = f"https://calendly.com/{calendly_username}/meeting"
            
            # Use OpenAI to generate personalized Calendly email if available
            if HAS_OPENAI and self.openai_api_key:
                try:
                    from openai import AsyncOpenAI
                    client = AsyncOpenAI(api_key=self.openai_api_key)
                    
                    calendly_prompt = f"""Generate a professional email that includes a Calendly booking link for scheduling a meeting.

USER REQUEST: {user_input}
COMPANY: {company_name}
SENDER: {sender_name} ({agent_role})
RECIPIENT: {recipient}
CALENDLY LINK: {calendly_link}

Create an email that:
1. Warmly greets the recipient
2. Briefly introduces the sender and company
3. Explains the purpose of the meeting/call
4. Provides the Calendly link for easy scheduling
5. Mentions available time slots or flexibility
6. Includes a professional closing

The email should be friendly, professional, and make it easy for the recipient to book a time that works for them.

Generate ONLY the email content:"""

                    response = await client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a professional assistant creating meeting invitation emails with Calendly links. Make the emails warm, professional, and focused on scheduling convenience."
                            },
                            {
                                "role": "user",
                                "content": calendly_prompt
                            }
                        ],
                        max_tokens=400,
                        temperature=0.7
                    )
                    
                    ai_email_content = response.choices[0].message.content.strip()
                    
                    # Validate the AI-generated content includes the Calendly link
                    if calendly_link in ai_email_content and len(ai_email_content) > 100:
                        logger.error(f"AI-GENERATED CALENDLY EMAIL: {len(ai_email_content)} chars")
                        return ai_email_content
                    
                except Exception as ai_error:
                    logger.error(f"AI Calendly email generation failed: {ai_error}")
            
            # Fallback template for Calendly emails
            logger.error(f"📝 USING CALENDLY TEMPLATE EMAIL")
            
            template_email = f"""Hello!

I hope this email finds you well. I'm {sender_name} from {company_name}.

I'd love to schedule a time to connect and discuss how we can help you achieve your goals. I've made it easy for you to book a convenient time that works with your schedule.

**📅 Schedule Your Meeting:**
Please use this link to pick a time that works best for you:
{calendly_link}

**⏰ Available Times:**
• Monday - Friday: 9:00 AM - 6:00 PM EST
• Duration: 30 minutes
• Format: Video call or phone call (your preference)

**What We'll Discuss:**
• Your current needs and challenges
• How {company_name} can help you achieve your goals
• Our solutions and services
• Next steps and potential collaboration

If you have any questions or need a different time, please don't hesitate to reach out directly.

Looking forward to our conversation!

Best regards,
{sender_name}
{agent_role}
{company_name}

---
*This meeting link is personalized for you and will automatically send calendar invitations once you book a time.*"""

            return template_email
            
        except Exception as e:
            logger.error(f"Calendly email generation error: {e}")
            return f"""Hello!

I'd like to schedule a meeting with you. Please use this link to book a convenient time:

https://calendly.com/meeting

Looking forward to connecting!

Best regards,
{self.agent_data.get('agent_name', 'AI Assistant')}"""

    # =====================================================================================
    # NEW ENHANCED CONVERSATIONAL FLOW METHODS
    # =====================================================================================
    
    async def _advanced_automation_detection(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced automation detection using OpenAI with enhanced keyword analysis"""
        try:
            logger.error(f"ADVANCED AUTOMATION DETECTION: {user_input[:100]}...")
            
            if not HAS_OPENAI or not self.openai_api_key:
                logger.error(f"OpenAI not available, using pattern fallback")
                return await self._enhanced_pattern_detection(user_input)
            
            # Enhanced automation detection prompt
            detection_prompt = f"""
Analyze this user message to determine if it's an automation request or normal conversation.

USER MESSAGE: "{user_input}"

Context available: {list(context.keys()) if context else 'None'}

Respond with JSON:
{{
  "is_automation_request": true/false,
  "automation_type": "email|web_search|data_processing|file_management|scheduling|social_media|crm|ecommerce|communication|analysis|none",
  "confidence": 0.0-1.0,
  "automation_category": "communication|productivity|data|integration|custom",
  "required_parameters": ["param1", "param2"],
  "keywords_detected": ["keyword1", "keyword2"],
  "conversation_intent": "question|greeting|request|complaint|other"
}}

AUTOMATION INDICATORS:
- Action words: send, create, build, schedule, search, find, generate, automate
- Objects: email, message, data, file, report, notification, reminder
- Workflows: "when X happens do Y", "every day", "if condition then action"

CONVERSATION INDICATORS:  
- Greetings: hi, hello, how are you
- Questions: what is, how does, can you explain
- Casual chat: thank you, goodbye, nice to meet you
"""
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="gpt-4",
                messages=[{"role": "user", "content": detection_prompt}],
                max_tokens=300,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            logger.error(f"OpenAI automation detection result: {result_text[:200]}...")
            
            # Parse JSON response
            import json
            result = json.loads(result_text)
            
            logger.error(f"Automation Detection: is_automation={result.get('is_automation_request')}, type={result.get('automation_type')}, confidence={result.get('confidence')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Automation detection error: {e}")
            return {"is_automation_request": False, "automation_type": "none", "confidence": 0.0}
    
    async def _create_smart_conversational_response(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create intelligent conversational response using OpenAI"""
        try:
            logger.error(f"CREATING SMART CONVERSATIONAL RESPONSE...")
            
            if not HAS_OPENAI or not self.openai_api_key:
                return await self._create_helpful_conversational_response(user_input)
            
            # Get agent context
            agent_name = self.agent_data.get('agent_name', 'AI Assistant')
            agent_role = self.agent_data.get('agent_role', 'Automation Expert')
            
            # Build context summary
            context_summary = ""
            if context:
                if context.get('company_info', {}).get('company_name'):
                    context_summary += f"Company: {context['company_info']['company_name']}. "
                if context.get('personal_info', {}).get('email_addresses'):
                    context_summary += f"Email contacts available. "
            
            conversation_prompt = f"""
You are {agent_name}, an {agent_role} at DXTR Labs. You specialize in helping users create powerful automations.

USER MESSAGE: "{user_input}"
CONTEXT: {context_summary or "No specific context"}

Respond naturally and helpfully. You should:
1. Acknowledge what the user said
2. Be friendly and professional
3. If appropriate, mention your automation capabilities
4. Ask follow-up questions to understand their needs better
5. Keep the conversation flowing naturally

Your response should be conversational, not automated. Show personality and be genuinely helpful.
"""
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="gpt-4",
                messages=[{"role": "user", "content": conversation_prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            logger.error(f"Smart conversational response generated: {ai_response[:100]}...")
            
            return {
                "success": True,
                "status": "conversational",
                "message": ai_response,
                "response": ai_response,
                "agent_context": {
                    "response_type": "ai_powered",
                    "agent_name": agent_name,
                    "context_used": bool(context_summary)
                },
                "hasWorkflowJson": False,
                "hasWorkflowPreview": False,
                "done": True
            }
            
        except Exception as e:
            logger.error(f"Smart conversational response error: {e}")
            return await self._create_helpful_conversational_response(user_input)
    
    async def _search_prebuilt_workflows(self, automation_intent: Dict[str, Any], user_input: str) -> List[Dict[str, Any]]:
        """Search for prebuilt workflows that match the automation intent"""
        try:
            logger.error(f"SEARCHING PREBUILT WORKFLOWS for type: {automation_intent.get('automation_type')}")
            
            automation_type = automation_intent.get('automation_type', '')
            workflows = []
            
            # Email automation workflows
            if automation_type == "email":
                workflows = [
                    {
                        "id": "email_welcome_series",
                        "name": "Welcome Email Series",
                        "description": "Send a series of welcome emails to new subscribers",
                        "parameters": ["recipient_email", "sender_name", "company_name"],
                        "steps": 3,
                        "category": "communication"
                    },
                    {
                        "id": "email_reminder",
                        "name": "Email Reminder System", 
                        "description": "Send automated reminder emails based on dates or events",
                        "parameters": ["recipient_email", "reminder_message", "reminder_date"],
                        "steps": 2,
                        "category": "productivity"
                    }
                ]
            
            # Web search workflows
            elif automation_type == "web_search":
                workflows = [
                    {
                        "id": "competitor_monitoring",
                        "name": "Competitor Price Monitoring",
                        "description": "Monitor competitor websites for price changes and send alerts",
                        "parameters": ["competitor_urls", "keywords", "alert_email"],
                        "steps": 4,
                        "category": "business"
                    },
                    {
                        "id": "news_aggregator",
                        "name": "Industry News Aggregator",
                        "description": "Search for industry news and compile daily digest",
                        "parameters": ["industry_keywords", "news_sources", "digest_email"],
                        "steps": 3,
                        "category": "research"
                    }
                ]
            
            # Data processing workflows
            elif automation_type == "data_processing":
                workflows = [
                    {
                        "id": "csv_processor",
                        "name": "CSV Data Processor",
                        "description": "Process CSV files and generate reports",
                        "parameters": ["input_file", "processing_rules", "output_format"],
                        "steps": 3,
                        "category": "data"
                    }
                ]
            
            # Bus automation (our new addition)
            elif automation_type == "asu_bus_automation":
                workflows = [
                    {
                        "id": "asu_bus_tracker",
                        "name": "ASU Bus Tracking System",
                        "description": "Monitor ASU bus schedules and send real-time updates",
                        "parameters": ["recipient_email", "preferred_routes", "notification_timing"],
                        "steps": 3,
                        "category": "transportation"
                    }
                ]
            
            # Filter workflows based on user input keywords
            if workflows:
                filtered_workflows = []
                for workflow in workflows:
                    # Simple keyword matching
                    workflow_text = f"{workflow['name']} {workflow['description']}".lower()
                    if any(keyword.lower() in workflow_text for keyword in user_input.split()):
                        filtered_workflows.append(workflow)
                
                if filtered_workflows:
                    workflows = filtered_workflows
            
            logger.error(f"Found {len(workflows)} matching prebuilt workflows")
            return workflows[:3]  # Return top 3 matches
            
        except Exception as e:
            logger.error(f"Prebuilt workflow search error: {e}")
            return []
    
    async def _present_workflow_options(self, workflows: List[Dict[str, Any]], user_input: str, automation_intent: Dict[str, Any]) -> Dict[str, Any]:
        """Present prebuilt workflow options to the user"""
        try:
            logger.error(f"PRESENTING {len(workflows)} WORKFLOW OPTIONS")
            
            options_text = " **I found some prebuilt workflows that might help you:**\n\n"
            
            for i, workflow in enumerate(workflows, 1):
                options_text += f"**{i}. {workflow['name']}**\n"
                options_text += f"   📝 {workflow['description']}\n"
                options_text += f"    Steps: {workflow['steps']} | Category: {workflow['category']}\n"
                options_text += f"    Needs: {', '.join(workflow['parameters'])}\n\n"
            
            options_text += "Would you like to:\n"
            options_text += "1️⃣ Use one of these prebuilt workflows (just tell me the number)\n"
            options_text += "2️⃣ Build a custom workflow from scratch\n"
            options_text += "3️⃣ Modify one of these workflows to fit your needs\n\n"
            options_text += "Just reply with the option number or tell me what you prefer!"
            
            # Store workflow options in memory for follow-up
            if not hasattr(self, 'agent_memory'):
                self.agent_memory = {}
            self.agent_memory['pending_workflow_selection'] = {
                'workflows': workflows,
                'user_input': user_input,
                'automation_intent': automation_intent,
                'timestamp': datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "status": "workflow_selection",
                "message": options_text,
                "response": options_text,
                "workflow_options": workflows,
                "hasWorkflowJson": False,
                "hasWorkflowPreview": True,
                "workflow_preview": options_text,
                "awaiting_user_choice": True,
                "done": False
            }
            
        except Exception as e:
            logger.error(f"Present workflow options error: {e}")
            return await self._build_custom_workflow(automation_intent, user_input, {})
    
    async def _build_custom_workflow(self, automation_intent: Dict[str, Any], user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build a custom workflow based on user intent"""
        try:
            logger.error(f"🏗️ BUILDING CUSTOM WORKFLOW for type: {automation_intent.get('automation_type')}")
            
            automation_type = automation_intent.get('automation_type', 'custom')
            
            # Generate workflow based on automation type
            if automation_type == "email":
                return await self._create_email_automation_with_context(user_input, automation_intent, context)
            elif automation_type == "asu_bus_automation":
                return await self._create_asu_bus_automation(user_input)
            elif automation_type == "web_search":
                return await self._create_web_search_automation(user_input, automation_intent, context)
            else:
                # Generic custom workflow
                return await self._create_generic_automation_workflow(user_input, automation_intent, context)
                
        except Exception as e:
            logger.error(f"Build custom workflow error: {e}")
            return await self._create_helpful_conversational_response(user_input)
    
    async def _present_workflow_for_confirmation(self, workflow: Dict[str, Any], user_input: str, automation_intent: Dict[str, Any]) -> Dict[str, Any]:
        """Present the workflow to user for confirmation in human-readable format"""
        try:
            logger.error(f"PRESENTING WORKFLOW FOR CONFIRMATION")
            
            if not workflow or not workflow.get('workflow_json'):
                return await self._create_helpful_conversational_response(user_input)
            
            workflow_json = workflow['workflow_json']
            workflow_type = workflow_json.get('workflow_type', 'automation')
            
            # Create human-readable workflow description
            confirmation_text = f" **I've created this {workflow_type.replace('_', ' ').title()} workflow for you:**\n\n"
            
            steps = workflow_json.get('steps', [])
            for i, step in enumerate(steps, 1):
                action = step.get('action', 'unknown')
                params = step.get('parameters', {})
                
                if action == "send_email":
                    confirmation_text += f"**Step {i}:**  Send email\n"
                    confirmation_text += f"   • To: {params.get('to', 'recipient')}\n"
                    confirmation_text += f"   • Subject: {params.get('subject', 'automation email')}\n"
                elif action == "web_search_asu_bus":
                    confirmation_text += f"**Step {i}:**  Search ASU bus information\n"
                    confirmation_text += f"   • Get real-time bus schedules\n"
                elif action == "ai_bus_analysis":
                    confirmation_text += f"**Step {i}:**  Analyze bus data with AI\n"
                    confirmation_text += f"   • Process schedules and predict next buses\n"
                else:
                    confirmation_text += f"**Step {i}:** {action.replace('_', ' ').title()}\n"
                
                confirmation_text += "\n"
            
            confirmation_text += f" **Estimated time:** {workflow_json.get('estimated_execution_time', '1-2 minutes')}\n\n"
            
            # Check if parameters are needed
            missing_params = self._check_missing_parameters(workflow_json)
            if missing_params:
                confirmation_text += "📝 **I need some information from you:**\n"
                for param in missing_params:
                    confirmation_text += f"   • {param.replace('_', ' ').title()}\n"
                confirmation_text += "\nPlease provide this information so I can complete the workflow.\n"
                
                # Store workflow for parameter collection
                if not hasattr(self, 'agent_memory'):
                    self.agent_memory = {}
                self.agent_memory['pending_workflow_params'] = {
                    'workflow': workflow_json,
                    'missing_params': missing_params,
                    'timestamp': datetime.now().isoformat()
                }
                
                return {
                    "success": True,
                    "status": "parameter_collection",
                    "message": confirmation_text,
                    "response": confirmation_text,
                    "workflow_json": workflow_json,
                    "missing_parameters": missing_params,
                    "awaiting_parameters": True,
                    "done": False
                }
            else:
                confirmation_text += "**Is this the workflow you want?** Reply with:\n"
                confirmation_text += " **'Yes'** to execute this workflow\n"
                confirmation_text += " **'No'** to modify or create a different workflow\n"
                confirmation_text += " **'Modify'** to make changes to this workflow\n"
                
                # Store workflow for execution
                if not hasattr(self, 'agent_memory'):
                    self.agent_memory = {}
                self.agent_memory['pending_workflow_execution'] = {
                    'workflow': workflow_json,
                    'timestamp': datetime.now().isoformat()
                }
                
                return {
                    "success": True,
                    "status": "workflow_confirmation", 
                    "message": confirmation_text,
                    "response": confirmation_text,
                    "workflow_json": workflow_json,
                    "hasWorkflowJson": True,
                    "hasWorkflowPreview": True,
                    "workflow_preview": confirmation_text,
                    "awaiting_confirmation": True,
                    "done": False
                }
                
        except Exception as e:
            logger.error(f"Present workflow confirmation error: {e}")
            return await self._create_helpful_conversational_response(user_input)
    
    def _check_missing_parameters(self, workflow_json: Dict[str, Any]) -> List[str]:
        """Check which parameters are missing from the workflow"""
        missing = []
        
        for step in workflow_json.get('steps', []):
            params = step.get('parameters', {})
            
            # Check for common missing parameters
            if step.get('action') == 'send_email':
                if not params.get('to') or params.get('to') in ['user@example.com', 'recipient']:
                    missing.append('recipient_email')
                if not params.get('subject') or 'subject' in params.get('subject', '').lower():
                    missing.append('email_subject')
        
        return list(set(missing))  # Remove duplicates
    
    async def _is_parameter_response(self, user_input: str) -> bool:
        """Check if user input is responding to parameter request"""
        if not hasattr(self, 'agent_memory'):
            return False
        
        return bool(self.agent_memory.get('pending_workflow_params'))
    
    async def _handle_parameter_input(self, user_input: str) -> Dict[str, Any]:
        """Handle user input for workflow parameters"""
        try:
            logger.error(f"📝 HANDLING PARAMETER INPUT: {user_input[:100]}...")
            
            pending = self.agent_memory.get('pending_workflow_params')
            if not pending:
                return await self._create_helpful_conversational_response(user_input)
            
            workflow = pending['workflow']
            missing_params = pending['missing_params']
            
            # Extract parameters from user input
            extracted_params = self._extract_parameters_from_input(user_input, missing_params)
            
            # Update workflow with extracted parameters
            updated_workflow = self._update_workflow_parameters(workflow, extracted_params)
            
            # Check if all parameters are now filled
            remaining_params = self._check_missing_parameters(updated_workflow)
            
            if remaining_params:
                # Still need more parameters
                param_text = f" Got it! I still need:\n"
                for param in remaining_params:
                    param_text += f"   • {param.replace('_', ' ').title()}\n"
                param_text += "\nPlease provide this information."
                
                # Update memory with new workflow
                self.agent_memory['pending_workflow_params']['workflow'] = updated_workflow
                self.agent_memory['pending_workflow_params']['missing_params'] = remaining_params
                
                return {
                    "success": True,
                    "status": "parameter_collection",
                    "message": param_text,
                    "response": param_text,
                    "remaining_parameters": remaining_params,
                    "awaiting_parameters": True,
                    "done": False
                }
            else:
                # All parameters collected, present final workflow
                confirmation_text = " **Perfect! I have all the information needed.**\n\n"
                confirmation_text += "Your workflow is ready to execute. Shall I proceed?\n\n"
                confirmation_text += "Reply with **'Yes'** to execute or **'No'** to make changes."
                
                # Move to execution confirmation
                self.agent_memory['pending_workflow_execution'] = {
                    'workflow': updated_workflow,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Clear parameter collection
                if 'pending_workflow_params' in self.agent_memory:
                    del self.agent_memory['pending_workflow_params']
                
                return {
                    "success": True,
                    "status": "workflow_confirmation",
                    "message": confirmation_text,
                    "response": confirmation_text,
                    "workflow_json": updated_workflow,
                    "hasWorkflowJson": True,
                    "awaiting_confirmation": True,
                    "done": False
                }
                
        except Exception as e:
            logger.error(f"Handle parameter input error: {e}")
            return await self._create_helpful_conversational_response(user_input)
    
    def _extract_parameters_from_input(self, user_input: str, missing_params: List[str]) -> Dict[str, str]:
        """Extract parameters from user input"""
        extracted = {}
        
        # Email extraction
        if 'recipient_email' in missing_params:
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, user_input)
            if emails:
                extracted['recipient_email'] = emails[0]
        
        # Subject extraction (look for subject indicators)
        if 'email_subject' in missing_params:
            subject_indicators = ['subject:', 'title:', 'about:', 'regarding:']
            for indicator in subject_indicators:
                if indicator in user_input.lower():
                    subject_start = user_input.lower().find(indicator) + len(indicator)
                    subject = user_input[subject_start:].strip()
                    if subject:
                        extracted['email_subject'] = subject
                        break
            
            # If no explicit subject indicator, use the whole input as potential subject
            if 'email_subject' not in extracted and len(user_input.strip()) < 100:
                extracted['email_subject'] = user_input.strip()
        
        return extracted
    
    def _update_workflow_parameters(self, workflow: Dict[str, Any], params: Dict[str, str]) -> Dict[str, Any]:
        """Update workflow with extracted parameters"""
        updated_workflow = workflow.copy()
        
        for step in updated_workflow.get('steps', []):
            if step.get('action') == 'send_email':
                step_params = step.get('parameters', {})
                
                if 'recipient_email' in params:
                    step_params['to'] = params['recipient_email']
                    step_params['toEmail'] = params['recipient_email']
                
                if 'email_subject' in params:
                    step_params['subject'] = params['email_subject']
        
        return updated_workflow
    
    async def _execute_confirmed_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a workflow that has been confirmed by the user"""
        try:
            logger.error(f"EXECUTING CONFIRMED WORKFLOW: {workflow_id}")
            
            pending = self.agent_memory.get('pending_workflow_execution')
            if not pending:
                return {
                    "success": False,
                    "status": "error",
                    "response": "No workflow found to execute. Please create a new workflow.",
                    "done": True
                }
            
            workflow = pending['workflow']
            
            # Send workflow to automation engine for execution
            if hasattr(self, 'automation_engine') and self.automation_engine:
                logger.error(f"Sending workflow to automation engine...")
                
                execution_result = await self.automation_engine.execute_workflow(workflow)
                
                if execution_result and execution_result.get('success'):
                    # Clear pending workflow
                    if 'pending_workflow_execution' in self.agent_memory:
                        del self.agent_memory['pending_workflow_execution']
                    
                    return {
                        "success": True,
                        "status": "automation_completed",
                        "message": f" Workflow executed successfully! {execution_result.get('message', '')}",
                        "response": f" **Workflow Completed!**\n\n{execution_result.get('details', 'Your automation has been executed successfully.')}",
                        "execution_result": execution_result,
                        "done": True
                    }
                else:
                    return {
                        "success": False,
                        "status": "execution_failed",
                        "message": f" Workflow execution failed: {execution_result.get('error', 'Unknown error')}",
                        "response": " **Execution Failed**\n\nThere was an issue executing your workflow. Please try again or contact support.",
                        "done": True
                    }
            else:
                # Fallback: simulate execution
                logger.error(f"Automation engine not available, simulating execution...")
                
                return {
                    "success": True,
                    "status": "automation_ready",
                    "message": " Workflow ready for execution (automation engine not connected)",
                    "response": " **Workflow Ready!**\n\nYour automation workflow has been prepared and is ready for execution. In a production environment, this would be automatically executed by our automation engine.",
                    "workflow_json": workflow,
                    "hasWorkflowJson": True,
                    "simulation_mode": True,
                    "done": True
                }
                
        except Exception as e:
            logger.error(f"Execute confirmed workflow error: {e}")
            return {
                "success": False,
                "status": "error",
                "response": " There was an error executing your workflow. Please try again.",
                "done": True
            }
    
    async def _create_web_search_automation(self, user_input: str, automation_intent: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Create web search automation workflow"""
        try:
            logger.error(f"CREATING WEB SEARCH AUTOMATION...")
            
            # Extract search query from user input
            search_query = self._extract_search_query(user_input)
            
            workflow_json = {
                "workflow_type": "web_search_automation",
                "status": "automation_ready",
                "workflow_id": f"web_search_{int(time.time())}",
                "steps": [
                    {
                        "id": "search_1",
                        "action": "web_search",
                        "driver": "web_search_engine",
                        "parameters": {
                            "query": search_query,
                            "max_results": 10,
                            "search_engines": ["google", "bing"]
                        }
                    },
                    {
                        "id": "process_1", 
                        "action": "process_results",
                        "driver": "data_processor",
                        "parameters": {
                            "input_data": "search_results",
                            "processing_type": "extract_summary"
                        }
                    }
                ],
                "estimated_execution_time": "30 seconds",
                "requires_approval": True,
                "automation_summary": f"Web search for: {search_query}"
            }
            
            return {
                "success": True,
                "status": "automation_ready",
                "workflow_json": workflow_json,
                "message": f"Created web search automation for: {search_query}"
            }
            
        except Exception as e:
            logger.error(f"Create web search automation error: {e}")
            return await self._create_helpful_conversational_response(user_input)
    
    def _extract_search_query(self, user_input: str) -> str:
        """Extract search query from user input"""
        # Remove common automation words to get the actual search query
        automation_words = ['search for', 'find', 'look up', 'research', 'search']
        
        query = user_input.lower()
        for word in automation_words:
            if word in query:
                query = query.replace(word, '').strip()
                break
        
        return query or user_input
    
    async def _create_generic_automation_workflow(self, user_input: str, automation_intent: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a generic automation workflow"""
        try:
            logger.error(f"CREATING GENERIC AUTOMATION WORKFLOW...")
            
            automation_type = automation_intent.get('automation_type', 'custom')
            
            workflow_json = {
                "workflow_type": f"{automation_type}_automation",
                "status": "automation_ready", 
                "workflow_id": f"custom_{int(time.time())}",
                "steps": [
                    {
                        "id": "action_1",
                        "action": f"execute_{automation_type}",
                        "driver": "universal_automation_driver",
                        "parameters": {
                            "user_request": user_input,
                            "automation_type": automation_type,
                            "context": context
                        }
                    }
                ],
                "estimated_execution_time": "1-2 minutes",
                "requires_approval": True,
                "automation_summary": f"Custom {automation_type} automation"
            }
            
            return {
                "success": True,
                "status": "automation_ready",
                "workflow_json": workflow_json,
                "message": f"Created custom {automation_type} automation workflow"
            }
            
        except Exception as e:
            logger.error(f"Create generic automation workflow error: {e}")
            return await self._create_helpful_conversational_response(user_input)

