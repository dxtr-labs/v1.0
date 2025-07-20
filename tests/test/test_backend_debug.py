import requests
import json

def test_backend_with_debug():
    """Test backend and force debug output"""
    
    url = "http://localhost:8002/api/test/agents/1b58f5f0-931e-46e5-b7d9-f76bd189b96d/chat"
    
    messages = [
        "hello debug test",
        "what can you do",
        "tell me about automation"
    ]
    
    for msg in messages:
        print(f"\n🔍 Testing: {msg}")
        payload = {
            "message": msg,
            "agentId": "1b58f5f0-931e-46e5-b7d9-f76bd189b96d"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {data.get('response')}")
                print(f"Status: {data.get('workflow_status')}")
                
                # Check if response looks like OpenAI
                response_text = data.get('response', '')
                if len(response_text) > 64 and 'automation' not in response_text.lower():
                    print("🎯 This looks like a REAL OpenAI response!")
                elif 'Let me help you create an automation' in response_text:
                    print("❌ This is the generic fallback response")
                else:
                    print("🤔 Unknown response type")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    test_backend_with_debug()
