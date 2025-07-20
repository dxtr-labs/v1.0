import requests
import json

# Try to find existing agents by checking the database or using a simple auth
print('Checking for existing agents...')

# Simple user creation and login
BACKEND_URL = 'http://localhost:8002'

test_user = {
    'email': 'test@dxtrlabs.com',
    'password': 'testpass123'
}

try:
    # Try login first (user might already exist)
    login_response = requests.post(f'{BACKEND_URL}/api/auth/login', json=test_user)
    print(f'Login response: {login_response.status_code}')
    
    if login_response.status_code == 200:
        # Extract session from response headers/cookies
        session_cookie = None
        if 'Set-Cookie' in login_response.headers:
            cookie_header = login_response.headers['Set-Cookie']
            if 'session_token=' in cookie_header:
                session_cookie = cookie_header.split('session_token=')[1].split(';')[0]
        
        if not session_cookie and hasattr(login_response, 'cookies'):
            session_cookie = login_response.cookies.get('session_token')
            
        if session_cookie:
            print(f'Got session: {session_cookie[:20]}...')
            cookies = {'session_token': session_cookie}
            
            # Get existing agents
            agents_response = requests.get(f'{BACKEND_URL}/api/agents', cookies=cookies)
            print(f'Agents response: {agents_response.status_code}')
            
            if agents_response.status_code == 200:
                agents_data = agents_response.json()
                agents = agents_data.get('agents', [])
                print(f'Found {len(agents)} agents')
                
                if agents:
                    for agent in agents[:3]:  # Show first 3
                        agent_id = agent.get('agent_id', 'unknown')
                        agent_name = agent.get('agent_name', 'unnamed')
                        print(f'Agent: {agent_id} - {agent_name}')
                else:
                    print('No agents found, creating one...')
                    # Create a test agent
                    agent_data = {
                        'agent_name': 'DXTR Test Assistant',
                        'agent_role': 'Personal Assistant',
                        'operation_mode': 'chat',
                        'agent_expectations': 'Be helpful and conversational'
                    }
                    
                    create_response = requests.post(f'{BACKEND_URL}/api/agents', json=agent_data, cookies=cookies)
                    print(f'Create agent response: {create_response.status_code}')
                    
                    if create_response.status_code in [200, 201]:
                        new_agent = create_response.json()
                        agent_id = new_agent.get('agent_id', 'unknown')
                        print(f'Created agent: {agent_id}')
            else:
                print(f'Failed to get agents: {agents_response.text}')
        else:
            print('No session token received')
    else:
        print(f'Login failed: {login_response.text}')
        
except Exception as e:
    print(f'Error: {e}')
