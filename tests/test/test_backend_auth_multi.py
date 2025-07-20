import requests
import json

def test_backend_with_auth_multi():
    """Test backend with multiple messages to check for generic vs. OpenAI responses"""
    url = "http://localhost:8002/api/agents/1b58f5f0-931e-46e5-b7d9-f76bd189b96d/chat"
    messages = [
        "hello",
        "How are you?",
        "What can you do for me?",
        "Tell me about DXTR Labs.",
        "I need help with email automation.",
        "Can you automate my workflow?",
        "Thank you!",
        "bye"
    ]
    headers = {
        'Content-Type': 'application/json',
        'x-user-id': 'test-user-123'
    }
    for msg in messages:
        payload = {
            "message": msg,
            "agentId": "1b58f5f0-931e-46e5-b7d9-f76bd189b96d",
            "agentConfig": {
                "name": "testbot",
                "role": "Personal Assistant",
                "mode": "chat"
            }
        }
        print(f"\n🔍 Testing message: {msg}")
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
            else:
                print(f"Error Response: {response.text}")
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    test_backend_with_auth_multi()
