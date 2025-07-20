"""
Asana Driver - Handles Asana project management operations
Supports: projects, tasks, teams, users, attachments
"""

import logging
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Union
import json
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# Add the parent directories to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(backend_dir)
mcp_dir = os.path.join(backend_dir, 'mcp')
sys.path.append(mcp_dir)

from mcp.universal_driver_manager import BaseUniversalDriver

class AsanaDriver(BaseUniversalDriver):
    """Universal driver for Asana project management operations"""
    
    def __init__(self):
        super().__init__()
        self.service_name = "asana_driver"
        self.supported_node_types = [
            'n8n-nodes-base.asana',
            'asana.project',
            'asana.task',
            'asana.team',
            'asana.user',
            'asana.attachment'
        ]
        self.base_url = "https://app.asana.com/api/1.0"
    
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
            # Get API token
            api_token = self._get_api_token(parameters, context)
            if not api_token:
                return {
                    "success": False,
                    "error": "Asana API token not found"
                }
            
            resource = node_type.split('.')[-1] if '.' in node_type else 'task'
            operation = parameters.get('operation', 'get')
            
            if resource == 'project':
                return await self._handle_project_operations(operation, parameters, api_token, context)
            elif resource == 'task':
                return await self._handle_task_operations(operation, parameters, api_token, context)
            elif resource == 'team':
                return await self._handle_team_operations(operation, parameters, api_token, context)
            elif resource == 'user':
                return await self._handle_user_operations(operation, parameters, api_token, context)
            elif resource == 'attachment':
                return await self._handle_attachment_operations(operation, parameters, api_token, context)
            else:
                return await self._handle_task_operations(operation, parameters, api_token, context)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "node_type": node_type
            }
    
    async def _handle_project_operations(self, operation: str, parameters: Dict[str, Any], api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle project operations"""
        self.logger.info(f"Handling Asana project operation: {operation}")
        
        try:
            if operation == 'get':
                return await self._get_project(parameters, api_token, context)
            elif operation == 'getAll':
                return await self._get_all_projects(parameters, api_token, context)
            elif operation == 'create':
                return await self._create_project(parameters, api_token, context)
            elif operation == 'update':
                return await self._update_project(parameters, api_token, context)
            elif operation == 'delete':
                return await self._delete_project(parameters, api_token, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown project operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"Project operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_task_operations(self, operation: str, parameters: Dict[str, Any], api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle task operations"""
        self.logger.info(f"Handling Asana task operation: {operation}")
        
        try:
            if operation == 'get':
                return await self._get_task(parameters, api_token, context)
            elif operation == 'getAll':
                return await self._get_all_tasks(parameters, api_token, context)
            elif operation == 'create':
                return await self._create_task(parameters, api_token, context)
            elif operation == 'update':
                return await self._update_task(parameters, api_token, context)
            elif operation == 'delete':
                return await self._delete_task(parameters, api_token, context)
            elif operation == 'search':
                return await self._search_tasks(parameters, api_token, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown task operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"Task operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_team_operations(self, operation: str, parameters: Dict[str, Any], api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle team operations"""
        self.logger.info(f"Handling Asana team operation: {operation}")
        
        try:
            if operation == 'get':
                return await self._get_team(parameters, api_token, context)
            elif operation == 'getAll':
                return await self._get_all_teams(parameters, api_token, context)
            elif operation == 'getUsers':
                return await self._get_team_users(parameters, api_token, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown team operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"Team operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_user_operations(self, operation: str, parameters: Dict[str, Any], api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle user operations"""
        self.logger.info(f"Handling Asana user operation: {operation}")
        
        try:
            if operation == 'get':
                return await self._get_user(parameters, api_token, context)
            elif operation == 'getAll':
                return await self._get_all_users(parameters, api_token, context)
            elif operation == 'me':
                return await self._get_current_user(parameters, api_token, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown user operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"User operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_attachment_operations(self, operation: str, parameters: Dict[str, Any], api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle attachment operations"""
        self.logger.info(f"Handling Asana attachment operation: {operation}")
        
        try:
            if operation == 'get':
                return await self._get_attachment(parameters, api_token, context)
            elif operation == 'getAll':
                return await self._get_all_attachments(parameters, api_token, context)
            elif operation == 'upload':
                return await self._upload_attachment(parameters, api_token, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown attachment operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"Attachment operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_project(self, parameters: Dict[str, Any], api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get a specific project"""
        project_id = parameters.get('project_id', '')
        
        if not project_id:
            return {
                "success": False,
                "error": "Project ID is required"
            }
        
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/projects/{project_id}", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data['data'],
                        "message": "Project retrieved successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('errors', [{'message': 'Unknown error'}])[0]['message']
                    }
    
    async def _get_all_projects(self, parameters: Dict[str, Any], api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get all projects"""
        workspace_id = parameters.get('workspace_id', '')
        team_id = parameters.get('team_id', '')
        
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        params = {}
        if workspace_id:
            params['workspace'] = workspace_id
        if team_id:
            params['team'] = team_id
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/projects", headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data['data'],
                        "count": len(data['data']),
                        "message": "Projects retrieved successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('errors', [{'message': 'Unknown error'}])[0]['message']
                    }
    
    async def _create_project(self, parameters: Dict[str, Any], api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new project"""
        name = parameters.get('name', '')
        workspace_id = parameters.get('workspace_id', '')
        team_id = parameters.get('team_id', '')
        notes = parameters.get('notes', '')
        color = parameters.get('color', '')
        
        if not name:
            return {
                "success": False,
                "error": "Project name is required"
            }
        
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'data': {
                'name': name,
                'notes': notes,
                'color': color
            }
        }
        
        if workspace_id:
            data['data']['workspace'] = workspace_id
        if team_id:
            data['data']['team'] = team_id
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/projects", headers=headers, json=data) as response:
                if response.status == 201:
                    response_data = await response.json()
                    return {
                        "success": True,
                        "data": response_data['data'],
                        "message": "Project created successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('errors', [{'message': 'Unknown error'}])[0]['message']
                    }
    
    async def _update_project(self, parameters: Dict[str, Any], api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update an existing project"""
        project_id = parameters.get('project_id', '')
        name = parameters.get('name', '')
        notes = parameters.get('notes', '')
        color = parameters.get('color', '')
        
        if not project_id:
            return {
                "success": False,
                "error": "Project ID is required"
            }
        
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        data = {'data': {}}
        if name:
            data['data']['name'] = name
        if notes:
            data['data']['notes'] = notes
        if color:
            data['data']['color'] = color
        
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{self.base_url}/projects/{project_id}", headers=headers, json=data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return {
                        "success": True,
                        "data": response_data['data'],
                        "message": "Project updated successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('errors', [{'message': 'Unknown error'}])[0]['message']
                    }
    
    async def _delete_project(self, parameters: Dict[str, Any], api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Delete a project"""
        project_id = parameters.get('project_id', '')
        
        if not project_id:
            return {
                "success": False,
                "error": "Project ID is required"
            }
        
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{self.base_url}/projects/{project_id}", headers=headers) as response:
                if response.status == 200:
                    return {
                        "success": True,
                        "message": "Project deleted successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('errors', [{'message': 'Unknown error'}])[0]['message']
                    }
    
    async def _create_task(self, parameters: Dict[str, Any], api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new task"""
        name = parameters.get('name', '')
        project_id = parameters.get('project_id', '')
        assignee = parameters.get('assignee', '')
        notes = parameters.get('notes', '')
        due_date = parameters.get('due_date', '')
        
        if not name:
            return {
                "success": False,
                "error": "Task name is required"
            }
        
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'data': {
                'name': name,
                'notes': notes
            }
        }
        
        if project_id:
            data['data']['projects'] = [project_id]
        if assignee:
            data['data']['assignee'] = assignee
        if due_date:
            data['data']['due_on'] = due_date
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/tasks", headers=headers, json=data) as response:
                if response.status == 201:
                    response_data = await response.json()
                    return {
                        "success": True,
                        "data": response_data['data'],
                        "message": "Task created successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('errors', [{'message': 'Unknown error'}])[0]['message']
                    }
    
    async def _get_task(self, parameters: Dict[str, Any], api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get a specific task"""
        task_id = parameters.get('task_id', '')
        
        if not task_id:
            return {
                "success": False,
                "error": "Task ID is required"
            }
        
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/tasks/{task_id}", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data['data'],
                        "message": "Task retrieved successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('errors', [{'message': 'Unknown error'}])[0]['message']
                    }
    
    async def _get_all_tasks(self, parameters: Dict[str, Any], api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get all tasks"""
        project_id = parameters.get('project_id', '')
        assignee = parameters.get('assignee', '')
        workspace_id = parameters.get('workspace_id', '')
        
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        params = {}
        if project_id:
            params['project'] = project_id
        if assignee:
            params['assignee'] = assignee
        if workspace_id:
            params['workspace'] = workspace_id
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/tasks", headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data['data'],
                        "count": len(data['data']),
                        "message": "Tasks retrieved successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('errors', [{'message': 'Unknown error'}])[0]['message']
                    }
    
    async def _update_task(self, parameters: Dict[str, Any], api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update an existing task"""
        task_id = parameters.get('task_id', '')
        name = parameters.get('name', '')
        notes = parameters.get('notes', '')
        assignee = parameters.get('assignee', '')
        due_date = parameters.get('due_date', '')
        completed = parameters.get('completed', None)
        
        if not task_id:
            return {
                "success": False,
                "error": "Task ID is required"
            }
        
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        data = {'data': {}}
        if name:
            data['data']['name'] = name
        if notes:
            data['data']['notes'] = notes
        if assignee:
            data['data']['assignee'] = assignee
        if due_date:
            data['data']['due_on'] = due_date
        if completed is not None:
            data['data']['completed'] = completed
        
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{self.base_url}/tasks/{task_id}", headers=headers, json=data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return {
                        "success": True,
                        "data": response_data['data'],
                        "message": "Task updated successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('errors', [{'message': 'Unknown error'}])[0]['message']
                    }
    
    async def _delete_task(self, parameters: Dict[str, Any], api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Delete a task"""
        task_id = parameters.get('task_id', '')
        
        if not task_id:
            return {
                "success": False,
                "error": "Task ID is required"
            }
        
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{self.base_url}/tasks/{task_id}", headers=headers) as response:
                if response.status == 200:
                    return {
                        "success": True,
                        "message": "Task deleted successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('errors', [{'message': 'Unknown error'}])[0]['message']
                    }
    
    async def _search_tasks(self, parameters: Dict[str, Any], api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Search for tasks"""
        text = parameters.get('text', '')
        workspace_id = parameters.get('workspace_id', '')
        
        if not text:
            return {
                "success": False,
                "error": "Search text is required"
            }
        
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'text': text,
            'resource_type': 'task'
        }
        
        if workspace_id:
            params['workspace'] = workspace_id
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/search", headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data['data'],
                        "count": len(data['data']),
                        "search_text": text,
                        "message": "Search completed successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('errors', [{'message': 'Unknown error'}])[0]['message']
                    }
    
    async def _get_current_user(self, parameters: Dict[str, Any], api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get current user information"""
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/users/me", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data['data'],
                        "message": "User information retrieved successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('errors', [{'message': 'Unknown error'}])[0]['message']
                    }
    
    def _get_api_token(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Optional[str]:
        """Get Asana API token"""
        
        # Try parameters first
        if 'api_token' in parameters:
            return parameters['api_token']
        
        # Try context credentials
        if context and 'credentials' in context:
            credentials = context['credentials']
            if 'asana' in credentials:
                return credentials['asana'].get('api_token', '')
        
        # Try environment variables
        return os.getenv('ASANA_API_TOKEN', '')
    
    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations"""
        return [
            'get', 'getAll', 'create', 'update', 'delete', 'search',
            'me', 'getUsers', 'upload'
        ]
