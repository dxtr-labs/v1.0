#!/usr/bin/env python3
"""
Direct OpenAI test to check if the integration is working
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env.local like the MCP engine does
env_path = Path(__file__).parent / '.env.local'
print(f"Looking for .env.local at: {env_path}")
load_dotenv(dotenv_path=env_path)

# Check if OpenAI API key is loaded
openai_key = os.getenv("OPENAI_API_KEY")
print(f"OpenAI API key found: {bool(openai_key)}")
if openai_key:
    print(f"Key starts with: {openai_key[:20]}...")

# Try importing OpenAI
try:
    import openai
    from openai import AsyncOpenAI
    print("✅ OpenAI import successful")
    
    # Test basic OpenAI call
    async def test_openai():
        if not openai_key:
            print("❌ No API key available")
            return
            
        try:
            client = AsyncOpenAI(api_key=openai_key)
            
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant from DXTR Labs."},
                    {"role": "user", "content": "Say hello and mention DXTR Labs"}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            result = response.choices[0].message.content.strip()
            print(f"✅ OpenAI response: {result}")
            
        except Exception as e:
            print(f"❌ OpenAI call failed: {e}")
    
    # Run the async test
    import asyncio
    asyncio.run(test_openai())
    
except ImportError as e:
    print(f"❌ OpenAI import failed: {e}")

# Test environment loading
print(f"\nEnvironment test:")
print(f"OPENAI_API_KEY length: {len(openai_key) if openai_key else 0}")

# Test if the backend can see the environment  
sys.path.append('backend')
try:
    from mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine
    
    # Create a test MCP instance
    mcp = CustomMCPLLMIterationEngine(
        agent_id="test-agent",
        session_id="test-session"
    )
    
    print(f"\n🔍 MCP Engine test:")
    print(f"Has OpenAI key: {bool(mcp.openai_api_key)}")
    if mcp.openai_api_key:
        print(f"Key starts with: {mcp.openai_api_key[:20]}...")
    
    # Try the AI response method
    async def test_mcp_ai():
        try:
            response = await mcp._generate_ai_conversational_response(
                user_input="hello test",
                agent_name="Test Agent", 
                agent_role="Test Assistant",
                previous_interactions=[],
                user_preferences={}
            )
            
            print(f"MCP AI response: {response}")
            
        except Exception as e:
            print(f"MCP AI response failed: {e}")
    
    asyncio.run(test_mcp_ai())
    
except Exception as e:
    print(f"❌ MCP test failed: {e}")
