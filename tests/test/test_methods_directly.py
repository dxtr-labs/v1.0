import sys
sys.path.append('./backend')

# Test our two-part system methods directly
import asyncio
from backend.mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine

async def test_methods_directly():
    """Test our context extraction and automation detection methods directly"""
    
    print("🧪 TESTING TWO-PART SYSTEM METHODS DIRECTLY")
    print("=" * 60)
    
    # Create instance (simplified)
    engine = CustomMCPLLMIterationEngine(
        agent_data={'agent_name': 'Test Agent', 'agent_role': 'Test'},
        openai_api_key='test-key-placeholder'
    )
    
    test_messages = [
        "Hello, my company name is TechCorp Inc and we sell healthy protein noodles. My email is john@techcorp.com",
        "Hi, my company name is TechCorp Inc. Please send an email to customer@example.com about our product launch.",
        "What can you help me with today?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing: {message}")
        
        try:
            # Test context extraction
            print("🧠 Context Extraction:")
            context = await engine._extract_context_information(message)
            print(f"  Context found: {context.get('has_useful_context', False)}")
            if context.get('company_info'):
                print(f"  Company: {context['company_info'].get('company_name', 'None')}")
            
            # Test automation detection  
            print("🤖 Automation Detection:")
            automation = await engine._detect_automation_intent(message, context)
            print(f"  Automation task: {automation.get('has_automation_task', False)}")
            print(f"  Type: {automation.get('automation_type', 'none')}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(test_methods_directly())
