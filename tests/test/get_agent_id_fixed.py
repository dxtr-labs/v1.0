import requests
import json

# Get agent ID for testing
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
                agents = agents_data.get('agents', [])
                print(f'✅ Found {len(agents)} agents')
                
                if agents:
                    # Use the first agent
                    first_agent = agents[0]
                    agent_id = first_agent.get('agent_id')
                    agent_name = first_agent.get('agent_name', 'unnamed')
                    print(f'🎯 Test Agent: {agent_id}')
                    print(f'📝 Agent Name: {agent_name}')
                    
                    # Save agent ID for the test
                    with open('test_agent_id.txt', 'w') as f:
                        f.write(agent_id)
                    print(f'💾 Saved agent ID to test_agent_id.txt')
                    
                else:
                    print('No agents found, creating one...')
                    # Create a test agent
                    agent_data = {
                        'agent_name': 'DXTR Test Assistant',
                        'agent_role': 'Personal Assistant',
                        'operation_mode': 'chat',
                        'agent_expectations': 'Be helpful and conversational while assisting with automation and DXTR Labs inquiries'
                    }
                    
                    create_response = requests.post(f'{BACKEND_URL}/api/agents', json=agent_data, cookies=cookies)
                    
                    if create_response.status_code in [200, 201]:
                        new_agent = create_response.json()
                        agent_id = new_agent.get('agent_id')
                        print(f'✅ Created agent: {agent_id}')
                        
                        # Save agent ID for the test
                        with open('test_agent_id.txt', 'w') as f:
                            f.write(agent_id)
                        print(f'💾 Saved agent ID to test_agent_id.txt')
                    else:
                        print(f'❌ Failed to create agent: {create_response.status_code} - {create_response.text}')
            else:
                print(f'❌ Failed to get agents: {agents_response.status_code} - {agents_response.text}')
        else:
            print('❌ No session token in response')
    else:
        print(f'❌ Login failed: {login_response.status_code} - {login_response.text}')
        
except Exception as e:
    print(f'❌ Error: {e}')
