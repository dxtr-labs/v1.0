import asyncio
import asyncpg
import json

async def update_user():
    conn = await asyncpg.connect(
        host='localhost', 
        port=5432, 
        user='postgres', 
        password='devhouse', 
        database='postgres'
    )
    
    smtp_config = {
        'smtp_config': {
            'host': 'mail.privateemail.com',
            'port': 587,
            'user': 'automation-engine@dxtr-labs.com',
            'password': 'LuckyPE2005$'
        }
    }
    
    result = await conn.execute(
        'UPDATE users SET service_keys = $1 WHERE email = $2',
        json.dumps(smtp_config),
        'morningautomation@example.com'
    )
    
    print(f'Update result: {result}')
    
    # Verify the update
    user = await conn.fetchrow(
        'SELECT service_keys FROM users WHERE email = $1', 
        'morningautomation@example.com'
    )
    if user:
        print(f'Updated service_keys: {user["service_keys"]}')
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(update_user())
