#!/usr/bin/env python3
"""
Debug pattern detection directly
"""
import asyncio
import sys
import os

# Add backend path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_pattern_detection():
    """Test the pattern detection function directly"""
    print("🔍 TESTING PATTERN DETECTION DIRECTLY")
    print("=" * 50)
    
    # Import the class
    from backend.mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine
    
    # Create instance
    processor = CustomMCPLLMIterationEngine("test_agent", openai_api_key="invalid_key")
    
    test_messages = [
        "create a sales pitch email for selling healthy protein bars and send email to slakshanand1105@gmail.com",
        "draft a professional welcome email for new customers and send to slakshanand1105@gmail.com",
        "compose a business proposal about AI solutions and send to slakshanand1105@gmail.com",
        "how are you doing today?",
        "send email to test@example.com"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n🧪 TEST {i}: {message}")
        print("-" * 40)
        
        # Test pattern detection directly
        result = await processor._enhanced_pattern_detection(message)
        
        print(f"Is Automation: {result.get('is_automation')}")
        print(f"Type: {result.get('automation_type')}")
        print(f"Confidence: {result.get('confidence')}")
        print(f"Email: {result.get('detected_email')}")
        print(f"Content Type: {result.get('content_type')}")
        print(f"Reasoning: {result.get('reasoning')}")

if __name__ == "__main__":
    asyncio.run(test_pattern_detection())
