import os
import requests

def test_openai_key_and_backend():
    """Test OpenAI API key availability and backend initialization"""
    
    print("🔍 OPENAI API KEY TEST")
    print("=" * 40)
    
    # Test environment variable
    openai_key = os.getenv("OPENAI_API_KEY")
    print(f"OpenAI API Key from env: {openai_key[:20] + '...' if openai_key else 'NOT FOUND'}")
    print(f"Key length: {len(openai_key) if openai_key else 0}")
    
    # Test OpenAI import
    try:
        import openai
        from openai import AsyncOpenAI
        print("✅ OpenAI package import successful")
    except ImportError as e:
        print(f"❌ OpenAI package import failed: {e}")
        return
    
    # Test backend response with detailed debugging
    url = "http://localhost:8002/api/test/agents/1b58f5f0-931e-46e5-b7d9-f76bd189b96d/chat"
    payload = {
        "message": "debug openai test",
        "agentId": "1b58f5f0-931e-46e5-b7d9-f76bd189b96d"
    }
    
    print("\n🔍 BACKEND TEST")
    print("=" * 40)
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data.get('response')}")
            print(f"Status: {data.get('workflow_status')}")
            print(f"Debug keys: {data.get('debug_info', {}).get('response_keys', [])}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_openai_key_and_backend()
