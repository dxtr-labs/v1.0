import requests
import json
import uuid

# Generate a test agent ID
agent_id = str(uuid.uuid4())
print(f"Testing with agent ID: {agent_id}")

# Test our two-part system 
test_payloads = [
    {
        'name': 'Context Extraction Only',
        'message': 'Hello, my company name is TechCorp Inc and we sell healthy protein noodles. My email is john@techcorp.com'
    },
    {
        'name': 'Automation Detection',
        'message': 'Hi, my company name is TechCorp Inc. Please send an email to customer@example.com about our new product launch.'
    }
]

for test in test_payloads:
    try:
        print(f"\n🧪 {test['name']}:")
        print(f"Message: {test['message']}")
        
        response = requests.post(
            f'http://localhost:8002/api/test/agents/{agent_id}/chat', 
            json={'message': test['message']}, 
            timeout=20
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f'Status: {result.get("status", "unknown")}')
            print(f'Response: {result.get("response", "No response")[:100]}...')
            print(f'Has workflow: {result.get("hasWorkflowJson", False)}')
            print(f'Workflow preview: {result.get("workflow_preview", "None")}')
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f'❌ Test failed: {e}')
        
print("\n🔍 Checking server logs for our debug messages...")
