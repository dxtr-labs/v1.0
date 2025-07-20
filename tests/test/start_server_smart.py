#!/usr/bin/env python3
"""
Quick Fix Server Startup with SQLite Fallback
This script starts the server with SQLite authentication when PostgreSQL is unavailable
"""

import os
import sys
import subprocess
import time

def check_postgresql():
    """Check if PostgreSQL is available"""
    try:
        result = subprocess.run([
            'psql', '--version'
        ], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def create_sqlite_fallback_main():
    """Create a modified main.py that uses SQLite fallback"""
    
    print("🔧 Creating SQLite fallback server...")
    
    # Read the original main.py
    with open('backend/main.py', 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Create modified version with SQLite fallback
    modified_content = original_content.replace(
        'from db.postgresql_manager import (',
        '''# Try PostgreSQL first, fallback to SQLite
try:
    from db.postgresql_manager import ('''
    ).replace(
        ')',
        ''')
    print("✅ Using PostgreSQL database")
    USE_SQLITE = False
except Exception as e:
    print(f"⚠️ PostgreSQL unavailable: {e}")
    print("🔄 Falling back to SQLite authentication...")
    from sqlite_auth_fallback import (
        create_user, authenticate_user, get_user_by_session, update_user_session,
        get_user_by_id, add_credits, deduct_credits, get_credit_history
    )
    USE_SQLITE = True
    
    # Mock database manager for SQLite fallback
    class MockDBManager:
        async def initialize(self): pass
        async def close(self): pass
    
    db_manager = MockDBManager()
    
    async def init_db(): 
        await db_manager.initialize()
        return True
    
    async def close_db(): 
        await db_manager.close()'''
    )
    
    # Write the modified version
    with open('backend/main_sqlite.py', 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print("✅ Created backend/main_sqlite.py with SQLite fallback")

def start_server_with_fallback():
    """Start the server with appropriate database backend"""
    
    print("🚀 Starting AutoFlow Server with Database Fallback")
    print("=" * 60)
    
    # Check if PostgreSQL is available
    has_postgresql = check_postgresql()
    
    if has_postgresql:
        print("✅ PostgreSQL detected - using full database")
        script_name = "main.py"
    else:
        print("⚠️ PostgreSQL not found - using SQLite fallback")
        create_sqlite_fallback_main()
        script_name = "main_sqlite.py"
    
    # Change to backend directory
    os.chdir('backend')
    
    print(f"📂 Working directory: {os.getcwd()}")
    print(f"🎯 Starting: {script_name}")
    print("=" * 60)
    
    # Start the server
    try:
        subprocess.run([sys.executable, script_name])
    except KeyboardInterrupt:
        print("\\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    start_server_with_fallback()
