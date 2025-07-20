import requests
import json

# Test the simplified two-part system
test_payload = {
    'message': 'Hello, my company name is TechCorp Inc and we sell healthy protein noodles. My email is john@techcorp.com'
}

try:
    print("🧠 CONTEXT EXTRACTION TEST:")
    print("Sending request...")
    
    # Test with the direct-openai endpoint which doesn't require existing agent
    response = requests.post(
        'http://localhost:8002/api/test/direct-openai/12345678-1234-1234-1234-123456789012/chat', 
        json=test_payload, 
        timeout=15
    )
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f'Status: {result.get("status", "unknown")}')
        print(f'Response preview: {result.get("response", "No response")[:100]}...')
        print(f'Has workflow: {result.get("hasWorkflowJson", False)}')
        
        # Show full response structure
        print("\n📋 Full response keys:")
        for key in result.keys():
            print(f"  - {key}: {type(result[key])}")
    else:
        print(f"Error response: {response.text}")
        
except Exception as e:
    print(f'❌ Test failed: {e}')
