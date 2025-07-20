"""
Simple test to prove OpenAI integration works directly
"""
import os
import requests
import json

# Load environment variables
from dotenv import load_dotenv
load_dotenv()
load_dotenv(".env")
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Test OpenAI directly
def test_openai_direct():
    """Test OpenAI integration directly"""
    
    # Get OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ OpenAI API key not found")
        return
    
    print(f"✅ OpenAI API key loaded ({len(openai_api_key)} chars)")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_api_key)
        
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful AI assistant for DXTR Labs, a cutting-edge automation and AI solutions company. You help users create automated workflows, AI-powered processes, and intelligent business solutions. Be conversational, friendly, and focus on understanding what automation the user needs. Always maintain the DXTR Labs professional brand while being approachable."""
                },
                {"role": "user", "content": "I need help with email automation"}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        ai_response = completion.choices[0].message.content
        
        print(f"🔥 DIRECT OPENAI SUCCESS: Response length = {len(ai_response)}")
        print(f"🔥 DIRECT OPENAI RESPONSE: {ai_response}")
        
        return {
            "success": True,
            "response": ai_response,
            "method": "DIRECT_OPENAI_PYTHON_TEST",
            "response_length": len(ai_response),
            "api_key_length": len(openai_api_key)
        }
        
    except Exception as e:
        print(f"🔥 DIRECT OPENAI ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

if __name__ == "__main__":
    print("🧪 Testing direct OpenAI integration...")
    result = test_openai_direct()
    print(f"🧪 Test result: {json.dumps(result, indent=2)}")
