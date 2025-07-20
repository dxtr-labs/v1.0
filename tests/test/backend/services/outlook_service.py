#!/usr/bin/env python3
"""
📧 Microsoft Outlook OAuth and Calendar Service for AI Agents
Provides Microsoft Outlook/Office 365 OAuth integration and calendar capabilities
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

class OutlookService:
    """
    Comprehensive Microsoft Outlook service that provides:
    - OAuth 2.0 authentication flow
    - Outlook calendar event creation and management
    - Teams meeting integration
    - Office 365 integration
    """
    
    def __init__(self):
        # Microsoft OAuth credentials (add these to .env.local)
        self.client_id = os.getenv("MICROSOFT_CLIENT_ID")
        self.client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
        self.tenant_id = os.getenv("MICROSOFT_TENANT_ID", "common")
        self.redirect_uri = os.getenv("MICROSOFT_REDIRECT_URI", "http://localhost:8002/api/oauth/outlook/callback")
        
        # Microsoft OAuth endpoints
        self.auth_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize"
        self.token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        self.api_base_url = "https://graph.microsoft.com/v1.0"
        
        # Scopes for Outlook and Calendar access
        self.scopes = [
            'https://graph.microsoft.com/calendars.readwrite',
            'https://graph.microsoft.com/user.read',
            'https://graph.microsoft.com/onlineMeetings.readwrite'
        ]
        
    def get_oauth_url(self, state: str = None) -> Dict[str, Any]:
        """
        Generate OAuth authorization URL for Microsoft Outlook
        """
        try:
            if not self.client_id:
                return {"error": "Microsoft OAuth credentials not configured"}
                
            params = {
                'client_id': self.client_id,
                'response_type': 'code',
                'redirect_uri': self.redirect_uri,
                'scope': ' '.join(self.scopes),
                'response_mode': 'query',
                'state': state or 'outlook_default'
            }
            
            oauth_url = f"{self.auth_url}?{urlencode(params, quote_via=quote_plus)}"
            logger.info(f"📧 Generated Microsoft Outlook OAuth URL")
            
            return {
                "oauth_url": oauth_url,
                "service": "outlook",
                "scopes": self.scopes
            }
            
        except Exception as e:
            logger.error(f"Microsoft Outlook OAuth URL generation error: {e}")
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
                'redirect_uri': self.redirect_uri,
                'scope': ' '.join(self.scopes)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.token_url, data=data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        logger.info("✅ Successfully exchanged code for Microsoft token")
                        return token_data
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Failed to exchange code for token: {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Microsoft token exchange error: {e}")
            return None
    
    async def create_meeting_events(self, access_token: str, meeting_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create multiple Microsoft Outlook calendar events with Teams meetings
        """
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Generate 5 meeting slots over next 2 weeks
            events = []
            base_time = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
            
            for i in range(5):
                # Schedule meetings every other day
                start_time = base_time + timedelta(days=i*2 + 1)
                end_time = start_time + timedelta(minutes=30)
                
                event_data = {
                    "subject": meeting_details.get('title', 'DXTR Labs Investor Meeting'),
                    "body": {
                        "contentType": "HTML",
                        "content": f"""
                        <h3>DXTR Labs Investment Discussion</h3>
                        <p>Thank you for your interest in DXTR Labs and our revolutionary AI automation platform.</p>
                        
                        <h4>Meeting Agenda:</h4>
                        <ul>
                            <li>Introduction to DXTR Labs platform and vision</li>
                            <li>Live demo of our AI automation capabilities</li>
                            <li>Discussion of investment opportunities</li>
                            <li>Q&A session about our technology and business model</li>
                        </ul>
                        
                        <p><strong>About DXTR Labs:</strong><br>
                        We're building intelligent AI agents that replace human workers with our DXT Agents platform. 
                        Our FastMCP LLM Protocol enables advanced workflow automation, and we have 2000+ templates 
                        with 100+ users on our waitlist, targeting the $66B+ AI automation market.</p>
                        
                        <p>Looking forward to our discussion!</p>
                        <p>Best regards,<br>DXTR Labs Team</p>
                        """
                    },
                    "start": {
                        "dateTime": start_time.isoformat(),
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": end_time.isoformat(),
                        "timeZone": "UTC"
                    },
                    "isOnlineMeeting": True,
                    "onlineMeetingProvider": "teamsForBusiness",
                    "allowNewTimeProposals": True,
                    "responseRequested": True,
                    "reminderMinutesBeforeStart": 15
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.api_base_url}/me/events",
                        headers=headers,
                        json=event_data
                    ) as response:
                        if response.status == 201:
                            event = await response.json()
                            
                            # Extract meeting details
                            teams_link = None
                            if 'onlineMeeting' in event:
                                teams_link = event['onlineMeeting'].get('joinUrl')
                            
                            events.append({
                                'id': event['id'],
                                'start_time': start_time.strftime('%Y-%m-%d %H:%M'),
                                'date_formatted': start_time.strftime('%A, %B %d at %I:%M %p'),
                                'calendar_link': event.get('webLink'),
                                'teams_meeting_link': teams_link,
                                'event_link': event.get('webLink')
                            })
                        else:
                            logger.error(f"Failed to create event {i}: {await response.text()}")
            
            logger.info(f"✅ Created {len(events)} Microsoft Outlook calendar events")
            return {
                'success': True,
                'meeting_events': events,
                'service': 'outlook'
            }
            
        except Exception as e:
            logger.error(f"❌ Microsoft Outlook event creation error: {e}")
            return {'success': False, 'error': str(e)}
    
    def format_outlook_events_for_email(self, events: List[Dict[str, Any]]) -> str:
        """
        Format Microsoft Outlook events for email content
        """
        if not events:
            return "No Outlook meeting events available."
        
        formatted_events = "📧 **Available Meeting Times (Microsoft Outlook):**\n\n"
        
        for i, event in enumerate(events, 1):
            formatted_events += f"**Option {i}:** {event.get('date_formatted', 'N/A')}\n"
            formatted_events += f"🔗 Calendar Link: {event.get('calendar_link', 'N/A')}\n"
            if event.get('teams_meeting_link'):
                formatted_events += f"👥 Teams Meeting: {event.get('teams_meeting_link')}\n"
            formatted_events += "\n"
        
        return formatted_events
    
    async def create_outlook_integration_email(self, access_token: str, recipient: str, purpose: str = "investor meeting") -> Dict[str, Any]:
        """
        Create Microsoft Outlook integration and generate email content
        """
        # Create meeting events
        meeting_details = {
            'title': f'DXTR Labs {purpose.title()}',
            'purpose': purpose
        }
        
        events_result = await self.create_meeting_events(access_token, meeting_details)
        
        if events_result.get('success'):
            events = events_result.get('meeting_events', [])
            
            # Generate email content
            email_content = f"""Subject: DXTR Labs Investment Opportunity - Microsoft Teams Meeting Options

Dear {recipient.split('@')[0].title()},

I hope this message finds you well. I'm excited to share information about DXTR Labs and our revolutionary AI automation platform.

🚀 **About DXTR Labs:**
We're building the future of work through AI automation with our DXT Agents platform:
• Intelligent AI agents that replace human workers
• FastMCP LLM Protocol for advanced workflow automation
• Universal automation templates (2000+)
• Growing user base with 100+ on our waitlist
• Targeting the $66B+ AI automation market

{self.format_outlook_events_for_email(events)}

💡 **Meeting Agenda:**
• Introduction to DXTR Labs platform and vision
• Live demo of our AI automation capabilities
• Discussion of investment opportunities and market potential
• Q&A session about our technology and business model

🎯 **Why This Matters:**
The AI automation revolution is here, and DXTR Labs is positioned to capture significant market share with our innovative approach to making AI agents universally accessible.

Please click any of the calendar links above to add the meeting to your Outlook calendar. Each meeting includes Microsoft Teams integration for seamless video conferencing.

Looking forward to our discussion!

Best regards,
DXTR Labs Team
automation-engine@dxtr-labs.com

P.S. All meetings include Microsoft Teams video conferencing for your convenience.
"""
            
            return {
                'success': True,
                'email_content': email_content,
                'meeting_events': events,
                'calendar_service': 'Microsoft Outlook'
            }
        else:
            return {
                'success': False,
                'error': 'Failed to create Microsoft Outlook meeting events'
            }

# Create global instance
outlook_service = OutlookService()

async def test_outlook_service():
    """Test the Microsoft Outlook service functionality"""
    print("📧 Testing Microsoft Outlook Service")
    print("=" * 40)
    
    # Test OAuth URL generation
    oauth_result = outlook_service.get_oauth_url("test_state")
    if "error" not in oauth_result:
        print(f"✅ OAuth URL generated: {oauth_result['oauth_url'][:50]}...")
    else:
        print(f"⚠️ OAuth URL generation: {oauth_result['error']}")
    
    print("✅ Microsoft Outlook service initialized successfully")
    print("📧 OAuth URL ready for user authorization")

if __name__ == "__main__":
    asyncio.run(test_outlook_service())
