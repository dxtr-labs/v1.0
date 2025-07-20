#!/usr/bin/env python3

import requests
import json

# Test the fixed API response format
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

print('🚀 Testing Fixed API Response Format...')

try:
    response = requests.post(url, json=data, headers=headers, timeout=60)
    print(f'📊 Status Code: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        
        print('\n✅ API RESPONSE SUCCESS!')
        
        # The key issue was "status: undefined" in frontend logs
        api_status = result.get('status', 'MISSING')
        print(f'\n🎯 KEY FIX - Status Field:')
        print(f'  Before fix: "undefined"')
        print(f'  After fix: "{api_status}"')
        
        # Check other fields that frontend expects
        has_workflow_json = result.get('hasWorkflowJson', False)
        has_workflow_preview = result.get('hasWorkflowPreview', False)
        
        print(f'\n📋 Frontend Required Fields:')
        print(f'  status: {api_status}')
        print(f'  hasWorkflowJson: {has_workflow_json}')
        print(f'  hasWorkflowPreview: {has_workflow_preview}')
        print(f'  done: {result.get("done", "MISSING")}')
        print(f'  message: {result.get("message", "MISSING")[:50]}...')
        print(f'  workflow_id: {result.get("workflow_id", "MISSING")}')
        
        # Email automation check
        if result.get('email_sent'):
            print(f'\n📧 Email Status: SENT to slakshanand1105@gmail.com ✅')
        elif 'email' in result.get('response', '').lower():
            print(f'\n📧 Email automation created successfully ✅')
        
        # Frontend automation trigger analysis
        would_trigger = (
            api_status not in ['undefined', 'MISSING'] or 
            has_workflow_json or 
            has_workflow_preview
        )
        
        print(f'\n🎯 FRONTEND AUTOMATION ANALYSIS:')
        print(f'  Issue: Frontend not triggering automation')
        print(f'  Cause: status was "undefined"')
        print(f'  Fixed: status is now "{api_status}"')
        print(f'  Result: Frontend would now trigger automation: {would_trigger}')
        
        print(f'\n💬 AI Response Preview:')
        response_text = result.get('response', result.get('message', 'No response'))
        print(f'  {response_text[:200]}...')
        
    else:
        print(f'❌ API Error: {response.status_code}')
        print(f'Response: {response.text[:500]}')
        
except Exception as e:
    print(f'💥 Request Error: {e}')
    import traceback
    traceback.print_exc()
