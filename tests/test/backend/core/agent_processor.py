"""
Simple Agent Processor - Executes Custom MCP LLM Code for Agents
Fetches agent's custom code, executes it with memory/personality, generates automations
"""

import os
import json
import logging
import asyncio
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env.local  
env_path = Path(__file__).parent.parent.parent / '.env.local'
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

class AgentProcessor:
    """
    Simple processor that fetches agent-specific custom MCP LLM code and executes it
    """
    
    def __init__(self, db_pool, automation_engine):
        self.db_pool = db_pool
        self.automation_engine = automation_engine
        
    async def process_with_agent(self, agent_id: str, user_input: str, user_id: str = None, request_data: dict = None) -> Dict[str, Any]:
        """
        Main entry point - fetches agent's custom MCP LLM code and processes user input
        """
        logger.error(f"🎯 CRITICAL DEBUG: AgentProcessor.process_with_agent called for agent {agent_id}")
        try:
            # 1. Fetch agent details and custom code
            agent_data = await self._fetch_agent_data(agent_id)
            if not agent_data:
                return {
                    "status": "error",
                    "message": "Agent not found or has no custom MCP LLM code"
                }
            
            # 2. Fetch conversation memory
            memory = await self._fetch_agent_memory(agent_id, user_id)
            
            # 3. Execute the agent's custom MCP LLM code
            result = await self._execute_custom_mcp_code(
                agent_data=agent_data,
                user_input=user_input,
                memory=memory,
                user_id=user_id,
                request_data=request_data
            )
            
            # 4. Update memory with the interaction
            await self._update_agent_memory(agent_id, user_id, user_input, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Agent processing error: {e}", exc_info=True)
            return {
                "status": "error", 
                "message": f"Agent processing failed: {str(e)}"
            }
    
    async def _fetch_agent_data(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Fetch agent details including custom MCP LLM code"""
        async with self.db_pool.acquire() as conn:
            query = """
                SELECT agent_id, agent_name, agent_role, agent_personality, 
                       agent_expectations, custom_mcp_code, trigger_config, 
                       operation_mode, created_at, updated_at
                FROM agents 
                WHERE agent_id = $1
            """
            row = await conn.fetchrow(query, agent_id)
            if row:
                return dict(row)
            return None
    
    async def _fetch_agent_memory(self, agent_id: str, user_id: str = None) -> Dict[str, Any]:
        """Fetch conversation memory for this agent and user"""
        try:
            async with self.db_pool.acquire() as conn:
                query = """
                    SELECT memory_data, updated_at
                    FROM agent_memory 
                    WHERE agent_id = $1 AND user_id = $2
                    ORDER BY updated_at DESC LIMIT 1
                """
                row = await conn.fetchrow(query, agent_id, user_id or 'system')
                
                if row:
                    return {
                        "conversation_history": row['memory_data'].get('conversation_history', []),
                        "context": row['memory_data'].get('context', {}),
                        "last_updated": row['updated_at'].isoformat()
                    }
                
                return {
                    "conversation_history": [],
                    "context": {},
                    "last_updated": None
                }
        except Exception as e:
            logger.warning(f"Memory fetch error: {e}")
            return {"conversation_history": [], "context": {}, "last_updated": None}
    
    async def _execute_custom_mcp_code(self, agent_data: Dict, user_input: str, 
                                     memory: Dict, user_id: str = None, trigger_context: Dict = None, request_data: Dict = None) -> Dict[str, Any]:
        """
        Execute using the Isolated Agent Engine for all agent interactions
        Each agent gets its own completely isolated engine instance
        """
        try:
            # Import and use the new Isolated Agent Engine system
            from mcp.agent_engine_manager import create_isolated_agent_engine
            
            logger.info(f"🎯 Using ISOLATED AGENT ENGINE for agent: {agent_data['agent_id']}")
            
            # Get OpenAI API key
            openai_api_key = os.getenv("OPENAI_API_KEY")
            logger.info(f"🔑 OpenAI API key available: {bool(openai_api_key)}")
            
            # Create or get isolated engine for this specific agent+user combination
            # This ensures no conversation bleeding between different agents
            session_id = f"user_{user_id}" if user_id else "anonymous_session"
            
            engine = create_isolated_agent_engine(
                agent_id=agent_data['agent_id'],
                session_id=session_id,
                agent_data=agent_data,
                agent_expectations=agent_data.get('agent_expectations', ''),
                agent_context={
                    'agent_data': agent_data,
                    'memory': memory,
                    'user_id': user_id
                },
                db_manager=self.db_manager,
                automation_engine=self.automation_engine,
                openai_api_key=openai_api_key
            )
            
            logger.info(f"🤖 AgentProcessor using isolated engine: {engine.instance_id}")
            logger.info(f"   Agent: {agent_data['agent_id']}, Session: {session_id}")
            
            # Process the user input through the Isolated Agent Engine
            result = await engine.process_user_request(user_input, request_data)
            
            logger.info(f"📤 Isolated engine returned: {result.get('status', 'no_status')}")
            logger.info(f"   Instance: {result.get('instance_id', 'no_instance')}")
            logger.info(f"   Message: {result.get('message', 'No message')[:100]}...")
            
            # Pass through the Isolated Agent Engine result with proper status mapping
            if result.get("success"):
                # Get the status from isolated engine or default to conversational
                engine_status = result.get("status", "conversational")
                
                # Map engine statuses to AgentProcessor expected statuses
                status_mapping = {
                    "completed": "completed",
                    "needs_parameters": "info_needed", 
                    "workflow_preview": "workflow_preview",
                    "preview_ready": "preview_ready",  # ADD EMAIL PREVIEW SUPPORT
                    "ai_service_selection": "ai_service_selection",  # ADD AI SERVICE SELECTION
                    "automation_ready": "automation_ready",  # ADD AUTOMATION READY
                    "automation_completed": "completed",  # ADD AUTOMATION COMPLETED
                    "automation_simulated": "completed",  # ADD AUTOMATION SIMULATED
                    "parameter_collection": "parameter_collection",  # ADD PARAMETER COLLECTION
                    "workflow_selection": "workflow_selection",  # ADD WORKFLOW SELECTION
                    "error": "error",
                    "conversational": "conversational"
                }
                
                mapped_status = status_mapping.get(engine_status, "conversational")
                
                # Build the response with all MCP data preserved
                response = {
                    "status": mapped_status,
                    "message": result.get("message", result.get("response", "")),
                    "workflow_id": result.get("workflow_id"),
                    "workflow_json": result.get("workflow"),
                    "workflow_preview": result.get("workflowPreviewContent"),
                    "automation_type": result.get("automation_type"),
                    "email_sent": result.get("email_sent"),
                    "execution_status": result.get("execution_status"),
                    "metadata": {
                        "engine": "custom_mcp_llm",
                        "iterations": result.get("iterations", 0),
                        "original_status": engine_status
                    }
                }
                
                # Add any additional fields from the MCP result
                for key, value in result.items():
                    if key not in response and key not in ['success', 'response']:
                        response[key] = value
                
                return response
            else:
                return {
                    "status": "error",
                    "message": result.get("message", result.get("response", "Custom MCP LLM processing failed"))
                }
                
        except Exception as e:
            logger.error(f"🚨 CRITICAL ERROR: Custom MCP LLM execution failed: {e}")
            logger.error(f"🚨 Exception type: {type(e).__name__}")
            logger.error(f"🚨 Agent data: {agent_data.get('agent_name', 'Unknown')}")
            logger.error(f"🚨 User input: {user_input[:50]}...")
            import traceback
            logger.error(f"🚨 Full traceback: {traceback.format_exc()}")
            # Fallback to default response
            return await self._default_agent_response(agent_data, user_input)
    
    async def _safe_execute_code(self, custom_code: str, context: Dict) -> Dict[str, Any]:
        """
        Safely execute custom MCP LLM code with proper sandboxing
        """
        # For now, this is a placeholder for custom code execution
        # In production, you'd want proper sandboxing (containers, restricted execution, etc.)
        
        # Check if this looks like an automation request
        user_input = context['user_input'].lower()
        
        if any(keyword in user_input for keyword in ['send email', 'create workflow', 'automate', 'schedule']):
            return await self._generate_automation_workflow(context)
        else:
            return await self._generate_conversational_response(context)
    
    async def _generate_automation_workflow(self, context: Dict) -> Dict[str, Any]:
        """Generate automation workflow based on user input"""
        user_input = context['user_input']
        agent = context['agent']
        
        # Simple email detection
        if 'email' in user_input.lower():
            # Extract email if provided
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, user_input)
            
            if emails:
                # Generate email workflow
                workflow = {
                    "type": "email_automation",
                    "agent_id": agent['id'],
                    "recipient": emails[0],
                    "content_type": "custom email",
                    "ai_service": "inhouse",
                    "needs_ai_generation": True,
                    "workflow": {
                        "name": f"Email from {agent['name']}",
                        "actions": [
                            {
                                "node": "mcpLLM",
                                "parameters": {
                                    "user_input": user_input,
                                    "agent_personality": agent['personality'],
                                    "content_type": "email"
                                }
                            },
                            {
                                "node": "emailSend", 
                                "parameters": {
                                    "toEmail": emails[0],
                                    "subject": f"Message from {agent['name']}",
                                    "content": "{ai_generated_content}"
                                }
                            }
                        ]
                    }
                }
                
                return {
                    "status": "workflow_preview",
                    "message": f"I'll create and send an email to {emails[0]}. Would you like me to proceed?",
                    "workflow_json": workflow,
                    "workflow_id": str(uuid.uuid4()),
                    "ai_service_used": "inhouse",
                    "estimated_credits": 2,
                    "preview_details": f"Email to {emails[0]} using {agent['name']}'s personality"
                }
            else:
                return {
                    "status": "info_needed",
                    "message": "I can help you send an email. Please provide the recipient's email address."
                }
        
        # Default automation response
        return {
            "status": "conversational",
            "message": f"I'm {agent['name']}, and I can help you with automation tasks. What would you like me to automate?"
        }
    
    async def _generate_conversational_response(self, context: Dict) -> Dict[str, Any]:
        """Generate conversational response based on agent personality"""
        agent = context['agent']
        user_input = context['user_input']
        memory = context['memory']
        
        # Simple personality-based responses
        personality = agent.get('personality', {})
        tone = personality.get('tone', 'friendly')
        
        if tone == 'friendly':
            response = f"Hi! I'm {agent['name']}, your {agent['role']}. {user_input} - I'd be happy to help you with that!"
        elif tone == 'professional':
            response = f"Hello. I am {agent['name']}, specializing in {agent['role']}. How may I assist you with: {user_input}?"
        else:
            response = f"I'm {agent['name']}. As your {agent['role']}, I can help you with various tasks. What would you like me to do?"
        
        return {
            "status": "conversational", 
            "message": response
        }
    
    async def _default_agent_response(self, agent_data: Dict, user_input: str) -> Dict[str, Any]:
        """Default response when no custom MCP code is available"""
        return {
            "status": "conversational",
            "message": f"Hello! I'm {agent_data['agent_name']}, your {agent_data['agent_role']}. I'm ready to help you, but I don't have custom programming yet. How can I assist you?"
        }
    
    async def _update_agent_memory(self, agent_id: str, user_id: str, user_input: str, result: Dict):
        """Update agent memory with enhanced context tracking for workflows"""
        try:
            async with self.db_pool.acquire() as conn:
                # Fetch current memory
                current_memory = await self._fetch_agent_memory(agent_id, user_id)
                
                # Add new interaction with enhanced context
                conversation_history = current_memory.get('conversation_history', [])
                
                # Create enhanced interaction record
                interaction_record = {
                    "timestamp": datetime.now().isoformat(),
                    "user_input": user_input,
                    "agent_response": result.get('message', ''),
                    "status": result.get('status', 'unknown'),
                    "workflow_id": result.get('workflow_id'),
                    "automation_type": result.get('automation_type'),
                    "action_required": result.get('action_required')
                }
                
                # Add email-specific context if present
                if result.get('status') == 'preview_ready' or result.get('automation_type') == 'email_preview':
                    interaction_record.update({
                        "email_context": {
                            "recipient": result.get('recipient'),
                            "email_subject": result.get('email_subject'),
                            "content_type": result.get('content_type'),
                            "workflow_stage": "preview_generated"
                        }
                    })
                
                # Track SEND_APPROVED_EMAIL context
                if user_input.startswith("SEND_APPROVED_EMAIL:"):
                    interaction_record.update({
                        "email_context": {
                            "workflow_stage": "email_confirmed_and_sent",
                            "action_type": "email_execution"
                        }
                    })
                
                conversation_history.append(interaction_record)
                
                # Keep only last 50 interactions
                if len(conversation_history) > 50:
                    conversation_history = conversation_history[-50:]
                
                # Enhanced context tracking
                context = current_memory.get('context', {})
                
                # Track active email workflows
                if result.get('status') == 'preview_ready':
                    context['active_email_workflow'] = {
                        "workflow_id": result.get('workflow_id'),
                        "recipient": result.get('recipient'),
                        "subject": result.get('email_subject'),
                        "stage": "awaiting_confirmation",
                        "created_at": datetime.now().isoformat()
                    }
                
                # Clear active workflow when completed
                if user_input.startswith("SEND_APPROVED_EMAIL:") and result.get('email_sent'):
                    context.pop('active_email_workflow', None)
                    context['last_completed_email'] = {
                        "completed_at": datetime.now().isoformat(),
                        "recipient": result.get('recipient', 'unknown')
                    }
                
                # Track content generation patterns for learning
                if result.get('automation_type') in ['email_preview', 'content_creation']:
                    content_patterns = context.get('content_generation_patterns', [])
                    content_patterns.append({
                        "request_type": result.get('content_type'),
                        "timestamp": datetime.now().isoformat(),
                        "success": result.get('success', False)
                    })
                    # Keep last 20 patterns
                    context['content_generation_patterns'] = content_patterns[-20:]
                
                memory_data = {
                    "conversation_history": conversation_history,
                    "context": context,
                    "last_interaction": datetime.now().isoformat()
                }
                
                # Upsert memory
                query = """
                    INSERT INTO agent_memory (agent_id, user_id, memory_data, updated_at)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (agent_id, user_id) 
                    DO UPDATE SET memory_data = $3, updated_at = $4
                """
                
                await conn.execute(query, agent_id, user_id or 'system', 
                                 json.dumps(memory_data), datetime.now())
                
                logger.debug(f"📝 Enhanced memory updated for agent {agent_id}: workflow_stage={interaction_record.get('email_context', {}).get('workflow_stage', 'none')}")
                
        except Exception as e:
            logger.warning(f"Memory update error: {e}")
    
    async def _fetch_agent_triggers(self, agent_id: str) -> Dict[str, Any]:
        """Fetch active triggers for the agent"""
        try:
            async with self.db_pool.acquire() as conn:
                query = """
                    SELECT trigger_type, trigger_config, is_active, created_at
                    FROM agent_triggers 
                    WHERE agent_id = $1 AND is_active = true
                    ORDER BY created_at DESC
                """
                rows = await conn.fetch(query, agent_id)
                
                triggers = []
                for row in rows:
                    triggers.append({
                        "type": row['trigger_type'],
                        "config": row['trigger_config'],
                        "active": row['is_active'],
                        "created": row['created_at'].isoformat()
                    })
                
                return {
                    "count": len(triggers),
                    "triggers": triggers,
                    "has_cron": any(t['type'] == 'cron' for t in triggers),
                    "has_webhook": any(t['type'] == 'webhook' for t in triggers),
                    "has_email": any(t['type'] == 'email_imap' for t in triggers)
                }
        except Exception as e:
            logger.warning(f"Trigger fetch error: {e}")
            return {"count": 0, "triggers": [], "has_cron": False, "has_webhook": False, "has_email": False}

    async def execute_manual_trigger(self, agent_id: str, user_id: str, trigger_input: Dict = None) -> Dict[str, Any]:
        """
        Execute agent workflow manually (one-click trigger from dashboard)
        """
        try:
            # Fetch agent data
            agent_data = await self._fetch_agent_data(agent_id)
            if not agent_data:
                return {
                    "status": "error",
                    "message": "Agent not found"
                }
            
            # Fetch memory
            memory = await self._fetch_agent_memory(agent_id, user_id)
            
            # Create trigger context for manual execution
            trigger_context = {
                "type": "manual",
                "source": "dashboard_button", 
                "initiated_by": user_id,
                "timestamp": datetime.now().isoformat(),
                "input_data": trigger_input or {}
            }
            
            # Default input for manual trigger
            default_input = trigger_input.get('message', 'Execute agent workflow manually')
            
            # Execute with trigger context
            result = await self._execute_custom_mcp_code(
                agent_data=agent_data,
                user_input=default_input,
                memory=memory,
                user_id=user_id,
                trigger_context=trigger_context
            )
            
            # Log the execution
            await self._log_agent_execution(
                agent_id=agent_id,
                user_id=user_id,
                trigger_type="manual",
                input_data=trigger_input,
                output_data=result,
                execution_status="success" if result.get("status") != "error" else "error"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Manual trigger execution error: {e}", exc_info=True)
            
            # Log failed execution
            await self._log_agent_execution(
                agent_id=agent_id,
                user_id=user_id,
                trigger_type="manual",
                input_data=trigger_input,
                output_data={},
                execution_status="error",
                error_message=str(e)
            )
            
            return {
                "status": "error",
                "message": f"Manual trigger execution failed: {str(e)}"
            }

    async def _log_agent_execution(self, agent_id: str, user_id: str, trigger_type: str, 
                                 input_data: Dict, output_data: Dict, execution_status: str,
                                 error_message: str = None) -> None:
        """Log agent execution to agent_executions table"""
        try:
            async with self.db_pool.acquire() as conn:
                query = """
                    INSERT INTO agent_executions 
                    (agent_id, user_id, trigger_type, input_data, output_data, execution_status, error_message)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """
                await conn.execute(
                    query, agent_id, user_id, trigger_type, 
                    json.dumps(input_data), json.dumps(output_data), 
                    execution_status, error_message
                )
        except Exception as e:
            logger.warning(f"Execution logging error: {e}")
