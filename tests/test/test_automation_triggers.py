"""
Direct test of automation system bypassing intent detection
"""
import requests
import json

BACKEND_URL = "http://localhost:8002"

# Get agent ID
with open('test_agent_id.txt', 'r') as f:
    agent_id = f.read().strip()

# Test different variations to see which one triggers automation
test_requests = [
    "send email to slakshanand1105@gmail.com with a sales pitch for healthy ramen noodles",
    "email slakshanand1105@gmail.com about healthy ramen noodles sales pitch",
    "create email automation for slakshanand1105@gmail.com with sales content",
    "draft email to slakshanand1105@gmail.com about ramen noodles",
    "send an email to slakshanand1105@gmail.com",
    "write email to slakshanand1105@gmail.com",
]

for i, request in enumerate(test_requests, 1):
    print(f"\n🎯 Test {i}: {request}")
    
    response = requests.post(
        f"{BACKEND_URL}/api/test/agents/{agent_id}/chat",
        json={"message": request},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        status = result.get('status', 'unknown')
        workflow_status = result.get('workflow_status', 'unknown') 
        has_json = result.get('hasWorkflowJson', False)
        
        print(f"   Status: {status}")
        print(f"   Workflow Status: {workflow_status}")
        print(f"   Has JSON: {has_json}")
        
        if has_json or status == "preview_ready":
            print(f"   ✅ AUTOMATION TRIGGERED!")
            break
        elif status == "conversational":
            print(f"   ❌ Conversational (not automation)")
        else:
            print(f"   ❓ Unknown result")
    else:
        print(f"   ❌ Request failed: {response.status_code}")
    
    # Add small delay between requests
    import time
    time.sleep(0.5)
