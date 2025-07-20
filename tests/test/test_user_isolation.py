import requests
import json

BACKEND_URL = "http://127.0.0.1:8000"

# Test creating agents for different users
def test_user_isolation():
    print("🧪 Testing user isolation...")
    
    # Test user 1
    user1_headers = {"x-user-id": "test_user_1"}
    user2_headers = {"x-user-id": "test_user_2"}
    
    print("\n👤 Creating agent for user 1...")
    agent1_data = {
        "name": "User1 Agent",
        "role": "Test Agent",
        "description": "Agent for user 1"
    }
    
    response1 = requests.post(f"{BACKEND_URL}/api/agents", 
                             json=agent1_data, 
                             headers=user1_headers)
    
    if response1.status_code == 200:
        print("✅ Agent created for user 1")
        print(json.dumps(response1.json(), indent=2))
    else:
        print(f"❌ Failed to create agent for user 1: {response1.status_code}")
        print(response1.text)
    
    print("\n👤 Creating agent for user 2...")
    agent2_data = {
        "name": "User2 Agent", 
        "role": "Test Agent",
        "description": "Agent for user 2"
    }
    
    response2 = requests.post(f"{BACKEND_URL}/api/agents",
                             json=agent2_data,
                             headers=user2_headers)
    
    if response2.status_code == 200:
        print("✅ Agent created for user 2")
        print(json.dumps(response2.json(), indent=2))
    else:
        print(f"❌ Failed to create agent for user 2: {response2.status_code}")
        print(response2.text)
    
    print("\n📋 Listing agents for user 1...")
    list1_response = requests.get(f"{BACKEND_URL}/api/agents", headers=user1_headers)
    if list1_response.status_code == 200:
        user1_agents = list1_response.json()
        print(f"✅ User 1 sees {len(user1_agents.get('agents', []))} agents")
        for agent in user1_agents.get('agents', []):
            print(f"  - {agent.get('name', 'Unknown')}")
    else:
        print(f"❌ Failed to list agents for user 1: {list1_response.status_code}")
    
    print("\n📋 Listing agents for user 2...")
    list2_response = requests.get(f"{BACKEND_URL}/api/agents", headers=user2_headers)
    if list2_response.status_code == 200:
        user2_agents = list2_response.json()
        print(f"✅ User 2 sees {len(user2_agents.get('agents', []))} agents")
        for agent in user2_agents.get('agents', []):
            print(f"  - {agent.get('name', 'Unknown')}")
    else:
        print(f"❌ Failed to list agents for user 2: {list2_response.status_code}")
    
    print("\n📋 Listing agents for default user (no header)...")
    list_default_response = requests.get(f"{BACKEND_URL}/api/agents")
    if list_default_response.status_code == 200:
        default_agents = list_default_response.json()
        print(f"✅ Default user sees {len(default_agents.get('agents', []))} agents")
        for agent in default_agents.get('agents', []):
            print(f"  - {agent.get('name', 'Unknown')}")
    else:
        print(f"❌ Failed to list agents for default user: {list_default_response.status_code}")

if __name__ == "__main__":
    test_user_isolation()
