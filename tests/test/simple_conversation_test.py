#!/usr/bin/env python3
"""
Simple conversation test
"""
import requests
import json

# Test the conversation
agent_id = "a99f903c-1fa5-4dc5-b15a-ec716b9a161a"
base_url = "http://localhost:8002"

print("Testing conversation flow...")

# Message 1: Hello
print("\n1. Sending: 'hello'")
response = requests.post(f"{base_url}/api/agents/{agent_id}/chat", 
                        json={"message": "hello"}, 
                        headers={"Content-Type": "application/json"})
if response.status_code == 200:
    result = response.json()
    print(f"Response: {result.get('response', '')}")
else:
    print(f"Error: {response.status_code}")

# Message 2: Automation request
print("\n2. Sending: 'find top 10 investors in ai field and send email about dxtr labs to them'")
response = requests.post(f"{base_url}/api/agents/{agent_id}/chat", 
                        json={"message": "find top 10 investors in ai field and send email about dxtr labs to them"}, 
                        headers={"Content-Type": "application/json"})
if response.status_code == 200:
    result = response.json()
    print(f"Response: {result.get('response', '')}")
    print(f"Status: {result.get('status', 'Unknown')}")
    print(f"Has workflow: {result.get('hasWorkflowJson', False)}")
else:
    print(f"Error: {response.status_code}")

# Message 3: Continuation
print("\n3. Sending: 'sure'")
response = requests.post(f"{base_url}/api/agents/{agent_id}/chat", 
                        json={"message": "sure"}, 
                        headers={"Content-Type": "application/json"})
if response.status_code == 200:
    result = response.json()
    print(f"Response: {result.get('response', '')}")
    print(f"Status: {result.get('status', 'Unknown')}")
else:
    print(f"Error: {response.status_code}")

print("\n✅ Test complete!")
