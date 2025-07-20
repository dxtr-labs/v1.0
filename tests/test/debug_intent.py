import requests
import json

BACKEND_URL = "http://localhost:8002"

# Get agent ID
with open('test_agent_id.txt', 'r') as f:
    agent_id = f.read().strip()

# Test the exact request that should trigger automation
request = "draft a sales pitch for selling healthy ramen noodles and send email to slakshanand1105@gmail.com"

print(f"🎯 Testing automation intent detection...")
print(f"Request: {request}")

response = requests.post(
    f"{BACKEND_URL}/api/test/agents/{agent_id}/chat",
    json={"message": request},
    timeout=30
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"Response status: {result.get('status')}")
    print(f"Response workflow_status: {result.get('workflow_status')}")
    print(f"Has JSON: {result.get('hasWorkflowJson')}")
    print(f"Response length: {len(result.get('response', ''))}")
    print(f"Response preview: {result.get('response', '')[:200]}...")
else:
    print(f"Error: {response.text}")
