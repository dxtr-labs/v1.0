import requests
import json

BACKEND_URL = "http://127.0.0.1:8000"

def test_with_customer_support_agent():
    print("🧪 Testing with Customer Support agents...")
    
    # Get list of customer support agents
    response = requests.get(f"{BACKEND_URL}/api/agents")
    
    if response.status_code == 200:
        result = response.json()
        agents = result.get('agents', [])
        
        # Find Customer Support agents
        customer_support_agents = [a for a in agents if 'Customer Support' in a.get('role', '')]
        
        print(f"Found {len(customer_support_agents)} Customer Support agents:")
        for agent in customer_support_agents:
            print(f"  - ID: {agent.get('AgentID', 'Unknown')} | Name: {agent.get('name', 'Unknown')}")
        
        if customer_support_agents:
            # Test with the first Customer Support agent
            test_agent = customer_support_agents[0]
            agent_id = test_agent['AgentID']
            
            print(f"\n📤 Testing email with agent {agent_id} ({test_agent['name']})...")
            
            chat_data = {
                "message": "send email to slakshanand1105@gmail.com good morning 5:46PM MST"
            }
            
            response = requests.post(f"{BACKEND_URL}/agents/{agent_id}/chat", 
                                   json=chat_data)
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Chat response received:")
                print(json.dumps(result, indent=2))
            else:
                print(f"❌ Chat failed: {response.status_code}")
                print(f"Response text: {response.text}")
        else:
            print("❌ No Customer Support agents found")
    else:
        print(f"❌ Failed to list agents: {response.status_code}")

if __name__ == "__main__":
    test_with_customer_support_agent()
