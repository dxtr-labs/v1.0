import requests
import json

# Test with the MCP AI endpoint which uses our custom engine
test_payload = {
    'message': 'Hi, my company name is TechCorp Inc and we sell healthy protein noodles. Please send an email to customer@example.com about our new product launch.'
}

try:
    print("🤖 TESTING OUR TWO-PART SYSTEM:")
    print("Sending automation request to MCP AI endpoint...")
    
    # This endpoint should use our CustomMCPLLMIterationEngine
    response = requests.post(
        'http://localhost:8002/api/chat/mcpai', 
        json=test_payload, 
        timeout=20
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response text: {response.text[:200]}...")
    
except Exception as e:
    print(f'❌ Test failed: {e}')
