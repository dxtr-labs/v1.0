#!/usr/bin/env python3
"""
Simplified main.py for testing
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="AutoFlow Test Server", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "AutoFlow Test Server is running!", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Server is healthy"}

@app.get("/api/trigger-templates")
async def get_trigger_templates():
    """Get trigger configuration templates."""
    templates = {
        "cron": {
            "name": "Timer Trigger",
            "description": "Schedule workflows to run at specific times",
            "examples": [
                {"name": "Daily at 9 AM", "config": {"hour": 9, "minute": 0}}
            ]
        },
        "webhook": {
            "name": "Webhook Trigger", 
            "description": "Trigger via HTTP requests",
            "examples": [
                {"name": "New Customer", "config": {"path": "/new-customer"}}
            ]
        }
    }
    
    return {"success": True, "templates": templates}

if __name__ == "__main__":
    logger.info("🚀 Starting AutoFlow Test Server...")
    logger.info("📡 Server will be available at: http://127.0.0.1:8002")
    
    uvicorn.run(
        "test_main:app",
        host="127.0.0.1",
        port=8002,
        reload=False,
        log_level="info"
    )
