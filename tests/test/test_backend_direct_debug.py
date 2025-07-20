import asyncio
import aiohttp
import json

async def test_backend_directly():
    """Test the backend API directly to see what it returns"""
    
    url = "http://localhost:8002/api/chat/mcpai"
    
    payload = {
        "message": "draft a sales pitch email for selling products in e commerce and send email to slakshanand1105@gmail.com"
    }
    
    # Add authentication headers to match frontend
    headers = {
        "Content-Type": "application/json",
        "x-user-id": "default_user"  # Use the same header the frontend uses
    }
    
    print("🚀 Testing backend directly...")
    print(f"📤 Request: {json.dumps(payload, indent=2)}")
    print(f"🔑 Headers: {headers}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=30) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Backend Response Status: {response.status}")
                    print(f"📥 Raw Response: {json.dumps(result, indent=2)}")
                    
                    # Check for email preview fields
                    email_fields = {
                        'status': result.get('status'),
                        'email_content': result.get('email_content'),
                        'recipient': result.get('recipient'), 
                        'email_subject': result.get('email_subject'),
                        'action_required': result.get('action_required'),
                        'hasWorkflowJson': result.get('hasWorkflowJson'),
                        'hasWorkflowPreview': result.get('hasWorkflowPreview'),
                        'isEmailPreview': result.get('isEmailPreview')
                    }
                    print(f"🔍 Email Fields Analysis: {json.dumps(email_fields, indent=2)}")
                    
                else:
                    print(f"❌ Backend Error: {response.status}")
                    text = await response.text()
                    print(f"Error Details: {text}")
                    
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_backend_directly())
