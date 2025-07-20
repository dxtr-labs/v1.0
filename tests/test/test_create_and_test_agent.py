import requests
import json

# First create a test agent, then test our system
try:
    print("🏗️ Creating test agent...")
    
    agent_payload = {
        'agent_name': 'Test Context Agent',
        'agent_role': 'Testing two-part context extraction system',
        'systemPrompt': 'You are a test agent for the two-part context + automation system.',
        'customMcpCode': '',
        'triggers': []
    }
    
    # Note: This might require auth, let's try
    create_response = requests.post(
        'http://localhost:8002/api/agents', 
        json=agent_payload,
        timeout=10
    )
    
    print(f"Agent creation status: {create_response.status_code}")
    print(f"Response: {create_response.text[:200]}...")
    
    if create_response.status_code == 201:
        agent_data = create_response.json()
        agent_id = agent_data.get('agent_id')
        print(f"✅ Agent created with ID: {agent_id}")
        
        # Now test our two-part system
        test_message = 'Hello, my company name is TechCorp Inc and we sell healthy protein noodles. Please send an email to customer@example.com'
        
        response = requests.post(
            f'http://localhost:8002/api/test/agents/{agent_id}/chat', 
            json={'message': test_message}, 
            timeout=20
        )
        
        print(f"\n🧪 Two-part system test:")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f'Response: {result.get("response", "No response")[:100]}...')
            print(f'Has workflow: {result.get("hasWorkflowJson", False)}')
        else:
            print(f"Error: {response.text}")
    
except Exception as e:
    print(f'❌ Test failed: {e}')
