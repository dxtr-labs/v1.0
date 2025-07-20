"""
FastAPI Main Application for AutoFlow AI Automation Platform - Clean Version
Direct OpenAI Test Implementation
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging
import uvicorn

# Load environment variables
load_dotenv()
load_dotenv(".env")
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log OpenAI API key status
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key:
    logger.info(f"✅ OpenAI API key loaded ({len(openai_key)} chars)")
else:
    logger.error("❌ OpenAI API key not found")

# Create FastAPI app
app = FastAPI(title="AutoFlow AI Platform", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AutoFlow AI Automation Platform", "status": "running"}

@app.post("/api/test/direct-openai/{agent_id}/chat")
async def test_direct_openai_chat(agent_id: str, request: Request):
    """Direct OpenAI call bypassing all complex backend logic - ISOLATION TEST."""
    try:
        body = await request.json()
        message = body.get('message', '').strip()
        
        if not message:
            return JSONResponse(status_code=400, content={"error": "Message is required"})
        
        logger.error(f"🔥 DIRECT OPENAI TEST: Message '{message}' for agent {agent_id}")
        print(f"🔥 DIRECT OPENAI TEST: Message '{message}' for agent {agent_id}")
        
        # Get OpenAI API key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            return JSONResponse(status_code=500, content={"error": "OpenAI API key not found"})
        
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
        return JSONResponse(status_code=500, content={"error": f"Direct OpenAI test failed: {str(e)}"})


# Main execution
if __name__ == "__main__":
    logger.info("🚀 Starting AutoFlow AI Automation Platform...")
    logger.info("📡 Backend Server URL: http://localhost:8002")
    logger.info("📚 API Documentation: http://localhost:8002/docs")
    
    uvicorn.run(
        "main_clean:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )
