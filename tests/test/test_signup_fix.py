#!/usr/bin/env python3
"""
Test the signup functionality with the correct field mapping
"""

import requests
import json

def test_signup_fix():
    """Test the signup API with the corrected field mapping"""
    
    frontend_url = "http://localhost:3002"
    
    try:
        # Test signup with the exact same data structure as the frontend
        signup_data = {
            "firstName": "Lakshanand",
            "lastName": "Sugumar", 
            "email": "test.signup.fix3@example.com",  # Using a different test email
            "password": "TestPass123$",
            "confirmPassword": "TestPass123$",
            "isOrganization": False
        }
        
        print("🧪 Testing Signup API Fix...")
        print(f"📤 Sending data: {json.dumps(signup_data, indent=2)}")
        
        response = requests.post(f"{frontend_url}/api/auth/signup", json=signup_data, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Signup completed successfully!")
            print(f"📋 Response: {json.dumps(result, indent=2)}")
            
        elif response.status_code == 400:
            result = response.json()
            print(f"❌ Bad Request (400): {result.get('error', 'Unknown error')}")
            print(f"📋 Full response: {json.dumps(result, indent=2)}")
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            try:
                result = response.json()
                print(f"📋 Error response: {json.dumps(result, indent=2)}")
            except:
                print(f"📋 Raw response: {response.text}")
                    
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_signup_fix()
