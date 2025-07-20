#!/usr/bin/env python3
"""
Fixed test script to verify the enhanced conversational system
Creates a real user and tests the conversation system properly
"""

import requests
import json
import sys
import os

def create_test_user():
    """Create a test user and return session token"""
    print("👤 Creating test user...")
    
    user_data = {
        "email": "test@dxtrlabs.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser"
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:8002/api/auth/signup',
            headers={'Content-Type': 'application/json'},
            json=user_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            session_token = result.get('session_token')
            user_id = result.get('user', {}).get('user_id')
            print(f"✅ User created successfully! ID: {user_id}")
            return session_token, user_id
        elif response.status_code == 400 and "already exists" in response.text:
            print("👤 User already exists, trying to login...")
            return login_test_user()
        else:
            print(f"❌ Failed to create user: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Exception creating user: {e}")
        return None, None

def login_test_user():
    """Login with test user"""
    print("🔐 Logging in test user...")
    
    login_data = {
        "email": "test@dxtrlabs.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:8002/api/auth/login',
            headers={'Content-Type': 'application/json'},
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            session_token = result.get('session_token')
            user_id = result.get('user', {}).get('user_id')
            print(f"✅ Login successful! ID: {user_id}")
            return session_token, user_id
        else:
            print(f"❌ Login failed: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Exception during login: {e}")
        return None, None

def test_backend_with_auth(session_token):
    """Test the backend API with proper authentication"""
    print("\n🔍 Testing Backend with Authentication...")
    
    # Use session token for authentication
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'session_token={session_token}'
    }
    
    test_messages = [
        "hello",
        "how are you today?", 
        "what can you do?",
        "tell me about DXTR Labs",
        "what makes DXTR Labs special?"
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
                print(f"Status: {result.get('status', 'No status')}")
                print(f"Done: {result.get('done', 'No done field')}")
                message_text = result.get('message', 'No message')
                
                # Print first 200 chars of message
                if len(message_text) > 200:
                    print(f"Message: {message_text[:200]}...")
                else:
                    print(f"Message: {message_text}")
                    
                # Check if it's mentioning DXTR Labs
                if 'DXTR' in message_text or 'dxtr' in message_text.lower():
                    print("🎯 ✅ DXTR Labs branding detected!")
                else:
                    print("⚠️ No DXTR Labs branding detected")
                    
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("-" * 50)

def test_openai_detection():
    """Test if responses indicate OpenAI usage"""
    print("\n🤖 Testing for OpenAI-Generated Content...")
    
    session_token, user_id = create_test_user()
    if not session_token:
        print("❌ Cannot test without authentication")
        return
    
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'session_token={session_token}'
    }
    
    # Test with a message that should trigger OpenAI
    test_message = "write me a creative story about AI"
    
    try:
        response = requests.post(
            'http://127.0.0.1:8002/api/chat/mcpai',
            headers=headers,
            json={'message': test_message},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            message_text = result.get('message', '')
            
            # Check for OpenAI-style responses
            ai_indicators = [
                'Once upon a time',
                'In a world where',
                'creative',
                'imagination',
                'story',
                'narrative'
            ]
            
            if any(indicator in message_text.lower() for indicator in ai_indicators):
                print("🤖 ✅ Response appears to be AI-generated!")
            else:
                print("⚠️ Response doesn't appear to be AI-generated")
                
            print(f"Response length: {len(message_text)} characters")
            
        else:
            print(f"❌ Request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    print("🚀 DXTR Labs Enhanced Conversational System Test")
    print("="*60)
    
    # Test 1: Create user and get authentication
    session_token, user_id = create_test_user()
    
    if session_token:
        # Test 2: Backend with proper authentication
        test_backend_with_auth(session_token)
        
        # Test 3: OpenAI content detection
        test_openai_detection()
    else:
        print("❌ Cannot continue without authentication")
    
    print("\n🏁 Testing Complete!")

if __name__ == "__main__":
    main()
