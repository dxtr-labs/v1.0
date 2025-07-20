import requests
import json

# Test automation detection (should trigger workflow creation)
test_payload = {
    'message': 'Hi, my company name is TechCorp Inc and we sell healthy protein noodles. Please send an email to customer@example.com about our new product launch.'
}

try:
    print("🤖 AUTOMATION DETECTION TEST:")
    print("Sending automation request...")
    
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
        print(f'Method used: {result.get("method", "unknown")}')
        
        # Check if our system detected automation
        test_info = result.get("test_info", {})
        print(f'Test info: {test_info}')
        
    else:
        print(f"Error response: {response.text}")
        
except Exception as e:
    print(f'❌ Test failed: {e}')
