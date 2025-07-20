"""
Usage Example: Building Personalized AI Agents

This example shows how to use the personalized AI agent system in your applications.
Perfect for understanding the API and implementing in your own projects.
"""

import asyncio
import os
from datetime import datetime

async def example_usage():
    """Example of how to use the personalized AI agent system."""
    
    print("📚 Personalized AI Agent System - Usage Example")
    print("=" * 60)
    
    # Step 1: Set up the orchestrator
    print("\n🚀 Step 1: Initialize the System")
    print("-" * 40)
    
    from backend.core.personalized_mcp_orchestrator import PersonalizedMCPOrchestrator
    from backend.db.postgresql_manager import db_manager
    
    # Initialize database manager first to get working config
    await db_manager.initialize()
    
    # Use the same database configuration that works
    orchestrator = PersonalizedMCPOrchestrator(db_manager.connection_config)
    await orchestrator.initialize()
    print("✅ Orchestrator ready")
    
    # Step 2: Create or get a user
    print("\n👤 Step 2: User Setup")
    print("-" * 40)
    
    await db_manager.initialize()
    
    # Create a test user (in real app, this comes from authentication)
    user_email = "example@company.com"
    user_password = "password123"
    
    try:
        user_id = await db_manager.create_user(
            email=user_email,
            password=user_password,
            username="ExampleUser"
        )
        print(f"✅ Created new user: {user_id}")
    except:
        # User exists, authenticate instead
        user = await db_manager.authenticate_user(user_email, user_password)
        user_id = user["user_id"]
        print(f"✅ Using existing user: {user_id}")
    
    # Step 3: Set up user memory with company context
    print("\n🧠 Step 3: User Memory Setup")
    print("-" * 40)
    
    # Initialize user memory with company information
    company_profile = {
        "company_name": "InnovateTech Solutions",
        "industry": "Software Development",
        "role": "Product Manager",
        "team_size": "25-50",
        "primary_goals": ["product development", "user experience", "market growth"]
    }
    
    await orchestrator.user_memory_manager.initialize_user_memory(user_id, company_profile)
    print("✅ User memory initialized with company context")
    
    # Step 4: Create specialized agents
    print("\n🤖 Step 4: Create Specialized Agents")
    print("-" * 40)
    
    # Create a marketing agent using preset
    marketing_agent_id = await orchestrator.create_agent_from_preset(
        user_id=user_id,
        preset_name="marketing_maestro",
        agent_name="Marketing Expert"
    )
    print(f"✅ Marketing agent created: {marketing_agent_id}")
    
    # Create a custom technical advisor agent
    tech_agent = await orchestrator.agent_manager.create_personalized_agent(
        user_id=user_id,
        agent_name="Technical Advisor",
        agent_role="Senior Software Architect",
        agent_personality="Detail-oriented, analytical, enjoys solving complex technical problems with clear explanations",
        agent_expectations="Provide technical guidance, code reviews, architecture decisions, and development best practices"
    )
    tech_agent_id = tech_agent["agent_id"]
    print(f"✅ Technical advisor created: {tech_agent_id}")
    
    # Step 5: Have personalized conversations
    print("\n💬 Step 5: Personalized Conversations")
    print("-" * 40)
    
    # Marketing conversation
    print("\\n📈 Marketing Agent Conversation:")
    marketing_session = await orchestrator.create_personalized_session(
        user_id=user_id,
        agent_id=marketing_agent_id
    )
    
    marketing_response = await orchestrator.process_message(
        session_id=marketing_session,
        user_message="We're launching a new SaaS product for small businesses. What marketing strategy would you recommend?"
    )
    
    print(f"🤖 {marketing_response['agent_name']}: {marketing_response['response']}")
    
    # Technical conversation
    print("\\n⚡ Technical Agent Conversation:")
    tech_session = await orchestrator.create_personalized_session(
        user_id=user_id,
        agent_id=tech_agent_id
    )
    
    tech_response = await orchestrator.process_message(
        session_id=tech_session,
        user_message="We need to scale our API to handle 10x more traffic. What architecture changes would you suggest?"
    )
    
    print(f"🤖 {tech_response['agent_name']}: {tech_response['response']}")
    
    # Step 6: Demonstrate learning and memory
    print("\n🎓 Step 6: Learning and Memory Updates")
    print("-" * 40)
    
    # Update user memory with new information learned from conversation
    learned_info = {
        "context_memory": {
            "current_projects": ["SaaS product launch", "API scaling project"],
            "recent_challenges": ["traffic scaling", "market positioning"]
        },
        "learned_preferences": {
            "favorite_tools": ["AWS", "Docker", "React"],
            "communication_style": "technical but accessible"
        }
    }
    
    await orchestrator.user_memory_manager.update_user_memory(user_id, learned_info)
    print("✅ User memory updated with learned information")
    
    # Update agent memory with interaction insights
    agent_learning = {
        "learned_preferences": {
            "user_specific_knowledge": {
                "technical_level": "senior",
                "prefers_detailed_explanations": True,
                "focuses_on_scalability": True
            }
        },
        "conversation_topics": ["API scaling", "SaaS marketing", "architecture design"]
    }
    
    await orchestrator.agent_manager.update_agent_memory(tech_agent_id, user_id, agent_learning)
    print("✅ Agent memory updated with interaction insights")
    
    # Step 7: Demonstrate memory persistence
    print("\n🔄 Step 7: Memory Persistence Demo")
    print("-" * 40)
    
    # Close current session
    await orchestrator.close_session(tech_session)
    
    # Start new session (simulating user returning later)
    new_session = await orchestrator.create_personalized_session(
        user_id=user_id,
        agent_id=tech_agent_id
    )
    
    # Agent should remember previous context
    memory_response = await orchestrator.process_message(
        session_id=new_session,
        user_message="Following up on our scaling discussion - what's the first step you'd recommend?"
    )
    
    print(f"🤖 {memory_response['agent_name']}: {memory_response['response']}")
    print("   ^ Notice how the agent remembers our previous conversation!")
    
    # Step 8: API-style usage (how frontend would interact)
    print("\n🌐 Step 8: API-Style Usage Example")
    print("-" * 40)
    
    # Simulate what a frontend application would do
    def simulate_api_call(endpoint, data):
        """Simulate an API call that a frontend would make."""
        print(f"POST {endpoint}")
        print(f"Data: {data}")
        return {"status": "success", "data": "simulated_response"}
    
    # Create agent via API
    create_agent_request = {
        "agent_name": "Sales Assistant",
        "preset_name": "support_assistant",
        "customizations": {
            "agent_personality": "Friendly, persuasive, customer-focused with strong sales acumen"
        }
    }
    simulate_api_call("/api/personalized-ai/agents", create_agent_request)
    
    # Start session via API
    start_session_request = {
        "agent_id": marketing_agent_id,
        "session_context": {"channel": "web_app", "user_intent": "product_launch"}
    }
    simulate_api_call("/api/personalized-ai/sessions", start_session_request)
    
    # Send message via API
    send_message_request = {
        "session_id": "session_123",
        "message": "Help me create a launch plan for our new product",
        "extract_learnings": True
    }
    simulate_api_call("/api/personalized-ai/messages", send_message_request)
    
    print("✅ API usage patterns demonstrated")
    
    # Step 9: Advanced features
    print("\n⚡ Step 9: Advanced Features")
    print("-" * 40)
    
    # Get user context for dashboard display
    user_context = await orchestrator.user_memory_manager.get_user_context(user_id)
    memory = user_context.get("memory_context", {})
    
    print("User Profile Summary:")
    profile = memory.get("user_profile", {})
    print(f"  Company: {profile.get('company_name', 'N/A')}")
    print(f"  Industry: {profile.get('industry', 'N/A')}")
    print(f"  Role: {profile.get('role', 'N/A')}")
    
    # Get all user agents
    user_agents = await orchestrator.agent_manager.get_user_agents(user_id)
    print(f"\\nUser has {len(user_agents)} agents:")
    for agent in user_agents:
        print(f"  • {agent['agent_name']} ({agent['agent_role']})")
    
    # Generate context prompt (what gets injected into AI)
    context_prompt = await orchestrator.user_memory_manager.generate_context_prompt(user_id)
    print(f"\\nContext injected into AI: {context_prompt}")
    
    # Step 10: Cleanup
    print("\n🧹 Step 10: Cleanup")
    print("-" * 40)
    
    await orchestrator.close_session(marketing_session)
    await orchestrator.close_session(new_session)
    await orchestrator.close()
    await db_manager.close()
    
    print("✅ All resources cleaned up")
    
    # Summary
    print("\n🎯 Usage Example Complete!")
    print("=" * 60)
    print("This example demonstrated:")
    print("  1. System initialization and setup")
    print("  2. User memory management with company context")
    print("  3. Creating agents with presets and custom configs")
    print("  4. Personalized conversations with context injection")
    print("  5. Learning and memory updates")
    print("  6. Memory persistence across sessions")
    print("  7. API-style interaction patterns")
    print("  8. Advanced context and agent management")
    print("  9. Proper resource cleanup")
    print("")
    print("🚀 Ready to integrate into your application!")

if __name__ == "__main__":
    print("🔧 Ensure database is initialized and running")
    print("🔧 This is a demonstration - adapt for your needs")
    print("")
    
    asyncio.run(example_usage())
