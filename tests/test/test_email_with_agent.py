import requests
import json

BACKEND_URL = "http://127.0.0.1:8000"

def test_agent_email_with_existing_agent():
    print("🧪 Testing email with existing Customer Support agent...")
    
    # Use Alex (Customer Support agent) which is in the default user's list
    agent_id = "757f5af0"  # Alex
    message = "Send an email to slakshanand1105@gmail.com good morning"
    
    print(f"\n📤 Sending email message to agent {agent_id}: {message}")
    
    chat_data = {
        "message": message
    }
    
    headers = {"x-user-id": "default_user"}
    
    response = requests.post(f"{BACKEND_URL}/agents/{agent_id}/chat", 
                           json=chat_data,
                           headers=headers)
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Chat response received:")
        print(json.dumps(result, indent=2))
    else:
        print(f"❌ Chat failed: {response.status_code}")
        print(f"Response text: {response.text}")

if __name__ == "__main__":
    test_agent_email_with_existing_agent()
