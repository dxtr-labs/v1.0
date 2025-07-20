import requests
import json

# Get agent ID for testing - debug version
BACKEND_URL = 'http://localhost:8002'

test_user = {
    'email': 'test@dxtrlabs.com',
    'password': 'testpass123'
}

try:
    # Login to get session token
    login_response = requests.post(f'{BACKEND_URL}/api/auth/login', json=test_user)
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        session_token = login_data.get('session_token')
        
        if session_token:
            print(f'✅ Session token: {session_token[:20]}...')
            cookies = {'session_token': session_token}
            
            # Get existing agents
            agents_response = requests.get(f'{BACKEND_URL}/api/agents', cookies=cookies)
            
            if agents_response.status_code == 200:
                agents_data = agents_response.json()
                print(f'📊 Full agents response: {json.dumps(agents_data, indent=2)}')
                
                agents = agents_data.get('agents', [])
                print(f'✅ Found {len(agents)} agents')
                
                if agents:
                    # Show all agent data
                    for i, agent in enumerate(agents):
                        print(f'Agent {i}: {json.dumps(agent, indent=2)}')
                        
                    # Try different possible keys for agent ID
                    first_agent = agents[0]
                    agent_id = first_agent.get('agent_id') or first_agent.get('id') or first_agent.get('uuid')
                    
                    if agent_id:
                        print(f'🎯 Test Agent ID: {agent_id}')
                        
                        # Save agent ID for the test
                        with open('test_agent_id.txt', 'w') as f:
                            f.write(agent_id)
                        print(f'💾 Saved agent ID to test_agent_id.txt')
                    else:
                        print('❌ Could not find agent ID in any expected field')
                        
                else:
                    print('No agents found')
            else:
                print(f'❌ Failed to get agents: {agents_response.status_code} - {agents_response.text}')
        else:
            print('❌ No session token in response')
    else:
        print(f'❌ Login failed: {login_response.status_code} - {login_response.text}')
        
except Exception as e:
    print(f'❌ Error: {e}')
