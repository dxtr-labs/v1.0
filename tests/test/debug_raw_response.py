import requests
import json

BACKEND_URL = "http://localhost:8002"

# Get agent ID
with open('test_agent_id.txt', 'r') as f:
    agent_id = f.read().strip()

# Test automation request
request = "draft a sales pitch for selling healthy ramen noodles and send email to slakshanand1105@gmail.com"

print(f"🎯 Testing: {request}")

response = requests.post(
    f"{BACKEND_URL}/api/test/agents/{agent_id}/chat",
    json={"message": request},
    timeout=30
)

print(f"Status: {response.status_code}")
print("Raw Response JSON:")
print(json.dumps(response.json(), indent=2))
