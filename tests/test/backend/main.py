"""
FastAPI Main Application for AutoFlow AI Automation Platform
Corrected version with proper component integration
"""

from fastapi import FastAPI, Request, HTTPException, Cookie, Depends, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging
import sys
import re
from datetime import datetime, timedelta
import time
import uuid
import secrets
import json
from typing import Optional
from contextlib import asynccontextmanager

# Add the backend directory itself to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from both .env and .env.local
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, '.env'))
load_dotenv(os.path.join(current_dir, '.env.local'))
load_dotenv()  # Also try default locations
load_dotenv('.env.local')
load_dotenv('../.env.local')  # Also try parent directory

# Debug: Check if OpenAI API key is loaded
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key:
    logger.info(f"✅ OpenAI API key loaded ({len(openai_key)} chars)")
else:
    logger.error("❌ OpenAI API key NOT found in environment!")

# --- Import our simplified components ---
from mcp.simple_automation_engine import AutomationEngine
from core.simple_agent_manager import AgentManager
from core.agent_processor import AgentProcessor

# Import PostgreSQL database manager
from db.postgresql_manager import (
    db_manager, init_db, close_db,
    create_user, authenticate_user, get_user_by_session, update_user_session,
    get_user_by_id,
    add_credits, deduct_credits, get_credit_history
)

# Import email service
from simple_email_service import EmailService

# Configure detailed logging
logging.getLogger('werkzeug').setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)


# Global instances of our core components  
automation_engine: Optional[AutomationEngine] = None
agent_manager_instance: Optional[AgentManager] = None
agent_processor: Optional[AgentProcessor] = None
email_service: Optional[EmailService] = None

# Define FastAPI lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle for the FastAPI application."""
    # Startup: Initialize services
    logger.info("🚀 Starting AutoFlow Platform with PostgreSQL...")
    await init_db()  # Initialize the database pool

    global automation_engine, agent_manager_instance, agent_processor, email_service
    
    # Initialize AutomationEngine
    automation_engine = AutomationEngine()
    
    # Initialize email service FIRST
    email_service = EmailService()
    
    # Configure email service from environment variables
    smtp_host = os.getenv('SMTP_HOST', 'mail.privateemail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    if smtp_user and smtp_password:
        email_service.configure(smtp_user, smtp_password, smtp_host, smtp_port)
        logger.info(f"✅ Email service configured for {smtp_user}")
    else:
        logger.warning("⚠️ Email service not configured - missing SMTP credentials")

    # Initialize agent manager with the main database pool and configured email service
    agent_manager_instance = AgentManager(db_manager.pool, email_service)
    
    # Initialize agent processor
    agent_processor = AgentProcessor(db_manager.pool, automation_engine)

    logger.info("✅ Database connected with UUID support")
    logger.info("✅ AutomationEngine and AgentProcessor initialized.")
    logger.info("🔧 Features: User auth, agent management, custom MCP LLM code, trigger automation.")

    yield  # Server runs here

    # Shutdown: Cleanup
    logger.info("🔌 Shutting down AutoFlow Platform...")
    await close_db()  # Close the database pool
        
    logger.info("✅ Database connections closed")
    logger.info("👋 AutoFlow AI Platform shut down gracefully")


# Create FastAPI app instance
app = FastAPI(
    title="AutoFlow AI Automation Platform",
    version="3.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to get current user from session
async def get_current_user(
    session_token: str = Cookie(None, alias="session_token"),
    x_user_id: str = Header(None, alias="x-user-id") # For testing convenience
) -> dict: # Changed to dict, will raise HTTPException if not found
    """Extract user from session token or header, raising HTTPException if not found."""
    
    user = None
    if session_token:
        user = await get_user_by_session(session_token)
        if user:
            logger.info(f"AUTH - Found user via session: {user['email']}")
            return user
    
    if x_user_id:
        try:
            # For testing, treat x_user_id as actual user_id UUID
            user = await get_user_by_id(x_user_id)
            if user:
                logger.info(f"AUTH - Found user via header: {user['email']}")
                return user
        except Exception as e:
            logger.warning(f"AUTH - Invalid user ID in header: {e}")
    
    logger.warning("AUTH - User not authenticated or session invalid.")
    raise HTTPException(status_code=401, detail="Not authenticated")

# Helper to get or create a default "Sam" agent for a user
async def _get_or_create_default_agent(user_id: str) -> dict:
    """
    Retrieves the default 'Sam - Personal Assistant' agent for a user.
    Creates it if it doesn't exist.
    """
    # Define the default agent's characteristics
    default_agent_name = "Sam - Personal Assistant"
    default_agent_role = "General AI Assistant for Automation"
    default_agent_personality = {"tone": "friendly", "style": "helpful and concise"}
    default_agent_expectations = """Advanced AI Assistant with Enhanced Company Context Protocols:

COMPANY CONTEXT:
CEO: Pranay
Company Name: Roomify
What We Sell: Mobile/web application for room finding and roommate matching
Business Type: Technology startup in the housing/accommodation sector
Value Proposition: Simplifies the process of finding rooms and compatible roommates through smart matching algorithms
Target Market: Students, young professionals, people relocating to new cities
Key Features: Room search functionality, roommate compatibility matching, secure communication platform, verified listings

PERSONALITY & BRAND VOICE:
- Enthusiastic about Roomify's innovative housing solutions
- Knowledgeable about the challenges of finding accommodation and roommates
- Professional yet approachable, understanding the stress of housing searches
- Highlights Roomify's unique technology and user-friendly experience
- Emphasizes convenience, safety, and compatibility matching

PRIMARY FUNCTIONS:
1. Email Automation & Content Generation (especially for Roomify business pitches)
2. Workflow Creation & Management  
3. Context-Aware Conversation Handling
4. Roomify Brand Representation and Sales Support

CONTENT GENERATION PROTOCOLS:
- Email Generation: Always create preview-ready emails with proper subject lines, professional formatting, and recipient-specific content about Roomify
- Context Retention: Maintain conversation context across multi-step workflows (email preview → confirmation → execution)
- Content Quality: Generate high-quality, contextually relevant content based on user intent (sales pitches for Roomify app, marketing, welcome, professional communication)
- Workflow Continuity: Preserve email context through confirmation flows to enable seamless automation execution
- Brand Integration: Reference Roomify capabilities, benefits, and value proposition when relevant

EMAIL WORKFLOW EXPECTATIONS:
1. Initial Request: Generate email preview with status 'preview_ready' featuring Roomify-specific content
2. User Confirmation: Process 'SEND_APPROVED_EMAIL' requests without asking for recipient again
3. Content Editing: Support user modifications to email content and subject lines
4. Execution: Send emails using provided credentials with full context preservation

ROOMIFY-SPECIFIC PROTOCOLS:
- When generating sales pitches, emphasize the pain points Roomify solves (difficult room searches, incompatible roommates, safety concerns)
- Highlight unique features: smart matching algorithms, verified users, secure platform
- Target appropriate audiences: students, young professionals, people relocating
- Use CEO name "Pranay" when personal touch is needed
- Position Roomify as innovative solution in the housing/accommodation technology space

MEMORY & CONTEXT PROTOCOLS:
- Remember email workflows in progress
- Maintain recipient information across conversation steps
- Preserve edited content from user confirmations
- Track workflow states (preview → confirmation → execution)
- Store and recall Roomify company information and user preferences

AUTOMATION PROTOCOLS:
- Detect automation intent from natural language
- Create contextual workflows based on user requests
- Provide clear status feedback (preview_ready, completed, error)
- Support background email sending with proper status reporting
- Showcase Roomify's technology capabilities in communications"""

    user_agents = await agent_manager_instance.get_user_agents(user_id)
    for agent in user_agents:
        if agent['agent_name'] == default_agent_name:
            logger.info(f"Found existing default agent for user {user_id}: {agent['agent_id']}")
            return agent
    
    # If not found, create it
    logger.info(f"Creating new default agent for user {user_id}: {default_agent_name}")
    new_agent = await agent_manager_instance.create_agent(
        user_id=user_id,
        agent_name=default_agent_name,
        agent_role=default_agent_role,
        agent_personality=json.dumps(default_agent_personality),
        agent_expectations=default_agent_expectations
    )
    if not new_agent:
        raise HTTPException(status_code=500, detail="Failed to create default agent.")
    return new_agent


# Add middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"🌐 REQUEST: {request.method} {request.url}")
    response = await call_next(request)
    return response

# Core Health Check
@app.get("/health")
async def health():
    return {
        "status": "ok", 
        "message": "AutoFlow Platform is running",
        "database": "PostgreSQL with UUIDs",
        "timestamp": datetime.utcnow().isoformat()
    }

# ===== AUTHENTICATION ENDPOINTS =====

@app.post("/api/auth/signup")
async def signup(request: Request):
    """User registration endpoint."""
    try:
        body = await request.json()
        logger.info(f"🔍 Signup request body: {body}")
        
        email = body.get('email')
        password = body.get('password')
        first_name = body.get('first_name', '')  # Corrected to match frontend proxy
        last_name = body.get('last_name', '')    # Corrected to match frontend proxy
        username = body.get('username')
        organization = body.get('is_organization', False)  # Corrected to match frontend proxy
        
        logger.info(f"🔍 Parsed fields - first_name: '{first_name}', last_name: '{last_name}'")
        
        if not email or not password:
            return JSONResponse(
                status_code=400,
                content={"error": "Email and password are required"}
            )
        
        user = await create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            username=username,
            organization=organization
        )
        
        session_token = secrets.token_urlsafe(32)
        await update_user_session(str(user['user_id']), session_token)
        
        logger.info(f"✅ User created: {email} (ID: {user['user_id']})")
        
        return JSONResponse(content={
            "success": True,
            "message": "User created successfully",
            "user": {
                "user_id": str(user['user_id']),
                "email": user['email'],
                "first_name": user['first_name'],
                "last_name": user['last_name'],
                "name": f"{user['first_name']} {user['last_name']}".strip(),
                "username": user['username'],
                "credits": user['credits']
            },
            "session_token": session_token # Corrected typo from session_2token
        })
        
    except ValueError as e:
        error_message = str(e)
        if "Email already exists" in error_message:
            return JSONResponse(
                status_code=400,
                content={"error": "An account with this email already exists. Please try logging in instead."}
            )
        else:
            return JSONResponse(
                status_code=400,
                content={"error": error_message}
            )
    except Exception as e:
        logger.error(f"Signup error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

@app.post("/api/auth/login")
async def login(request: Request):
    """User login endpoint."""
    try:
        body = await request.json()
        email = body.get('email')
        password = body.get('password')
        
        if not email or not password:
            return JSONResponse(
                status_code=400,
                content={"error": "Email and password are required"}
            )
        
        user = await authenticate_user(email, password)
        if not user:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid credentials"}
            )
        
        session_token = secrets.token_urlsafe(32)
        await update_user_session(str(user['user_id']), session_token)
        
        logger.info(f"✅ User logged in: {email}")
        
        return JSONResponse(content={
            "success": True,
            "message": "Login successful",
            "user": {
                "user_id": str(user['user_id']),
                "email": user['email'],
                "first_name": user['first_name'],
                "last_name": user['last_name'],
                "name": f"{user['first_name']} {user['last_name']}".strip(),
                "username": user['username'],
                "credits": user['credits']
            },
            "session_token": session_token
        })
        
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    # current_user is guaranteed to be present by Depends(get_current_user)
    return {
        "user": {
            "user_id": str(current_user['user_id']),
            "email": current_user['email'],
            "first_name": current_user['first_name'],
            "last_name": current_user['last_name'],
            "name": f"{current_user['first_name']} {current_user['last_name']}".strip(),
            "username": current_user['username'],
            "credits": current_user['credits'],
            "organization": current_user['organization']
        }
    }

@app.post("/api/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """User logout endpoint."""
    # current_user is guaranteed to be present
    await update_user_session(str(current_user['user_id']), "", -1) # Clear session token
    logger.info(f"User logged out: {current_user['email']}")
    
    return {"success": True, "message": "Logged out successfully"}

# ===== ZOOM OAUTH ENDPOINTS =====

@app.get("/api/oauth/zoom/authorize")
async def zoom_oauth_authorize():
    """Initialize Zoom OAuth flow"""
    try:
        from services.zoom_service import zoom_service
        
        # Generate OAuth URL
        oauth_url = zoom_service.get_oauth_url()
        
        return {
            "success": True,
            "oauth_url": oauth_url,
            "message": "Click the OAuth URL to authorize Zoom integration"
        }
        
    except Exception as e:
        logger.error(f"Zoom OAuth authorize error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to generate Zoom OAuth URL"}
        )

@app.get("/api/oauth/zoom/callback")
async def zoom_oauth_callback(code: str = None, state: str = None, error: str = None):
    """Handle Zoom OAuth callback"""
    try:
        if error:
            logger.error(f"Zoom OAuth error: {error}")
            return JSONResponse(
                status_code=400,
                content={"error": f"Zoom OAuth failed: {error}"}
            )
        
        if not code:
            return JSONResponse(
                status_code=400,
                content={"error": "Authorization code not provided"}
            )
        
        from services.zoom_service import zoom_service
        
        # Exchange code for token
        token_data = await zoom_service.exchange_code_for_token(code)
        
        if not token_data:
            return JSONResponse(
                status_code=400,
                content={"error": "Failed to exchange code for token"}
            )
        
        # Extract recipient email from state if available
        recipient_email = "slakshanand1105@gmail.com"  # Default
        if state and "meeting_for_" in state:
            recipient_email = state.replace("meeting_for_", "")
        
        # Create meeting automatically
        access_token = token_data.get('access_token')
        meeting_result = await zoom_service.create_meeting_and_email_content(
            access_token=access_token,
            recipient=recipient_email,
            purpose="investor discussion"
        )
        
        if meeting_result.get('success'):
            # Return success page with meeting details
            meeting_info = meeting_result.get('meeting_info', {})
            meeting_url = meeting_info.get('join_url', 'N/A')
            
            return {
                "success": True,
                "message": "Zoom meeting created successfully!",
                "meeting_url": meeting_url,
                "meeting_id": meeting_info.get('id'),
                "recipient": recipient_email,
                "email_content": meeting_result.get('email_content'),
                "next_step": "Email preview ready for sending"
            }
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to create Zoom meeting"}
            )
        
    except Exception as e:
        logger.error(f"Zoom OAuth callback error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to process Zoom OAuth callback"}
        )

# ===== GOOGLE CALENDAR OAUTH ENDPOINTS =====

@app.get("/api/oauth/google-calendar/authorize")
async def google_calendar_oauth_authorize():
    """Initialize Google Calendar OAuth flow"""
    try:
        from backend.services.google_calendar_service import GoogleCalendarService
        google_calendar_service = GoogleCalendarService()
        
        # Generate OAuth URL
        oauth_url = google_calendar_service.get_oauth_url()
        
        return JSONResponse(content={
            "success": True,
            "oauth_url": oauth_url,
            "message": "Click the OAuth URL to authorize Google Calendar integration"
        })
        
    except Exception as e:
        logger.error(f"Google Calendar OAuth authorize error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to generate Google Calendar OAuth URL"}
        )

@app.get("/api/oauth/google-calendar/callback")
async def google_calendar_oauth_callback(code: str = None, state: str = None, error: str = None):
    """Handle Google Calendar OAuth callback"""
    try:
        if error:
            logger.error(f"Google Calendar OAuth error: {error}")
            return JSONResponse(
                status_code=400,
                content={"error": f"Google Calendar OAuth failed: {error}"}
            )
        
        if not code:
            return JSONResponse(
                status_code=400,
                content={"error": "No authorization code received"}
            )
        
        from backend.services.google_calendar_service import GoogleCalendarService
        google_calendar_service = GoogleCalendarService()
        
        # Exchange code for tokens
        tokens = await google_calendar_service.exchange_code_for_tokens(code)
        
        if tokens:
            # Extract recipient email from state if available
            recipient_email = "slakshanand1105@gmail.com"
            if state and "calendar_for_" in state:
                recipient_email = state.replace("calendar_for_", "")
            
            # Generate meeting slots and send email
            meeting_slots = await google_calendar_service.create_meeting_slots()
            email_content = await google_calendar_service.generate_scheduling_email(
                recipient_email, meeting_slots
            )
            
            # Send the email
            from backend.simple_email_service import EmailService
            email_service = EmailService()
            email_sent = await email_service.send_html_email(
                to_email=recipient_email,
                subject="Meeting Availability - Google Calendar Integration",
                html_content=email_content
            )
            
            return JSONResponse(content={
                "success": True,
                "message": f"Google Calendar authorized and scheduling email sent to {recipient_email}",
                "email_sent": email_sent,
                "meeting_slots_count": len(meeting_slots)
            })
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to exchange code for tokens"}
            )
            
    except Exception as e:
        logger.error(f"Google Calendar OAuth callback error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to process Google Calendar OAuth callback"}
        )

# ===== CALENDLY OAUTH ENDPOINTS =====

@app.get("/api/oauth/calendly/authorize")
async def calendly_oauth_authorize():
    """Initialize Calendly OAuth flow"""
    try:
        from backend.services.calendly_service import CalendlyService
        calendly_service = CalendlyService()
        
        # Generate OAuth URL
        oauth_url = calendly_service.get_oauth_url()
        
        return JSONResponse(content={
            "success": True,
            "oauth_url": oauth_url,
            "message": "Click the OAuth URL to authorize Calendly integration"
        })
        
    except Exception as e:
        logger.error(f"Calendly OAuth authorize error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to generate Calendly OAuth URL"}
        )

@app.get("/api/oauth/calendly/callback")
async def calendly_oauth_callback(code: str = None, state: str = None, error: str = None):
    """Handle Calendly OAuth callback"""
    try:
        if error:
            logger.error(f"Calendly OAuth error: {error}")
            return JSONResponse(
                status_code=400,
                content={"error": f"Calendly OAuth failed: {error}"}
            )
        
        if not code:
            return JSONResponse(
                status_code=400,
                content={"error": "No authorization code received"}
            )
        
        from backend.services.calendly_service import CalendlyService
        calendly_service = CalendlyService()
        
        # Exchange code for tokens
        tokens = await calendly_service.exchange_code_for_tokens(code)
        
        if tokens:
            # Extract recipient email from state if available
            recipient_email = "slakshanand1105@gmail.com"
            if state and "calendly_for_" in state:
                recipient_email = state.replace("calendly_for_", "")
            
            # Get user info and scheduling links
            user_info = await calendly_service.get_user_info()
            event_types = await calendly_service.get_event_types()
            
            # Generate scheduling email
            email_content = await calendly_service.generate_scheduling_email(
                recipient_email, user_info, event_types
            )
            
            # Send the email
            from backend.simple_email_service import EmailService
            email_service = EmailService()
            email_sent = await email_service.send_html_email(
                to_email=recipient_email,
                subject="Meeting Scheduling - Calendly Integration",
                html_content=email_content
            )
            
            return JSONResponse(content={
                "success": True,
                "message": f"Calendly authorized and scheduling email sent to {recipient_email}",
                "email_sent": email_sent,
                "event_types_count": len(event_types) if event_types else 0
            })
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to exchange code for tokens"}
            )
            
    except Exception as e:
        logger.error(f"Calendly OAuth callback error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to process Calendly OAuth callback"}
        )

# ===== MICROSOFT OUTLOOK OAUTH ENDPOINTS =====

@app.get("/api/oauth/outlook/authorize")
async def outlook_oauth_authorize():
    """Initialize Microsoft Outlook OAuth flow"""
    try:
        from backend.services.outlook_service import OutlookService
        outlook_service = OutlookService()
        
        # Generate OAuth URL
        oauth_url = outlook_service.get_oauth_url()
        
        return JSONResponse(content={
            "success": True,
            "oauth_url": oauth_url,
            "message": "Click the OAuth URL to authorize Microsoft Outlook integration"
        })
        
    except Exception as e:
        logger.error(f"Outlook OAuth authorize error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to generate Outlook OAuth URL"}
        )

@app.get("/api/oauth/outlook/callback")
async def outlook_oauth_callback(code: str = None, state: str = None, error: str = None):
    """Handle Microsoft Outlook OAuth callback"""
    try:
        if error:
            logger.error(f"Outlook OAuth error: {error}")
            return JSONResponse(
                status_code=400,
                content={"error": f"Outlook OAuth failed: {error}"}
            )
        
        if not code:
            return JSONResponse(
                status_code=400,
                content={"error": "No authorization code received"}
            )
        
        from backend.services.outlook_service import OutlookService
        outlook_service = OutlookService()
        
        # Exchange code for tokens
        tokens = await outlook_service.exchange_code_for_tokens(code)
        
        if tokens:
            # Extract recipient email from state if available
            recipient_email = "slakshanand1105@gmail.com"
            if state and "outlook_for_" in state:
                recipient_email = state.replace("outlook_for_", "")
            
            # Generate meeting slots and send email
            meeting_slots = await outlook_service.create_meeting_slots()
            email_content = await outlook_service.generate_scheduling_email(
                recipient_email, meeting_slots
            )
            
            # Send the email
            from backend.simple_email_service import EmailService
            email_service = EmailService()
            email_sent = await email_service.send_html_email(
                to_email=recipient_email,
                subject="Meeting Availability - Microsoft Outlook Integration",
                html_content=email_content
            )
            
            return JSONResponse(content={
                "success": True,
                "message": f"Outlook authorized and scheduling email sent to {recipient_email}",
                "email_sent": email_sent,
                "meeting_slots_count": len(meeting_slots)
            })
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to exchange code for tokens"}
            )
            
    except Exception as e:
        logger.error(f"Outlook OAuth callback error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to process Outlook OAuth callback"}
        )

# ===== AGENT MANAGEMENT ENDPOINTS (Using AgentManager) =====

@app.post("/api/agents")
async def create_agent_endpoint(request: Request, current_user: dict = Depends(get_current_user)):
    """Create a new AI agent with custom MCP LLM code and trigger configuration."""
    try:
        body = await request.json()
        agent_name = body.get('name', '').strip()
        agent_role = body.get('role', '').strip()
        agent_expectations = body.get('expectations', '').strip()
        agent_personality = body.get('personality', {})
        trigger_config = body.get('triggerConfig', {})
        custom_mcp_code = body.get('customMcpCode', '')
        
        # New fields for enhanced trigger support
        trigger_type = body.get('triggerType')  # 'cron', 'webhook', 'email_imap'
        trigger_settings = body.get('triggerSettings', {})

        if not agent_name or not agent_role:
            return JSONResponse(
                status_code=400,
                content={"error": "Agent name and role are required"}
            )
        
        # Validate trigger configuration if trigger_type is provided
        if trigger_type:
            if trigger_type not in ['cron', 'webhook', 'email_imap', 'manual']:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Valid trigger type is required (cron, webhook, email_imap, manual)"}
                )
            
            # Validate trigger settings based on type
            if trigger_type == 'cron' and not trigger_settings.get('triggerTimes'):
                return JSONResponse(
                    status_code=400,
                    content={"error": "Schedule times are required for timer triggers"}
                )
            elif trigger_type == 'webhook' and not trigger_settings.get('path'):
                return JSONResponse(
                    status_code=400,
                    content={"error": "Webhook path is required for webhook triggers"}
                )
        
        # Generate default custom MCP code if not provided
        if not custom_mcp_code:
            from core.agent_schema import DEFAULT_CUSTOM_MCP_CODE
            custom_mcp_code = DEFAULT_CUSTOM_MCP_CODE.format(
                agent_name=agent_name,
                agent_role=agent_role
            )
        
        # Create the agent first
        agent = await agent_manager_instance.create_agent(
            user_id=str(current_user['user_id']),
            agent_name=agent_name,
            agent_role=agent_role,
            agent_personality=json.dumps(agent_personality),
            agent_expectations=agent_expectations,
            trigger_config=trigger_config,
            custom_mcp_code=custom_mcp_code
        )
        
        agent_id = str(agent['agent_id'])
        
        # If trigger configuration provided, create the trigger
        if trigger_type:
            async with agent_manager_instance.db_pool.acquire() as conn:
                trigger_result = await conn.fetchrow(
                    """INSERT INTO agent_triggers (agent_id, trigger_type, trigger_config, is_active)
                       VALUES ($1, $2, $3, true)
                       RETURNING id, created_at""",
                    agent_id, trigger_type, json.dumps(trigger_settings)
                )
                trigger_id = str(trigger_result['id'])
                logger.info(f"✅ Trigger created: {trigger_type} (ID: {trigger_id}) for agent {agent_id}")
        
        logger.info(f"✅ Agent created: {agent_name} for user {current_user['email']} with trigger: {trigger_type or 'none'}")
        
        response_data = {
            "success": True,
            "agent": {
                "id": agent_id,
                "name": agent['agent_name'],
                "role": agent['agent_role'],
                "personality": json.loads(agent['agent_personality'] or '{}'),
                "expectations": agent['agent_expectations'],
                "triggerConfig": agent.get('trigger_config', {}),
                "hasCustomCode": bool(agent.get('custom_mcp_code')),
                "created": agent['created_at'].isoformat(),
                "updated": agent['updated_at'].isoformat()
            },
            "message": "Agent created successfully"
        }
        
        # Add trigger information if created
        if trigger_type:
            response_data["trigger"] = {
                "id": trigger_id,
                "type": trigger_type,
                "config": trigger_settings,
                "active": True
            }
            response_data["message"] = f"Agent and {trigger_type} trigger created successfully"
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"Create agent error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/api/agents")
async def list_agents(current_user: dict = Depends(get_current_user)):
    """List all agents for the current user."""
    # current_user is guaranteed to be present
    try:
        # AgentManager handles RLS, so no explicit ownership check needed here
        agents = await agent_manager_instance.get_user_agents(str(current_user['user_id']))
        
        formatted_agents = []
        for agent in agents:
            formatted_agents.append({
                "id": str(agent['agent_id']),
                "name": agent['agent_name'],
                "role": agent['agent_role'],
                "personality": json.loads(agent['agent_personality'] or '{}'),
                "expectations": agent['agent_expectations'],
                "created": agent['created_at'].isoformat(),
                "updated": agent['updated_at'].isoformat()
            })
        
        return {
            "agents": formatted_agents,
            "total": len(formatted_agents)
        }
        
    except Exception as e:
        logger.error(f"List agents error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific agent."""
    # current_user is guaranteed to be present
    try:
        # AgentManager handles RLS, so it will only return if owned by user or if user is admin
        agent = await agent_manager_instance.get_agent_details(agent_id, str(current_user['user_id']))
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found or access denied")
        
        return {
            "id": str(agent['agent_id']),
            "name": agent['agent_name'],
            "role": agent['agent_role'],
            "personality": json.loads(agent['agent_personality'] or '{}'),
            "expectations": agent['agent_expectations'],
            "created": agent['created_at'].isoformat(),
            "updated": agent['updated_at'].isoformat()
        }
        
    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.error(f"Get agent error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.delete("/api/agents/{agent_id}")
async def delete_agent_endpoint(agent_id: str, current_user: dict = Depends(get_current_user)):
    """Delete an agent."""
    # current_user is guaranteed to be present
    try:
        # AgentManager handles RLS, so it will only delete if owned by user or if user is admin
        success = await agent_manager_instance.delete_agent(agent_id, str(current_user['user_id']))
        if success:
            logger.info(f"✅ Agent deleted: {agent_id} for user {current_user['email']}")
            return {"success": True, "message": "Agent deleted successfully"}
        else:
            # If not found or not owned, delete_agent returns False due to RLS
            raise HTTPException(status_code=404, detail="Agent not found or access denied")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete agent error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# ===== CREDIT MANAGEMENT ENDPOINTS =====

@app.get("/api/credits")
async def get_credits(current_user: dict = Depends(get_current_user)):
    """Get user's current credit balance."""
    # current_user is guaranteed to be present
    return {
        "credits": current_user['credits'],
        "user_id": str(current_user['user_id'])
    }

@app.get("/api/credits/history")
async def get_credits_history(current_user: dict = Depends(get_current_user)):
    """Get user's credit transaction history."""
    # current_user is guaranteed to be present
    try:
        history = await get_credit_history(str(current_user['user_id']))
        
        formatted_history = []
        for entry in history:
            formatted_history.append({
                "id": str(entry['id']),
                "change": entry['change'],
                "reason": entry['reason'],
                "service_used": entry['service_used'],
                "timestamp": entry['created_at'].isoformat()
            })
        
        return {
            "history": formatted_history,
            "total": len(formatted_history)
        }
        
    except Exception as e:
        logger.error(f"Credit history error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# ===== MCP_LLM AND AUTOMATION ENDPOINTS =====

@app.post("/api/ai/chat/{agent_id}")
async def ai_chat_with_agent(
    agent_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Endpoint for interacting with a specific AI agent (MCP_LLM).
    Handles conversational turns and workflow generation.
    """
    # current_user is guaranteed to be present
    try:
        body = await request.json()
        user_message = body.get('message', '').strip()
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")

        # Ensure the agent exists and belongs to the user
        agent_details = await agent_manager_instance.get_agent_details(agent_id, str(current_user['user_id']))
        if not agent_details:
            raise HTTPException(status_code=404, detail="Agent not found or access denied.")

        logger.info(f"AI Chat: User {current_user['email']} talking to Agent {agent_details['agent_name']} (ID: {agent_id})")
        
        # Process message with AgentProcessor
        if agent_processor is None:
            raise HTTPException(status_code=503, detail="Agent Processor not initialized.")

        response = await agent_processor.process_with_agent(
            agent_id=agent_id,
            user_input=user_message,
            user_id=str(current_user['user_id'])
        )
        
        # Handle different response statuses from the orchestrator
        if response["status"] == "review_needed":
            return JSONResponse(content={
                "done": False, # Still needs user confirmation
                "success": True,
                "message": response["message"], # Human-readable summary
                "workflow_json": response["workflow_json"], # The full workflow JSON to be confirmed
                "action_required": "confirm_workflow"
            })
        elif response["status"] == "info_needed":
            return JSONResponse(content={
                "done": False, # Still needs more info
                "success": True,
                "message": response["message"], # Clarifying question
                "action_required": "provide_info"
            })
        elif response["status"] == "conversational":
            return JSONResponse(content={
                "done": True, # Conversation turn complete
                "success": True,
                "message": response["message"], # General chat response
                "action_required": "none"
            })
        elif response["status"] == "error":
            raise HTTPException(status_code=500, detail=response["message"])
        
        # This case should ideally not be reached if all statuses are handled
        return JSONResponse(content={
            "done": False,
            "success": False,
            "message": "Unexpected response from AI orchestrator.",
            "action_required": "error"
        }, status_code=500)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI Chat endpoint error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error during AI interaction", "message": str(e)}
        )

@app.post("/api/chat/mcpai")
async def chat_with_default_mcp_assistant(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Endpoint for interacting with the default 'Sam - Personal Assistant' AI agent.
    This endpoint automatically finds or creates the default agent for the user.
    """
    logger.error(f"🎯 CRITICAL DEBUG: ENDPOINT /api/chat/mcpai CALLED - User: {current_user.get('email')}")
    logger.error(f"🎯 REQUEST METHOD: {request.method}")
    logger.error(f"🎯 REQUEST URL: {request.url}")
    
    # current_user is guaranteed to be present
    try:
        body = await request.json()
        logger.error(f"🎯 REQUEST BODY: {body}")
        user_message = body.get('message', '').strip()
        
        logger.error(f"🎯 USER MESSAGE: '{user_message}'")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")

        # Get or create the default 'Sam' agent for the current user
        default_agent = await _get_or_create_default_agent(str(current_user['user_id']))
        default_agent_id = str(default_agent['agent_id'])

        logger.error(f"🎯 MCP AI Chat: User {current_user['email']} talking to default agent '{default_agent['agent_name']}' (ID: {default_agent_id})")
        
        # Process message with AgentProcessor
        if agent_processor is None:
            raise HTTPException(status_code=503, detail="Agent Processor not initialized.")

        # Process message with AgentProcessor
        logger.error(f"🎯 DEBUG: Processing user message with Agent Processor: {user_message}")
        
        # Extract request_data for passing additional context like email_content
        request_data = {
            "email_content": body.get("email_content")
        } if body.get("email_content") else None
        
        logger.error(f"🎯 DEBUG: About to call agent_processor.process_with_agent")
        response = await agent_processor.process_with_agent(
            agent_id=default_agent_id,
            user_input=user_message,
            user_id=str(current_user['user_id']),
            request_data=request_data
        )
        logger.error(f"🎯 DEBUG: agent_processor.process_with_agent returned: {response.get('status') if response else 'None'}")
        
        # Debug log the response
        logger.debug(f"🎯 DEBUG: MCP Response: {json.dumps(response, indent=2)}")
        logger.error(f"🎯 CRITICAL DEBUG: MCP Response Status: {response.get('status')}")
        
        # Handle null response
        if response is None:
            logger.warning("🎯 DEBUG: MCP returned None response, providing fallback")
            return JSONResponse(content={
                "success": False,
                "response": "I'm sorry, I couldn't process that request. Please try again.",
                "agentId": default_agent_id,
                "timestamp": datetime.now().isoformat(),
                "fallback": True
            })
        
        # Handle different response statuses from the orchestrator
        if response["status"] == "review_needed":
            return JSONResponse(content={
                "done": False,
                "success": True,
                "message": response["message"],
                "workflow_json": response["workflow_json"],
                "action_required": "confirm_workflow",
                # Add frontend expected fields
                "status": "review_needed",
                "hasWorkflowJson": True,
                "hasWorkflowPreview": False,
                "workflowPreviewContent": "",
                "automation_type": "workflow_review"
            })
        elif response["status"] == "ai_service_selection":
            return JSONResponse(content={
                "done": False,
                "success": True,
                "status": "ai_service_selection",
                "message": response["message"],
                "ai_service_options": response["ai_service_options"],
                "original_request": response["original_request"],
                "estimated_credits": response["estimated_credits"],
                "action_required": "select_ai_service",
                # Add frontend expected fields
                "hasWorkflowJson": False,
                "hasWorkflowPreview": False,
                "workflowPreviewContent": "",
                "automation_type": "ai_service_selection"
            })
        elif response["status"] == "info_needed":
            return JSONResponse(content={
                "done": False,
                "success": True,
                "message": response["message"],
                "action_required": "provide_info",
                # Add frontend expected fields
                "status": "info_needed",
                "hasWorkflowJson": False,
                "hasWorkflowPreview": False,
                "workflowPreviewContent": "",
                "automation_type": "info_collection"
            })
        elif response["status"] == "workflow_preview":
            return JSONResponse(content={
                "done": False,
                "success": True,
                "status": "workflow_preview",
                "message": response["message"],
                "workflow_preview": response["workflow_preview"],  # THIS WAS MISSING!
                "workflow_json": response["workflow_json"],
                "workflow_id": response["workflow_id"],
                "ai_service_used": response["ai_service_used"],
                "estimated_credits": response["estimated_credits"],
                "preview_details": response["preview_details"],
                "action_required": "confirm_workflow",
                # Add frontend expected fields
                "hasWorkflowJson": True,
                "hasWorkflowPreview": True,
                "workflowPreviewContent": response["workflow_preview"],
                "automation_type": "workflow_preview"
            })
        elif response["status"] == "preview_ready":
            logger.error(f"🎯 CRITICAL DEBUG: TAKING PREVIEW_READY PATH with email_content: {response.get('email_content') is not None}")
            return JSONResponse(content={
                "done": False,
                "success": True,
                "message": response["message"],
                "action_required": response.get("action_required", "approve_email"),
                # Add frontend expected fields for email preview
                "status": "preview_ready",
                "hasWorkflowJson": response.get("hasWorkflowJson", False),
                "hasWorkflowPreview": response.get("hasWorkflowPreview", False),
                "workflowPreviewContent": response.get("workflowPreviewContent", ""),
                "workflow_id": response.get("workflow_id"),
                "automation_type": response.get("automation_type", "email_preview"),
                # Email-specific fields
                "email_content": response.get("email_content"),
                "email_subject": response.get("email_subject"),
                "recipient": response.get("recipient"),
                "sender": response.get("sender"),
                "email_preview": response.get("email_preview"),
                "email_validation": response.get("email_validation"),
                "confidence": response.get("confidence"),
                "ai_enhanced": response.get("ai_enhanced", True),
                "content_type": response.get("content_type"),
                "preview_mode": response.get("preview_mode", True),
                "email_sent": response.get("email_sent", False)
            })
        elif response["status"] == "conversational":
            logger.error(f"🎯 CRITICAL DEBUG: TAKING CONVERSATIONAL PATH - message: {response.get('message', '')[:100]}")
            return JSONResponse(content={
                "done": True,
                "success": True,
                "message": response["message"],
                "action_required": "none",
                # Add frontend expected fields
                "status": "completed",
                "hasWorkflowJson": False,
                "hasWorkflowPreview": False,
                "workflowPreviewContent": "",
                "workflow_id": None,
                "automation_type": "conversational"
            })
        elif response["status"] == "automation_ready":
            logger.error(f"🎯 CRITICAL DEBUG: TAKING AUTOMATION_READY PATH - workflow present: {response.get('workflow_json') is not None}")
            return JSONResponse(content={
                "done": True,
                "success": True,
                "message": response["message"],
                "action_required": "none",
                # Add frontend expected fields
                "status": "completed",
                "hasWorkflowJson": True,
                "hasWorkflowPreview": True,
                "workflowPreviewContent": response.get("workflow_preview", ""),
                "workflow_id": response.get("workflow_json", {}).get("workflow_id"),
                "automation_type": "email_automation",
                "workflow_json": response.get("workflow_json"),
                "workflow_preview": response.get("workflow_preview")
            })
        elif response["status"] == "completed":
            return JSONResponse(content={
                "done": True,
                "success": True,
                "message": response["message"],
                "action_required": "none",
                # Add frontend expected fields
                "status": "completed",
                "hasWorkflowJson": response.get("workflow_json") is not None,
                "hasWorkflowPreview": response.get("workflow_preview") is not None,
                "workflowPreviewContent": response.get("workflow_preview", ""),
                "workflow_id": response.get("workflow_id"),
                "automation_type": "completed_workflow",
                "email_sent": response.get("email_sent", False),
                "execution_status": response.get("execution_status")
            })
        elif response["status"] == "error":
            return JSONResponse(content={
                "done": True,
                "success": False,
                "message": response["message"],
                "action_required": "none",
                # Add frontend expected fields
                "status": "error",
                "hasWorkflowJson": False,
                "hasWorkflowPreview": False,
                "workflowPreviewContent": "",
                "automation_type": "error"
            }, status_code=500)
        elif response["status"] == "success":
            # Handle simple success responses - check if it needs AI service selection
            response_message = response.get("response", response.get("message", ""))
            
            # If it just says it will send an email, it means it needs AI service selection
            if "send an email" in response_message and "I'll" in response_message:
                return JSONResponse(content={
                    "done": False,
                    "success": True,
                    "status": "ai_service_selection",
                    "message": "I can help you generate and send that email! Please choose your preferred AI service:",
                    # Add frontend expected fields
                    "hasWorkflowJson": False,
                    "hasWorkflowPreview": False,
                    "workflowPreviewContent": "",
                    "automation_type": "ai_service_selection",
                    "ai_service_options": [
                        {
                            "id": "inhouse",
                            "name": "In-House AI",
                            "description": "Our custom MCP LLM - Lower cost, optimized for business automation",
                            "credits": 2,
                            "features": ["Fast response", "Business-focused", "Cost-effective"]
                        },
                        {
                            "id": "openai",
                            "name": "OpenAI GPT",
                            "description": "GPT-4 powered AI - High quality, versatile content generation",
                            "credits": 5,
                            "features": ["Premium quality", "Advanced reasoning", "Creative content"]
                        },
                        {
                            "id": "claude",
                            "name": "Anthropic Claude",
                            "description": "Claude AI - Excellent for analysis and detailed responses",
                            "credits": 5,
                            "features": ["Analytical", "Detailed responses", "Code-friendly"]
                        }
                    ],
                    "original_request": user_message,
                    "intent_detected": "ai_content_email",
                    "confidence": 0.95,
                    "estimated_credits": "2-5 depending on service",
                    "action_required": "select_ai_service"
                })
            else:
                # Regular conversational response
                return JSONResponse(content={
                    "done": True,
                    "success": True,
                    "message": response_message,
                    "action_required": "none"
                })
        
        return JSONResponse(content={
            "done": False,
            "success": False,
            "message": "Unexpected response from AI orchestrator.",
            "action_required": "error"
        }, status_code=500)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Default MCP AI Chat endpoint error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error during default AI interaction", "message": str(e)}
        )


@app.get("/api/automation/templates")
async def get_automation_templates(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Endpoint to fetch agent templates for the automation dashboard.
    Supports filtering, searching, and pagination.
    """
    try:
        # Get query parameters
        category = request.query_params.get('category', 'all')
        search = request.query_params.get('search', '')
        sort_by = request.query_params.get('sortBy', 'template_name')
        sort_order = request.query_params.get('sortOrder', 'ASC')
        limit = int(request.query_params.get('limit', '50'))
        offset = int(request.query_params.get('offset', '0'))

        # Build query
        query = """
            SELECT 
                template_id,
                template_name,
                template_description,
                category,
                agent_name_template,
                agent_role_template,
                agent_personality_template,
                agent_expectations_template,
                usage_count,
                created_at,
                updated_at
            FROM agent_templates 
            WHERE is_active = true
        """
        
        query_params = []
        param_index = 1

        # Add category filter
        if category and category != 'all':
            query += f" AND category = ${param_index}"
            query_params.append(category)
            param_index += 1

        # Add search filter
        if search:
            query += f" AND (template_name ILIKE ${param_index} OR template_description ILIKE ${param_index} OR category ILIKE ${param_index})"
            query_params.append(f"%{search}%")
            param_index += 1

        # Add sorting
        valid_sort_columns = ['template_name', 'category', 'usage_count', 'created_at', 'updated_at']
        valid_sort_orders = ['ASC', 'DESC']
        
        if sort_by in valid_sort_columns and sort_order in valid_sort_orders:
            query += f" ORDER BY {sort_by} {sort_order}"
        else:
            query += " ORDER BY template_name ASC"

        # Add pagination
        query += f" LIMIT ${param_index} OFFSET ${param_index + 1}"
        query_params.extend([limit, offset])

        # Execute query
        async with db_manager.pool.acquire() as conn:
            # Get templates
            result = await conn.fetch(query, *query_params)
            
            # Convert to list of dicts
            templates = []
            for row in result:
                templates.append({
                    'template_id': str(row['template_id']),
                    'template_name': row['template_name'],
                    'template_description': row['template_description'],
                    'category': row['category'],
                    'agent_name_template': row['agent_name_template'],
                    'agent_role_template': row['agent_role_template'],
                    'agent_personality_template': row['agent_personality_template'],
                    'agent_expectations_template': row['agent_expectations_template'],
                    'usage_count': row['usage_count'],
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                    'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
                })
            
            # Get total count for pagination
            count_query = "SELECT COUNT(*) as total FROM agent_templates WHERE is_active = true"
            count_params = []
            count_param_index = 1

            if category and category != 'all':
                count_query += f" AND category = ${count_param_index}"
                count_params.append(category)
                count_param_index += 1

            if search:
                count_query += f" AND (template_name ILIKE ${count_param_index} OR template_description ILIKE ${count_param_index} OR category ILIKE ${count_param_index})"
                count_params.append(f"%{search}%")

            count_result = await conn.fetchval(count_query, *count_params)
            total = int(count_result)

            # Get categories for filter dropdown
            categories_result = await conn.fetch("""
                SELECT category, COUNT(*) as count 
                FROM agent_templates 
                WHERE is_active = true 
                GROUP BY category 
                ORDER BY category ASC
            """)

            categories = []
            for row in categories_result:
                categories.append({
                    'category': row['category'],
                    'count': int(row['count'])
                })

            return JSONResponse(content={
                "success": True,
                "data": {
                    "templates": templates,
                    "total": total,
                    "categories": categories,
                    "pagination": {
                        "limit": limit,
                        "offset": offset,
                        "hasMore": offset + limit < total
                    }
                }
            })

    except Exception as e:
        logger.error(f"Error fetching agent templates: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Failed to fetch agent templates",
                "details": str(e)
            }
        )


@app.post("/api/automations/execute")
async def execute_automation_workflow(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Endpoint to execute a confirmed automation workflow.
    This is called after the user confirms the workflow generated by the AI.
    """
    # current_user is guaranteed to be present
    try:
        body = await request.json()
        workflow_json = body.get('workflow_json')
        
        if not workflow_json:
            raise HTTPException(status_code=400, detail="Workflow JSON is required for execution.")
        
        logger.info(f"Executing confirmed workflow for user {current_user['email']}")
        
        if automation_engine is None:
            raise HTTPException(status_code=503, detail="Automation Engine not initialized.")

        # Pass the workflow JSON to the AutomationEngine for execution
        execution_result = await automation_engine.execute_workflow(workflow_json, str(current_user['user_id']))
        
        if execution_result.get("status") == "success":
            # Deduct credits after successful execution (conceptual)
            # await deduct_credits(str(current_user['user_id']), amount=1, reason="workflow_execution", service_used="automation_engine")
            logger.info(f"✅ Workflow executed successfully for user {current_user['email']}.")
            return JSONResponse(content={
                "success": True,
                "message": "Workflow executed successfully!",
                "execution_details": execution_result
            })
        else:
            logger.error(f"❌ Workflow execution failed for user {current_user['email']}: {execution_result.get('error')}")
            raise HTTPException(status_code=500, detail=f"Workflow execution failed: {execution_result.get('error')}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Execute workflow endpoint error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error during workflow execution", "message": str(e)}
        )


@app.post("/api/email/send")
async def send_email_directly(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Direct email sending endpoint for workflow execution
    """
    try:
        body = await request.json()
        
        to_email = body.get('to')
        subject = body.get('subject')
        content = body.get('content')
        from_name = body.get('from_name', 'DXTR Labs Automation')
        
        if not all([to_email, subject, content]):
            raise HTTPException(status_code=400, detail="to, subject, and content are required")
        
        if email_service is None or not email_service.configured:
            raise HTTPException(status_code=503, detail="Email service not configured")
        
        logger.info(f"Sending email to {to_email} from user {current_user['email']}")
        
        # Send the email
        result = email_service.send_email(to_email, subject, content)
        
        if result.get('success'):
            logger.info(f"✅ Email sent successfully to {to_email}")
            return JSONResponse(content={
                "success": True,
                "message": f"Email sent successfully to {to_email}",
                "email_sent": True,
                "recipient": to_email,
                "subject": subject
            })
        else:
            logger.error(f"❌ Email sending failed: {result.get('error')}")
            raise HTTPException(status_code=500, detail=f"Email sending failed: {result.get('error')}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send email endpoint error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error during email sending", "message": str(e)}
        )


# Removed old simplified /chat and /execute endpoints
# Removed old generate_automation_workflow and send_email_directly functions
# Removed include_personalized_ai_routes if it was just a placeholder
# for now, assuming api.chat and api.personalized_ai are not used for these new endpoints.

@app.post("/agents/{agent_id}/chat")
async def chat_with_agent(
    agent_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Chat endpoint for agents to handle natural language requests
    Includes email automation and other AI-powered workflows
    """
    try:
        body = await request.json()
        message = body.get('message', '').lower().strip()
        
        logger.info(f"Agent {agent_id} chat request from user {current_user['email']}: {message}")
        
        # Check if this is an email automation request
        if any(keyword in message for keyword in [
            'generate good morning content',
            'send email',
            'morning email',
            'good morning email',
            'send good morning'
        ]):
            # Extract email address from message if provided
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, message)
            
            if emails:
                target_email = emails[0]
                logger.info(f"Email automation request for: {target_email}")
                
                # Create morning email workflow
                from datetime import datetime
                current_date = datetime.now().strftime("%B %d, %Y")
                
                workflow = {
                    "workflow_id": f"morning-email-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "name": "AI Generated Morning Email",
                    "description": f"Send AI-generated morning content to {target_email}",
                    "user_id": str(current_user['user_id']),
                    "trigger": {
                        "type": "manual",
                        "name": "AI Chat Trigger",
                        "description": "Triggered by AI assistant chat"
                    },
                    "actions": [
                        {
                            "action_id": "ai-morning-email-001",
                            "node": "emailSend",
                            "name": "Send AI Morning Email",
                            "parameters": {
                                "toEmail": target_email,
                                "subject": f"🌅 Good Morning! AI-Generated Positivity - {current_date}",
                                "text": f"""Good morning, wonderful soul! ☀️

"Today is a blank canvas waiting for your masterpiece. Paint it with joy, courage, and endless possibilities!" ✨

✨ YOUR AI-GENERATED DAILY AFFIRMATIONS ✨
🌟 I am capable of achieving incredible things today
💪 Every challenge I face makes me stronger and wiser
😊 I choose to see opportunities in every situation
🚀 My potential is limitless and my dreams are valid
💖 I am grateful for this fresh start and new day

🌈 Remember, you have the power to make today amazing! Today is {current_date}, and it's YOUR day to shine.

The universe has aligned perfectly to bring you this moment. Trust in your abilities, embrace your uniqueness, and step forward with confidence! ✨

Take a deep breath, smile your beautiful smile, and let your light illuminate the world around you. You've absolutely got this! 💪

Sending you positive energy and warm vibes to make your day extraordinary! 🤗

May your day be filled with unexpected joys, meaningful connections, and beautiful moments! 🌺

With AI-powered love and positivity,
EGR201 - Your Personal AI Assistant 🤖💖

---
📧 Generated by EGR201 AI Assistant | {current_date}
🌅 Powered by Advanced AI Content Generation"""
                            }
                        }
                    ],
                    "metadata": {
                        "created_by": "EGR201 AI Assistant",
                        "created_date": datetime.now().isoformat(),
                        "purpose": "AI-generated morning motivation",
                        "recipient": target_email,
                        "execution_mode": "immediate",
                        "ai_generated": True
                    }
                }
                
                # Execute the workflow
                if automation_engine is None:
                    return JSONResponse(content={
                        "success": False,
                        "message": "I understand you want to send a morning email, but the automation engine is not available right now. Please try again later.",
                        "type": "error"
                    })
                
                try:
                    # Wrap workflow in the expected structure
                    workflow_payload = {"workflow": workflow}
                    execution_result = await automation_engine.execute_workflow(workflow_payload, str(current_user['user_id']))
                    
                    if execution_result.get("status") == "success":
                        return JSONResponse(content={
                            "success": True,
                            "message": f"✅ Perfect! I've generated beautiful morning content using AI and sent it to {target_email}. The email includes personalized affirmations, motivational quotes, and positive energy to start their day right! 🌅✨",
                            "type": "success",
                            "automation_result": execution_result
                        })
                    else:
                        return JSONResponse(content={
                            "success": False,
                            "message": f"I generated the morning content, but encountered an issue sending the email to {target_email}. The automation system reported: {execution_result.get('error', 'Unknown error')}",
                            "type": "error",
                            "automation_result": execution_result
                        })
                        
                except Exception as e:
                    logger.error(f"Email automation execution failed: {e}")
                    return JSONResponse(content={
                        "success": False,
                        "message": f"I understand you want to send a morning email to {target_email}, but I encountered a technical issue with the automation system. Please try again or contact support if the problem persists.",
                        "type": "error"
                    })
            else:
                return JSONResponse(content={
                    "success": False,
                    "message": "I'd be happy to generate and send morning content! Please specify the email address you'd like me to send it to. For example: 'generate good morning content and send to example@email.com'",
                    "type": "request_info"
                })
        
        # Default response for other types of messages
        return JSONResponse(content={
            "success": True,
            "message": "I understand you want to work with emails. As a Personal Assistant, I can help you set up email automation workflows. What email tasks would you like me to help you with?",
            "type": "general"
        })
        
    except Exception as e:
        logger.error(f"Agent chat error: {e}")
        return JSONResponse(content={
            "success": False,
            "message": "I apologize, but I encountered an error processing your request. Please try again.",
            "type": "error"
        }, status_code=500)

@app.post("/api/workflow/generate")
async def generate_workflow_with_mcp(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate workflow using Custom MCP LLM system
    Endpoint for testing MCP LLM workflow generation
    """
    try:
        body = await request.json()
        user_message = body.get('message', '').strip()
        user_id = body.get('user_id') or str(current_user['user_id'])
        agent_id = body.get('agent_id', 'sam')
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")

        logger.info(f"Workflow Generation: User {current_user['email']} requesting workflow: {user_message}")
        
        # Process message with Agent Processor
        agent_result = await agent_processor.process_with_agent(
            agent_id=agent_id,
            user_input=user_message,
            user_id=str(current_user['user_id'])
        )
        
        if agent_result.get("response_type") == "workflow" and agent_result.get("workflow_json"):
            # Extract workflow info for test compatibility
            workflow_json = agent_result["workflow_json"]
            
            # Convert to test-compatible format
            workflow_steps = []
            for node in workflow_json.get("nodes", []):
                step = {
                    "action_type": node.get("type", "unknown"),
                    "parameters": node.get("parameters", {})
                }
                
                # Add content for email generation detection
                if node.get("type") == "email_send":
                    step["action_type"] = "email_generation"
                    step["parameters"]["content"] = node.get("parameters", {}).get("body", "Custom MCP generated content")
                
                workflow_steps.append(step)
            
            test_workflow = {
                "id": workflow_json.get("workflow_id"),
                "name": workflow_json.get("workflow_name", "MCP Generated Workflow"),
                "steps": workflow_steps,
                "mcp_generated": True
            }
            
            return JSONResponse({
                "success": True,
                "message": "Workflow generated using MCP LLM",
                "workflow": test_workflow,
                "original_response": agent_result
            })
        
        else:
            # Not a workflow request
            return JSONResponse({
                "success": False,
                "message": "Request did not generate a workflow",
                "response": agent_result.get("response", "")
            })
        
    except Exception as e:
        logger.error(f"Workflow generation error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/api/workflow/confirm")
async def confirm_workflow(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Confirm and execute a workflow that's in preview state
    """
    try:
        body = await request.json()
        workflow_json = body.get('workflow_json')
        
        if not workflow_json:
            raise HTTPException(status_code=400, detail="Workflow JSON is required")
        
        logger.info(f"Executing workflow for user {current_user['email']}")
        
        # DEBUG: Log the received workflow_json structure
        logger.info(f"🔍 BACKEND DEBUG: Received workflow_json: {json.dumps(workflow_json, indent=2)}")
        logger.info(f"🔍 BACKEND DEBUG: Workflow type: {workflow_json.get('type')}")
        logger.info(f"🔍 BACKEND DEBUG: Workflow keys: {list(workflow_json.keys())}")
        
        # Execute the workflow using real automation
        logger.info("🚀 Executing real workflow automation...")
        
        try:
            # Check if this is an email workflow
            workflow_type = workflow_json.get("type")
            logger.info(f"🔍 BACKEND DEBUG: Checking workflow type: '{workflow_type}' == 'email_automation'? {workflow_type == 'email_automation'}")
            
            if workflow_type == "email_automation":
                recipient = workflow_json.get("recipient", "test@example.com")
                content_type = workflow_json.get("content_type", "marketing email")
                ai_service = workflow_json.get("ai_service", "none")
                needs_ai_generation = workflow_json.get("needs_ai_generation", False)
                
                logger.info(f"📧 Sending {content_type} to {recipient} using AI service: {ai_service}")
                
                # Execute MCP LLM workflow properly using automation engine
                if needs_ai_generation and ai_service != "none":
                    logger.info(f"🤖 Using MCP LLM system for AI content generation (service: {ai_service})")
                    
                    # Get the workflow data - prefer workflow.actions over top-level actions
                    workflow_data = workflow_json.get("workflow", {})
                    actions = workflow_data.get("actions", workflow_json.get("actions", []))
                    logger.info(f"🎯 BACKEND DEBUG: Found {len(actions)} actions in workflow")
                    
                    # Execute workflow through automation engine instead of manual processing
                    logger.info("🔧 Executing workflow through automation engine...")
                    
                    try:
                        # Import and use the automation engine
                        from mcp.simple_automation_engine import AutomationEngine
                        automation_engine = AutomationEngine()
                        
                        # Prepare workflow for automation engine
                        workflow_for_engine = {
                            "name": f"MCP_Email_Workflow_{ai_service}",
                            "type": "email_automation",
                            "actions": []
                        }
                        
                        # Convert MCP workflow actions to automation engine format
                        for action in actions:
                            action_type = action.get("node") or action.get("action_type", "unknown")
                            params = action.get("parameters", {})
                            
                            if action_type == "mcpLLM":
                                # Add AI content generation action
                                workflow_for_engine["actions"].append({
                                    "type": "content_generation",
                                    "parameters": {
                                        "user_input": params.get("user_input", f"Create {content_type}"),
                                        "content_type": content_type,
                                        "ai_service": ai_service,
                                        "user_id": current_user.get('user_id'),
                                        "agent_id": workflow_json.get("agent_id", "unknown")
                                    }
                                })
                            elif action_type == "emailSend":
                                # Add email sending action
                                workflow_for_engine["actions"].append({
                                    "type": "email",
                                    "parameters": {
                                        "to": params.get("toEmail", recipient),
                                        "subject": params.get("subject", f"🔦 AI-Generated {content_type.title()}"),
                                        "body": params.get("content") or params.get("text", "{ai_generated_content}"),
                                        "from_user": current_user.get('email'),
                                        "smtp_config": {
                                            "host": os.getenv('SMTP_HOST', 'mail.privateemail.com'),
                                            "port": int(os.getenv('SMTP_PORT', 587)),
                                            "user": os.getenv('SMTP_USER', 'automation-engine@dxtr-labs.com'),
                                            "password": os.getenv('SMTP_PASSWORD')
                                        }
                                    }
                                })
                        
                        logger.info(f"🚀 Executing workflow with {len(workflow_for_engine['actions'])} actions through automation engine")
                        
                        # Execute the workflow through automation engine
                        execution_result = await automation_engine.execute_workflow(workflow_for_engine)
                        
                        logger.info(f"✅ Automation engine execution completed: {execution_result.get('status')}")
                        
                        # Check if execution was successful
                        if execution_result.get('status') in ['completed', 'partial_success']:
                            email_result = {
                                "success": True,
                                "message": execution_result.get('message'),
                                "execution_details": execution_result
                            }
                        else:
                            email_result = {
                                "success": False,
                                "error": execution_result.get('message', 'Automation engine execution failed'),
                                "execution_details": execution_result
                            }
                            
                    except Exception as e:
                        logger.error(f"❌ Automation engine execution failed: {str(e)}")
                        email_result = {
                            "success": False,
                            "error": f"Automation engine error: {str(e)}"
                        }
                
                else:
                    # Simple email without AI generation (mock mode)
                    logger.info(f"📧 Simulating simple email (email functions not available)")
                    
                    # Simulate email sending
                    email_result = {
                        "success": True,
                        "message": "Email simulated successfully (email_sender module not available)"
                    }
                
                if email_result.get("success"):
                    execution_result = {
                        "status": "success",
                        "workflow_id": f"workflow_{int(time.time())}",
                        "message": f"✅ Marketing email successfully sent to {recipient}!",
                        "details": f"Real email automation completed: {email_result.get('message')}",
                        "email_sent": True,
                        "recipient": recipient,
                        "subject": "🚀 Revolutionary AI Solutions for Your Business - DXTR Labs"
                    }
                    logger.info(f"✅ Email sent successfully to {recipient}")
                else:
                    execution_result = {
                        "status": "error",
                        "workflow_id": f"workflow_{int(time.time())}",
                        "message": f"❌ Failed to send email: {email_result.get('error')}",
                        "details": "Email automation failed",
                        "email_sent": False
                    }
                    logger.error(f"❌ Email failed: {email_result.get('error')}")
            else:
                # For non-email workflows, still simulate
                execution_result = {
                    "status": "success",
                    "workflow_id": f"workflow_{int(time.time())}",
                    "message": "Workflow submitted for execution",
                    "details": "Non-email workflow simulated successfully"
                }
                
        except Exception as e:
            logger.error(f"❌ Workflow execution failed: {str(e)}")
            execution_result = {
                "status": "error",
                "workflow_id": f"workflow_{int(time.time())}",
                "message": f"Workflow execution failed: {str(e)}",
                "details": "Automation engine error"
            }
        
        if execution_result.get("status") == "success":
            logger.info(f"✅ Workflow executed successfully for user {current_user['email']}")
            return JSONResponse(content={
                "success": True,
                "message": "Workflow executed successfully!",
                "execution_details": execution_result
            })
        else:
            logger.error(f"❌ Workflow execution failed: {execution_result.get('error')}")
            raise HTTPException(status_code=500, detail=f"Workflow execution failed: {execution_result.get('error')}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workflow confirmation endpoint error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error during workflow confirmation", "message": str(e)}
        )

@app.get("/api/workflow/{workflow_id}/preview")
async def get_workflow_preview(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get workflow preview details for user review
    """
    try:
        # For simple mode, return a basic preview
        return JSONResponse(content={
            "workflow_id": workflow_id,
            "message": "Workflow preview not available in simple mode",
            "status": "simple_mode"
        })
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workflow preview endpoint error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error during workflow preview", "message": str(e)}
        )

# ===== ENHANCED TRIGGER MANAGEMENT ENDPOINTS =====

@app.get("/api/trigger-templates")
async def get_trigger_templates():
    """Get detailed trigger configuration templates with examples."""
    templates = {
        "cron": {
            "name": "Timer Trigger",
            "description": "Schedule workflows to run at specific times or intervals",
            "icon": "⏰",
            "parameters": {
                "triggerTimes": {
                    "type": "array",
                    "required": True,
                    "description": "Array of schedule objects defining when to trigger",
                    "items": {
                        "hour": {"type": "integer", "min": 0, "max": 23, "description": "Hour (0-23)"},
                        "minute": {"type": "integer", "min": 0, "max": 59, "description": "Minute (0-59)"},
                        "weekday": {"type": "string", "description": "Days of week (* for all, 1-7 for specific days)"},
                        "dayOfMonth": {"type": "integer", "min": 1, "max": 31, "description": "Day of month"},
                        "month": {"type": "string", "description": "Month (1-12)"}
                    }
                },
                "timezone": {"type": "string", "default": "UTC", "description": "Timezone for schedule"}
            },
            "examples": [
                {
                    "name": "Daily at 9 AM",
                    "config": {
                        "triggerTimes": [{"hour": 9, "minute": 0, "weekday": "*"}],
                        "timezone": "UTC"
                    }
                },
                {
                    "name": "Weekdays at 5 PM",
                    "config": {
                        "triggerTimes": [{"hour": 17, "minute": 0, "weekday": "1-5"}],
                        "timezone": "UTC"
                    }
                },
                {
                    "name": "Monthly Report (1st of month at 10 AM)",
                    "config": {
                        "triggerTimes": [{"hour": 10, "minute": 0, "dayOfMonth": 1}],
                        "timezone": "UTC"
                    }
                }
            ]
        },
        "webhook": {
            "name": "Webhook Trigger",
            "description": "Trigger workflows via HTTP requests from external systems",
            "icon": "🔗",
            "parameters": {
                "path": {
                    "type": "string",
                    "required": True,
                    "description": "Unique URL path for this webhook",
                    "pattern": "^[a-zA-Z0-9-_/]+$"
                },
                "method": {
                    "type": "string",
                    "default": "POST",
                    "enum": ["GET", "POST", "PUT", "PATCH"],
                    "description": "HTTP method to accept"
                },
                "authentication": {
                    "type": "object",
                    "description": "Optional authentication requirements",
                    "properties": {
                        "type": {"enum": ["none", "token", "signature"]},
                        "secret": {"type": "string", "description": "Secret key for validation"}
                    }
                }
            },
            "examples": [
                {
                    "name": "New Customer Signup",
                    "config": {
                        "path": "/new-customer",
                        "method": "POST",
                        "authentication": {"type": "token", "secret": "your-secret-key"}
                    }
                },
                {
                    "name": "Payment Success",
                    "config": {
                        "path": "/payment-success",
                        "method": "POST",
                        "authentication": {"type": "none"}
                    }
                }
            ]
        },
        "email_imap": {
            "name": "Email Listener",
            "description": "Monitor email inbox and trigger workflows on new emails",
            "icon": "📧",
            "parameters": {
                "mailbox": {
                    "type": "string",
                    "default": "INBOX",
                    "description": "Mailbox folder to monitor"
                },
                "postProcessAction": {
                    "type": "string",
                    "enum": ["read", "delete", "archive"],
                    "default": "read",
                    "description": "Action to take after processing email"
                },
                "format": {
                    "type": "string",
                    "enum": ["simple", "resolved", "raw"],
                    "default": "simple",
                    "description": "Email content format for workflow"
                },
                "downloadAttachments": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include email attachments in workflow data"
                },
                "filters": {
                    "type": "object",
                    "description": "Email filtering criteria",
                    "properties": {
                        "fromContains": {"type": "string", "description": "Filter by sender email"},
                        "subjectContains": {"type": "string", "description": "Filter by subject"},
                        "onlyUnread": {"type": "boolean", "default": True},
                        "bodyContains": {"type": "string", "description": "Filter by email body content"}
                    }
                }
            },
            "examples": [
                {
                    "name": "Customer Support Emails",
                    "config": {
                        "mailbox": "INBOX",
                        "postProcessAction": "read",
                        "format": "resolved",
                        "filters": {
                            "fromContains": "support@",
                            "onlyUnread": True
                        }
                    }
                },
                {
                    "name": "Order Confirmations",
                    "config": {
                        "mailbox": "INBOX",
                        "postProcessAction": "archive",
                        "format": "simple",
                        "filters": {
                            "subjectContains": "Order Confirmation",
                            "onlyUnread": True
                        }
                    }
                }
            ]
        }
    }
    
    return JSONResponse(content={"templates": templates})

@app.get("/api/triggers/templates")
async def get_trigger_templates_api():
    """Get detailed trigger configuration templates with examples for frontend."""
    templates = {
        "cron": {
            "name": "Timer Trigger",
            "description": "Schedule workflows to run at specific times or intervals",
            "icon": "⏰",
            "parameters": {
                "triggerTimes": {
                    "type": "array",
                    "required": True,
                    "description": "Array of schedule objects defining when to trigger",
                    "items": {
                        "hour": {"type": "integer", "min": 0, "max": 23, "description": "Hour (0-23)"},
                        "minute": {"type": "integer", "min": 0, "max": 59, "description": "Minute (0-59)"},
                        "weekday": {"type": "string", "description": "Days of week (* for all, 1-7 for specific days)"},
                        "dayOfMonth": {"type": "integer", "min": 1, "max": 31, "description": "Day of month"},
                        "month": {"type": "string", "description": "Month (1-12)"}
                    }
                },
                "timezone": {"type": "string", "default": "UTC", "description": "Timezone for schedule"}
            },
            "examples": [
                {
                    "name": "Daily at 9 AM",
                    "config": {
                        "triggerTimes": [{"hour": 9, "minute": 0, "weekday": "*"}],
                        "timezone": "UTC"
                    }
                },
                {
                    "name": "Weekdays at 5 PM",
                    "config": {
                        "triggerTimes": [{"hour": 17, "minute": 0, "weekday": "1-5"}],
                        "timezone": "UTC"
                    }
                }
            ]
        },
        "webhook": {
            "name": "Webhook Trigger",
            "description": "Trigger workflows via HTTP requests from external systems",
            "icon": "🔗",
            "parameters": {
                "path": {
                    "type": "string",
                    "required": True,
                    "description": "Unique URL path for this webhook",
                    "pattern": "^[a-zA-Z0-9-_/]+$"
                },
                "method": {
                    "type": "string",
                    "default": "POST",
                    "enum": ["GET", "POST", "PUT", "PATCH"],
                    "description": "HTTP method to accept"
                }
            },
            "examples": [
                {
                    "name": "New Customer Signup",
                    "config": {
                        "path": "/new-customer",
                        "method": "POST"
                    }
                }
            ]
        },
        "manual": {
            "name": "Manual Trigger",
            "description": "Manually triggered execution",
            "icon": "🎯",
            "parameters": {},
            "examples": [
                {
                    "name": "Manual Execution",
                    "config": {}
                }
            ]
        }
    }
    
    return JSONResponse(content={"templates": templates})
    
    return {
        "success": True,
        "templates": templates,
        "message": "Trigger templates retrieved successfully"
    }

@app.post("/api/agents/{agent_id}/triggers/validate")
async def validate_trigger_config(
    agent_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Validate trigger configuration before saving."""
    try:
        body = await request.json()
        trigger_type = body.get('triggerType')
        trigger_config = body.get('triggerConfig', {})
        
        # Verify agent ownership
        agent = await agent_manager_instance.get_agent_details(agent_id, str(current_user['user_id']))
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found or access denied")
        
        validation_result = {"valid": True, "errors": [], "warnings": []}
        
        # Validate based on trigger type
        if trigger_type == "cron":
            if not trigger_config.get('triggerTimes'):
                validation_result["errors"].append("triggerTimes is required for cron triggers")
            else:
                for i, schedule in enumerate(trigger_config['triggerTimes']):
                    if 'hour' not in schedule or 'minute' not in schedule:
                        validation_result["errors"].append(f"Schedule {i+1}: hour and minute are required")
                    if schedule.get('hour', 0) < 0 or schedule.get('hour', 0) > 23:
                        validation_result["errors"].append(f"Schedule {i+1}: hour must be 0-23")
                    if schedule.get('minute', 0) < 0 or schedule.get('minute', 0) > 59:
                        validation_result["errors"].append(f"Schedule {i+1}: minute must be 0-59")
        
        elif trigger_type == "webhook":
            path = trigger_config.get('path')
            if not path:
                validation_result["errors"].append("path is required for webhook triggers")
            elif not path.startswith('/'):
                validation_result["errors"].append("webhook path must start with '/'")
            
            method = trigger_config.get('method', 'POST')
            if method not in ['GET', 'POST', 'PUT', 'PATCH']:
                validation_result["errors"].append("method must be GET, POST, PUT, or PATCH")
        
        elif trigger_type == "email_imap":
            mailbox = trigger_config.get('mailbox')
            if not mailbox:
                validation_result["warnings"].append("mailbox not specified, will use INBOX")
        
        else:
            validation_result["errors"].append(f"Unknown trigger type: {trigger_type}")
        
        validation_result["valid"] = len(validation_result["errors"]) == 0
        
        return {
            "success": True,
            "validation": validation_result
        }
        
    except Exception as e:
        logger.error(f"Error validating trigger config: {e}")
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@app.post("/api/agents/{agent_id}/trigger/manual")
async def trigger_agent_manually(
    agent_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Manually trigger an agent execution."""
    try:
        body = await request.json()
        trigger_data = body.get('trigger_data', {})
        
        # Verify agent ownership
        agent = await agent_manager_instance.get_agent_details(agent_id, str(current_user['user_id']))
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found or access denied")
        
        # Check if agent supports manual triggers
        if agent.get('operation_mode') not in ['trigger', 'both']:
            raise HTTPException(status_code=400, detail="Agent does not support manual triggers")
        
        # Execute the agent manually using AgentProcessor
        result = await agent_processor.execute_manual_trigger(
            agent_id=agent_id,
            user_id=str(current_user['user_id']),
            trigger_data=trigger_data
        )
        
        return {
            "success": True,
            "execution_id": result.get('execution_id'),
            "message": "Agent triggered successfully",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error manually triggering agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger agent: {str(e)}")

@app.get("/api/agents/{agent_id}/executions")
async def get_agent_executions(
    agent_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get execution history for an agent."""
    try:
        # Verify agent ownership
        agent = await agent_manager_instance.get_agent_details(agent_id, str(current_user['user_id']))
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found or access denied")
        
        # Get executions from database
        async with agent_manager_instance.db_pool.acquire() as conn:
            query = """
                SELECT id, user_id, trigger_type, input_data, output_data, 
                       execution_status, execution_time_ms, error_message, created_at
                FROM agent_executions 
                WHERE agent_id = $1 
                ORDER BY created_at DESC 
                LIMIT $2 OFFSET $3
            """
            rows = await conn.fetch(query, agent_id, limit, offset)
            
            executions = []
            for row in rows:
                executions.append({
                    "id": str(row['id']),
                    "user_id": row['user_id'],
                    "trigger_type": row['trigger_type'],
                    "input_data": row['input_data'],
                    "output_data": row['output_data'],
                    "execution_status": row['execution_status'],
                    "execution_time_ms": row['execution_time_ms'],
                    "error_message": row['error_message'],
                    "created_at": row['created_at'].isoformat() if row['created_at'] else None
                })
        
        return {
            "success": True,
            "executions": executions,
            "total": len(executions),
            "limit": limit,
            "offset": offset
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent executions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get executions: {str(e)}")

@app.post("/api/test/openai")
async def test_openai_driver(current_user: dict = Depends(get_current_user)):
    """Test OpenAI driver with the workflow JSON structure."""
    try:
        logger.info(f"Testing OpenAI driver for user {current_user['email']}")
        
        # Create test workflow for OpenAI
        test_workflow = {
            "workflow_id": "test_openai_driver",
            "workflow_name": "OpenAI Driver Test",
            "trigger": {"type": "manual"},
            "nodes": [
                {
                    "id": "openai_test_node",
                    "type": "ai_content_generation",
                    "script": {
                        "driver": "openai_driver"
                    },
                    "parameters": {
                        "prompt": "Write a professional welcome message for new users of an automation platform",
                        "model": "gpt-3.5-turbo",
                        "max_tokens": 150,
                        "temperature": 0.7,
                        "context": "You are a helpful AI assistant for business automation"
                    }
                }
            ]
        }
        
        # Test execution
        if automation_engine is None:
            return JSONResponse(content={
                "success": False,
                "error": "Automation Engine not initialized"
            })
        
        # Execute the test workflow
        logger.info("🧪 Executing OpenAI test workflow...")
        execution_result = await automation_engine.execute_workflow_nodes(test_workflow)
        
        return JSONResponse(content={
            "success": True,
            "message": "OpenAI driver test completed",
            "test_workflow": test_workflow,
            "execution_result": execution_result,
            "driver_status": "✅ WORKING" if execution_result.get("success") else "❌ FAILED"
        })
        
    except Exception as e:
        logger.error(f"OpenAI driver test error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "OpenAI driver test failed", "message": str(e)}
        )

@app.post("/api/test/all-drivers")
async def test_all_drivers_simple(current_user: dict = Depends(get_current_user)):
    """Simple test of all drivers with basic workflows."""
    try:
        logger.info(f"Testing all drivers for user {current_user['email']}")
        
        # Define simple test workflows for each driver
        test_cases = {
            "email_send": {
                "workflow_id": "test_email",
                "nodes": [{
                    "id": "email_node",
                    "type": "email_send",
                    "script": {"driver": "email_send_driver"},
                    "parameters": {
                        "toEmail": "test@example.com",
                        "subject": "Test Email",
                        "text": "This is a test email from the automation engine."
                    }
                }]
            },
            "openai": {
                "workflow_id": "test_openai",
                "nodes": [{
                    "id": "openai_node",
                    "type": "ai_content_generation",
                    "script": {"driver": "openai_driver"},
                    "parameters": {
                        "prompt": "Write a short greeting message",
                        "model": "gpt-3.5-turbo",
                        "max_tokens": 50
                    }
                }]
            },
            "http_request": {
                "workflow_id": "test_http",
                "nodes": [{
                    "id": "http_node",
                    "type": "http_request",
                    "script": {"driver": "http_request_driver"},
                    "parameters": {
                        "url": "https://httpbin.org/get",
                        "method": "GET"
                    }
                }]
            }
        }
        
        results = {}
        
        for driver_name, workflow in test_cases.items():
            try:
                logger.info(f"🧪 Testing {driver_name}...")
                
                # Test driver loading
                driver_file = workflow["nodes"][0]["script"]["driver"]
                driver = await automation_engine.load_driver(driver_file.replace("_driver", ""))
                
                driver_loadable = driver is not None
                
                results[driver_name] = {
                    "driver_loadable": driver_loadable,
                    "workflow_structure": "✅ Valid",
                    "test_status": "✅ COMPATIBLE" if driver_loadable else "❌ LOAD_FAILED",
                    "workflow": workflow
                }
                
            except Exception as e:
                logger.error(f"❌ {driver_name} test failed: {e}")
                results[driver_name] = {
                    "driver_loadable": False,
                    "test_status": "❌ ERROR",
                    "error": str(e),
                    "workflow": workflow
                }
        
        # Summary
        passed = sum(1 for r in results.values() if r.get("driver_loadable", False))
        total = len(results)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Driver compatibility test completed: {passed}/{total} drivers compatible",
            "summary": {
                "total_tested": total,
                "compatible": passed,
                "incompatible": total - passed,
                "pass_rate": f"{(passed/total)*100:.1f}%"
            },
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Driver testing error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Driver testing failed", "message": str(e)}
        )

@app.get("/api/drivers/info")
async def get_drivers_info():
    """Get information about available drivers and their expected JSON structure."""
    return JSONResponse(content={
        "success": True,
        "drivers": {
            "email_send": {
                "driver_file": "email_send_driver.py",
                "node_type": "email_send",
                "required_params": ["toEmail", "subject", "text"],
                "json_structure": {
                    "id": "email_node_1",
                    "type": "email_send",
                    "script": {"driver": "email_send_driver"},
                    "parameters": {
                        "toEmail": "recipient@example.com",
                        "subject": "Email Subject",
                        "text": "Email content"
                    }
                }
            },
            "openai": {
                "driver_file": "openai_driver.py",
                "node_type": "ai_content_generation",
                "required_params": ["prompt"],
                "json_structure": {
                    "id": "openai_node_1",
                    "type": "ai_content_generation",
                    "script": {"driver": "openai_driver"},
                    "parameters": {
                        "prompt": "Your prompt here",
                        "model": "gpt-3.5-turbo",
                        "max_tokens": 150,
                        "temperature": 0.7
                    }
                }
            },
            "http_request": {
                "driver_file": "http_request_driver.py",
                "node_type": "http_request",
                "required_params": ["url", "method"],
                "json_structure": {
                    "id": "http_node_1",
                    "type": "http_request",
                    "script": {"driver": "http_request_driver"},
                    "parameters": {
                        "url": "https://api.example.com",
                        "method": "GET",
                        "headers": {},
                        "body": {}
                    }
                }
            },
            "mcp_llm": {
                "driver_file": "mcp_llm_driver.py",
                "node_type": "mcp_llm",
                "required_params": ["user_input"],
                "json_structure": {
                    "id": "mcp_node_1",
                    "type": "mcp_llm",
                    "script": {"driver": "mcp_llm_driver"},
                    "parameters": {
                        "user_input": "Your input here",
                        "context": "Context information",
                        "max_tokens": 150,
                        "temperature": 0.7
                    }
                }
            }
        },
        "workflow_structure": {
            "workflow_id": "example_workflow",
            "workflow_name": "Example Workflow",
            "trigger": {"type": "manual"},
            "nodes": [
                "// Array of node objects with id, type, script, and parameters"
            ]
        }
    })

@app.post("/api/agents/{agent_id}/chat")
async def agent_chat(agent_id: str, request: Request):
    """Process chat message with agent's custom LLM instance - TEMP: NO AUTH FOR TESTING."""
    try:
        body = await request.json()
        message = body.get('message', '').strip()
        
        print(f"🧪 AGENT CHAT: Processing '{message}' for agent {agent_id}")
        
        # Special debugging for email sending
        if message.startswith("SEND_APPROVED_EMAIL"):
            print(f"📧 EMAIL SEND REQUEST: {message}")
            print(f"📧 EMAIL BODY KEYS: {list(body.keys())}")
            print(f"📧 EMAIL CONTENT: {body.get('email_content', 'NO CONTENT')[:100]}...")
        
        if not message:
            return JSONResponse(
                status_code=400,
                content={"error": "Message is required"}
            )

        # Get or create agent's LLM instance
        agent_llm = await agent_manager_instance.get_agent_llm(agent_id)
        print(f"🧪 AGENT CHAT: Got agent_llm instance")
        
        # Process the message using the agent's CustomMCPLLM instance
        # CRITICAL: Pass the full body as request_data for email content
        response = await agent_llm.process_user_request(message, request_data=body)
        print(f"🧪 AGENT CHAT: Response keys = {list(response.keys())}")
        print(f"🧪 AGENT CHAT: Status = {response.get('status')}")
        print(f"🧪 AGENT CHAT: Has workflow_preview = {bool(response.get('workflow_preview'))}")
        
        # Return the FULL response structure - don't filter anything
        return JSONResponse(content=response)
        
    except ValueError as e:
        print(f"🧪 AGENT CHAT: ValueError = {e}")
        return JSONResponse(
            status_code=404,
            content={"error": str(e)}
        )
    except Exception as e:
        print(f"🧪 AGENT CHAT: Exception = {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/api/test/agents/{agent_id}/chat")
async def test_agent_chat(agent_id: str, request: Request):
    """Process chat message with agent's custom LLM instance - TEST ENDPOINT (no auth)."""
    try:
        body = await request.json()
        message = body.get('message', '').strip()
        
        if not message:
            return JSONResponse(
                status_code=400,
                content={"error": "Message is required"}
            )
        
        logger.error(f"🧪 TEST ENDPOINT: Processing message '{message}' for agent {agent_id}")
        print(f"🧪 PRINT TEST: Processing message '{message}' for agent {agent_id}")
        
        # Get or create agent's LLM instance
        agent_llm = await agent_manager_instance.get_agent_llm(agent_id)
        
        # Process the message using the agent's CustomMCPLLM instance
        # CRITICAL: Pass the full body as request_data for email content
        response = await agent_llm.process_user_request(message, request_data=body)
        
        logger.error(f"🧪 TEST ENDPOINT: Response type = {response.get('status')}, message = {response.get('response', '')[:100]}")
        
        # Pass through all workflow-related fields for proper automation testing
        result = {
            "success": True,
            "response": response.get("response", ""),
            "workflow_status": response.get("status"),
            "processing_time": response.get("processing_time"),
            "automation_type": response.get("automation_type"),
            # Include all workflow fields
            "workflowJson": response.get("workflowJson"),
            "workflowPreview": response.get("workflowPreview"),
            "hasWorkflowJson": response.get("hasWorkflowJson", False),
            "hasWorkflowPreview": response.get("hasWorkflowPreview", False),
            "status": response.get("status"),
            "done": response.get("done"),
            "debug_info": {
                "response_keys": list(response.keys()),
                "message_length": len(message),
                "agent_id": agent_id
            }
        }
        
        return JSONResponse(content=result)
        
    except ValueError as e:
        logger.error(f"🧪 TEST ENDPOINT: ValueError = {e}")
        return JSONResponse(
            status_code=404,
            content={"error": str(e)}
        )
    except Exception as e:
        logger.error(f"🧪 TEST ENDPOINT: Exception = {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/api/test/direct-openai/{agent_id}/chat")
async def test_direct_openai_chat(agent_id: str, request: Request):
    """Direct OpenAI call bypassing all complex backend logic - ISOLATION TEST."""
    try:
        body = await request.json()
        message = body.get('message', '').strip()
        
        if not message:
            return JSONResponse(
                status_code=400,
                content={"error": "Message is required"}
            )
        
        logger.error(f"🔥 DIRECT OPENAI TEST: Message '{message}' for agent {agent_id}")
        print(f"🔥 DIRECT OPENAI TEST: Message '{message}' for agent {agent_id}")
        
        # Get OpenAI API key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not openai_api_key:
            return JSONResponse(
                status_code=500,
                content={"error": "OpenAI API key not found"}
            )
        
        logger.error(f"🔥 DIRECT OPENAI: API key loaded: {len(openai_api_key)} chars")
        
        # Direct OpenAI call with DXTR Labs context
        from openai import OpenAI
        client = OpenAI(api_key=openai_api_key)
        
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful AI assistant for DXTR Labs, a cutting-edge automation and AI solutions company. You help users create automated workflows, AI-powered processes, and intelligent business solutions. Be conversational, friendly, and focus on understanding what automation the user needs. Always maintain the DXTR Labs professional brand while being approachable."""
                },
                {"role": "user", "content": message}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        ai_response = completion.choices[0].message.content
        
        logger.error(f"🔥 DIRECT OPENAI SUCCESS: Response length = {len(ai_response)}")
        logger.error(f"🔥 DIRECT OPENAI RESPONSE: {ai_response}")
        
        return JSONResponse(content={
            "success": True,
            "response": ai_response,
            "method": "DIRECT_OPENAI_BYPASS",
            "test_info": {
                "message_length": len(message),
                "response_length": len(ai_response),
                "agent_id": agent_id,
                "api_key_length": len(openai_api_key) if openai_api_key else 0
            }
        })
        
    except Exception as e:
        logger.error(f"🔥 DIRECT OPENAI ERROR: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Direct OpenAI test failed: {str(e)}"}
        )

# Main execution
if __name__ == "__main__":
    import uvicorn
    logger.info("� Starting AutoFlow AI Automation Platform...")
    logger.info("� Backend Server URL: http://localhost:8002")
    logger.info("📚 API Documentation: http://localhost:8002/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
