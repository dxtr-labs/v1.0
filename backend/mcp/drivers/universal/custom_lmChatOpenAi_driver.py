"""
Custom LM Chat OpenAI Driver - Handles OpenAI language model chat operations
Supports: custom chat completions, streaming, conversation management
"""

import logging
import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional, AsyncGenerator
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# Add the parent directories to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(backend_dir)
mcp_dir = os.path.join(backend_dir, 'mcp')
sys.path.append(mcp_dir)

from mcp.universal_driver_manager import BaseUniversalDriver

class CustomLmChatOpenAiDriver(BaseUniversalDriver):
    """Custom driver for OpenAI chat completions"""
    
    def __init__(self):
        super().__init__()
        self.service_name = "custom_lmChatOpenAi_driver"
        self.supported_node_types = [
            'n8n-nodes-base.lmChatOpenAi',
            'custom.lmChatOpenAi',
            'openai.chat',
            'openai.completion'
        ]
        self.api_base = "https://api.openai.com/v1"
    
    def get_supported_node_types(self) -> List[str]:
        return self.supported_node_types
    
    def get_required_parameters(self, node_type: str) -> List[str]:
        return ['model', 'messages']
    
    async def execute(self, node_type: str, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        if node_type not in self.supported_node_types:
            return {
                "success": False,
                "error": f"Unsupported node type: {node_type}",
                "supported_types": self.supported_node_types
            }
        
        try:
            return await self.execute_chat_completion(parameters, context)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "node_type": node_type
            }
    
    async def execute_chat_completion(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute OpenAI chat completion"""
        self.logger.info("Executing OpenAI chat completion")
        
        try:
            # Get API key from credentials or environment
            api_key = self._get_api_key(parameters, context)
            if not api_key:
                return {
                    "success": False,
                    "error": "OpenAI API key not found"
                }
            
            # Extract parameters
            model = parameters.get('model', 'gpt-3.5-turbo')
            messages = parameters.get('messages', [])
            max_tokens = parameters.get('max_tokens', parameters.get('maxTokens', 1000))
            temperature = parameters.get('temperature', 0.7)
            stream = parameters.get('stream', False)
            
            # Format messages
            formatted_messages = self._format_messages(messages, context)
            
            # Prepare request payload
            payload = {
                "model": model,
                "messages": formatted_messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": stream
            }
            
            # Add optional parameters
            if 'top_p' in parameters:
                payload['top_p'] = parameters['top_p']
            if 'presence_penalty' in parameters:
                payload['presence_penalty'] = parameters['presence_penalty']
            if 'frequency_penalty' in parameters:
                payload['frequency_penalty'] = parameters['frequency_penalty']
            if 'stop' in parameters:
                payload['stop'] = parameters['stop']
            
            # Make API request
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"OpenAI API error: {response.status} - {error_text}",
                            "status_code": response.status
                        }
                    
                    if stream:
                        # Handle streaming response
                        return await self._handle_streaming_response(response)
                    else:
                        # Handle regular response
                        result = await response.json()
                        return self._format_completion_result(result)
            
        except Exception as e:
            self.logger.error(f"OpenAI chat completion failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_api_key(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Optional[str]:
        """Get OpenAI API key from various sources"""
        
        # Try parameters first
        if 'api_key' in parameters:
            return parameters['api_key']
        
        # Try context credentials
        if context and 'credentials' in context:
            credentials = context['credentials']
            if 'openai' in credentials:
                return credentials['openai'].get('api_key')
            if 'openaiApi' in credentials:
                return credentials['openaiApi'].get('apiKey')
        
        # Try environment variable
        return os.getenv('OPENAI_API_KEY')
    
    def _format_messages(self, messages: List[Dict[str, Any]], context: Dict[str, Any] = None) -> List[Dict[str, str]]:
        """Format messages for OpenAI API"""
        
        formatted_messages = []
        
        # Handle different message formats
        for message in messages:
            if isinstance(message, dict):
                role = message.get('role', 'user')
                content = message.get('content', message.get('message', ''))
                
                # Handle template variables
                if context and 'input_data' in context:
                    content = self._substitute_variables(content, context['input_data'])
                
                formatted_messages.append({
                    "role": role,
                    "content": str(content)
                })
            elif isinstance(message, str):
                formatted_messages.append({
                    "role": "user",
                    "content": message
                })
        
        # Add system message if specified
        if context and 'system_message' in context:
            formatted_messages.insert(0, {
                "role": "system",
                "content": context['system_message']
            })
        
        return formatted_messages
    
    def _substitute_variables(self, text: str, data: Any) -> str:
        """Substitute template variables in text"""
        
        if not isinstance(text, str):
            return str(text)
        
        # Handle {{variable}} patterns
        import re
        
        def replace_variable(match):
            var_name = match.group(1).strip()
            
            # Handle $json references
            if var_name.startswith('$json'):
                path = var_name[5:].lstrip('.')
                if path:
                    return str(self._get_nested_value(data, path, ''))
                else:
                    return json.dumps(data) if isinstance(data, (dict, list)) else str(data)
            
            # Handle direct variable references
            if isinstance(data, dict):
                return str(data.get(var_name, f'{{{{{var_name}}}}}'))
            
            return match.group(0)
        
        return re.sub(r'{{([^}]+)}}', replace_variable, text)
    
    def _get_nested_value(self, data: Any, path: str, default: Any = None) -> Any:
        """Get nested value from dict using dot notation"""
        
        if not isinstance(data, dict):
            return default
        
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    async def _handle_streaming_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Handle streaming response from OpenAI"""
        
        content_chunks = []
        
        async for line in response.content:
            line = line.decode('utf-8').strip()
            
            if line.startswith('data: '):
                data_str = line[6:]
                
                if data_str == '[DONE]':
                    break
                
                try:
                    data = json.loads(data_str)
                    if 'choices' in data and data['choices']:
                        delta = data['choices'][0].get('delta', {})
                        if 'content' in delta:
                            content_chunks.append(delta['content'])
                except json.JSONDecodeError:
                    continue
        
        full_content = ''.join(content_chunks)
        
        return {
            "success": True,
            "data": {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": full_content
                    },
                    "finish_reason": "stop",
                    "index": 0
                }],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                },
                "model": "gpt-3.5-turbo",
                "streaming": True
            },
            "message": f"Streaming completion received: {len(full_content)} characters"
        }
    
    def _format_completion_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format OpenAI completion result"""
        
        try:
            choices = result.get('choices', [])
            if not choices:
                return {
                    "success": False,
                    "error": "No choices returned from OpenAI"
                }
            
            choice = choices[0]
            message = choice.get('message', {})
            content = message.get('content', '')
            
            return {
                "success": True,
                "data": result,
                "message": content,
                "model": result.get('model', 'unknown'),
                "usage": result.get('usage', {}),
                "finish_reason": choice.get('finish_reason', 'unknown'),
                "response_length": len(content)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to format completion result: {e}",
                "raw_result": result
            }
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported OpenAI models"""
        return [
            'gpt-4',
            'gpt-4-0613',
            'gpt-4-32k',
            'gpt-4-32k-0613',
            'gpt-3.5-turbo',
            'gpt-3.5-turbo-0613',
            'gpt-3.5-turbo-16k',
            'gpt-3.5-turbo-16k-0613'
        ]
    
    def get_default_parameters(self) -> Dict[str, Any]:
        """Get default parameters for OpenAI chat"""
        return {
            'model': 'gpt-3.5-turbo',
            'temperature': 0.7,
            'max_tokens': 1000,
            'top_p': 1.0,
            'presence_penalty': 0.0,
            'frequency_penalty': 0.0,
            'stream': False
        }
