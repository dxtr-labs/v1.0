#!/usr/bin/env python3
"""
Complete Login System Diagnostic and Fix
"""

import subprocess
import sys
import os
import time

def check_postgres():
    """Check if PostgreSQL is running"""
    print("🔍 Checking PostgreSQL...")
    try:
        # Try to connect to postgres using psql
        result = subprocess.run([
            'psql', '-h', 'localhost', '-U', 'postgres', '-d', 'postgres', 
            '-c', 'SELECT version();'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ PostgreSQL is running")
            return True
        else:
            print(f"❌ PostgreSQL connection failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ psql command not found - PostgreSQL might not be installed")
        return False
    except Exception as e:
        print(f"❌ PostgreSQL check failed: {e}")
        return False

def check_database_tables():
    """Check if required database tables exist"""
    print("🔍 Checking database tables...")
    try:
        result = subprocess.run([
            'psql', '-h', 'localhost', '-U', 'postgres', '-d', 'postgres',
            '-c', "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            tables = result.stdout
            print(f"📊 Database tables found:\n{tables}")
            
            # Check for required tables
            if 'users' in tables:
                print("✅ Users table exists")
            else:
                print("❌ Users table missing - need to run database setup")
                return False
            return True
        else:
            print(f"❌ Failed to check tables: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Table check failed: {e}")
        return False

def fix_server_startup():
    """Create a fixed server startup script"""
    print("🔧 Creating fixed server startup script...")
    
    startup_script = '''@echo off
echo Starting AutoFlow Backend Server...
cd /d "C:\\Users\\sugua\\Desktop\\redo\\backend"
echo Current directory: %CD%
C:\\Python312\\python.exe main.py
pause
'''
    
    with open('start_backend_fixed.bat', 'w') as f:
        f.write(startup_script)
    
    print("✅ Created start_backend_fixed.bat")
    print("   Run this script to start the server from the correct directory")

def create_login_test():
    """Create a comprehensive login test"""
    print("🔧 Creating login test script...")
    
    test_script = '''#!/usr/bin/env python3
import requests
import json
import time

def comprehensive_login_test():
    base_url = "http://localhost:8002"
    
    print("Testing Comprehensive Login Test")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    print("\\n1. Testing basic connectivity...")
    try:
        response = requests.get(f"{base_url}/docs", timeout=3)
        print(f"   Server accessible: {response.status_code}")
    except Exception as e:
        print(f"   Server not accessible: {e}")
        print("   Fix: Make sure backend server is running")
        return False
    
    # Test 2: Test signup
    print("\\n2. Testing user signup...")
    signup_data = {
        "email": f"test_{int(time.time())}@example.com",
        "password": "test123456",
        "first_name": "Test",
        "last_name": "User",
        "username": f"testuser_{int(time.time())}"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/signup",
            json=signup_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Signup successful: {result.get('message')}")
            session_token = result.get('session_token')
            print(f"   Session token: {session_token[:20]}..." if session_token else "   No session token")
        else:
            print(f"   Signup failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   Signup request failed: {e}")
        return False
    
    # Test 3: Test login with the same credentials
    print("\\n3. Testing user login...")
    login_data = {
        "email": signup_data["email"],
        "password": signup_data["password"]
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Login successful: {result.get('message')}")
            session_token = result.get('session_token')
            print(f"   Session token: {session_token[:20]}..." if session_token else "   No session token")
            
            # Test 4: Test authenticated endpoint
            print("\\n4. Testing authenticated endpoint...")
            try:
                auth_response = requests.get(
                    f"{base_url}/api/auth/me",
                    headers={"Authorization": f"Bearer {session_token}"},
                    timeout=10
                )
                print(f"   Auth endpoint status: {auth_response.status_code}")
                if auth_response.status_code == 200:
                    print("   Authentication working correctly")
                    return True
                else:
                    print(f"   Auth endpoint failed: {auth_response.text}")
            except Exception as e:
                print(f"   Auth endpoint test failed: {e}")
                
        else:
            print(f"   Login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   Login request failed: {e}")
        return False
    
    return False

if __name__ == "__main__":
    success = comprehensive_login_test()
    if success:
        print("\\nLogin system is working correctly!")
    else:
        print("\\nLogin system has issues - check server and database")
'''
    
    with open('test_login_comprehensive.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ Created test_login_comprehensive.py")

def main():
    print("🔧 AutoFlow Login System Diagnostic")
    print("=" * 50)
    
    # Step 1: Check if we're in the right directory
    current_dir = os.getcwd()
    print(f"📂 Current directory: {current_dir}")
    
    if not os.path.exists('backend'):
        print("❌ Backend directory not found!")
        print("   Please run this script from the project root directory")
        return
    
    # Step 2: Check PostgreSQL
    postgres_ok = check_postgres()
    
    # Step 3: Check database tables
    if postgres_ok:
        tables_ok = check_database_tables()
    else:
        tables_ok = False
    
    # Step 4: Create fixes
    fix_server_startup()
    create_login_test()
    
    print("\\n" + "=" * 50)
    print("🎯 DIAGNOSIS COMPLETE")
    print("=" * 50)
    
    if postgres_ok and tables_ok:
        print("✅ Database setup looks good")
        print("\\n🚀 Next steps:")
        print("   1. Stop the current backend server")
        print("   2. Run: start_backend_fixed.bat")
        print("   3. Run: python test_login_comprehensive.py")
    else:
        print("❌ Database issues found")
        print("\\n🔧 Required fixes:")
        if not postgres_ok:
            print("   1. Install and start PostgreSQL")
            print("   2. Create database with credentials: postgres/devhouse")
        if not tables_ok:
            print("   3. Run database setup script to create tables")
        print("   4. Run: start_backend_fixed.bat")
        print("   5. Run: python test_login_comprehensive.py")

if __name__ == "__main__":
    main()
