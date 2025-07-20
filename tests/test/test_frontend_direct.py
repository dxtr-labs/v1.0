import requests
import json

# Test the frontend API route (which should forward to backend)
def test_frontend_api():
    url = "http://localhost:3000/api/chat/mcpai"
    
    payload = {
        "message": "Hello, can you tell me about DXTR Labs?",
        "agentId": "1b85f5f0-331e-46e5-b7d8-f7bd1f8db8e6d",  # From the screenshot URL
        "agentConfig": {
            "name": "testbot", 
            "role": "Personal Assistant",
            "personality": {},
            "llm_config": {}
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"🔍 Testing frontend API: {url}")
    print(f"📝 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Error Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"🚨 Request failed: {e}")

if __name__ == "__main__":
    test_frontend_api()
