"""
Demonstration Script: Personalized AI Agents in Action

This script demonstrates the complete flow of your personalized AI agent system:
1. User registration and memory initialization
2. Agent creation with personality and context
3. Personalized conversations with memory persistence
4. Learning and adaptation over time

Run this script to see how your system creates truly personalized AI experiences.
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add backend to path
sys.path.append('backend')

from backend.core.personalized_mcp_orchestrator import (
    PersonalizedMCPOrchestrator, 
    create_quick_marketing_agent,
    setup_user_with_template
)
from backend.db.postgresql_manager import db_manager

async def demo_personalized_ai_system():
    """
    Complete demonstration of the personalized AI agent system.
    """
    print("🚀 Starting Personalized AI Agent System Demo")
    print("=" * 60)
    
    try:
        # Initialize database manager first to get working config
        await db_manager.initialize()
        
        # Use the same database configuration that works
        orchestrator = PersonalizedMCPOrchestrator(db_manager.connection_config)
        await orchestrator.initialize()
        
        print("✅ Orchestrator initialized")
        
        # Demo 1: Create a new user with personalized context
        print("\\n📝 Demo 1: Creating User with Personalized Context")
        print("-" * 50)
        
        # Create test user
        user_email = "demo@techstartup.com"
        user_password = "securepass123"
        
        # Initialize database manager
        await db_manager.initialize()
        
        try:
            user_data = await db_manager.create_user(
                email=user_email,
                password=user_password,
                username="StartupFounder"
            )
            user_id = user_data["user_id"]  # Extract UUID from dict
            print(f"✅ Created user: {user_id}")
        except Exception as e:
            # User might already exist
            user = await db_manager.authenticate_user(user_email, user_password)
            user_id = user["user_id"]
            print(f"✅ Using existing user: {user_id}")
        
        # Set up user with startup founder template
        await setup_user_with_template(orchestrator, user_id, "startup_founder")
        print("✅ User memory initialized with startup founder template")
        
        # Add specific company context
        company_context = {
            "user_profile": {
                "company_name": "TechFlow AI",
                "industry": "Artificial Intelligence",
                "role": "Founder & CEO",
                "team_size": "12 people"
            },
            "context_memory": {
                "current_projects": ["AI automation platform", "Customer onboarding system"],
                "ongoing_challenges": ["Scaling customer support", "Lead qualification"],
                "key_metrics_tracked": ["Monthly recurring revenue", "Customer acquisition cost"]
            }
        }
        
        await orchestrator.user_memory_manager.update_user_memory(user_id, company_context)
        print("✅ Added specific company context for TechFlow AI")
        
        # Demo 2: Create personalized marketing agent
        print("\\n🤖 Demo 2: Creating Personalized Marketing Agent")
        print("-" * 50)
        
        marketing_agent_id = await create_quick_marketing_agent(orchestrator, user_id)
        print(f"✅ Created Marketing Maestro agent: {marketing_agent_id}")
        
        # Customize the agent with specific context
        agent_context = {
            "learned_preferences": {
                "user_specific_knowledge": {
                    "company_focus": "B2B AI automation",
                    "target_audience": "Small to medium businesses",
                    "preferred_channels": ["LinkedIn", "Email", "Content marketing"]
                }
            },
            "conversation_topics": ["lead generation", "content strategy", "marketing automation"]
        }
        
        await orchestrator.agent_manager.update_agent_memory(
            marketing_agent_id, user_id, agent_context
        )
        print("✅ Customized agent with TechFlow AI marketing context")
        
        # Demo 3: Personalized conversation with context injection
        print("\\n💬 Demo 3: Personalized Conversation")
        print("-" * 50)
        
        # Create session
        session_id = await orchestrator.create_personalized_session(
            user_id=user_id,
            agent_id=marketing_agent_id,
            session_context={"demo_session": True}
        )
        print(f"✅ Created personalized session: {session_id}")
        
        # Conversation 1: Initial greeting
        print("\\n👤 User: Hi! I need help with lead generation for my startup.")
        
        response1 = await orchestrator.process_message(
            session_id, 
            "Hi! I need help with lead generation for my startup."
        )
        
        print(f"🤖 {response1['agent_name']}: {response1['response']}")
        print(f"   Context used: {response1['context_used']}")
        
        # Conversation 2: Specific question about tools
        print("\\n👤 User: What automation tools would work best for our B2B SaaS customer onboarding?")
        
        response2 = await orchestrator.process_message(
            session_id,
            "What automation tools would work best for our B2B SaaS customer onboarding?"
        )
        
        print(f"🤖 {response2['agent_name']}: {response2['response']}")
        
        # Conversation 3: Learning from interaction
        print("\\n👤 User: We've been using HubSpot but considering switching to Salesforce. What do you think?")
        
        response3 = await orchestrator.process_message(
            session_id,
            "We've been using HubSpot but considering switching to Salesforce. What do you think?"
        )
        
        print(f"🤖 {response3['agent_name']}: {response3['response']}")
        
        # Demo 4: Memory persistence and learning
        print("\\n🧠 Demo 4: Memory and Learning")
        print("-" * 50)
        
        # Check what the system learned
        session_summary = await orchestrator.get_session_summary(session_id)
        print(f"Session summary: {json.dumps(session_summary, indent=2)}")
        
        # Simulate learning from tools mentioned
        learning_data = {
            "learned_preferences": {
                "favorite_tools": ["HubSpot", "Salesforce"],
                "user_specific_knowledge": {
                    "considering_crm_switch": True,
                    "current_crm": "HubSpot",
                    "evaluation_crm": "Salesforce"
                }
            }
        }
        
        await orchestrator.user_memory_manager.update_user_memory(user_id, learning_data)
        print("✅ System learned about CRM preferences and stored in user memory")
        
        # Demo 5: Create second session to show memory persistence
        print("\\n🔄 Demo 5: Memory Persistence Across Sessions")
        print("-" * 50)
        
        # Close first session
        await orchestrator.close_session(session_id)
        print("✅ Closed first session")
        
        # Create new session (simulating user returning later)
        session_id2 = await orchestrator.create_personalized_session(
            user_id=user_id,
            agent_id=marketing_agent_id
        )
        print(f"✅ Created new session: {session_id2}")
        
        # New conversation should remember previous context
        print("\\n👤 User: Hi again! I wanted to follow up on our CRM discussion.")
        
        response4 = await orchestrator.process_message(
            session_id2,
            "Hi again! I wanted to follow up on our CRM discussion."
        )
        
        print(f"🤖 {response4['agent_name']}: {response4['response']}")
        print("   ^ Notice how the agent remembers the previous CRM discussion!")
        
        # Demo 6: Multiple agents with different personalities
        print("\\n👥 Demo 6: Multiple Agent Personalities")
        print("-" * 50)
        
        # Create a support agent
        support_agent_id = await orchestrator.create_agent_from_preset(
            user_id=user_id,
            preset_name="support_assistant",
            agent_name="Customer Success Manager"
        )
        print(f"✅ Created support agent: {support_agent_id}")
        
        # Session with support agent
        support_session_id = await orchestrator.create_personalized_session(
            user_id=user_id,
            agent_id=support_agent_id
        )
        
        print("\\n👤 User: How can we improve our customer onboarding process?")
        
        support_response = await orchestrator.process_message(
            support_session_id,
            "How can we improve our customer onboarding process?"
        )
        
        print(f"🤖 {support_response['agent_name']}: {support_response['response']}")
        print("   ^ Notice the different personality and approach!")
        
        # Demo 7: Agent memory comparison
        print("\\n📊 Demo 7: Agent Memory Analysis")
        print("-" * 50)
        
        # Get agent contexts to show different learned information
        marketing_agent = await orchestrator.agent_manager.get_agent_with_context(
            marketing_agent_id, user_id
        )
        support_agent = await orchestrator.agent_manager.get_agent_with_context(
            support_agent_id, user_id
        )
        
        print("Marketing Agent Memory:")
        print(json.dumps(marketing_agent.get("agent_memory_context", {}), indent=2))
        
        print("\\nSupport Agent Memory:")
        print(json.dumps(support_agent.get("agent_memory_context", {}), indent=2))
        
        # Demo complete
        print("\\n🎉 Demo Complete!")
        print("=" * 60)
        print("Key Features Demonstrated:")
        print("✅ Personalized user context and memory")
        print("✅ Agent creation with distinct personalities")
        print("✅ Dynamic context injection in conversations")
        print("✅ Persistent learning and memory updates")
        print("✅ Multi-session memory persistence")
        print("✅ Multiple agents with different approaches")
        print("✅ Secure RLS-based data isolation")
        
        # Cleanup
        await orchestrator.close_session(session_id2)
        await orchestrator.close_session(support_session_id)
        await orchestrator.close()
        await db_manager.close()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔧 Make sure PostgreSQL is running and database is initialized!")
    print("🔧 Run: node scripts/init-database.js (if not already done)")
    print("\\nStarting demo in 3 seconds...")
    
    import time
    time.sleep(3)
    
    asyncio.run(demo_personalized_ai_system())
