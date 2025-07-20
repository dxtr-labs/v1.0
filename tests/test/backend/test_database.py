#!/usr/bin/env python3
"""
Database Connection and Permission Test
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('.env.local')

async def test_database_connection():
    """Test database connection and permissions"""
    
    # Database configuration
    db_config = {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", 5432)),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD", "devhouse"),
        "database": os.getenv("PGDATABASE", "postgres")
    }
    
    print("🔍 Testing Database Connection...")
    print(f"Host: {db_config['host']}")
    print(f"Port: {db_config['port']}")
    print(f"User: {db_config['user']}")
    print(f"Database: {db_config['database']}")
    print("=" * 50)
    
    try:
        # Test basic connection
        conn = await asyncpg.connect(**db_config)
        print("✅ Database connection successful!")
        
        # Test current user and database
        result = await conn.fetchrow("SELECT current_user, current_database()")
        print(f"Current user: {result['current_user']}")
        print(f"Current database: {result['current_database']}")
        
        # Check if users table exists
        tables_result = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'users'
        """)
        
        if tables_result:
            print("✅ 'users' table exists")
            
            # Check table structure
            columns_result = await conn.fetch("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """)
            
            print("📋 Users table structure:")
            for col in columns_result:
                print(f"  - {col['column_name']}: {col['data_type']}")
                
            # Check if we can select from users table
            try:
                count_result = await conn.fetchrow("SELECT COUNT(*) as count FROM users")
                print(f"✅ Can read from users table. Row count: {count_result['count']}")
                
                # Try to get a sample user to test the service_keys column
                sample_user = await conn.fetchrow("SELECT user_id, email, service_keys FROM users LIMIT 1")
                if sample_user:
                    print(f"📝 Sample user: {sample_user['email']}")
                    print(f"📝 Service keys column exists: {'service_keys' in sample_user}")
                else:
                    print("ℹ️ No users found in table")
                    
            except Exception as e:
                print(f"❌ Cannot read from users table: {e}")
                
        else:
            print("❌ 'users' table does not exist")
            
            # List all available tables
            all_tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            print("📋 Available tables:")
            for table in all_tables:
                print(f"  - {table['table_name']}")
        
        # Check available roles
        roles_result = await conn.fetch("SELECT rolname FROM pg_roles ORDER BY rolname")
        print(f"\n📋 Available roles:")
        for role in roles_result:
            print(f"  - {role['rolname']}")
            
        # Check if app_user role exists
        app_user_exists = await conn.fetchrow("SELECT 1 FROM pg_roles WHERE rolname = 'app_user'")
        if app_user_exists:
            print("✅ 'app_user' role exists")
        else:
            print("❌ 'app_user' role does not exist")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_database_connection())
