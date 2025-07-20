#!/usr/bin/env python3

"""
FINAL DIAGNOSIS TEST
This test will definitively determine what's wrong with the OpenAI integration
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment like the backend
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, 'backend', '.env'))

async def test_exact_backend_flow():
    """Test the exact flow that should happen in the backend"""
    
    print("🔬 FINAL DIAGNOSIS: Backend OpenAI Flow Test")
    print("=" * 50)
    
    # Step 1: Check OpenAI availability (exactly like backend)
    HAS_OPENAI = False
    try:
        import openai
        from openai import AsyncOpenAI
        HAS_OPENAI = True
        print("✅ Step 1: OpenAI package imported successfully")
    except ImportError:
        print("❌ Step 1: OpenAI package import failed")
        return
    
    # Step 2: Check API key (exactly like backend)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    print(f"✅ Step 2: API key loaded ({len(openai_api_key) if openai_api_key else 0} chars)")
    
    if not openai_api_key:
        print("❌ Step 2: No API key available")
        return
    
    # Step 3: Test the exact conversational response logic
    print("\n🧪 Step 3: Testing conversational response generation...")
    
    user_input = "hello"
    agent_name = "testbot"
    agent_role = "Personal Assistant"
    
    try:
        client = AsyncOpenAI(api_key=openai_api_key)
        print("✅ Step 3a: AsyncOpenAI client created")
        
        # Use the exact prompt from the backend
        prompt = f"""You are {agent_name}, a {agent_role} from DXTR Labs.

DXTR Labs Company Context:
- We create AI-powered digital employees that automate real business tasks
- Unlike basic chatbots, our agents combine conversation with real action
- We specialize in email automation, data processing, and workflow creation
- Our digital employees work 24/7 and learn user preferences

Your personality should be:
- Friendly and conversational (avoid corporate descriptions)
- Enthusiastic about helping with automation
- Focus on what you can DO for the user, not just company facts
- Be natural and engaging, like a helpful colleague
- When greeting users, be welcoming but focus on how you can help

User message: "{user_input}"

Provide a natural, conversational response that:
- Greets the user warmly if it's a greeting
- Asks how you can help with their automation needs
- Shows enthusiasm for digital employee solutions
- Stays conversational, not corporate-sounding
- Offers to help with specific automation tasks
- Avoids just listing company facts unless directly asked

Keep the response friendly, helpful, and focused on the user's needs."""

        print("✅ Step 3b: Prompt prepared")
        
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are {agent_name}, a {agent_role} from DXTR Labs. You're a helpful digital employee who loves automation and making people's work easier. Be conversational, friendly, and focus on how you can help users with their automation needs. Avoid just reciting company facts - instead, be engaging and offer specific help."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        ai_response = response.choices[0].message.content.strip()
        print("✅ Step 3c: OpenAI API call successful!")
        print(f"\n🎯 RESULT: OpenAI Response ({len(ai_response)} chars):")
        print("-" * 40)
        print(ai_response)
        print("-" * 40)
        
        # Analyze the response
        if len(ai_response) > 64 and "Let me help you create an automation" not in ai_response:
            print("\n🎉 SUCCESS: This is a proper OpenAI conversational response!")
            print("✅ The OpenAI integration logic is working correctly")
            print("❗ Issue must be in the backend routing/exception handling")
        else:
            print("\n🤔 UNEXPECTED: Response seems generic or too short")
            
    except Exception as e:
        print(f"❌ Step 3: OpenAI API call failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_exact_backend_flow())
