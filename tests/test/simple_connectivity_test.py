import requests
import json

print("Testing MCP API...")

try:
    # Test basic GET endpoint
    response = requests.get("http://localhost:8002/docs", timeout=5)
    print(f"GET /docs: Status {response.status_code}")
except Exception as e:
    print(f"GET /docs failed: {e}")

try:
    # Test MCP API endpoint
    response = requests.post(
        "http://localhost:8002/api/chat/mcpai",
        json={"message": "Hello test"},
        timeout=10
    )
    print(f"POST /api/chat/mcpai: Status {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response received: {result.get('status', 'unknown')}")
except Exception as e:
    print(f"POST /api/chat/mcpai failed: {e}")

print("Test complete.")
