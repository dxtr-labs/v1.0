"""
Trello Driver - Handles Trello project management operations
Supports: boards, lists, cards, members, attachments
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

class TrelloDriver(BaseUniversalDriver):
    """Universal driver for Trello project management operations"""
    
    def __init__(self):
        super().__init__()
        self.service_name = "trello_driver"
        self.supported_node_types = [
            'n8n-nodes-base.trello',
            'trello.board',
            'trello.list',
            'trello.card',
            'trello.member',
            'trello.attachment'
        ]
        self.base_url = "https://api.trello.com/1"
    
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
            # Get API credentials
            api_key, api_token = self._get_api_credentials(parameters, context)
            if not api_key or not api_token:
                return {
                    "success": False,
                    "error": "Trello API key and token are required"
                }
            
            resource = node_type.split('.')[-1] if '.' in node_type else 'card'
            operation = parameters.get('operation', 'get')
            
            if resource == 'board':
                return await self._handle_board_operations(operation, parameters, api_key, api_token, context)
            elif resource == 'list':
                return await self._handle_list_operations(operation, parameters, api_key, api_token, context)
            elif resource == 'card':
                return await self._handle_card_operations(operation, parameters, api_key, api_token, context)
            elif resource == 'member':
                return await self._handle_member_operations(operation, parameters, api_key, api_token, context)
            elif resource == 'attachment':
                return await self._handle_attachment_operations(operation, parameters, api_key, api_token, context)
            else:
                return await self._handle_card_operations(operation, parameters, api_key, api_token, context)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "node_type": node_type
            }
    
    async def _handle_board_operations(self, operation: str, parameters: Dict[str, Any], api_key: str, api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle board operations"""
        self.logger.info(f"Handling Trello board operation: {operation}")
        
        try:
            if operation == 'get':
                return await self._get_board(parameters, api_key, api_token, context)
            elif operation == 'getAll':
                return await self._get_all_boards(parameters, api_key, api_token, context)
            elif operation == 'create':
                return await self._create_board(parameters, api_key, api_token, context)
            elif operation == 'update':
                return await self._update_board(parameters, api_key, api_token, context)
            elif operation == 'delete':
                return await self._delete_board(parameters, api_key, api_token, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown board operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"Board operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_list_operations(self, operation: str, parameters: Dict[str, Any], api_key: str, api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle list operations"""
        self.logger.info(f"Handling Trello list operation: {operation}")
        
        try:
            if operation == 'get':
                return await self._get_list(parameters, api_key, api_token, context)
            elif operation == 'getAll':
                return await self._get_all_lists(parameters, api_key, api_token, context)
            elif operation == 'create':
                return await self._create_list(parameters, api_key, api_token, context)
            elif operation == 'update':
                return await self._update_list(parameters, api_key, api_token, context)
            elif operation == 'archive':
                return await self._archive_list(parameters, api_key, api_token, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown list operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"List operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_card_operations(self, operation: str, parameters: Dict[str, Any], api_key: str, api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle card operations"""
        self.logger.info(f"Handling Trello card operation: {operation}")
        
        try:
            if operation == 'get':
                return await self._get_card(parameters, api_key, api_token, context)
            elif operation == 'getAll':
                return await self._get_all_cards(parameters, api_key, api_token, context)
            elif operation == 'create':
                return await self._create_card(parameters, api_key, api_token, context)
            elif operation == 'update':
                return await self._update_card(parameters, api_key, api_token, context)
            elif operation == 'delete':
                return await self._delete_card(parameters, api_key, api_token, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown card operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"Card operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_member_operations(self, operation: str, parameters: Dict[str, Any], api_key: str, api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle member operations"""
        self.logger.info(f"Handling Trello member operation: {operation}")
        
        try:
            if operation == 'get':
                return await self._get_member(parameters, api_key, api_token, context)
            elif operation == 'getAll':
                return await self._get_all_members(parameters, api_key, api_token, context)
            elif operation == 'me':
                return await self._get_current_member(parameters, api_key, api_token, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown member operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"Member operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_attachment_operations(self, operation: str, parameters: Dict[str, Any], api_key: str, api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle attachment operations"""
        self.logger.info(f"Handling Trello attachment operation: {operation}")
        
        try:
            if operation == 'get':
                return await self._get_attachment(parameters, api_key, api_token, context)
            elif operation == 'getAll':
                return await self._get_all_attachments(parameters, api_key, api_token, context)
            elif operation == 'create':
                return await self._create_attachment(parameters, api_key, api_token, context)
            elif operation == 'delete':
                return await self._delete_attachment(parameters, api_key, api_token, context)
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
    
    async def _get_board(self, parameters: Dict[str, Any], api_key: str, api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get a specific board"""
        board_id = parameters.get('board_id', '')
        
        if not board_id:
            return {
                "success": False,
                "error": "Board ID is required"
            }
        
        params = {
            'key': api_key,
            'token': api_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/boards/{board_id}", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "message": "Board retrieved successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('message', 'Unknown error')
                    }
    
    async def _get_all_boards(self, parameters: Dict[str, Any], api_key: str, api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get all boards for the authenticated user"""
        member_id = parameters.get('member_id', 'me')
        
        params = {
            'key': api_key,
            'token': api_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/members/{member_id}/boards", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "count": len(data),
                        "message": "Boards retrieved successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('message', 'Unknown error')
                    }
    
    async def _create_board(self, parameters: Dict[str, Any], api_key: str, api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new board"""
        name = parameters.get('name', '')
        desc = parameters.get('desc', '')
        visibility = parameters.get('visibility', 'private')
        
        if not name:
            return {
                "success": False,
                "error": "Board name is required"
            }
        
        params = {
            'key': api_key,
            'token': api_token,
            'name': name,
            'desc': desc,
            'prefs_permissionLevel': visibility
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/boards", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "message": "Board created successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('message', 'Unknown error')
                    }
    
    async def _update_board(self, parameters: Dict[str, Any], api_key: str, api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update an existing board"""
        board_id = parameters.get('board_id', '')
        name = parameters.get('name', '')
        desc = parameters.get('desc', '')
        
        if not board_id:
            return {
                "success": False,
                "error": "Board ID is required"
            }
        
        params = {
            'key': api_key,
            'token': api_token
        }
        
        if name:
            params['name'] = name
        if desc:
            params['desc'] = desc
        
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{self.base_url}/boards/{board_id}", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "message": "Board updated successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('message', 'Unknown error')
                    }
    
    async def _delete_board(self, parameters: Dict[str, Any], api_key: str, api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Delete a board"""
        board_id = parameters.get('board_id', '')
        
        if not board_id:
            return {
                "success": False,
                "error": "Board ID is required"
            }
        
        params = {
            'key': api_key,
            'token': api_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{self.base_url}/boards/{board_id}", params=params) as response:
                if response.status == 200:
                    return {
                        "success": True,
                        "message": "Board deleted successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('message', 'Unknown error')
                    }
    
    async def _create_list(self, parameters: Dict[str, Any], api_key: str, api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new list"""
        name = parameters.get('name', '')
        board_id = parameters.get('board_id', '')
        position = parameters.get('position', 'bottom')
        
        if not name:
            return {
                "success": False,
                "error": "List name is required"
            }
        
        if not board_id:
            return {
                "success": False,
                "error": "Board ID is required"
            }
        
        params = {
            'key': api_key,
            'token': api_token,
            'name': name,
            'idBoard': board_id,
            'pos': position
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/lists", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "message": "List created successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('message', 'Unknown error')
                    }
    
    async def _get_all_lists(self, parameters: Dict[str, Any], api_key: str, api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get all lists for a board"""
        board_id = parameters.get('board_id', '')
        
        if not board_id:
            return {
                "success": False,
                "error": "Board ID is required"
            }
        
        params = {
            'key': api_key,
            'token': api_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/boards/{board_id}/lists", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "count": len(data),
                        "message": "Lists retrieved successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('message', 'Unknown error')
                    }
    
    async def _create_card(self, parameters: Dict[str, Any], api_key: str, api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new card"""
        name = parameters.get('name', '')
        list_id = parameters.get('list_id', '')
        desc = parameters.get('desc', '')
        due_date = parameters.get('due_date', '')
        
        if not name:
            return {
                "success": False,
                "error": "Card name is required"
            }
        
        if not list_id:
            return {
                "success": False,
                "error": "List ID is required"
            }
        
        params = {
            'key': api_key,
            'token': api_token,
            'name': name,
            'idList': list_id,
            'desc': desc
        }
        
        if due_date:
            params['due'] = due_date
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/cards", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "message": "Card created successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('message', 'Unknown error')
                    }
    
    async def _get_card(self, parameters: Dict[str, Any], api_key: str, api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get a specific card"""
        card_id = parameters.get('card_id', '')
        
        if not card_id:
            return {
                "success": False,
                "error": "Card ID is required"
            }
        
        params = {
            'key': api_key,
            'token': api_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/cards/{card_id}", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "message": "Card retrieved successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('message', 'Unknown error')
                    }
    
    async def _get_all_cards(self, parameters: Dict[str, Any], api_key: str, api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get all cards for a list or board"""
        list_id = parameters.get('list_id', '')
        board_id = parameters.get('board_id', '')
        
        if not list_id and not board_id:
            return {
                "success": False,
                "error": "List ID or Board ID is required"
            }
        
        params = {
            'key': api_key,
            'token': api_token
        }
        
        if list_id:
            url = f"{self.base_url}/lists/{list_id}/cards"
        else:
            url = f"{self.base_url}/boards/{board_id}/cards"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "count": len(data),
                        "message": "Cards retrieved successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('message', 'Unknown error')
                    }
    
    async def _update_card(self, parameters: Dict[str, Any], api_key: str, api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update an existing card"""
        card_id = parameters.get('card_id', '')
        name = parameters.get('name', '')
        desc = parameters.get('desc', '')
        due_date = parameters.get('due_date', '')
        list_id = parameters.get('list_id', '')
        
        if not card_id:
            return {
                "success": False,
                "error": "Card ID is required"
            }
        
        params = {
            'key': api_key,
            'token': api_token
        }
        
        if name:
            params['name'] = name
        if desc:
            params['desc'] = desc
        if due_date:
            params['due'] = due_date
        if list_id:
            params['idList'] = list_id
        
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{self.base_url}/cards/{card_id}", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "message": "Card updated successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('message', 'Unknown error')
                    }
    
    async def _delete_card(self, parameters: Dict[str, Any], api_key: str, api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Delete a card"""
        card_id = parameters.get('card_id', '')
        
        if not card_id:
            return {
                "success": False,
                "error": "Card ID is required"
            }
        
        params = {
            'key': api_key,
            'token': api_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{self.base_url}/cards/{card_id}", params=params) as response:
                if response.status == 200:
                    return {
                        "success": True,
                        "message": "Card deleted successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('message', 'Unknown error')
                    }
    
    async def _get_current_member(self, parameters: Dict[str, Any], api_key: str, api_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get current member information"""
        params = {
            'key': api_key,
            'token': api_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/members/me", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "message": "Member information retrieved successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('message', 'Unknown error')
                    }
    
    def _get_api_credentials(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> tuple:
        """Get Trello API credentials"""
        
        # Try parameters first
        api_key = parameters.get('api_key', '')
        api_token = parameters.get('api_token', '')
        
        if api_key and api_token:
            return api_key, api_token
        
        # Try context credentials
        if context and 'credentials' in context:
            credentials = context['credentials']
            if 'trello' in credentials:
                cred = credentials['trello']
                api_key = cred.get('api_key', '')
                api_token = cred.get('api_token', '')
                if api_key and api_token:
                    return api_key, api_token
        
        # Try environment variables
        api_key = os.getenv('TRELLO_API_KEY', '')
        api_token = os.getenv('TRELLO_API_TOKEN', '')
        
        return api_key, api_token
    
    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations"""
        return [
            'get', 'getAll', 'create', 'update', 'delete', 'archive',
            'me'
        ]
