#!/usr/bin/env python3
"""Test the actual sales pitch email automation"""

import requests
import json

# Test the exact sales pitch request
session_token = 'XgThOdqavjspglvAqVO2vA4URIizlay9T8-2JzJnS3U'

url = 'http://localhost:8002/api/chat/mcpai'
headers = {
    'Content-Type': 'application/json',
    'Cookie': f'session_token={session_token}'
}

data = {
    'message': 'draft a sales pitch email for selling the harmless antibiotics for animals and send email to slakshanand1105@gmail.com',
    'agentConfig': {
        'agent_id': 'sales_assistant',
        'name': 'Sales AI Assistant', 
        'role': 'Professional Sales Agent'
    },
    'session_id': 'test_session_123'
}

print('🧪 Testing Sales Pitch Email Automation...')
print(f'Request: {data["message"]}')

try:
    response = requests.post(url, json=data, headers=headers, timeout=60)
    print(f'📊 Status Code: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        
        print('\n✅ API RESPONSE SUCCESS!')
        print(f'Status: {result.get("status")}')
        print(f'Message: {result.get("message")}')
        print(f'Has Workflow JSON: {result.get("hasWorkflowJson")}')
        print(f'Email Sent: {result.get("email_sent", False)}')
        print(f'Automation Type: {result.get("automation_type")}')
        
        # Check if email was actually sent
        if result.get("email_sent"):
            print('\n🎉 EMAIL WAS SENT SUCCESSFULLY!')
            print('📧 Check slakshanand1105@gmail.com for the sales pitch email!')
        else:
            print('\n⚠️ Email was not sent - this may be just workflow creation')
            print('The API may need to actually execute the workflow to send the email')
            
    else:
        print(f'❌ API Error: {response.status_code}')
        print(f'Response: {response.text}')
        
except Exception as e:
    print(f'💥 Request Error: {e}')
    import traceback
    traceback.print_exc()
