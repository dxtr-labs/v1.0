#!/usr/bin/env python3
"""
Test SQLite authentication system directly
"""

import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_sqlite_auth():
    """Test SQLite authentication functionality"""
    print("🧪 Testing SQLite Authentication System...")
    
    try:
        # Import SQLite auth system
        from sqlite_auth_fallback import (
            create_user, authenticate_user, get_user_by_session, 
            update_user_session
        )
        print("✅ SQLite auth system imported successfully")
        
        # Test user creation
        print("\n1. Testing user creation...")
        test_email = "test@autoflow.ai"
        test_password = "testpass123"
        
        try:
            user = await create_user(
                email=test_email,
                password=test_password,
                first_name="Test",
                last_name="User",
                username="testuser"
            )
            print(f"✅ User created: {user['email']} (ID: {user['user_id']})")
        except ValueError as e:
            if "Email already exists" in str(e):
                print(f"ℹ️ User already exists: {test_email}")
            else:
                print(f"❌ User creation error: {e}")
                return False
        
        # Test authentication
        print("\n2. Testing authentication...")
        auth_user = await authenticate_user(test_email, test_password)
        if auth_user:
            print(f"✅ Authentication successful: {auth_user['email']}")
            user_id = str(auth_user['user_id'])
        else:
            print("❌ Authentication failed")
            return False
        
        # Test session management
        print("\n3. Testing session management...")
        session_token = "test_session_token_123"
        session_updated = await update_user_session(user_id, session_token)
        if session_updated:
            print(f"✅ Session token updated: {session_token}")
        
        # Test session retrieval
        session_user = await get_user_by_session(session_token)
        if session_user and session_user['user_id'] == auth_user['user_id']:
            print(f"✅ Session retrieval successful: {session_user['email']}")
        else:
            print("❌ Session retrieval failed")
            return False
        
        print("\n🎉 All SQLite authentication tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ SQLite auth test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_server_imports():
    """Test if server dependencies can be imported"""
    print("\n🔍 Testing server dependencies...")
    
    try:
        import uvicorn
        print("✅ uvicorn imported")
        
        import fastapi
        print("✅ FastAPI imported")
        
        # Test backend imports
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        try:
            from mcp.simple_automation_engine import AutomationEngine
            print("✅ AutomationEngine imported")
        except Exception as e:
            print(f"⚠️ AutomationEngine import issue: {e}")
        
        try:
            from core.simple_agent_manager import AgentManager
            print("✅ AgentManager imported")
        except Exception as e:
            print(f"⚠️ AgentManager import issue: {e}")
        
        try:
            from core.agent_processor import AgentProcessor
            print("✅ AgentProcessor imported")
        except Exception as e:
            print(f"⚠️ AgentProcessor import issue: {e}")
        
        try:
            from simple_email_service import EmailService
            print("✅ EmailService imported")
        except Exception as e:
            print(f"⚠️ EmailService import issue: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Server dependency test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SQLite Authentication System Test")
    print("=" * 50)
    
    asyncio.run(test_sqlite_auth())
    asyncio.run(test_server_imports())
    
    print("\n📋 Test Summary:")
    print("- SQLite auth system functionality")
    print("- Server dependency imports")
    print("- Login flow components")
