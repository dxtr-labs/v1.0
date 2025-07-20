import requests
import json

def test_backend_with_auth():
    """Test backend with proper frontend authentication simulation"""
    
    url = "http://localhost:8002/api/agents/1b58f5f0-931e-46e5-b7d9-f76bd189b96d/chat"
    
    # Simulate the exact payload the frontend sends
    payload = {
        "message": "hello",
        "agentId": "1b58f5f0-931e-46e5-b7d9-f76bd189b96d",
        "agentConfig": {
            "name": "testbot",
            "role": "Personal Assistant",
            "mode": "chat"
        }
    }
    
    # Use the exact headers the frontend sends - try x-user-id for testing
    headers = {
        'Content-Type': 'application/json',
        'x-user-id': 'test-user-123'
    }
    
    print("🔍 Testing backend with frontend-like request...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_backend_with_auth()
