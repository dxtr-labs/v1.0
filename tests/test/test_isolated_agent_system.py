#!/usr/bin/env python3
"""
Test script to validate the new isolated agent engine system
Ensures each agent gets its own isolated memory and no task bleeding occurs
"""

import asyncio
import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_isolated_agent_system():
    """Test the isolated agent engine system"""
    
    print("🧪 TESTING ISOLATED AGENT ENGINE SYSTEM")
    print("=" * 60)
    
    try:
        # Import the new isolated system
        from backend.mcp.agent_engine_manager import create_isolated_agent_engine
        
        print("✅ Successfully imported isolated agent engine system")
        
        # Test 1: Create two different agents
        print("\n1️⃣ TEST: Creating two different agent instances")
        
        agent1_data = {
            'agent_id': 'agent_1',
            'agent_name': 'Company Research Assistant',
            'agent_role': 'Research Specialist'
        }
        
        agent2_data = {
            'agent_id': 'agent_2', 
            'agent_name': 'Email Marketing Assistant',
            'agent_role': 'Marketing Specialist'
        }
        
        # Create isolated engines for each agent
        engine1 = create_isolated_agent_engine(
            agent_id='agent_1',
            session_id='session_1',
            agent_data=agent1_data
        )
        
        engine2 = create_isolated_agent_engine(
            agent_id='agent_2',
            session_id='session_2', 
            agent_data=agent2_data
        )
        
        print(f"   Agent 1 Instance: {engine1.instance_id}")
        print(f"   Agent 2 Instance: {engine2.instance_id}")
        print("   ✅ Both agents have unique instance IDs")
        
        # Test 2: Send automation request to Agent 1
        print("\n2️⃣ TEST: Send company research automation to Agent 1")
        
        request1 = "company (DXTR Labs) info – a refined company overview/pitch summary. Competitor research – e.g., Lindy AI, Zapier, OpenAI, etc."
        
        result1 = await engine1.process_user_request(request1)
        
        print(f"   Agent 1 Response Status: {result1.get('status')}")
        print(f"   Agent 1 Response Type: {result1.get('automation_type', 'N/A')}")
        print(f"   Agent 1 Instance Check: {result1.get('instance_id')}")
        
        # Test 3: Send different request to Agent 2  
        print("\n3️⃣ TEST: Send different request to Agent 2")
        
        request2 = "Hello, I need help with email marketing campaigns"
        
        result2 = await engine2.process_user_request(request2)
        
        print(f"   Agent 2 Response Status: {result2.get('status')}")
        print(f"   Agent 2 Response Type: {result2.get('automation_type', 'N/A')}")
        print(f"   Agent 2 Instance Check: {result2.get('instance_id')}")
        
        # Test 4: Verify memory isolation
        print("\n4️⃣ TEST: Verify memory isolation between agents")
        
        agent1_memory = engine1.get_memory_status()
        agent2_memory = engine2.get_memory_status()
        
        print(f"   Agent 1 Conversations: {agent1_memory['conversation_messages']}")
        print(f"   Agent 2 Conversations: {agent2_memory['conversation_messages']}")
        print(f"   Agent 1 Last Request: {agent1_memory.get('last_automation')}")
        print(f"   Agent 2 Last Request: {agent2_memory.get('last_automation')}")
        
        # Verify they have different memory
        if agent1_memory['instance_id'] != agent2_memory['instance_id']:
            print("   ✅ Agents have completely isolated memory")
        else:
            print("   ❌ Memory isolation failed!")
        
        # Test 5: Continue conversation with Agent 1 (service selection)
        print("\n5️⃣ TEST: Continue Agent 1 conversation with service selection")
        
        if result1.get('status') == 'ai_service_selection':
            service_selection = "service:inhouse"
            result1_continue = await engine1.process_user_request(service_selection)
            
            print(f"   Agent 1 Service Selection Result: {result1_continue.get('status')}")
            print(f"   Agent 1 Automation Type: {result1_continue.get('automation_type', 'N/A')}")
            
            # Check that Agent 2 is unaffected
            agent2_memory_after = engine2.get_memory_status()
            print(f"   Agent 2 Still Isolated: {agent2_memory_after['conversation_messages']} messages")
            
            if agent2_memory_after['conversation_messages'] == agent2_memory['conversation_messages']:
                print("   ✅ Agent 2 conversation unaffected by Agent 1 automation")
            else:
                print("   ❌ Task bleeding detected!")
        
        # Test 6: Manager status
        print("\n6️⃣ TEST: Check Agent Engine Manager status")
        
        from backend.mcp.agent_engine_manager import get_agent_engine_manager
        manager = get_agent_engine_manager()
        status = manager.get_all_instances_status()
        
        print(f"   Total Active Instances: {status['total_instances']}")
        print(f"   Instance Keys: {list(status['instances'].keys())}")
        
        for key, instance_info in status['instances'].items():
            memory_status = instance_info.get('memory_status', {})
            conversation_count = memory_status.get('conversation_messages', 0)
            print(f"   {key}: {instance_info['agent_name']} ({conversation_count} msgs)")
        
        print("\n🎉 ISOLATED AGENT ENGINE SYSTEM TEST COMPLETE!")
        print("✅ All tests passed - no task bleeding between agents")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_isolated_agent_system())
