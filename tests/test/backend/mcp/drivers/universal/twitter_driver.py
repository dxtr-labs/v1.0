"""
Twitter/X Driver - Handles Twitter/X social media operations
Supports: tweets, users, followers, media, direct messages
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

class TwitterDriver(BaseUniversalDriver):
    """Universal driver for Twitter/X social media operations"""
    
    def __init__(self):
        super().__init__()
        self.service_name = "twitter_driver"
        self.supported_node_types = [
            'n8n-nodes-base.twitter',
            'twitter.tweet',
            'twitter.user',
            'twitter.follower',
            'twitter.media',
            'twitter.dm',
            'twitter.search'
        ]
        self.base_url = "https://api.twitter.com/2"
    
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
            bearer_token = self._get_bearer_token(parameters, context)
            if not bearer_token:
                return {
                    "success": False,
                    "error": "Twitter Bearer token is required"
                }
            
            resource = node_type.split('.')[-1] if '.' in node_type else 'tweet'
            operation = parameters.get('operation', 'get')
            
            if resource == 'tweet':
                return await self._handle_tweet_operations(operation, parameters, bearer_token, context)
            elif resource == 'user':
                return await self._handle_user_operations(operation, parameters, bearer_token, context)
            elif resource == 'follower':
                return await self._handle_follower_operations(operation, parameters, bearer_token, context)
            elif resource == 'media':
                return await self._handle_media_operations(operation, parameters, bearer_token, context)
            elif resource == 'dm':
                return await self._handle_dm_operations(operation, parameters, bearer_token, context)
            elif resource == 'search':
                return await self._handle_search_operations(operation, parameters, bearer_token, context)
            else:
                return await self._handle_tweet_operations(operation, parameters, bearer_token, context)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "node_type": node_type
            }
    
    async def _handle_tweet_operations(self, operation: str, parameters: Dict[str, Any], bearer_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle tweet operations"""
        self.logger.info(f"Handling Twitter tweet operation: {operation}")
        
        try:
            if operation == 'get':
                return await self._get_tweet(parameters, bearer_token, context)
            elif operation == 'create':
                return await self._create_tweet(parameters, bearer_token, context)
            elif operation == 'delete':
                return await self._delete_tweet(parameters, bearer_token, context)
            elif operation == 'like':
                return await self._like_tweet(parameters, bearer_token, context)
            elif operation == 'retweet':
                return await self._retweet(parameters, bearer_token, context)
            elif operation == 'getUserTweets':
                return await self._get_user_tweets(parameters, bearer_token, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown tweet operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"Tweet operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_user_operations(self, operation: str, parameters: Dict[str, Any], bearer_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle user operations"""
        self.logger.info(f"Handling Twitter user operation: {operation}")
        
        try:
            if operation == 'get':
                return await self._get_user(parameters, bearer_token, context)
            elif operation == 'getByUsername':
                return await self._get_user_by_username(parameters, bearer_token, context)
            elif operation == 'me':
                return await self._get_current_user(parameters, bearer_token, context)
            elif operation == 'follow':
                return await self._follow_user(parameters, bearer_token, context)
            elif operation == 'unfollow':
                return await self._unfollow_user(parameters, bearer_token, context)
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
    
    async def _handle_search_operations(self, operation: str, parameters: Dict[str, Any], bearer_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle search operations"""
        self.logger.info(f"Handling Twitter search operation: {operation}")
        
        try:
            if operation == 'tweets':
                return await self._search_tweets(parameters, bearer_token, context)
            elif operation == 'users':
                return await self._search_users(parameters, bearer_token, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown search operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"Search operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_tweet(self, parameters: Dict[str, Any], bearer_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get a specific tweet"""
        tweet_id = parameters.get('tweet_id', '')
        
        if not tweet_id:
            return {
                "success": False,
                "error": "Tweet ID is required"
            }
        
        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'tweet.fields': 'author_id,created_at,public_metrics,text,attachments',
            'expansions': 'author_id'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/tweets/{tweet_id}", headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "message": "Tweet retrieved successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('detail', 'Unknown error')
                    }
    
    async def _create_tweet(self, parameters: Dict[str, Any], bearer_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new tweet"""
        text = parameters.get('text', '')
        reply_to_tweet_id = parameters.get('reply_to_tweet_id', '')
        media_ids = parameters.get('media_ids', [])
        
        if not text:
            return {
                "success": False,
                "error": "Tweet text is required"
            }
        
        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'text': text
        }
        
        if reply_to_tweet_id:
            data['reply'] = {
                'in_reply_to_tweet_id': reply_to_tweet_id
            }
        
        if media_ids:
            data['media'] = {
                'media_ids': media_ids
            }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/tweets", headers=headers, json=data) as response:
                if response.status == 201:
                    response_data = await response.json()
                    return {
                        "success": True,
                        "data": response_data,
                        "message": "Tweet created successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('detail', 'Unknown error')
                    }
    
    async def _delete_tweet(self, parameters: Dict[str, Any], bearer_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Delete a tweet"""
        tweet_id = parameters.get('tweet_id', '')
        
        if not tweet_id:
            return {
                "success": False,
                "error": "Tweet ID is required"
            }
        
        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{self.base_url}/tweets/{tweet_id}", headers=headers) as response:
                if response.status == 200:
                    return {
                        "success": True,
                        "message": "Tweet deleted successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('detail', 'Unknown error')
                    }
    
    async def _like_tweet(self, parameters: Dict[str, Any], bearer_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Like a tweet"""
        tweet_id = parameters.get('tweet_id', '')
        user_id = parameters.get('user_id', '')
        
        if not tweet_id or not user_id:
            return {
                "success": False,
                "error": "Tweet ID and User ID are required"
            }
        
        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'tweet_id': tweet_id
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/users/{user_id}/likes", headers=headers, json=data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return {
                        "success": True,
                        "data": response_data,
                        "message": "Tweet liked successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('detail', 'Unknown error')
                    }
    
    async def _retweet(self, parameters: Dict[str, Any], bearer_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Retweet a tweet"""
        tweet_id = parameters.get('tweet_id', '')
        user_id = parameters.get('user_id', '')
        
        if not tweet_id or not user_id:
            return {
                "success": False,
                "error": "Tweet ID and User ID are required"
            }
        
        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'tweet_id': tweet_id
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/users/{user_id}/retweets", headers=headers, json=data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return {
                        "success": True,
                        "data": response_data,
                        "message": "Tweet retweeted successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('detail', 'Unknown error')
                    }
    
    async def _get_user_tweets(self, parameters: Dict[str, Any], bearer_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tweets from a specific user"""
        user_id = parameters.get('user_id', '')
        max_results = parameters.get('max_results', 10)
        exclude_retweets = parameters.get('exclude_retweets', False)
        
        if not user_id:
            return {
                "success": False,
                "error": "User ID is required"
            }
        
        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'tweet.fields': 'author_id,created_at,public_metrics,text',
            'max_results': min(max_results, 100)
        }
        
        if exclude_retweets:
            params['exclude'] = 'retweets'
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/users/{user_id}/tweets", headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "count": len(data.get('data', [])),
                        "message": "User tweets retrieved successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('detail', 'Unknown error')
                    }
    
    async def _get_user(self, parameters: Dict[str, Any], bearer_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get a specific user by ID"""
        user_id = parameters.get('user_id', '')
        
        if not user_id:
            return {
                "success": False,
                "error": "User ID is required"
            }
        
        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'user.fields': 'created_at,description,public_metrics,verified'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/users/{user_id}", headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "message": "User retrieved successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('detail', 'Unknown error')
                    }
    
    async def _get_user_by_username(self, parameters: Dict[str, Any], bearer_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get a user by username"""
        username = parameters.get('username', '')
        
        if not username:
            return {
                "success": False,
                "error": "Username is required"
            }
        
        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'user.fields': 'created_at,description,public_metrics,verified'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/users/by/username/{username}", headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "message": "User retrieved successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('detail', 'Unknown error')
                    }
    
    async def _get_current_user(self, parameters: Dict[str, Any], bearer_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get current authenticated user"""
        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'user.fields': 'created_at,description,public_metrics,verified'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/users/me", headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "message": "Current user retrieved successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('detail', 'Unknown error')
                    }
    
    async def _follow_user(self, parameters: Dict[str, Any], bearer_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Follow a user"""
        user_id = parameters.get('user_id', '')
        target_user_id = parameters.get('target_user_id', '')
        
        if not user_id or not target_user_id:
            return {
                "success": False,
                "error": "User ID and Target User ID are required"
            }
        
        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'target_user_id': target_user_id
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/users/{user_id}/following", headers=headers, json=data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return {
                        "success": True,
                        "data": response_data,
                        "message": "User followed successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('detail', 'Unknown error')
                    }
    
    async def _search_tweets(self, parameters: Dict[str, Any], bearer_token: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Search for tweets"""
        query = parameters.get('query', '')
        max_results = parameters.get('max_results', 10)
        result_type = parameters.get('result_type', 'mixed')  # recent, popular, mixed
        
        if not query:
            return {
                "success": False,
                "error": "Search query is required"
            }
        
        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'query': query,
            'tweet.fields': 'author_id,created_at,public_metrics,text',
            'max_results': min(max_results, 100)
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/tweets/search/recent", headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "count": len(data.get('data', [])),
                        "query": query,
                        "message": "Tweet search completed successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('detail', 'Unknown error')
                    }
    
    def _get_bearer_token(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Optional[str]:
        """Get Twitter Bearer token"""
        
        # Try parameters first
        if 'bearer_token' in parameters:
            return parameters['bearer_token']
        
        # Try context credentials
        if context and 'credentials' in context:
            credentials = context['credentials']
            if 'twitter' in credentials:
                return credentials['twitter'].get('bearer_token', '')
        
        # Try environment variables
        return os.getenv('TWITTER_BEARER_TOKEN', '')
    
    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations"""
        return [
            'get', 'create', 'delete', 'like', 'retweet',
            'getByUsername', 'me', 'follow', 'unfollow',
            'getUserTweets', 'tweets', 'users'
        ]
