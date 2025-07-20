#!/usr/bin/env python3
"""
AutoFlow AI Platform - SQLite Fallback Version
Backend server with SQLite authentication when PostgreSQL is unavailable
"""

import os
import sys
import logging
import secrets
import uvicorn
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI, Request, HTTPException, Cookie, Depends, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try PostgreSQL first, fallback to SQLite
try:
    from db.postgresql_manager import (
        db_manager, init_db, close_db,
        create_user, authenticate_user, get_user_by_session, update_user_session,
        get_user_by_id, add_credits, deduct_credits, get_credit_history
    )
    logger.info("✅ Using PostgreSQL database")
    USE_SQLITE = False
except Exception as e:
    logger.warning(f"⚠️ PostgreSQL unavailable: {e}")
    logger.info("🔄 Falling back to SQLite authentication...")
    
    from sqlite_auth_fallback import (
        create_user, authenticate_user, get_user_by_session, update_user_session,
        get_user_by_id, add_credits, deduct_credits, get_credit_history
    )
    USE_SQLITE = True
    
    # Mock database manager for SQLite fallback
    class MockDBManager:
        async def initialize(self): 
            logger.info("✅ SQLite database initialized")
        async def close(self): 
            logger.info("✅ SQLite database closed")
    
    db_manager = MockDBManager()
    
    async def init_db(): 
        await db_manager.initialize()
        return True
    
    async def close_db(): 
        await db_manager.close()

# Import other components with fallbacks
try:
    from mcp.simple_automation_engine import AutomationEngine
except ImportError:
    try:
        from mcp.automation_engine import AutomationEngine
    except ImportError:
        # Create a minimal fallback AutomationEngine
        class AutomationEngine:
            def __init__(self):
                logger.warning("⚠️ Using fallback AutomationEngine")
                pass

from core.simple_agent_manager import AgentManager
from core.agent_processor import AgentProcessor
from simple_email_service import EmailService

# Global instances
automation_engine = None
agent_manager = None
agent_processor = None
email_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    global automation_engine, agent_manager, agent_processor, email_service
    
    logger.info("🚀 Starting AutoFlow Platform with SQLite fallback...")
    
    try:
        # Initialize database
        await init_db()
        
        # Initialize components
        automation_engine = AutomationEngine()
        agent_manager = AgentManager()
        
        # Initialize email service
        email_service = EmailService()
        
        # Initialize agent processor
        agent_processor = AgentProcessor()
        
        logger.info("✅ AutomationEngine and AgentProcessor initialized.")
        logger.info("🔧 Features: User auth, agent management, custom MCP LLM code, trigger automation.")
        logger.info("🚀 Universal drivers initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    finally:
        # Cleanup
        logger.info("🔌 Shutting down AutoFlow Platform...")
        await close_db()
        logger.info("👋 AutoFlow AI Platform shut down gracefully")

# Create FastAPI app
app = FastAPI(
    title="AutoFlow AI Platform",
    description="AI-powered automation platform with SQLite fallback",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to get current user from session
async def get_current_user(
    session_token: str = Cookie(None, alias="session_token"),
    authorization: str = Header(None)
):
    """Extract user from session token or header, raising HTTPException if not found."""
    
    # Try session token from cookie first
    if session_token:
        user = await get_user_by_session(session_token)
        if user:
            logger.info(f"AUTH - Found user via session: {user['email']}")
            return user
    
    # Try authorization header (Bearer token or user ID)
    if authorization:
        try:
            if authorization.startswith('Bearer '):
                token = authorization[7:]
                user = await get_user_by_session(token)
                if user:
                    logger.info(f"AUTH - Found user via header: {user['email']}")
                    return user
        except Exception as e:
            logger.warning(f"AUTH - Invalid user ID in header: {e}")
    
    logger.warning("AUTH - User not authenticated or session invalid.")
    raise HTTPException(status_code=401, detail="Not authenticated")

# ===== HEALTH CHECK =====
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "SQLite" if USE_SQLITE else "PostgreSQL",
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
        first_name = body.get('first_name', '')
        last_name = body.get('last_name', '')
        username = body.get('username')
        organization = body.get('is_organization', False)
        
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
            "session_token": session_token
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
    return {
        "user": {
            "user_id": str(current_user['user_id']),
            "email": current_user['email'],
            "first_name": current_user['first_name'],
            "last_name": current_user['last_name'],
            "name": f"{current_user['first_name']} {current_user['last_name']}".strip(),
            "username": current_user['username'],
            "credits": current_user['credits'],
            "organization": current_user.get('organization', False)
        }
    }

# ===== CHAT ENDPOINTS =====

@app.post("/api/chat/mcpai")
async def chat_mcpai(request: Request):
    """Public MCP AI chat endpoint (no auth required)"""
    try:
        body = await request.json()
        message = body.get('message', '')
        session_id = body.get('session_id', 'anonymous')
        
        if not message:
            return JSONResponse(
                status_code=400,
                content={"error": "Message is required"}
            )
        
        # Process with agent processor
        result = await agent_processor.process_message(
            message=message,
            session_id=session_id,
            user_id="anonymous"
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"MCPAI chat error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

@app.post("/chat")
async def chat_authenticated(request: Request, current_user: dict = Depends(get_current_user)):
    """Authenticated chat endpoint"""
    try:
        body = await request.json()
        message = body.get('message', '')
        session_id = body.get('session_id', f"user_{current_user['user_id']}")
        
        if not message:
            return JSONResponse(
                status_code=400,
                content={"error": "Message is required"}
            )
        
        # Process with agent processor
        result = await agent_processor.process_message(
            message=message,
            session_id=session_id,
            user_id=str(current_user['user_id'])
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Authenticated chat error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

# Main execution
if __name__ == "__main__":
    logger.info("🚀 Starting AutoFlow AI Automation Platform with SQLite fallback...")
    logger.info("🌐 Backend Server URL: http://localhost:8002")
    logger.info("📚 API Documentation: http://localhost:8002/docs")
    
    uvicorn.run(
        "main_sqlite:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )