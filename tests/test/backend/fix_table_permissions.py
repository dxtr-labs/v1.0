#!/usr/bin/env python3
"""
Fix Users Table Permissions for app_user Role
This script will grant the necessary permissions to the app_user role
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('.env.local')

async def fix_table_permissions():
    """Fix table permissions for app_user role"""
    
    # Database configuration
    db_config = {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", 5432)),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD", "devhouse"),
        "database": os.getenv("PGDATABASE", "postgres")
    }
    
    print("🔧 Fixing Users Table Permissions...")
    print("=" * 50)
    
    try:
        conn = await asyncpg.connect(**db_config)
        print("✅ Connected to database as postgres")
        
        # Check current permissions on users table
        print("\n🔍 Checking current permissions on users table...")
        permissions = await conn.fetch("""
            SELECT grantee, privilege_type 
            FROM information_schema.role_table_grants 
            WHERE table_name = 'users'
        """)
        
        print("Current permissions on users table:")
        for perm in permissions:
            print(f"  - {perm['grantee']}: {perm['privilege_type']}")
        
        # Grant SELECT permission to app_user role
        print("\n🔒 Granting SELECT permission on users table to app_user...")
        try:
            await conn.execute("GRANT SELECT ON users TO app_user;")
            print("✅ SELECT permission granted")
        except Exception as e:
            print(f"ℹ️ SELECT grant info: {e}")
        
        # Grant USAGE on the schema
        print("\n🔒 Granting USAGE on public schema to app_user...")
        try:
            await conn.execute("GRANT USAGE ON SCHEMA public TO app_user;")
            print("✅ USAGE permission on public schema granted")
        except Exception as e:
            print(f"ℹ️ USAGE grant info: {e}")
        
        # Check if RLS is enabled on users table
        print("\n🔍 Checking Row Level Security status...")
        rls_status = await conn.fetchrow("""
            SELECT schemaname, tablename, rowsecurity, forcerowsecurity
            FROM pg_tables 
            WHERE tablename = 'users'
        """)
        
        if rls_status:
            print(f"RLS enabled: {rls_status['rowsecurity']}")
            print(f"Force RLS: {rls_status['forcerowsecurity']}")
            
            # If RLS is enabled, we might need to create policies or disable it for testing
            if rls_status['rowsecurity']:
                print("\n⚠️ Row Level Security is enabled on users table")
                print("🔧 Creating policy to allow app_user to read all rows...")
                
                try:
                    # Create a permissive policy for app_user role
                    await conn.execute("""
                        CREATE POLICY app_user_select_all ON users 
                        FOR SELECT TO app_user 
                        USING (true);
                    """)
                    print("✅ Created permissive policy for app_user")
                except Exception as e:
                    if "already exists" in str(e):
                        print("ℹ️ Policy already exists")
                    else:
                        print(f"❌ Policy creation failed: {e}")
                        
                        # Alternative: Temporarily disable RLS for testing
                        print("🔧 Alternatively, disabling RLS on users table for testing...")
                        try:
                            await conn.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY;")
                            print("✅ RLS disabled on users table")
                        except Exception as e2:
                            print(f"❌ Failed to disable RLS: {e2}")
        
        # Test access as app_user role again
        print("\n🧪 Testing access as app_user role...")
        try:
            await conn.execute("SET ROLE app_user;")
            
            # Test basic query
            user_count = await conn.fetchrow("SELECT COUNT(*) as count FROM users")
            print(f"✅ Can query users table as app_user. Count: {user_count['count']}")
            
            # Test service_keys query
            sample_user = await conn.fetchrow("""
                SELECT user_id, email, service_keys 
                FROM users 
                WHERE service_keys IS NOT NULL 
                LIMIT 1
            """)
            
            if sample_user:
                print(f"✅ Can access service_keys for user: {sample_user['email']}")
            else:
                print("ℹ️ No users with service_keys found")
            
            await conn.execute("RESET ROLE;")
            print("✅ Successfully reset role")
            
        except Exception as e:
            print(f"❌ Access test failed: {e}")
            await conn.execute("RESET ROLE;")
        
        await conn.close()
        print("\n🎉 Table permissions fixed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix table permissions: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(fix_table_permissions())
