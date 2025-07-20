import requests
import json

# Test the chat endpoint with debug logging
def test_chat():
    url = "http://localhost:8002/api/chat/mcpai"
    
    payload = {
        "message": "Hello, can you tell me about DXTR Labs?",
        "agent_id": "1b85f5f0-331e-46e5-b7d8-f7bd1f8db8e6d",  # From the URL in screenshot
        "conversation_id": "test-conversation-123"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-token"  # You might need proper auth
    }
    
    print(f"🔍 Testing chat endpoint: {url}")
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
    test_chat()
