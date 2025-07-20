#!/usr/bin/env python3

import requests
import json

# Debug what the MCP LLM is actually returning
session_token = 'XgThOdqavjspglvAqVO2vA4URIizlay9T8-2JzJnS3U'

url = 'http://localhost:8002/api/chat/mcpai'
headers = {
    'Content-Type': 'application/json',
    'Cookie': f'session_token={session_token}'
}

data = {
    'message': 'draft a sales pitch email for selling the harmless antibiotics for animals and send email to slakshanand1105@gmail.com',  # The exact user request
    'agentConfig': {
        'agent_id': 'sales_assistant',
        'name': 'Sales AI Assistant',
        'role': 'Professional Sales Agent'
    },
    'session_id': 'debug_session'
}

print('🧪 Debugging MCP LLM Response...')

try:
    response = requests.post(url, json=data, headers=headers, timeout=30)
    print(f'📊 Status Code: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        
        print('\n🔍 RAW API RESPONSE STRUCTURE:')
        print(f'Response type: {type(result)}')
        print(f'Response keys: {list(result.keys())}')
        
        print('\n📋 ALL RESPONSE FIELDS:')
        for key, value in result.items():
            value_str = str(value)
            if len(value_str) > 100:
                value_str = value_str[:100] + '...'
            print(f'  {key}: {value_str}')
        
        # Check if the issue is that MCP LLM is not being called
        if 'ai_enhanced' in result:
            print(f'\n🤖 AI Enhanced: {result["ai_enhanced"]}')
        if 'fallback_used' in result:
            print(f'🔄 Fallback Used: {result["fallback_used"]}')
        
        print(f'\n🎯 Missing Expected Fields Analysis:')
        expected = ['status', 'hasWorkflowJson', 'hasWorkflowPreview', 'done', 'workflow_id']
        for field in expected:
            exists = field in result
            print(f'  {field}: {"✅ EXISTS" if exists else "❌ MISSING"}')
            
    else:
        print(f'❌ API Error: {response.status_code}')
        print(f'Response: {response.text}')
        
except Exception as e:
    print(f'💥 Request Error: {e}')
    import traceback
    traceback.print_exc()
