#!/usr/bin/env python3
"""
Test the infinite loop fix by simulating the exact user flow
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from mcp.simple_mcp_llm import SimpleMCPLLM

async def test_infinite_loop_fix():
    """Test the exact flow that was causing infinite loop"""
    
    print("=== Testing Infinite Loop Fix ===\n")
    
    mcp = SimpleMCPLLM()
    
    # Step 1: User types AI request (should trigger service selection)
    print("1. User types: 'write email using AI to test@example.com about project update'")
    response1 = await mcp.process_user_input("user123", "agent456", "write email using AI to test@example.com about project update")
    print(f"   Response status: {response1['status']}")
    print(f"   Should be 'ai_service_selection': {response1['status'] == 'ai_service_selection'}")
    print()
    
    # Step 2: User selects AI service (should proceed to workflow preview)
    print("2. User selects AI service: 'write email using AI to test@example.com about project update service:openai'")
    response2 = await mcp.process_user_input("user123", "agent456", "write email using AI to test@example.com about project update service:openai")
    print(f"   Response status: {response2['status']}")
    print(f"   Should be 'workflow_preview': {response2['status'] == 'workflow_preview'}")
    
    if response2['status'] == 'workflow_preview':
        print("   ✅ SUCCESS: AI service selection proceeds to workflow preview!")
        print(f"   Workflow title: {response2.get('workflow_preview', {}).get('title', 'N/A')}")
        print(f"   AI service used: {response2.get('ai_service_used', 'N/A')}")
        print(f"   Estimated credits: {response2.get('estimated_credits', 'N/A')}")
    else:
        print("   ❌ FAILED: Still not proceeding to workflow preview")
        print(f"   Actual response: {response2}")
    print()
    
    # Step 3: Test with different AI services
    print("3. Testing with Claude AI service:")
    response3 = await mcp.process_user_input("user123", "agent456", "generate content using AI service:claude")
    print(f"   Response status: {response3['status']}")
    print(f"   Should be 'workflow_preview': {response3['status'] == 'workflow_preview'}")
    print()
    
    # Step 4: Test that non-AI requests work normally
    print("4. Testing normal conversation (no AI keywords):")
    response4 = await mcp.process_user_input("user123", "agent456", "Hello, how are you?")
    print(f"   Response status: {response4['status']}")
    print(f"   Should be 'success': {response4['status'] == 'success'}")
    print()
    
    print("=== Test Summary ===")
    all_tests_passed = (
        response1['status'] == 'ai_service_selection' and
        response2['status'] == 'workflow_preview' and
        response3['status'] == 'workflow_preview' and
        response4['status'] == 'success'
    )
    
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! Infinite loop should be fixed!")
    else:
        print("❌ Some tests failed. Need further debugging.")
    
    return all_tests_passed

if __name__ == "__main__":
    result = asyncio.run(test_infinite_loop_fix())
    if result:
        print("\n✅ System ready for testing with user!")
    else:
        print("\n❌ System needs more debugging.")
