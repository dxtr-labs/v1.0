#!/usr/bin/env python3
import asyncio
import asyncpg
import sys
import os

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def check_agents():
    """Check what agents exist in the database"""
    
    try:
        # Connect to database
        conn = await asyncpg.connect("postgresql://postgres:devhouse@localhost:5432/postgres")
        
        # Get agents
        agents = await conn.fetch("SELECT * FROM agents LIMIT 3")
        
        print("🔍 Available agents in database:")
        for agent in agents:
            print(f"  Agent: {dict(agent)}")
            print("  ---")
        
        await conn.close()
        
        if agents:
            return str(agents[0]['agent_id'])
        return None
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None

if __name__ == "__main__":
    agent_id = asyncio.run(check_agents())
    if agent_id:
        print(f"\n✅ Using agent ID: {agent_id}")
    else:
        print("\n❌ No agents found")
