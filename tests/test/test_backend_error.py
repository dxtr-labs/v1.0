import requests
import json

# Test if we can reach the backend endpoint
def test_backend_endpoint():
    url = "http://localhost:8002/api/agents/1b58f5f0-931e-46e5-b7d9-f76bd189b96d/chat"
    
    # Test with the same data the frontend is sending
    payload = {
        "message": "hello",
        "agentId": "1b58f5f0-931e-46e5-b7d9-f76bd189b96d"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Cookie": "session_token=ZyVZdEfF57uZ6d3wdY5XiGBWe6MWwRemOcAMYHfxRxA"  # Same cookie from frontend logs
    }
    
    print(f"🔍 Testing backend endpoint: {url}")
    print(f"📝 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        print(f"📄 Response Text: {response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"🚨 Request failed: {e}")

if __name__ == "__main__":
    test_backend_endpoint()
