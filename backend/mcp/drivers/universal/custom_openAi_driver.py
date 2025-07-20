"""
Custom OpenAI Driver - Handles OpenAI API operations beyond chat
Supports: embeddings, completions, fine-tuning, moderation
"""

import logging
import asyncio
import aiohttp
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

class CustomOpenAiDriver(BaseUniversalDriver):
    """Custom driver for OpenAI API operations"""
    
    def __init__(self):
        super().__init__()
        self.service_name = "custom_openAi_driver"
        self.supported_node_types = [
            'n8n-nodes-base.openAi',
            'custom.openAi',
            'openai.embeddings',
            'openai.moderation',
            'openai.completion',
            'openai.fine_tuning'
        ]
        self.api_base = "https://api.openai.com/v1"
    
    def get_supported_node_types(self) -> List[str]:
        return self.supported_node_types
    
    def get_required_parameters(self, node_type: str) -> List[str]:
        return ['operation']
    
    async def execute(self, node_type: str, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        if node_type not in self.supported_node_types:
            return {
                "success": False,
                "error": f"Unsupported node type: {node_type}",
                "supported_types": self.supported_node_types
            }
        
        try:
            operation = parameters.get('operation', 'completion')
            
            if operation == 'embeddings':
                return await self.create_embeddings(parameters, context)
            elif operation == 'completion':
                return await self.create_completion(parameters, context)
            elif operation == 'moderation':
                return await self.moderate_content(parameters, context)
            elif operation == 'fine_tuning':
                return await self.fine_tune_model(parameters, context)
            elif operation == 'list_models':
                return await self.list_models(parameters, context)
            elif operation == 'get_model':
                return await self.get_model(parameters, context)
            else:
                return await self.create_completion(parameters, context)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "node_type": node_type
            }
    
    async def create_embeddings(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create embeddings using OpenAI API"""
        self.logger.info("Creating embeddings")
        
        try:
            # Get API key
            api_key = self._get_api_key(parameters, context)
            if not api_key:
                return {
                    "success": False,
                    "error": "OpenAI API key not found"
                }
            
            # Extract parameters
            input_text = parameters.get('input', parameters.get('text', ''))
            model = parameters.get('model', 'text-embedding-ada-002')
            
            # Handle input from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, list):
                    input_text = [str(item) for item in input_data]
                elif isinstance(input_data, dict):
                    input_text = input_data.get('text', str(input_data))
                else:
                    input_text = str(input_data)
            
            # Prepare request
            payload = {
                "model": model,
                "input": input_text
            }
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/embeddings",
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
                    
                    result = await response.json()
                    
                    # Extract embeddings
                    embeddings = [item['embedding'] for item in result.get('data', [])]
                    
                    return {
                        "success": True,
                        "embeddings": embeddings,
                        "model": result.get('model', model),
                        "usage": result.get('usage', {}),
                        "embedding_count": len(embeddings),
                        "embedding_dimension": len(embeddings[0]) if embeddings else 0,
                        "message": f"Created {len(embeddings)} embeddings"
                    }
            
        except Exception as e:
            self.logger.error(f"Embeddings creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_completion(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create text completion using OpenAI API"""
        self.logger.info("Creating completion")
        
        try:
            # Get API key
            api_key = self._get_api_key(parameters, context)
            if not api_key:
                return {
                    "success": False,
                    "error": "OpenAI API key not found"
                }
            
            # Extract parameters
            prompt = parameters.get('prompt', '')
            model = parameters.get('model', 'text-davinci-003')
            max_tokens = parameters.get('max_tokens', 100)
            temperature = parameters.get('temperature', 0.7)
            
            # Handle prompt from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, str):
                    prompt = input_data
                elif isinstance(input_data, dict):
                    prompt = input_data.get('prompt', input_data.get('text', str(input_data)))
                else:
                    prompt = str(input_data)
            
            # Prepare request
            payload = {
                "model": model,
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
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
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/completions",
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
                    
                    result = await response.json()
                    
                    # Extract completion
                    choices = result.get('choices', [])
                    if not choices:
                        return {
                            "success": False,
                            "error": "No choices returned from OpenAI"
                        }
                    
                    completion = choices[0].get('text', '')
                    
                    return {
                        "success": True,
                        "completion": completion,
                        "model": result.get('model', model),
                        "usage": result.get('usage', {}),
                        "finish_reason": choices[0].get('finish_reason', 'unknown'),
                        "completion_length": len(completion),
                        "message": f"Completion created: {len(completion)} characters"
                    }
            
        except Exception as e:
            self.logger.error(f"Completion creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def moderate_content(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Moderate content using OpenAI moderation API"""
        self.logger.info("Moderating content")
        
        try:
            # Get API key
            api_key = self._get_api_key(parameters, context)
            if not api_key:
                return {
                    "success": False,
                    "error": "OpenAI API key not found"
                }
            
            # Extract parameters
            input_text = parameters.get('input', parameters.get('text', ''))
            
            # Handle input from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, str):
                    input_text = input_data
                elif isinstance(input_data, dict):
                    input_text = input_data.get('text', str(input_data))
                else:
                    input_text = str(input_data)
            
            # Prepare request
            payload = {
                "input": input_text
            }
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/moderations",
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
                    
                    result = await response.json()
                    
                    # Extract moderation result
                    results = result.get('results', [])
                    if not results:
                        return {
                            "success": False,
                            "error": "No moderation results returned"
                        }
                    
                    moderation = results[0]
                    
                    return {
                        "success": True,
                        "flagged": moderation.get('flagged', False),
                        "categories": moderation.get('categories', {}),
                        "category_scores": moderation.get('category_scores', {}),
                        "input_text": input_text,
                        "text_length": len(input_text),
                        "message": f"Content moderated: {'flagged' if moderation.get('flagged') else 'clean'}"
                    }
            
        except Exception as e:
            self.logger.error(f"Content moderation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def fine_tune_model(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fine-tune a model using OpenAI API"""
        self.logger.info("Fine-tuning model")
        
        try:
            # Get API key
            api_key = self._get_api_key(parameters, context)
            if not api_key:
                return {
                    "success": False,
                    "error": "OpenAI API key not found"
                }
            
            action = parameters.get('action', 'create')
            
            if action == 'create':
                return await self._create_fine_tune_job(parameters, api_key)
            elif action == 'list':
                return await self._list_fine_tune_jobs(parameters, api_key)
            elif action == 'get':
                return await self._get_fine_tune_job(parameters, api_key)
            elif action == 'cancel':
                return await self._cancel_fine_tune_job(parameters, api_key)
            else:
                return {
                    "success": False,
                    "error": f"Unknown fine-tuning action: {action}"
                }
            
        except Exception as e:
            self.logger.error(f"Fine-tuning failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_models(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """List available models"""
        self.logger.info("Listing models")
        
        try:
            # Get API key
            api_key = self._get_api_key(parameters, context)
            if not api_key:
                return {
                    "success": False,
                    "error": "OpenAI API key not found"
                }
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/models",
                    headers=headers
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"OpenAI API error: {response.status} - {error_text}",
                            "status_code": response.status
                        }
                    
                    result = await response.json()
                    models = result.get('data', [])
                    
                    return {
                        "success": True,
                        "models": models,
                        "model_count": len(models),
                        "message": f"Retrieved {len(models)} models"
                    }
            
        except Exception as e:
            self.logger.error(f"Model listing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_model(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get specific model information"""
        self.logger.info("Getting model info")
        
        try:
            # Get API key
            api_key = self._get_api_key(parameters, context)
            if not api_key:
                return {
                    "success": False,
                    "error": "OpenAI API key not found"
                }
            
            model_id = parameters.get('model_id', parameters.get('model', ''))
            if not model_id:
                return {
                    "success": False,
                    "error": "Model ID is required"
                }
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/models/{model_id}",
                    headers=headers
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"OpenAI API error: {response.status} - {error_text}",
                            "status_code": response.status
                        }
                    
                    result = await response.json()
                    
                    return {
                        "success": True,
                        "model": result,
                        "model_id": model_id,
                        "message": f"Retrieved model info for {model_id}"
                    }
            
        except Exception as e:
            self.logger.error(f"Model info retrieval failed: {e}")
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
    
    async def _create_fine_tune_job(self, parameters: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """Create a fine-tuning job"""
        
        training_file = parameters.get('training_file')
        model = parameters.get('model', 'gpt-3.5-turbo')
        
        if not training_file:
            return {
                "success": False,
                "error": "Training file is required for fine-tuning"
            }
        
        payload = {
            "training_file": training_file,
            "model": model
        }
        
        # Add optional parameters
        if 'validation_file' in parameters:
            payload['validation_file'] = parameters['validation_file']
        if 'hyperparameters' in parameters:
            payload['hyperparameters'] = parameters['hyperparameters']
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/fine_tuning/jobs",
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
                
                result = await response.json()
                
                return {
                    "success": True,
                    "job": result,
                    "job_id": result.get('id'),
                    "message": f"Fine-tuning job created: {result.get('id')}"
                }
    
    async def _list_fine_tune_jobs(self, parameters: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """List fine-tuning jobs"""
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_base}/fine_tuning/jobs",
                headers=headers
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"OpenAI API error: {response.status} - {error_text}",
                        "status_code": response.status
                    }
                
                result = await response.json()
                jobs = result.get('data', [])
                
                return {
                    "success": True,
                    "jobs": jobs,
                    "job_count": len(jobs),
                    "message": f"Retrieved {len(jobs)} fine-tuning jobs"
                }
    
    async def _get_fine_tune_job(self, parameters: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """Get fine-tuning job details"""
        
        job_id = parameters.get('job_id')
        if not job_id:
            return {
                "success": False,
                "error": "Job ID is required"
            }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_base}/fine_tuning/jobs/{job_id}",
                headers=headers
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"OpenAI API error: {response.status} - {error_text}",
                        "status_code": response.status
                    }
                
                result = await response.json()
                
                return {
                    "success": True,
                    "job": result,
                    "job_id": job_id,
                    "status": result.get('status'),
                    "message": f"Retrieved fine-tuning job: {job_id}"
                }
    
    async def _cancel_fine_tune_job(self, parameters: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """Cancel fine-tuning job"""
        
        job_id = parameters.get('job_id')
        if not job_id:
            return {
                "success": False,
                "error": "Job ID is required"
            }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/fine_tuning/jobs/{job_id}/cancel",
                headers=headers
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"OpenAI API error: {response.status} - {error_text}",
                        "status_code": response.status
                    }
                
                result = await response.json()
                
                return {
                    "success": True,
                    "job": result,
                    "job_id": job_id,
                    "message": f"Fine-tuning job cancelled: {job_id}"
                }
    
    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations"""
        return ['embeddings', 'completion', 'moderation', 'fine_tuning', 'list_models', 'get_model']
    
    def get_embedding_models(self) -> List[str]:
        """Get list of supported embedding models"""
        return ['text-embedding-ada-002', 'text-embedding-3-small', 'text-embedding-3-large']
    
    def get_completion_models(self) -> List[str]:
        """Get list of supported completion models"""
        return ['text-davinci-003', 'text-davinci-002', 'text-curie-001', 'text-babbage-001', 'text-ada-001']
