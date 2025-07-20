"""
Custom Agent Driver - Handles AI agent operations and management
Supports: agent creation, execution, conversation management
"""

import logging
import asyncio
import json
from typing import Dict, Any, List, Optional, Union
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# Add the parent directories to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(backend_dir)
mcp_dir = os.path.join(backend_dir, 'mcp')
sys.path.append(mcp_dir)

from mcp.universal_driver_manager import BaseUniversalDriver

class CustomAgentDriver(BaseUniversalDriver):
    """Custom driver for AI agent operations"""
    
    def __init__(self):
        super().__init__()
        self.service_name = "custom_agent_driver"
        self.supported_node_types = [
            'n8n-nodes-base.agent',
            'custom.agent',
            'agent.execute',
            'agent.chat',
            'agent.memory'
        ]
        self.agent_sessions = {}
    
    def get_supported_node_types(self) -> List[str]:
        return self.supported_node_types
    
    def get_required_parameters(self, node_type: str) -> List[str]:
        return ['agent_id', 'action']
    
    async def execute(self, node_type: str, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        if node_type not in self.supported_node_types:
            return {
                "success": False,
                "error": f"Unsupported node type: {node_type}",
                "supported_types": self.supported_node_types
            }
        
        try:
            action = parameters.get('action', 'execute')
            
            if action == 'create':
                return await self.create_agent(parameters, context)
            elif action == 'execute':
                return await self.execute_agent(parameters, context)
            elif action == 'chat':
                return await self.chat_with_agent(parameters, context)
            elif action == 'memory':
                return await self.manage_agent_memory(parameters, context)
            elif action == 'delete':
                return await self.delete_agent(parameters, context)
            else:
                return await self.execute_agent(parameters, context)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "node_type": node_type
            }
    
    async def create_agent(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new AI agent"""
        self.logger.info("Creating new AI agent")
        
        try:
            agent_id = parameters.get('agent_id', f"agent_{len(self.agent_sessions) + 1}")
            agent_config = parameters.get('config', {})
            
            # Agent configuration
            agent = {
                "id": agent_id,
                "name": agent_config.get('name', f"Agent {agent_id}"),
                "description": agent_config.get('description', ''),
                "system_prompt": agent_config.get('system_prompt', 'You are a helpful AI assistant.'),
                "model": agent_config.get('model', 'gpt-3.5-turbo'),
                "temperature": agent_config.get('temperature', 0.7),
                "max_tokens": agent_config.get('max_tokens', 1000),
                "tools": agent_config.get('tools', []),
                "memory": agent_config.get('memory', []),
                "context_window": agent_config.get('context_window', 4000),
                "created_at": self._get_current_timestamp(),
                "status": "active"
            }
            
            # Store agent session
            self.agent_sessions[agent_id] = agent
            
            result = {
                "success": True,
                "agent_id": agent_id,
                "agent": agent,
                "message": f"Agent '{agent_id}' created successfully"
            }
            
            self.logger.info(f"Agent created: {agent_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Agent creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_agent(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute agent with given input"""
        self.logger.info("Executing agent")
        
        try:
            agent_id = parameters.get('agent_id')
            input_text = parameters.get('input', parameters.get('message', ''))
            
            if not agent_id or agent_id not in self.agent_sessions:
                return {
                    "success": False,
                    "error": f"Agent '{agent_id}' not found"
                }
            
            agent = self.agent_sessions[agent_id]
            
            # Prepare conversation context
            conversation_context = self._build_conversation_context(agent, input_text, context)
            
            # Execute agent reasoning
            response = await self._execute_agent_reasoning(agent, conversation_context)
            
            # Update agent memory
            self._update_agent_memory(agent, input_text, response)
            
            result = {
                "success": True,
                "agent_id": agent_id,
                "input": input_text,
                "response": response,
                "agent_status": agent.get('status', 'active'),
                "memory_size": len(agent.get('memory', [])),
                "message": "Agent executed successfully"
            }
            
            self.logger.info(f"Agent executed: {agent_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Agent execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def chat_with_agent(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Chat with agent in conversational mode"""
        self.logger.info("Chatting with agent")
        
        try:
            agent_id = parameters.get('agent_id')
            message = parameters.get('message', '')
            conversation_id = parameters.get('conversation_id', 'default')
            
            if not agent_id or agent_id not in self.agent_sessions:
                return {
                    "success": False,
                    "error": f"Agent '{agent_id}' not found"
                }
            
            agent = self.agent_sessions[agent_id]
            
            # Get or create conversation
            if 'conversations' not in agent:
                agent['conversations'] = {}
            
            if conversation_id not in agent['conversations']:
                agent['conversations'][conversation_id] = {
                    "messages": [],
                    "created_at": self._get_current_timestamp()
                }
            
            conversation = agent['conversations'][conversation_id]
            
            # Add user message
            conversation['messages'].append({
                "role": "user",
                "content": message,
                "timestamp": self._get_current_timestamp()
            })
            
            # Generate response
            response = await self._generate_chat_response(agent, conversation, message)
            
            # Add assistant response
            conversation['messages'].append({
                "role": "assistant",
                "content": response,
                "timestamp": self._get_current_timestamp()
            })
            
            # Trim conversation if too long
            self._trim_conversation(conversation, agent.get('context_window', 4000))
            
            result = {
                "success": True,
                "agent_id": agent_id,
                "conversation_id": conversation_id,
                "message": message,
                "response": response,
                "conversation_length": len(conversation['messages']),
                "message": "Chat completed successfully"
            }
            
            self.logger.info(f"Chat completed: {agent_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Chat failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def manage_agent_memory(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Manage agent memory operations"""
        self.logger.info("Managing agent memory")
        
        try:
            agent_id = parameters.get('agent_id')
            memory_action = parameters.get('memory_action', 'get')
            
            if not agent_id or agent_id not in self.agent_sessions:
                return {
                    "success": False,
                    "error": f"Agent '{agent_id}' not found"
                }
            
            agent = self.agent_sessions[agent_id]
            
            if memory_action == 'get':
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "memory": agent.get('memory', []),
                    "memory_size": len(agent.get('memory', [])),
                    "message": "Memory retrieved successfully"
                }
            
            elif memory_action == 'add':
                memory_item = parameters.get('memory_item', {})
                if not agent.get('memory'):
                    agent['memory'] = []
                agent['memory'].append({
                    **memory_item,
                    "timestamp": self._get_current_timestamp()
                })
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "memory_size": len(agent['memory']),
                    "message": "Memory item added successfully"
                }
            
            elif memory_action == 'clear':
                agent['memory'] = []
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "message": "Memory cleared successfully"
                }
            
            elif memory_action == 'search':
                query = parameters.get('query', '')
                results = self._search_memory(agent, query)
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "query": query,
                    "results": results,
                    "result_count": len(results),
                    "message": f"Memory search completed: {len(results)} results"
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown memory action: {memory_action}"
                }
            
        except Exception as e:
            self.logger.error(f"Memory management failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_agent(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Delete an agent"""
        self.logger.info("Deleting agent")
        
        try:
            agent_id = parameters.get('agent_id')
            
            if not agent_id or agent_id not in self.agent_sessions:
                return {
                    "success": False,
                    "error": f"Agent '{agent_id}' not found"
                }
            
            del self.agent_sessions[agent_id]
            
            return {
                "success": True,
                "agent_id": agent_id,
                "message": f"Agent '{agent_id}' deleted successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Agent deletion failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_conversation_context(self, agent: Dict[str, Any], input_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Build conversation context for agent"""
        
        conversation_context = {
            "system_prompt": agent.get('system_prompt', ''),
            "agent_name": agent.get('name', ''),
            "agent_description": agent.get('description', ''),
            "input": input_text,
            "memory": agent.get('memory', []),
            "tools": agent.get('tools', []),
            "context_data": context.get('input_data', {}) if context else {}
        }
        
        return conversation_context
    
    async def _execute_agent_reasoning(self, agent: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Execute agent reasoning process"""
        
        # This is a simplified version - in practice, you'd integrate with your LLM
        system_prompt = context.get('system_prompt', '')
        input_text = context.get('input', '')
        memory = context.get('memory', [])
        
        # Build prompt with memory context
        prompt_parts = [system_prompt]
        
        if memory:
            prompt_parts.append("Previous context:")
            for mem_item in memory[-5:]:  # Last 5 memory items
                prompt_parts.append(f"- {mem_item}")
        
        prompt_parts.append(f"User: {input_text}")
        prompt_parts.append("Assistant:")
        
        full_prompt = "\\n".join(prompt_parts)
        
        # Here you would call your LLM API
        # For now, return a simple response
        return f"Agent response to: {input_text}"
    
    async def _generate_chat_response(self, agent: Dict[str, Any], conversation: Dict[str, Any], message: str) -> str:
        """Generate chat response using agent configuration"""
        
        # Build conversation history
        messages = conversation.get('messages', [])
        
        # Add system prompt
        full_context = [{"role": "system", "content": agent.get('system_prompt', '')}]
        
        # Add recent messages
        recent_messages = messages[-10:]  # Last 10 messages
        full_context.extend(recent_messages)
        
        # Here you would call your LLM API with the conversation context
        # For now, return a simple response
        return f"Agent response to: {message}"
    
    def _update_agent_memory(self, agent: Dict[str, Any], input_text: str, response: str) -> None:
        """Update agent memory with new interaction"""
        
        if 'memory' not in agent:
            agent['memory'] = []
        
        memory_item = {
            "input": input_text,
            "response": response,
            "timestamp": self._get_current_timestamp(),
            "type": "interaction"
        }
        
        agent['memory'].append(memory_item)
        
        # Trim memory if it gets too long
        max_memory_size = agent.get('max_memory_size', 100)
        if len(agent['memory']) > max_memory_size:
            agent['memory'] = agent['memory'][-max_memory_size:]
    
    def _search_memory(self, agent: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """Search agent memory for relevant items"""
        
        memory = agent.get('memory', [])
        results = []
        
        query_lower = query.lower()
        
        for item in memory:
            # Simple text search - you could implement more sophisticated search
            if isinstance(item, dict):
                item_text = f"{item.get('input', '')} {item.get('response', '')}".lower()
                if query_lower in item_text:
                    results.append(item)
        
        return results
    
    def _trim_conversation(self, conversation: Dict[str, Any], max_tokens: int) -> None:
        """Trim conversation to fit within context window"""
        
        messages = conversation.get('messages', [])
        
        # Simple token estimation (4 chars ≈ 1 token)
        total_chars = sum(len(msg.get('content', '')) for msg in messages)
        
        while total_chars > max_tokens * 4 and len(messages) > 2:
            # Remove oldest messages but keep system message
            if messages[0].get('role') == 'system':
                messages.pop(1)
            else:
                messages.pop(0)
            
            total_chars = sum(len(msg.get('content', '')) for msg in messages)
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def get_agent_list(self) -> List[Dict[str, Any]]:
        """Get list of all agents"""
        return [
            {
                "id": agent_id,
                "name": agent.get('name', ''),
                "status": agent.get('status', ''),
                "created_at": agent.get('created_at', ''),
                "memory_size": len(agent.get('memory', []))
            }
            for agent_id, agent in self.agent_sessions.items()
        ]
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about an agent"""
        return self.agent_sessions.get(agent_id)
    
    def get_supported_actions(self) -> List[str]:
        """Get list of supported agent actions"""
        return ['create', 'execute', 'chat', 'memory', 'delete']
