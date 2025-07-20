import os
import sys
sys.path.insert(0, 'backend')

# Load the .env file like the backend does
from dotenv import load_dotenv
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, 'backend', '.env'))

print("🔍 DIRECT OPENAI TEST")
print("=" * 40)

# Check OpenAI API key
openai_key = os.getenv("OPENAI_API_KEY")
print(f"OpenAI API Key: {openai_key[:20] + '...' if openai_key else 'NOT FOUND'}")
print(f"Key length: {len(openai_key) if openai_key else 0}")

# Test OpenAI import and API call
try:
    import openai
    from openai import AsyncOpenAI
    print("✅ OpenAI package import successful")
    
    if openai_key:
        print("\n🧪 Testing direct OpenAI API call...")
        client = openai.OpenAI(api_key=openai_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello in a friendly way."}
            ],
            temperature=0.7,
            max_tokens=50
        )
        
        print(f"✅ OpenAI API call successful!")
        print(f"Response: {response.choices[0].message.content}")
    else:
        print("❌ No API key available for direct test")
        
except Exception as e:
    print(f"❌ OpenAI test failed: {e}")
    import traceback
    traceback.print_exc()
