#!/usr/bin/env python3
"""
Direct backend test without authentication
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from mcp.simple_mcp_llm import SimpleMCPLLM

def test_backend_logic():
    """Test the backend logic directly"""
    print('🧪 Direct Backend Logic Test')
    print('=' * 40)
    
    llm = SimpleMCPLLM()
    
    # Test 1: Initial AI request (should trigger service selection)
    print('\n📝 Test 1: Initial AI request')
    message1 = "using ai generate a sales pitch to sell healthy ice cream products and send those in email to slakshanand1105@gmail.com"
    result1 = llm.process_message(message1)
    print(f"Status: {result1.get('status')}")
    print(f"Message: {result1.get('message')}")
    if result1.get('status') == 'ai_service_selection':
        print("✅ Correctly triggered AI service selection")
    else:
        print("❌ Did not trigger AI service selection")
        print(f"Full result: {result1}")
    
    # Test 2: Service selection (should trigger workflow preview)
    print('\n📝 Test 2: Service selection')
    message2 = "service:inhouse using ai generate a sales pitch to sell healthy ice cream products and send those in email to slakshanand1105@gmail.com"
    result2 = llm.process_message(message2)
    print(f"Status: {result2.get('status')}")
    print(f"Message: {result2.get('message')}")
    if result2.get('status') == 'workflow_preview':
        print("✅ Correctly generated workflow preview")
        workflow_preview = result2.get('workflow_preview', {})
        print(f"Title: {workflow_preview.get('title')}")
        print(f"Steps: {len(workflow_preview.get('steps', []))}")
    else:
        print("❌ Did not generate workflow preview")
        print(f"Full result: {result2}")

if __name__ == "__main__":
    test_backend_logic()
