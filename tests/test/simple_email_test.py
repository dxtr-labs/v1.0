import requests
import json

# Quick test to check automation engine
print("Testing email automation...")

cookies = requests.cookies.RequestsCookieJar()
cookies.set('session_token', 'I6ARJ94zy-mr2lODRw2zvW_j5LmG0peKurVdJi9ny1A')

workflow = {
    'workflow': {
        'workflow_id': 'test-001',
        'user_id': '890f97f1-f0b4-4439-8dc4-1213510c71e3',
        'trigger': {'type': 'manual'},
        'actions': [{
            'action_id': 'email-001',
            'node': 'emailSend',
            'parameters': {
                'toEmail': 'slakshanand1105@gmail.com',
                'subject': 'Test Email from Sam',
                'text': 'Hello! This is a test email from your AI assistant.'
            }
        }]
    }
}

response = requests.post(
    'http://localhost:8001/api/automations/execute',
    json={'workflow_json': workflow},
    cookies=cookies
)

print(f'Status: {response.status_code}')
print(f'Response: {response.text}')
