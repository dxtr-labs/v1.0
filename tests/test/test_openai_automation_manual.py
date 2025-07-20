"""
Manual OpenAI Test for Automation Detection
Test OpenAI directly to see what it's returning
"""
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')
load_dotenv('backend/.env.local')

def test_openai_automation_detection():
    """Test OpenAI automation detection manually"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OpenAI API key found")
        return
    
    print(f"✅ OpenAI API key found: {api_key[:20]}...")
    
    client = OpenAI(api_key=api_key)
    
    # Test message
    test_message = "Send email to slakshanand1105@gmail.com about TechCorp services"
    
    print(f"\n🧪 Testing message: {test_message}")
    
    # System prompt (same as in the backend)
    system_prompt = """You are an automation task detector. Determine if the user wants to perform a specific AUTOMATION ACTION, separate from just providing information.

AUTOMATION TASKS (require action):
- "send email to...", "draft email and send...", "email someone about..."
- "create automation for...", "set up workflow to..."
- "fetch data from...", "scrape website...", "get information from..."
- "schedule task...", "automate daily...", "set up recurring..."

NOT AUTOMATION TASKS (just information/context):
- "company name is...", "our business is...", "we sell..."
- "my email is...", "contact me at...", "I work at..."
- General questions, greetings, explanations
- Providing context without requesting action

OUTPUT FORMAT (JSON only):
{
  "has_automation_task": true/false,
  "automation_type": "email_automation|data_fetching|workflow_creation|scheduling|none",
  "specific_action": "string describing the specific action requested",
  "action_verbs": ["list of action verbs found"],
  "target_recipient": "email address if found",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}"""

    user_prompt = f"Analyze this message for automation tasks:\n\n'{test_message}'"
    
    try:
        print(f"\n🤖 Calling OpenAI...")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=300
        )
        
        content = response.choices[0].message.content.strip()
        print(f"\n📋 Raw OpenAI Response:")
        print(content)
        
        try:
            result = json.loads(content)
            print(f"\n✅ Parsed JSON Result:")
            print(json.dumps(result, indent=2))
            
            print(f"\n🎯 Analysis:")
            print(f"   Has Automation Task: {result.get('has_automation_task')}")
            print(f"   Automation Type: {result.get('automation_type')}")
            print(f"   Target Recipient: {result.get('target_recipient')}")
            print(f"   Confidence: {result.get('confidence')}")
            print(f"   Reasoning: {result.get('reasoning')}")
            
            if result.get('has_automation_task'):
                print(f"\n✅ AUTOMATION SHOULD BE DETECTED!")
            else:
                print(f"\n❌ OpenAI says no automation task")
                
        except json.JSONDecodeError:
            print(f"\n❌ Failed to parse JSON response")
            
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")

if __name__ == "__main__":
    test_openai_automation_detection()
    
    print(f"\n💡 This test shows what OpenAI automation detection is returning")
    print(f"If it detects automation but the backend doesn't create workflows,")
    print(f"the issue is in the workflow generation logic, not detection.")
