#!/usr/bin/env python3
"""
Ultra simple test with timeout
"""

import urllib.request
import json

try:
    print("🔍 Testing server connection...")
    
    # Test health endpoint with timeout
    with urllib.request.urlopen("http://localhost:8002/health", timeout=5) as response:
        data = json.loads(response.read().decode())
        print(f"✅ Server response: {data}")
        
    print("\n🔍 Testing chat endpoint...")
    
    # Test chat endpoint
    chat_data = {
        "message": "Send an email about project status",
        "session_id": "test123"
    }
    
    req = urllib.request.Request(
        "http://localhost:8002/api/chat/mcpai",
        data=json.dumps(chat_data).encode(),
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req, timeout=10) as response:
        result = json.loads(response.read().decode())
        print(f"✅ Chat response: {result.get('status')}")
        
        # Check the workflow status
        if result.get('status') == 'ai_service_selection':
            print("🎉 Workflow status is correctly 'ai_service_selection' (not 'completed')!")
        else:
            print(f"Status: {result.get('status')}")
            
except Exception as e:
    print(f"❌ Error: {e}")
