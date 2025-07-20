#!/usr/bin/env python3
"""
Simple test script to check database users and test the system
"""

import asyncio
import asyncpg
import os
import aiohttp
import json
from dotenv import load_dotenv

load_dotenv()

async def check_database():
    """Check existing users in database"""
    try:
        # Use the actual database URL from .env
        db_url = "postgresql://postgres:devhouse@34.44.98.81:5432/postgres"
        
        conn = await asyncpg.connect(db_url)
        
        # Check if users table exists and get existing users
        users = await conn.fetch('SELECT email, user_id FROM users LIMIT 5')
        print('🔍 Existing users in database:')
        for user in users:
            print(f'  - {user["email"]} (ID: {user["user_id"]})')
            
        await conn.close()
        return users
    except Exception as e:
        print(f'❌ Error checking database: {e}')
        return []

async def test_basic_functionality():
    """Test basic system functionality with known user"""
    print('\n🧪 Testing Basic System Functionality')
    print('=' * 50)
    
    # Check database first
    users = await check_database()
    
    if not users:
        print('❌ No users found in database. Please create a user first.')
        return
    
    # Use the first user for testing
    test_email = users[0]['email']
    print(f'📝 Testing with existing user: {test_email}')
    
    # Test messages that should NOT trigger AI service selection
    simple_messages = [
        "Hello, how are you?",
        "What's the weather like?",
        "Can you help me?"
    ]
    
    # Test messages that SHOULD trigger AI service selection
    ai_messages = [
        "Using AI, send an email to test@example.com",
        "Use AI to generate content and email it to john@company.com"
    ]
    
    async with aiohttp.ClientSession() as session:
        base_url = "http://localhost:8002"
        
        # First try to signup (might fail if user exists)
        signup_data = {
            "email": "testuser@example.com",
            "password": "testpass123",
            "firstName": "Test",
            "lastName": "User"
        }
        
        async with session.post(f"{base_url}/api/auth/signup", json=signup_data) as response:
            if response.status == 200:
                print("✅ New test user created")
                test_email = "testuser@example.com"
                test_password = "testpass123"
            else:
                print("ℹ️ Using existing user")
                test_email = "testuser@example.com"  # Try known user
                test_password = "testpass123"
        
        # Login
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        async with session.post(f"{base_url}/api/auth/login", json=login_data) as response:
            if response.status == 200:
                result = await response.json()
                auth_token = result.get("token")
                print(f"✅ Authentication successful for {test_email}")
                
                # Test the 4 issues
                await test_issue_1_ai_specificity(session, auth_token, simple_messages, ai_messages)
                await test_issue_2_workflow_preview(session, auth_token)
                
            else:
                print(f"❌ Authentication failed: {response.status}")
                response_text = await response.text()
                print(f"Response: {response_text}")

async def test_issue_1_ai_specificity(session, auth_token, simple_messages, ai_messages):
    """Test Issue 1: AI keyword specificity"""
    print('\n🔍 Testing Issue 1: AI Keyword Specificity')
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    base_url = "http://localhost:8002"
    
    # Test simple messages (should NOT trigger AI selection)
    print('\n📝 Testing simple messages (should NOT trigger AI selection):')
    for message in simple_messages:
        data = {
            "message": message,
            "agentId": "test-agent",
            "agentConfig": {
                "name": "Test Agent",
                "role": "assistant",
                "personality": {},
                "llm_config": {}
            }
        }
        
        async with session.post(f"{base_url}/api/mcpai/chat", headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                status = result.get("status", "success")
                if status == "ai_service_selection":
                    print(f"  ❌ '{message}' triggered AI selection (should not)")
                else:
                    print(f"  ✅ '{message}' did not trigger AI selection")
            else:
                print(f"  ❌ Request failed for '{message}': {response.status}")
    
    # Test AI messages (should trigger AI selection)
    print('\n📝 Testing AI messages (should trigger AI selection):')
    for message in ai_messages:
        data = {
            "message": message,
            "agentId": "test-agent",
            "agentConfig": {
                "name": "Test Agent",
                "role": "assistant",
                "personality": {},
                "llm_config": {}
            }
        }
        
        async with session.post(f"{base_url}/api/mcpai/chat", headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                status = result.get("status", "success")
                if status == "ai_service_selection":
                    print(f"  ✅ '{message}' correctly triggered AI selection")
                else:
                    print(f"  ❌ '{message}' did not trigger AI selection (should have)")
            else:
                print(f"  ❌ Request failed for '{message}': {response.status}")

async def test_issue_2_workflow_preview(session, auth_token):
    """Test Issue 2: Clean workflow preview"""
    print('\n🔍 Testing Issue 2: Clean Workflow Preview')
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    base_url = "http://localhost:8002"
    
    # Test with service selection to get workflow preview
    data = {
        "message": "service:inhouse Using AI, send an email to test@example.com with a welcome message",
        "agentId": "test-agent",
        "agentConfig": {
            "name": "Test Agent",
            "role": "assistant",
            "personality": {},
            "llm_config": {}
        }
    }
    
    async with session.post(f"{base_url}/api/mcpai/chat", headers=headers, json=data) as response:
        if response.status == 200:
            result = await response.json()
            
            if result.get("status") == "workflow_preview":
                workflow_preview = result.get("workflow_preview", {})
                
                # Check for clean preview structure
                has_title = "title" in workflow_preview
                has_description = "description" in workflow_preview
                has_steps = "steps" in workflow_preview and isinstance(workflow_preview["steps"], list)
                has_estimated_credits = "estimated_credits" in workflow_preview
                
                if has_title and has_description and has_steps and has_estimated_credits:
                    print("  ✅ Clean workflow preview structure detected")
                    print(f"  ✅ Title: {workflow_preview.get('title')}")
                    print(f"  ✅ Steps: {len(workflow_preview.get('steps', []))} steps")
                    print(f"  ✅ Credits: {workflow_preview.get('estimated_credits')}")
                else:
                    print("  ❌ Workflow preview structure incomplete")
            else:
                print(f"  ❌ Expected workflow_preview status, got: {result.get('status')}")
        else:
            print(f"  ❌ Request failed: {response.status}")

async def main():
    print('🚀 Quick System Test')
    print('=' * 50)
    await test_basic_functionality()

if __name__ == "__main__":
    asyncio.run(main())
