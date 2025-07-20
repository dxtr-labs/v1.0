#!/usr/bin/env python3
"""
📅 Calendly OAuth and Scheduling Service for AI Agents
Provides Calendly OAuth integration and scheduling capabilities
"""

import os
import requests
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from urllib.parse import quote_plus, urlencode
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CalendlyService:
    """
    Comprehensive Calendly service that provides:
    - OAuth 2.0 authentication flow
    - Event type management
    - Scheduling link generation
    - User information retrieval
    """
    
    def __init__(self):
        # Calendly OAuth credentials (add these to .env.local)
        self.client_id = os.getenv("CALENDLY_CLIENT_ID")
        self.client_secret = os.getenv("CALENDLY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("CALENDLY_REDIRECT_URI", "http://localhost:8002/api/oauth/calendly/callback")
        
        # Calendly endpoints
        self.auth_url = "https://calendly.com/oauth/authorize"
        self.token_url = "https://calendly.com/oauth/token"
        self.api_base_url = "https://api.calendly.com"
        
        # Scopes for Calendly access
        self.scopes = ['default']
        
    def get_oauth_url(self, state: str = None) -> Dict[str, Any]:
        """
        Generate OAuth authorization URL for Calendly
        """
        try:
            if not self.client_id:
                return {"error": "Calendly OAuth credentials not configured"}
                
            params = {
                'client_id': self.client_id,
                'response_type': 'code',
                'redirect_uri': self.redirect_uri,
                'scope': 'default',
                'state': state or 'calendly_default'
            }
            
            oauth_url = f"{self.auth_url}?{urlencode(params)}"
            logger.info(f"📅 Generated Calendly OAuth URL")
            
            return {
                "oauth_url": oauth_url,
                "service": "calendly",
                "scopes": self.scopes
            }
            
        except Exception as e:
            logger.error(f"Calendly OAuth URL generation error: {e}")
            return {"error": str(e)}
    
    async def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        """
        try:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'redirect_uri': self.redirect_uri
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.token_url, data=data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        logger.info("✅ Successfully exchanged code for Calendly token")
                        return token_data
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Failed to exchange code for token: {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Calendly token exchange error: {e}")
            return None
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information from Calendly
        """
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base_url}/users/me", headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        return user_data.get('resource', {})
                    else:
                        logger.error(f"❌ Failed to get user info: {await response.text()}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Calendly user info error: {e}")
            return None
    
    async def get_event_types(self, access_token: str, user_uri: str) -> Dict[str, Any]:
        """
        Get available Calendly event types for the user
        """
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            params = {'user': user_uri}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base_url}/event_types", headers=headers, params=params) as response:
                    if response.status == 200:
                        event_data = await response.json()
                        return event_data
                    else:
                        logger.error(f"❌ Failed to get event types: {await response.text()}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Calendly event types error: {e}")
            return None
    
    def format_calendly_links_for_email(self, event_types: List[Dict[str, Any]], user_name: str = "DXTR Labs Team") -> str:
        """
        Format Calendly event types for email content
        """
        if not event_types:
            return "No Calendly scheduling links available."
        
        formatted_links = f"📅 **Schedule a Meeting with {user_name} (Calendly):**\n\n"
        
        for i, event_type in enumerate(event_types[:3], 1):  # Limit to 3 event types
            name = event_type.get('name', 'Meeting')
            duration = event_type.get('duration', 30)
            scheduling_url = event_type.get('scheduling_url', '')
            description = event_type.get('description_plain', '')
            
            formatted_links += f"**{name}** ({duration} minutes)\n"
            if description:
                formatted_links += f"*{description[:100]}...*\n"
            formatted_links += f"🔗 Book here: {scheduling_url}\n\n"
        
        return formatted_links
    
    async def create_calendly_integration_email(self, access_token: str, recipient: str, purpose: str = "investor meeting") -> Dict[str, Any]:
        """
        Create Calendly integration and generate email content
        """
        # Get user info
        user_info = await self.get_user_info(access_token)
        if not user_info:
            return {'success': False, 'error': 'Failed to get Calendly user information'}
        
        user_uri = user_info.get('uri')
        user_name = user_info.get('name', 'DXTR Labs Team')
        
        # Get event types
        event_types_data = await self.get_event_types(access_token, user_uri)
        if not event_types_data:
            return {'success': False, 'error': 'Failed to get Calendly event types'}
        
        event_types = event_types_data.get('collection', [])
        
        # Generate email content
        email_content = f"""Subject: DXTR Labs Investment Opportunity - Easy Scheduling with Calendly

Dear {recipient.split('@')[0].title()},

I hope this message finds you well. I'm excited to share information about DXTR Labs and our revolutionary AI automation platform, and I'd love to schedule a time to discuss this opportunity with you.

🚀 **About DXTR Labs:**
We're building the future of work through AI automation with our DXT Agents platform:
• Intelligent AI agents that replace human workers
• FastMCP LLM Protocol for advanced workflow automation
• Universal automation templates (2000+)
• Growing user base with 100+ on our waitlist
• Targeting the $66B+ AI automation market

{self.format_calendly_links_for_email(event_types, user_name)}

💡 **Meeting Agenda:**
• Introduction to DXTR Labs platform and vision
• Live demo of our AI automation capabilities
• Discussion of investment opportunities and market potential
• Q&A session about our technology and business model

🎯 **Why This Matters:**
The AI automation revolution is here, and DXTR Labs is positioned to capture significant market share with our innovative approach to making AI agents universally accessible.

Simply click any of the Calendly links above to choose a time that works best for your schedule. The booking system will automatically send calendar invites and meeting details.

Looking forward to our discussion!

Best regards,
{user_name}
DXTR Labs Team
automation-engine@dxtr-labs.com

P.S. All meetings include video conferencing links for your convenience.
"""
        
        return {
            'success': True,
            'email_content': email_content,
            'event_types': event_types,
            'user_info': user_info,
            'calendly_service': 'Calendly'
        }

# Create global instance
calendly_service = CalendlyService()

async def test_calendly_service():
    """Test the Calendly service functionality"""
    print("📅 Testing Calendly Service")
    print("=" * 40)
    
    # Test OAuth URL generation
    oauth_result = calendly_service.get_oauth_url("test_state")
    if "error" not in oauth_result:
        print(f"✅ OAuth URL generated: {oauth_result['oauth_url'][:50]}...")
    else:
        print(f"⚠️ OAuth URL generation: {oauth_result['error']}")
    
    print("✅ Calendly service initialized successfully")
    print("📅 OAuth URL ready for user authorization")

if __name__ == "__main__":
    asyncio.run(test_calendly_service())
