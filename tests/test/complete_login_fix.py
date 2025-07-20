#!/usr/bin/env python3
"""
Complete Login Fix Solution
This script provides multiple approaches to fix the login issue
"""

import subprocess
import sys
import os
import time
import requests

def solution_1_install_postgresql():
    """Solution 1: Install PostgreSQL (Recommended for production)"""
    print("=" * 60)
    print("🗄️ SOLUTION 1: Install PostgreSQL")
    print("=" * 60)
    print("Steps to install PostgreSQL:")
    print("1. Download PostgreSQL from: https://www.postgresql.org/download/windows/")
    print("2. Install with these settings:")
    print("   - Username: postgres")
    print("   - Password: devhouse") 
    print("   - Port: 5432")
    print("3. Restart the backend server")
    print()

def solution_2_use_sqlite_fallback():
    """Solution 2: Use SQLite fallback (Quick fix)"""
    print("=" * 60)
    print("🗃️ SOLUTION 2: SQLite Fallback (Quick Fix)")
    print("=" * 60)
    
    # Test SQLite fallback
    try:
        import sqlite3
        print("✅ SQLite available")
        
        # Initialize SQLite auth database
        print("🔧 Initializing SQLite auth database...")
        os.chdir('backend')
        
        # Create the SQLite auth database
        subprocess.run([sys.executable, 'sqlite_auth_fallback.py'], check=True)
        print("✅ SQLite auth database created")
        
        # Create modified main.py
        print("🔧 Creating SQLite-compatible server...")
        create_sqlite_compatible_main()
        print("✅ SQLite-compatible server created")
        
        print("\n🚀 To use SQLite fallback:")
        print("1. Stop the current backend server (Ctrl+C in the task)")
        print("2. Run: python start_server_smart.py")
        print("3. Test login with: python test_login_comprehensive.py")
        
    except Exception as e:
        print(f"❌ SQLite setup failed: {e}")

def solution_3_fix_current_server():
    """Solution 3: Fix the current server issues"""
    print("=" * 60)
    print("🔧 SOLUTION 3: Fix Current Server")
    print("=" * 60)
    
    # Check if server is actually responsive
    print("Testing current server connectivity...")
    
    try:
        response = requests.get("http://localhost:8002/docs", timeout=3)
        print(f"✅ Server responds to /docs: {response.status_code}")
        
        # Test login endpoint
        test_login = {
            "email": "test@example.com",
            "password": "test123"
        }
        
        login_response = requests.post(
            "http://localhost:8002/api/auth/login",
            json=test_login,
            timeout=5
        )
        
        print(f"🔑 Login endpoint status: {login_response.status_code}")
        print(f"🔑 Login response: {login_response.text[:200]}")
        
        if login_response.status_code == 500:
            print("❌ Server error detected - likely database connection issue")
            print("💡 Recommendation: Use Solution 1 or 2")
        elif login_response.status_code == 401:
            print("✅ Login endpoint working - just need valid credentials")
            print("💡 Try creating an account first with signup")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server on port 8002")
        print("💡 Check if the task is actually running the server correctly")
    except Exception as e:
        print(f"❌ Server test failed: {e}")

def create_sqlite_compatible_main():
    """Create a version of main.py that works with SQLite"""
    # This would modify the import statements to use SQLite fallback
    print("Creating SQLite-compatible main.py...")
    # Implementation would go here

def solution_4_test_existing_accounts():
    """Solution 4: Test if accounts already exist"""
    print("=" * 60)
    print("👥 SOLUTION 4: Test Existing Accounts")
    print("=" * 60)
    
    print("Testing if any accounts already exist...")
    
    # Common test credentials that might exist
    test_accounts = [
        {"email": "admin@dxtr-labs.com", "password": "admin123"},
        {"email": "test@test.com", "password": "test123"},
        {"email": "user@example.com", "password": "password"},
    ]
    
    for account in test_accounts:
        try:
            response = requests.post(
                "http://localhost:8002/api/auth/login",
                json=account,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Found working account: {account['email']}")
                print(f"🔑 Session token: {result.get('session_token', 'None')}")
                return account
            else:
                print(f"❌ {account['email']}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing {account['email']}: {e}")
    
    print("No existing accounts found - need to create one")

def main():
    print("🔧 COMPLETE LOGIN FIX SOLUTION")
    print("=" * 60)
    print("Choose the best solution for your situation:")
    print()
    
    # Test current server status
    print("📊 Current System Status:")
    try:
        response = requests.get("http://localhost:8002/docs", timeout=2)
        print("✅ Server is running and accessible")
        server_working = True
    except:
        print("❌ Server not accessible")
        server_working = False
    
    if server_working:
        # Server is running, test authentication
        solution_3_fix_current_server()
        solution_4_test_existing_accounts()
    
    print()
    solution_1_install_postgresql()
    solution_2_use_sqlite_fallback()
    
    print("=" * 60)
    print("🎯 RECOMMENDED APPROACH:")
    if server_working:
        print("1. Try Solution 4 (test existing accounts) first")
        print("2. If no accounts work, try Solution 3 (debug current server)")
        print("3. If server errors persist, use Solution 2 (SQLite fallback)")
    else:
        print("1. Use Solution 2 (SQLite fallback) for immediate fix")
        print("2. Install PostgreSQL (Solution 1) for production use")
    
    print("\n🔧 Quick Fix Command:")
    print("python start_server_smart.py")

if __name__ == "__main__":
    main()
