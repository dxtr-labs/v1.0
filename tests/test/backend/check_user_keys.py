#!/usr/bin/env python3
"""
Check user service_keys in database
"""
import asyncio
import asyncpg
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('.env.local')

async def check_user_service_keys():
    """Check what service_keys the test user has"""
    
    # Database configuration
    db_config = {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", 5432)),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD", "devhouse"),
        "database": os.getenv("PGDATABASE", "postgres")
    }
    
    print("🔍 Checking user service_keys...")
    print("=" * 40)
    
    try:
        conn = await asyncpg.connect(**db_config)
        print("✅ Connected to database")
        
        # Find our test user
        test_email = "morningautomation@example.com"
        
        user_data = await conn.fetchrow("""
            SELECT user_id, email, service_keys 
            FROM users 
            WHERE email = $1
        """, test_email)
        
        if user_data:
            print(f"✅ Found user: {user_data['email']}")
            print(f"📧 User ID: {user_data['user_id']}")
            
            service_keys = user_data['service_keys']
            print(f"🔑 Service keys type: {type(service_keys)}")
            
            if service_keys:
                if isinstance(service_keys, str):
                    print("📝 Service keys are stored as string, parsing JSON...")
                    try:
                        parsed_keys = json.loads(service_keys)
                        print(f"✅ Parsed service keys: {json.dumps(parsed_keys, indent=2)}")
                    except Exception as e:
                        print(f"❌ Failed to parse JSON: {e}")
                        print(f"Raw service_keys: {service_keys}")
                else:
                    print(f"✅ Service keys (dict): {json.dumps(service_keys, indent=2)}")
            else:
                print("❌ No service_keys found for user")
                
                # Add some test SMTP config
                print("\n🔧 Adding test SMTP config...")
                smtp_config = {
                    "smtp_config": {
                        "host": "mail.privateemail.com",
                        "port": 587,
                        "user": "automation-engine@dxtr-labs.com",
                        "password": "LuckyPE2005$"
                    }
                }
                
                await conn.execute("""
                    UPDATE users 
                    SET service_keys = $1 
                    WHERE user_id = $2
                """, json.dumps(smtp_config), user_data['user_id'])
                
                print(f"✅ Added SMTP config to user {user_data['email']}")
        else:
            print(f"❌ User not found: {test_email}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_user_service_keys())
