#!/usr/bin/env python3
"""
Clean minimal version of custom_mcp_llm_iteration.py to get server working
"""

import asyncio
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List

# Configure logging
logger = logging.getLogger(__name__)

# OpenAI integration
try:
    import openai
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
    logger.info("OpenAI package loaded successfully - full AI capabilities available")
except ImportError:
    OPENAI_AVAILABLE = False
    logger.error("OpenAI package not available - automation intent detection will be limited")

class CustomMCPLLMIterationEngine:
    """Minimal MCP LLM Engine for agent processing"""
    
    def __init__(self, db_manager=None, automation_engine=None, agent_data=None, agent_expectations=None):
        """Initialize the MCP engine"""
        self.db_manager = db_manager
        self.automation_engine = automation_engine
        self.agent_data = agent_data or {}
        self.agent_expectations = agent_expectations or ""
        self.openai_client = None
        self._processing_lock = False
        self.agent_memory = {}
        
        # Initialize OpenAI if available
        if OPENAI_AVAILABLE:
            try:
                import os
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key:
                    self.openai_client = AsyncOpenAI(api_key=api_key)
                    logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        
        logger.info(f"MCP Engine initialized with agent: {self.agent_data.get('agent_name', 'Unknown')}")

    def _instant_response(self, message: str) -> Dict[str, Any]:
        """Create an instant response"""
        return {
            "success": True,
            "status": "conversational",
            "response": message,
            "done": True
        }

    async def process_user_request(self, user_input: str, request_data: dict = None) -> Dict[str, Any]:
        """Process user request with simplified logic"""
        
        logger.info(f"Processing request: {user_input[:100]}...")
        
        start_time = datetime.now()
        
        if self._processing_lock:
            return self._instant_response("I'm currently processing another request. Please wait a moment and try again.")
        
        self._processing_lock = True
        
        try:
            # Simple automation detection
            automation_keywords = [
                'send email', 'create email', 'email to', 'send to',
                'search for', 'find information', 'research',
                'create workflow', 'automate', 'schedule',
                'process data', 'analyze', 'generate report'
            ]
            
            user_lower = user_input.lower()
            is_automation = any(keyword in user_lower for keyword in automation_keywords)
            
            if is_automation:
                # Simple automation response
                return {
                    "success": True,
                    "status": "automation_ready",
                    "message": "I understand you want to create an automation. Let me help with that!",
                    "response": f"I can help you with that automation request: '{user_input[:100]}...'\n\nI'll create a workflow to handle this task. Would you like me to proceed?",
                    "workflow_json": {
                        "id": "simple_automation",
                        "name": "User Automation Request",
                        "nodes": [
                            {
                                "id": "trigger",
                                "type": "n8n-nodes-base.manualTrigger",
                                "parameters": {}
                            }
                        ],
                        "connections": {}
                    },
                    "hasWorkflowJson": True,
                    "done": True
                }
            else:
                # Conversational response
                if OPENAI_AVAILABLE and self.openai_client:
                    try:
                        # Use OpenAI for conversational responses
                        response = await self.openai_client.chat.completions.create(
                            model="gpt-4",
                            messages=[
                                {
                                    "role": "system",
                                    "content": f"You are {self.agent_data.get('agent_name', 'a helpful assistant')} with the role of {self.agent_data.get('agent_role', 'Personal Assistant')}. You are helpful, friendly, and professional."
                                },
                                {
                                    "role": "user",
                                    "content": user_input
                                }
                            ],
                            max_tokens=500,
                            temperature=0.7
                        )
                        
                        ai_response = response.choices[0].message.content
                        
                        return {
                            "success": True,
                            "status": "conversational",
                            "response": ai_response,
                            "done": True
                        }
                        
                    except Exception as e:
                        logger.error(f"OpenAI API error: {e}")
                        # Fall back to simple response
                
                # Simple fallback conversational response
                greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
                questions = ['what', 'how', 'why', 'when', 'where', 'who']
                thanks = ['thank', 'thanks', 'appreciate']
                
                if any(greeting in user_lower for greeting in greetings):
                    response = f"Hello! I'm {self.agent_data.get('agent_name', 'your assistant')}. How can I help you today?"
                elif any(question in user_lower for question in questions):
                    response = "That's a great question! I'm here to help you with information and automation tasks. What specifically would you like to know more about?"
                elif any(thank in user_lower for thank in thanks):
                    response = "You're very welcome! I'm happy to help. Is there anything else you'd like assistance with?"
                else:
                    response = f"I understand you're saying: '{user_input[:100]}...' I'm here to help with information and automation tasks. How can I assist you further?"
                
                return {
                    "success": True,
                    "status": "conversational",
                    "response": response,
                    "done": True
                }
        
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            return {
                "success": False,
                "status": "error",
                "response": "I apologize, but I encountered an issue processing your request. Please try again in a moment.",
                "done": True
            }
        
        finally:
            self._processing_lock = False
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Request processed in {processing_time:.3f}s")

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

# Export the main class
__all__ = ['CustomMCPLLMIterationEngine']
