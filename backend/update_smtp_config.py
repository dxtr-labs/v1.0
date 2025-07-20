#!/usr/bin/env python3
"""
Update User SMTP Config with Correct Password
"""
import asyncio
import asyncpg
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('.env.local')

async def update_smtp_config():
    """Update SMTP config with correct password"""
    
    # Database configuration
    db_config = {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", 5432)),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD", "devhouse"),
        "database": os.getenv("PGDATABASE", "postgres")
    }
    
    print("🔧 Updating SMTP Configuration...")
    print("=" * 40)
    
    try:
        conn = await asyncpg.connect(**db_config)
        print("✅ Connected to database")
        
        # Find our test user
        test_email = "morningautomation@example.com"
        
        # Update with the correct SMTP config
        smtp_config = {
            "smtp_config": {
                "host": "mail.privateemail.com",
                "port": 587,
                "user": "automation-engine@dxtr-labs.com",
                "password": "Lakshu11042005$"  # Correct working password
            }
        }
        
        await conn.execute("""
            UPDATE users 
            SET service_keys = $1 
            WHERE email = $2
        """, json.dumps(smtp_config), test_email)
        
        print(f"✅ Updated SMTP config for user {test_email}")
        
        # Verify the update
        user_data = await conn.fetchrow("""
            SELECT user_id, email, service_keys 
            FROM users 
            WHERE email = $1
        """, test_email)
        
        if user_data:
            service_keys = user_data['service_keys']
            if isinstance(service_keys, str):
                service_keys = json.loads(service_keys)
            
            smtp_config = service_keys.get('smtp_config', {})
            print(f"📧 Verified SMTP config:")
            print(f"   Host: {smtp_config.get('host')}")
            print(f"   Port: {smtp_config.get('port')}")
            print(f"   User: {smtp_config.get('user')}")
            print(f"   Password: {smtp_config.get('password', 'Not set')[:5]}...")
        
        await conn.close()
        print("\n🎉 SMTP configuration updated successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(update_smtp_config())
