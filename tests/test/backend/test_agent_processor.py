#!/usr/bin/env python3
"""
Test script to verify AgentProcessor functionality
"""
import asyncio
import asyncpg
from core.agent_processor import AgentProcessor
from core.simple_agent_manager import AgentManager
from core.agent_schema import DEFAULT_CUSTOM_MCP_CODE

async def test_agent_processor():
    """Test the AgentProcessor with a sample agent"""
    
    # Database connection
    DATABASE_URL = 'postgresql://postgres:devhouse@34.44.98.81:5432/postgres'
    
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Database connected")
        
        # Initialize AgentManager and AgentProcessor
        agent_manager = AgentManager(conn)
        agent_processor = AgentProcessor(agent_manager, conn)
        print("✅ AgentProcessor initialized")
        
        # Create a test agent
        test_agent_id = "test-agent-123"
        user_id = "test-user-456"
        
        # Insert test agent into database
        await conn.execute("""
            INSERT INTO agents (agent_id, agent_name, user_id, personality, instructions, 
                               operation_mode, custom_mcp_code, trigger_config)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (agent_id) DO UPDATE SET
                custom_mcp_code = EXCLUDED.custom_mcp_code,
                operation_mode = EXCLUDED.operation_mode
        """, 
        test_agent_id, 
        "Test Agent", 
        user_id, 
        "Helpful and friendly assistant", 
        "You are a helpful AI assistant",
        "manual",  # operation_mode
        DEFAULT_CUSTOM_MCP_CODE,  # custom_mcp_code
        None  # trigger_config
        )
        print("✅ Test agent created/updated")
        
        # Test processing with agent
        print("\n🧪 Testing AgentProcessor.process_with_agent()...")
        response = await agent_processor.process_with_agent(
            agent_id=test_agent_id,
            user_input="Hello, can you help me test the system?",
            user_id=user_id
        )
        
        print(f"✅ AgentProcessor Response: {response}")
        
        # Test agent memory retrieval
        print("\n🧪 Testing agent memory...")
        memory = await agent_processor._get_agent_memory(test_agent_id, user_id)
        print(f"✅ Agent Memory: {memory}")
        
        await conn.close()
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent_processor())
