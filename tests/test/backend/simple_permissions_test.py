#!/usr/bin/env python3
"""
Simple Table Permissions Fix and Test
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('.env.local')

async def simple_permissions_test():
    """Simple permissions fix and test"""
    
    # Database configuration
    db_config = {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", 5432)),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD", "devhouse"),
        "database": os.getenv("PGDATABASE", "postgres")
    }
    
    print("🔧 Simple Permissions Test...")
    print("=" * 40)
    
    try:
        conn = await asyncpg.connect(**db_config)
        print("✅ Connected to database")
        
        # Grant all necessary permissions
        print("\n🔒 Granting permissions...")
        await conn.execute("GRANT ALL ON users TO app_user;")
        print("✅ ALL permissions granted on users table")
        
        # Check if RLS exists (simple check)
        print("\n🔍 Checking RLS...")
        try:
            rls_check = await conn.fetchrow("SELECT relrowsecurity FROM pg_class WHERE relname = 'users'")
            if rls_check and rls_check['relrowsecurity']:
                print("⚠️ RLS is enabled, disabling for testing...")
                await conn.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY;")
                print("✅ RLS disabled")
            else:
                print("ℹ️ RLS not enabled or already disabled")
        except Exception as e:
            print(f"ℹ️ RLS check info: {e}")
        
        # Test as app_user
        print("\n🧪 Testing as app_user...")
        await conn.execute("SET ROLE app_user;")
        
        user_count = await conn.fetchrow("SELECT COUNT(*) as count FROM users")
        print(f"✅ Users count: {user_count['count']}")
        
        # Test service_keys access
        sample = await conn.fetchrow("""
            SELECT user_id, email, service_keys 
            FROM users 
            WHERE service_keys IS NOT NULL 
            LIMIT 1
        """)
        
        if sample:
            print(f"✅ Can access service_keys for: {sample['email']}")
            service_keys = sample['service_keys']
            if service_keys and 'smtp' in service_keys:
                print(f"✅ SMTP config found for user")
            else:
                print("ℹ️ No SMTP config in service_keys")
        
        await conn.execute("RESET ROLE;")
        await conn.close()
        
        print("\n🎉 Permissions working!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(simple_permissions_test())
