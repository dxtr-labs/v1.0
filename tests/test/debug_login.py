import requests
import json

# Debug login response to find session token
BACKEND_URL = 'http://localhost:8002'

test_user = {
    'email': 'test@dxtrlabs.com',
    'password': 'testpass123'
}

print('Testing login response details...')

try:
    login_response = requests.post(f'{BACKEND_URL}/api/auth/login', json=test_user)
    print(f'Status: {login_response.status_code}')
    print(f'Headers: {dict(login_response.headers)}')
    print(f'Cookies: {dict(login_response.cookies)}')
    
    try:
        response_data = login_response.json()
        print(f'Response body: {json.dumps(response_data, indent=2)}')
    except:
        print(f'Response text: {login_response.text}')
        
except Exception as e:
    print(f'Error: {e}')
