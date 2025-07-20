"""
Database migration to add workflows table
"""

import asyncio
import asyncpg
import os
import logging

logger = logging.getLogger(__name__)

async def add_workflows_table():
    """Add workflows table to the database"""
    
    connection_config = {
        'user': os.getenv('PGUSER', 'postgres'),
        'password': os.getenv('PGPASSWORD', 'devhouse'),
        'database': os.getenv('PGDATABASE', 'postgres'),
        'host': os.getenv('PGHOST', 'localhost'),
        'port': int(os.getenv('PGPORT', '5432'))
    }
    
    conn = await asyncpg.connect(**connection_config)
    
    try:
        # Create workflows table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS workflows (
                workflow_id UUID PRIMARY KEY,
                agent_id UUID NOT NULL,
                script JSONB NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE CASCADE
            )
        ''')
        
        # Create index for faster agent_id lookups
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_workflows_agent_id ON workflows(agent_id)
        ''')
        
        print("✅ Workflows table created successfully")
        
    except Exception as e:
        print(f"❌ Error creating workflows table: {e}")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(add_workflows_table())
