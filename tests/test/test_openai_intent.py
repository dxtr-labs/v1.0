#!/usr/bin/env python3
"""
Test OpenAI Intent Detection directly
"""
import asyncio
import os
from dotenv import load_dotenv

async def test_openai_intent():
    """Test OpenAI intent detection directly"""
    print("🤖 TESTING OPENAI INTENT DETECTION")
    print("=" * 50)
    
    load_dotenv('.env.local')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_key:
        print("❌ No OpenAI API key found!")
        return
    
    print(f"✅ OpenAI API Key: {openai_key[:20]}...")
    
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=openai_key)
        
        test_messages = [
            "create a sales pitch email for selling healthy protein bars and send email to slakshanand1105@gmail.com",
            "draft a professional welcome email for new customers and send to slakshanand1105@gmail.com",
            "how are you doing today?",
            "what can you help me with?"
        ]
        
        system_prompt = """You are an expert automation intent classifier. Analyze user messages and determine if they want to create an automation or just have a conversation.

AUTOMATION INDICATORS:
- Email automation: "send email", "draft email", "email someone", "compose email"
- Content creation: "write", "draft", "create", "generate", "compose" + sending
- Data fetching: "fetch", "get data", "scrape", "retrieve from website"
- Workflow creation: "automate", "create workflow", "build automation"
- Scheduling: "schedule", "recurring", "daily", "weekly"

CONVERSATIONAL INDICATORS:
- Questions: "how are you", "what can you do", "help me understand"
- Greetings: "hi", "hello", "hey", "good morning"
- General chat: casual conversation without action requests

OUTPUT FORMAT (JSON only):
{
  "is_automation": true/false,
  "automation_type": "email_automation|content_creation|data_fetching|workflow|scheduling|none",
  "confidence": 0.0-1.0,
  "detected_email": "email@example.com or null",
  "content_type": "sales_pitch|report|proposal|email|none",
  "action_verbs": ["send", "create", "write"],
  "reasoning": "brief explanation of classification"
}"""
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n🧪 TEST {i}: {message}")
            print("-" * 40)
            
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Classify this user message:\n\n'{message}'"}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            print(f"🤖 OpenAI Response:")
            print(content)
            
            try:
                import json
                result = json.loads(content)
                print(f"\n✅ Parsed Result:")
                print(f"   Is Automation: {result.get('is_automation')}")
                print(f"   Type: {result.get('automation_type')}")
                print(f"   Confidence: {result.get('confidence')}")
                print(f"   Email: {result.get('detected_email')}")
                print(f"   Content Type: {result.get('content_type')}")
            except json.JSONDecodeError:
                print("❌ Failed to parse JSON")
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_openai_intent())
