import requests
import json

def create_morning_email_automation():
    """
    Create an automation workflow to generate happy morning content and send email
    """
    
    # Step 1: Authenticate
    signup_data = {
        "username": "morninguser",
        "email": "morninguser@example.com", 
        "password": "morning123"
    }
    
    print("🌅 Creating morning automation workflow...")
    
    # Signup (if needed)
    signup_response = requests.post("http://127.0.0.1:8001/api/auth/signup", json=signup_data)
    print(f"Signup Status: {signup_response.status_code}")
    
    # Login
    login_data = {
        "email": "morninguser@example.com",
        "password": "morning123"
    }
    
    login_response = requests.post("http://127.0.0.1:8001/api/auth/login", json=login_data)
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    session_token = login_response.json().get('session_token')
    print(f"✅ Authenticated successfully")
    
    # Step 2: Create morning content generation and email workflow
    workflow_request = {
        "message": f"""
        Create an automation workflow that:
        1. Generates happy, positive morning content with inspirational quotes and good vibes
        2. Sends this content via email to slakshanand1105@gmail.com
        3. Include today's date: July 14, 2025
        4. Make it warm, encouraging, and uplifting
        5. Add some motivational elements for starting the day
        
        The email should have:
        - Subject: "🌅 Good Morning! Your Daily Dose of Positivity - July 14, 2025"
        - Warm greeting
        - Inspirational quote
        - Positive affirmations
        - Have a great day message
        """
    }
    
    # Send to MCP AI
    mcpai_response = requests.post(
        "http://127.0.0.1:8001/api/chat/mcpai",
        json=workflow_request,
        cookies={"session_token": session_token},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"MCP AI Response Status: {mcpai_response.status_code}")
    
    if mcpai_response.status_code == 200:
        response_data = mcpai_response.json()
        print("✅ Morning email automation workflow created!")
        print(f"Response: {response_data.get('message', 'No message')}")
        
        if response_data.get('workflow_json'):
            print("\n📋 Generated Workflow:")
            print(json.dumps(response_data['workflow_json'], indent=2))
            
        print(f"\n📧 Email will be sent to: slakshanand1105@gmail.com")
        print("🌅 Content: Happy morning inspiration for July 14, 2025")
        
        return response_data
    else:
        print(f"❌ Failed to create workflow: {mcpai_response.text}")
        return None

if __name__ == "__main__":
    try:
        result = create_morning_email_automation()
        if result:
            print("\n🎉 Morning email automation successfully set up!")
        else:
            print("\n❌ Failed to set up morning email automation")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Is it running on port 8001?")
    except Exception as e:
        print(f"❌ Error: {e}")
