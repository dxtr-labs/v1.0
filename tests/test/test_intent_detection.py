import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine

async def test_intent_detection():
    """Test the OpenAI intent detection directly"""
    
    # Initialize the orchestrator
    orchestrator = CustomMCPLLMIterationEngine(agent_id="test_agent")
    
    # Test cases
    test_cases = [
        "Draft a sales pitch email about our company and send to slakshanand1105@gmail.com",
        "Using AI generate a sales pitch for selling healthy ice creams and send to slakshanand1105@gmail.com",
        "compose an email about protein ramen and email it to the user",
        "search for top investors in food industry",
        "hello how are you today"
    ]
    
    for test_input in test_cases:
        print(f"\n🔍 Testing: '{test_input}'")
        print("-" * 50)
        
        # Call the intent detection method directly
        result = await orchestrator._openai_intent_detection(test_input)
        
        print(f"Is Automation: {result.get('is_automation', 'Unknown')}")
        print(f"Automation Type: {result.get('automation_type', 'Unknown')}")
        print(f"Confidence: {result.get('confidence', 'Unknown')}")
        print(f"Reasoning: {result.get('reasoning', 'Unknown')}")
        print(f"Full Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_intent_detection())
