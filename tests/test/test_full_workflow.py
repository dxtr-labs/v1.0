import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.mcp.simple_mcp_llm import MCP_LLM_Orchestrator

async def test_full_workflow():
    """Test the complete AI workflow with all steps"""
    
    # Initialize the orchestrator
    orchestrator = MCP_LLM_Orchestrator()
    
    print("🎯 Testing complete AI workflow...")
    
    # Test with service specified (should work directly)
    user_message_with_service = "service:inhouse Using AI generate a sales pitch for selling healthy ice creams and send to slakshanand1105@gmail.com"
    result = await orchestrator.process_user_input("test_user", "test_agent", user_message_with_service)
    
    print(f"Result Status: {result.get('status', 'Unknown')}")
    
    if result.get('workflow_steps'):
        print(f"✅ Workflow generated with {len(result['workflow_steps'])} steps:")
        for i, step in enumerate(result['workflow_steps'], 1):
            print(f"  Step {i}: {step.get('node', 'Unknown')} - {step.get('description', 'No description')}")
    
    if result.get('message'):
        print(f"📝 Message: {result['message']}")
    
    if result.get('estimated_cost'):
        print(f"💰 Estimated Cost: {result['estimated_cost']} credits")
    
    print(f"\n📊 Full result keys: {list(result.keys())}")

if __name__ == "__main__":
    asyncio.run(test_full_workflow())
