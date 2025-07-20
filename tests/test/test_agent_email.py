import requests
import json

BACKEND_URL = "http://127.0.0.1:8000"

def test_agent_email():
    print("🧪 Testing agent email functionality...")
    
    # Use the agent ID from your request: 02a3e7cb
    agent_id = "02a3e7cb"
    message = "send email to slakshanand1105@gmail.com good morning 5:46PM MST"
    
    # Test with default user (no header)
    print(f"\n📤 Sending message to agent {agent_id}: {message}")
    
    chat_data = {
        "message": message
    }
    
    response = requests.post(f"{BACKEND_URL}/agents/{agent_id}/chat", 
                           json=chat_data)
    
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Chat response received:")
        print(json.dumps(result, indent=2))
    else:
        print(f"❌ Chat failed: {response.status_code}")
        print(f"Response text: {response.text}")

if __name__ == "__main__":
    test_agent_email()
