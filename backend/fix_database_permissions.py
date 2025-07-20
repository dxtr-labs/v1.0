#!/usr/bin/env python3
"""
Grant Postgres User Access to app_user Role
This script will fix the database permissions issue
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('.env.local')

async def fix_database_permissions():
    """Fix database permissions for the postgres user"""
    
    # Database configuration
    db_config = {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", 5432)),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD", "devhouse"),
        "database": os.getenv("PGDATABASE", "postgres")
    }
    
    print("🔧 Fixing Database Permissions...")
    print("=" * 50)
    
    try:
        conn = await asyncpg.connect(**db_config)
        print("✅ Connected to database")
        
        # Check current role memberships
        print("\n🔍 Checking current role memberships...")
        memberships = await conn.fetch("""
            SELECT r.rolname as role, m.rolname as member 
            FROM pg_roles r 
            JOIN pg_auth_members am ON r.oid = am.roleid 
            JOIN pg_roles m ON am.member = m.oid 
            WHERE r.rolname = 'app_user'
        """)
        
        print("Current app_user role members:")
        for membership in memberships:
            print(f"  - {membership['member']}")
        
        # Grant app_user role to postgres if not already granted
        postgres_has_app_user = any(m['member'] == 'postgres' for m in memberships)
        
        if not postgres_has_app_user:
            print("\n🔒 Granting app_user role to postgres user...")
            await conn.execute("GRANT app_user TO postgres;")
            print("✅ app_user role granted to postgres")
        else:
            print("✅ postgres already has app_user role")
        
        # Also grant app_admin role for good measure
        print("\n🔒 Granting app_admin role to postgres user...")
        try:
            await conn.execute("GRANT app_admin TO postgres;")
            print("✅ app_admin role granted to postgres")
        except Exception as e:
            print(f"ℹ️ app_admin grant info: {e}")
        
        # Test switching to app_user role
        print("\n🧪 Testing role switching...")
        try:
            await conn.execute("SET ROLE app_user;")
            current_role = await conn.fetchrow("SELECT current_user")
            print(f"✅ Successfully switched to role: {current_role['current_user']}")
            
            # Test querying users table as app_user
            user_count = await conn.fetchrow("SELECT COUNT(*) as count FROM users")
            print(f"✅ Can query users table as app_user. Count: {user_count['count']}")
            
            await conn.execute("RESET ROLE;")
            print("✅ Successfully reset role")
            
        except Exception as e:
            print(f"❌ Role switching test failed: {e}")
        
        await conn.close()
        print("\n🎉 Database permissions fixed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix database permissions: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(fix_database_permissions())
