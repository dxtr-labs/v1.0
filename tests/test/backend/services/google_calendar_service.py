#!/usr/bin/env python3
"""
🗓️ Google Calendar OAuth and Meeting Service for AI Agents
Provides Google Calendar OAuth integration and event creation capabilities
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

class GoogleCalendarService:
    """
    Comprehensive Google Calendar service that provides:
    - OAuth 2.0 authentication flow
    - Calendar event creation and management
    - Meeting slot generation
    - Google Meet integration
    """
    
    def __init__(self):
        # Google OAuth credentials (add these to .env.local)
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8002/api/oauth/google/callback")
        
        # OAuth endpoints
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.api_base_url = "https://www.googleapis.com/calendar/v3"
        
        # Scopes for calendar access
        self.scopes = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events'
        ]
        
    def get_oauth_url(self, state: str = None) -> Dict[str, Any]:
        """
        Generate OAuth authorization URL for Google Calendar
        """
        try:
            if not self.client_id or not self.client_secret:
                return {"error": "Google OAuth credentials not configured"}
                
            params = {
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
                'scope': ' '.join(self.scopes),
                'response_type': 'code',
                'access_type': 'offline',
                'include_granted_scopes': 'true',
                'state': state or 'google_calendar_default'
            }
            
            oauth_url = f"{self.auth_url}?{urlencode(params)}"
            logger.info(f"🗓️ Generated Google Calendar OAuth URL")
            
            return {
                "oauth_url": oauth_url,
                "service": "google_calendar",
                "scopes": self.scopes
            }
            
        except Exception as e:
            logger.error(f"Google Calendar OAuth URL generation error: {e}")
            return {"error": str(e)}
    
    async def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        """
        try:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': authorization_code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.token_url, data=data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        logger.info("✅ Successfully exchanged code for Google Calendar token")
                        return token_data
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Failed to exchange code for token: {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Google Calendar token exchange error: {e}")
            return None
    
    async def create_meeting_slots(self, access_token: str, meeting_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create multiple Google Calendar meeting slots
        """
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Generate 5 meeting slots over next 2 weeks
            slots = []
            base_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
            
            for i in range(5):
                # Schedule meetings every other day
                start_time = base_time + timedelta(days=i*2 + 1)
                end_time = start_time + timedelta(minutes=30)
                
                event_data = {
                    'summary': meeting_details.get('title', 'DXTR Labs Investor Meeting'),
                    'description': f'Investment discussion about DXTR Labs AI automation platform. Learn about our revolutionary DXT Agents that replace human workers with intelligent automation.',
                    'start': {
                        'dateTime': start_time.isoformat(),
                        'timeZone': 'America/New_York',
                    },
                    'end': {
                        'dateTime': end_time.isoformat(),
                        'timeZone': 'America/New_York',
                    },
                    'conferenceData': {
                        'createRequest': {
                            'requestId': f"dxtr-{i}-{int(datetime.now().timestamp())}",
                            'conferenceSolutionKey': {
                                'type': 'hangoutsMeet'
                            }
                        }
                    },
                    'attendees': [],
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                            {'method': 'popup', 'minutes': 15}       # 15 minutes before
                        ]
                    }
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.api_base_url}/calendars/primary/events?conferenceDataVersion=1",
                        headers=headers,
                        json=event_data
                    ) as response:
                        if response.status == 200:
                            event = await response.json()
                            
                            # Extract meeting details
                            meet_link = None
                            if 'conferenceData' in event and 'entryPoints' in event['conferenceData']:
                                for entry in event['conferenceData']['entryPoints']:
                                    if entry.get('entryPointType') == 'video':
                                        meet_link = entry.get('uri')
                                        break
                            
                            slots.append({
                                'id': event['id'],
                                'start_time': start_time.strftime('%Y-%m-%d %H:%M'),
                                'date_formatted': start_time.strftime('%A, %B %d at %I:%M %p'),
                                'calendar_link': event.get('htmlLink'),
                                'google_meet_link': meet_link,
                                'event_link': event.get('htmlLink')
                            })
                        else:
                            logger.error(f"Failed to create event {i}: {await response.text()}")
            
            logger.info(f"✅ Created {len(slots)} Google Calendar meeting slots")
            return {
                'success': True,
                'meeting_slots': slots,
                'service': 'google_calendar'
            }
            
        except Exception as e:
            logger.error(f"❌ Google Calendar meeting creation error: {e}")
            return {'success': False, 'error': str(e)}
    
    def format_meeting_slots_for_email(self, slots: List[Dict[str, Any]]) -> str:
        """
        Format Google Calendar meeting slots for email content
        """
        if not slots:
            return "No meeting slots available."
        
        formatted_slots = "📅 **Available Meeting Times (Google Calendar):**\n\n"
        
        for i, slot in enumerate(slots, 1):
            formatted_slots += f"**Option {i}:** {slot.get('date_formatted', 'N/A')}\n"
            formatted_slots += f"🔗 Calendar Link: {slot.get('calendar_link', 'N/A')}\n"
            if slot.get('google_meet_link'):
                formatted_slots += f"📹 Google Meet: {slot.get('google_meet_link')}\n"
            formatted_slots += "\n"
        
        return formatted_slots
    
    async def create_calendar_integration_email(self, access_token: str, recipient: str, purpose: str = "investor meeting") -> Dict[str, Any]:
        """
        Create Google Calendar integration and generate email content
        """
        # Create meeting slots
        meeting_details = {
            'title': f'DXTR Labs {purpose.title()}',
            'purpose': purpose
        }
        
        slots_result = await self.create_meeting_slots(access_token, meeting_details)
        
        if slots_result.get('success'):
            slots = slots_result.get('meeting_slots', [])
            
            # Generate email content
            email_content = f"""Subject: DXTR Labs Investment Opportunity - Multiple Meeting Options Available

Dear {recipient.split('@')[0].title()},

I hope this message finds you well. I'm excited to share information about DXTR Labs and our revolutionary AI automation platform.

🚀 **About DXTR Labs:**
We're building the future of work through AI automation with our DXT Agents platform:
• Intelligent AI agents that replace human workers
• FastMCP LLM Protocol for advanced workflow automation  
• Universal automation templates (2000+)
• Growing user base with 100+ on our waitlist
• Targeting the $66B+ AI automation market

{self.format_meeting_slots_for_email(slots)}

💡 **Meeting Agenda:**
• Introduction to DXTR Labs platform and vision
• Live demo of our AI automation capabilities
• Discussion of investment opportunities and market potential
• Q&A session about our technology and business model

🎯 **Why This Matters:**
The AI automation revolution is here, and DXTR Labs is positioned to capture significant market share with our innovative approach to making AI agents universally accessible.

Please click any of the calendar links above to schedule a meeting at your convenience. Each link will automatically add the meeting to your calendar with Google Meet details.

Looking forward to our discussion!

Best regards,
DXTR Labs Team
automation-engine@dxtr-labs.com

P.S. Each meeting link includes Google Meet video conferencing for your convenience.
"""
            
            return {
                'success': True,
                'email_content': email_content,
                'meeting_slots': slots,
                'calendar_service': 'Google Calendar'
            }
        else:
            return {
                'success': False,
                'error': 'Failed to create Google Calendar meeting slots'
            }

# Create global instance
google_calendar_service = GoogleCalendarService()

async def test_google_calendar_service():
    """Test the Google Calendar service functionality"""
    print("🗓️ Testing Google Calendar Service")
    print("=" * 40)
    
    # Test OAuth URL generation
    oauth_result = google_calendar_service.get_oauth_url("test_state")
    if "error" not in oauth_result:
        print(f"✅ OAuth URL generated: {oauth_result['oauth_url'][:50]}...")
    else:
        print(f"⚠️ OAuth URL generation: {oauth_result['error']}")
    
    print("✅ Google Calendar service initialized successfully")
    print("🗓️ OAuth URL ready for user authorization")

if __name__ == "__main__":
    asyncio.run(test_google_calendar_service())
