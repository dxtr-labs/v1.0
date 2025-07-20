import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.mcp.simple_mcp_llm import MCP_LLM_Orchestrator

async def test_ai_sales_pitch():
    """Test the AI sales pitch request that's not working"""
    
    # Initialize the orchestrator
    orchestrator = MCP_LLM_Orchestrator()
    
    # Test the problematic request
    user_message = "Using AI generate a sales pitch for selling healthy ice creams and send to slakshanand1105@gmail.com"
    
    print("🔍 Testing intent analysis...")
    intent_analysis = orchestrator.analyze_user_intent(user_message)
    
    print(f"Primary Intent: {intent_analysis['primary_intent']}")
    print(f"Confidence: {intent_analysis['confidence']}")
    print(f"Extracted Emails: {intent_analysis['extracted_emails']}")
    print(f"Requires AI Service: {intent_analysis['requires_ai_service']}")
    
    print("\n🚀 Testing full workflow processing...")
    try:
        # Test the original request (should prompt for service selection)
        result = await orchestrator.process_user_input("test_user", "test_agent", user_message)
        print(f"Result Status: {result.get('status', 'Unknown')}")
        print(f"Result Message: {result.get('message', 'No message')[:200]}...")
        
        if result.get('ai_service_options'):
            print(f"AI Service Options Available: {len(result['ai_service_options'])}")
        
        print("\n🎯 Testing with AI service specified...")
        # Test with service specified (should work directly)
        user_message_with_service = "service:inhouse Using AI generate a sales pitch for selling healthy ice creams and send to slakshanand1105@gmail.com"
        result2 = await orchestrator.process_user_input("test_user", "test_agent", user_message_with_service)
        print(f"Result Status: {result2.get('status', 'Unknown')}")
        print(f"Result Type: {type(result2)}")
        if 'workflow_steps' in result2:
            print(f"Workflow Steps: {len(result2['workflow_steps'])}")
        if 'message' in result2:
            print(f"Message: {result2['message'][:200]}...")
        
    except Exception as e:
        print(f"Error in workflow processing: {e}")

if __name__ == "__main__":
    asyncio.run(test_ai_sales_pitch())
