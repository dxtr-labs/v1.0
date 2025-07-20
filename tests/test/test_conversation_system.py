#!/usr/bin/env python3
"""
Test script to verify the enhanced conversational system
Tests multiple scenarios to see what's not working
"""

import requests
import json
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_backend_direct():
    """Test the backend API directly with proper authentication"""
    print("\n🔍 Testing Backend Direct Connection...")
    
    # Test with header authentication (for development)
    headers = {
        'Content-Type': 'application/json',
        'x-user-id': 'test-user-123'  # Using header auth for testing
    }
    
    test_messages = [
        "hello",
        "how are you today?",
        "what can you do?",
        "tell me about DXTR Labs"
    ]
    
    for message in test_messages:
        print(f"\n📤 Testing message: '{message}'")
        
        try:
            response = requests.post(
                'http://127.0.0.1:8002/api/chat/mcpai',
                headers=headers,
                json={'message': message},
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success!")
                print(f"Message: {result.get('message', 'No message')}")
                print(f"Status: {result.get('status', 'No status')}")
                print(f"Done: {result.get('done', 'No done field')}")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("-" * 50)

def test_openai_integration():
    """Test if OpenAI integration is working"""
    print("\n🤖 Testing OpenAI Integration...")
    
    try:
        # Import the MCP system
        from mcp.custom_mcp_llm_iteration import CustomMCPLLMIteration
        
        # Create MCP instance
        mcp = CustomMCPLLMIteration()
        
        # Test direct OpenAI call
        test_prompt = "Hello, please respond as DXTR Labs AI assistant"
        
        print(f"📤 Testing OpenAI with: '{test_prompt}'")
        
        # Test the AI conversational response method
        response = mcp._generate_ai_conversational_response(
            user_message=test_prompt,
            context="Test conversation",
            user_preferences={}
        )
        
        print(f"✅ OpenAI Response: {response}")
        
    except Exception as e:
        print(f"❌ OpenAI Integration Error: {e}")

def main():
    print("🚀 DXTR Labs Conversational System Test")
    print("="*60)
    
    # Test 1: Backend Direct
    test_backend_direct()
    
    # Test 2: OpenAI Integration
    test_openai_integration()
    
    print("\n🏁 Testing Complete!")

if __name__ == "__main__":
    main()
