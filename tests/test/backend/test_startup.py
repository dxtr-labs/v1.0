#!/usr/bin/env python3
"""
Simple test script to identify startup issues
"""

print("🚀 Starting simple test...")

try:
    print("📦 Loading environment...")
    from dotenv import load_dotenv
    load_dotenv('.env.local')
    print("✅ Environment loaded")
    
    print("📦 Importing FastAPI...")
    from fastapi import FastAPI
    print("✅ FastAPI imported")
    
    print("📦 Testing database connection...")
    import asyncio
    import asyncpg
    import os
    
    async def test_db():
        try:
            conn = await asyncpg.connect(
                host=os.getenv('PGHOST', 'localhost'),
                port=int(os.getenv('PGPORT', 5432)),
                database=os.getenv('PGDATABASE', 'postgres'),
                user=os.getenv('PGUSER', 'postgres'),
                password=os.getenv('PGPASSWORD', 'devhouse'),
                timeout=5  # Add timeout
            )
            print("✅ Database connection successful")
            await conn.close()
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    print("🔌 Testing database connection...")
    db_success = asyncio.run(test_db())
    
    if db_success:
        print("📦 Testing core imports...")
        try:
            from core.simple_agent_manager import AgentManager
            print("✅ AgentManager imported")
            
            from core.agent_processor import AgentProcessor
            print("✅ AgentProcessor imported")
            
            from mcp.simple_automation_engine import AutomationEngine
            print("✅ AutomationEngine imported")
            
        except Exception as e:
            print(f"❌ Core import failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("🎯 All tests completed!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
