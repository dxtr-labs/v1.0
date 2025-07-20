#!/usr/bin/env python3
"""
🔗 Zoom OAuth and Meeting Service for AI Agents
Provides Zoom OAuth integration and meeting creation capabilities
"""

import os
import requests
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from urllib.parse import quote_plus, urlencode
import json
import base64
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ZoomService:
    """
    Comprehensive Zoom service that provides:
    - OAuth 2.0 authentication flow
    - Meeting creation and management
    - User authorization
    - Meeting link generation
    """
    
    def __init__(self):
        # Zoom OAuth credentials (add these to .env.local)
        self.zoom_client_id = os.getenv("ZOOM_CLIENT_ID")
        self.zoom_client_secret = os.getenv("ZOOM_CLIENT_SECRET")
        self.zoom_account_id = os.getenv("ZOOM_ACCOUNT_ID")
        
        # OAuth endpoints
        self.auth_url = "https://zoom.us/oauth/authorize"
        self.token_url = "https://zoom.us/oauth/token"
        self.api_base_url = "https://api.zoom.us/v2"
        
        # Redirect URI for OAuth (should match your app configuration)
        self.redirect_uri = os.getenv("ZOOM_REDIRECT_URI", "http://localhost:8002/api/oauth/zoom/callback")
        
        # Storage for user tokens (in production, use a proper database)
        self.user_tokens = {}
        
    def get_oauth_url(self, state: str = None) -> str:
        """
        Generate OAuth authorization URL for Zoom
        """
        params = {
            'response_type': 'code',
            'client_id': self.zoom_client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'meeting:write meeting:read user:read',
            'state': state or 'default_state'
        }
        
        oauth_url = f"{self.auth_url}?{urlencode(params)}"
        logger.info(f"🔗 Generated Zoom OAuth URL: {oauth_url}")
        return oauth_url
    
    async def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        """
        try:
            # Prepare basic auth header
            auth_string = f"{self.zoom_client_id}:{self.zoom_client_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'redirect_uri': self.redirect_uri
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.token_url, headers=headers, data=data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        logger.info("✅ Successfully exchanged code for Zoom token")
                        return token_data
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Failed to exchange code for token: {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Token exchange error: {e}")
            return None
    
    async def create_meeting(self, access_token: str, meeting_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a Zoom meeting
        """
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Default meeting settings
            meeting_data = {
                'topic': meeting_details.get('topic', 'AI Automation Meeting'),
                'type': 2,  # Scheduled meeting
                'start_time': meeting_details.get('start_time', self._get_default_meeting_time()),
                'duration': meeting_details.get('duration', 30),  # 30 minutes default
                'timezone': meeting_details.get('timezone', 'America/New_York'),
                'agenda': meeting_details.get('agenda', 'Discussion about AI automation opportunities'),
                'settings': {
                    'host_video': True,
                    'participant_video': True,
                    'join_before_host': False,
                    'mute_upon_entry': True,
                    'watermark': False,
                    'use_pmi': False,
                    'approval_type': 0,  # Automatically approve
                    'audio': 'both',  # Both telephony and VoIP
                    'auto_recording': 'none'
                }
            }
            
            # Get user ID first
            user_info = await self._get_user_info(access_token)
            if not user_info:
                return None
                
            user_id = user_info.get('id', 'me')
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/users/{user_id}/meetings",
                    headers=headers,
                    json=meeting_data
                ) as response:
                    if response.status == 201:
                        meeting_info = await response.json()
                        logger.info(f"✅ Successfully created Zoom meeting: {meeting_info.get('id')}")
                        return meeting_info
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Failed to create meeting: {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Meeting creation error: {e}")
            return None
    
    async def _get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information from Zoom
        """
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base_url}/users/me", headers=headers) as response:
                    if response.status == 200:
                        user_info = await response.json()
                        return user_info
                    else:
                        logger.error(f"❌ Failed to get user info: {await response.text()}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ User info error: {e}")
            return None
    
    def _get_default_meeting_time(self) -> str:
        """
        Get default meeting time (1 hour from now)
        """
        future_time = datetime.now() + timedelta(hours=1)
        return future_time.strftime('%Y-%m-%dT%H:%M:%S')
    
    def format_meeting_info_for_email(self, meeting_info: Dict[str, Any], purpose: str = "investor meeting") -> str:
        """
        Format meeting information for email content
        """
        if not meeting_info:
            return "Failed to create Zoom meeting. Please try again."
        
        meeting_url = meeting_info.get('join_url', 'N/A')
        meeting_id = meeting_info.get('id', 'N/A')
        meeting_password = meeting_info.get('password', 'N/A')
        topic = meeting_info.get('topic', 'Meeting')
        start_time = meeting_info.get('start_time', 'N/A')
        duration = meeting_info.get('duration', 30)
        
        formatted_info = f"""
🔗 Zoom Meeting Details:

📅 Meeting Topic: {topic}
🕐 Start Time: {start_time}
⏱️ Duration: {duration} minutes
🆔 Meeting ID: {meeting_id}
🔐 Password: {meeting_password}

🎯 Join Meeting:
{meeting_url}

📞 Dial-in Information:
Meeting ID: {meeting_id}
Password: {meeting_password}

This meeting has been set up for {purpose}. Please join at the scheduled time.
"""
        return formatted_info
    
    async def create_meeting_and_email_content(self, access_token: str, recipient: str, purpose: str = "investor discussion") -> Dict[str, Any]:
        """
        Create a meeting and generate email content
        """
        # Create meeting
        meeting_details = {
            'topic': f'DXTR Labs {purpose.title()}',
            'duration': 30,
            'agenda': f'Discussion about DXTR Labs AI automation platform and {purpose} opportunities'
        }
        
        meeting_info = await self.create_meeting(access_token, meeting_details)
        
        if meeting_info:
            # Generate email content
            email_content = f"""Subject: Zoom Meeting Invitation - DXTR Labs {purpose.title()}

Dear {recipient.split('@')[0].title()},

I hope this message finds you well. I'm excited to invite you to a Zoom meeting to discuss DXTR Labs and our revolutionary AI automation platform.

{self.format_meeting_info_for_email(meeting_info, purpose)}

🚀 About DXTR Labs:
We're building the future of work through AI automation with our DXT Agents platform. We've developed:
• Intelligent AI agents that replace human workers
• FastMCP LLM Protocol for advanced workflow automation
• Universal automation templates (2000+)
• Growing user base with 100+ on our waitlist

💡 Meeting Agenda:
• Introduction to DXTR Labs platform
• Demo of our AI automation capabilities
• Discussion of {purpose} opportunities
• Q&A session

🎯 Why This Matters:
The AI automation market represents a $66B+ opportunity, and we're positioned to capture significant market share with our innovative approach.

Looking forward to our discussion!

Best regards,
DXTR Labs Team
automation-engine@dxtr-labs.com

P.S. If you have any technical difficulties joining the meeting, please don't hesitate to reach out.
"""
            
            return {
                'meeting_info': meeting_info,
                'email_content': email_content,
                'meeting_url': meeting_info.get('join_url'),
                'success': True
            }
        else:
            return {
                'success': False,
                'error': 'Failed to create Zoom meeting'
            }

# Create global instance
zoom_service = ZoomService()

async def test_zoom_service():
    """Test the Zoom service functionality"""
    print("🔗 Testing Zoom Service")
    print("=" * 40)
    
    # Test OAuth URL generation
    oauth_url = zoom_service.get_oauth_url("test_state")
    print(f"✅ OAuth URL generated: {oauth_url[:50]}...")
    
    # Test meeting creation (would need actual token)
    print("✅ Zoom service initialized successfully")
    print("🔗 OAuth URL ready for user authorization")

if __name__ == "__main__":
    asyncio.run(test_zoom_service())
