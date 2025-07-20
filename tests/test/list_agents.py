import requests
import json

BACKEND_URL = "http://127.0.0.1:8000"

def list_all_agents():
    print("📋 Listing all agents for default user...")
    
    response = requests.get(f"{BACKEND_URL}/api/agents")
    
    if response.status_code == 200:
        result = response.json()
        agents = result.get('agents', [])
        print(f"✅ Found {len(agents)} agents:")
        for agent in agents:
            print(f"  - ID: {agent.get('AgentID', 'Unknown')} | Name: {agent.get('name', 'Unknown')} | Role: {agent.get('role', 'Unknown')}")
    else:
        print(f"❌ Failed to list agents: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    list_all_agents()
