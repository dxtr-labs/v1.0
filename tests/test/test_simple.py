#!/usr/bin/env python3
import requests
import time

print("🧪 Testing with error logging...")

# Login
login_response = requests.post('http://127.0.0.1:8002/api/auth/login', 
                             headers={'Content-Type': 'application/json'},
                             json={'email': 'test@dxtrlabs.com', 'password': 'testpass123'}, 
                             timeout=10)

if login_response.status_code == 200:
    result = login_response.json()
    session_token = result.get('session_token')
    print(f'✅ Logged in')
    
    # Test message
    test_response = requests.post('http://127.0.0.1:8002/api/chat/mcpai',
                                headers={'Content-Type': 'application/json', 'Cookie': f'session_token={session_token}'},
                                json={'message': 'hello world'},
                                timeout=30)
    
    print(f'Response: {test_response.status_code}')
    if test_response.status_code == 200:
        result = test_response.json()
        print(f'Status: {result.get("status")}')
        message = result.get("message", "")
        print(f'Message length: {len(message)}')
        print(f'First 100 chars: {message[:100]}')
    else:
        print(f'Error: {test_response.text}')
else:
    print(f'Login failed: {login_response.text}')

print("🏁 Test complete")
