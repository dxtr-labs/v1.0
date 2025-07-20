#!/usr/bin/env python3
"""
Test signup with the exact same data as the user but with debug info
"""

import requests
import json

def test_user_signup_debug():
    """Test signup with the exact same data as the user"""
    
    frontend_url = "http://localhost:3002"
    
    # Test with different email since user's might already exist
    test_signup_data = {
        "firstName": "Lakshanand",
        "lastName": "Sugumar", 
        "email": "suguanu24.test@gmail.com",  # Modified to avoid duplicate
        "password": "Lakshu11042005$",
        "confirmPassword": "Lakshu11042005$",
        "isOrganization": False
    }
    
    print("🧪 Testing User's Exact Signup Data...")
    print(f"📤 Sending data: {json.dumps(test_signup_data, indent=2)}")
    
    try:
        response = requests.post(f"{frontend_url}/api/auth/signup", json=test_signup_data, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        try:
            result = response.json()
            print(f"📋 Response Body: {json.dumps(result, indent=2)}")
        except:
            print(f"📋 Raw Response: {response.text}")
            
        # Test with original email to see duplicate error
        print("\n" + "="*50)
        print("🔍 Testing with original email (might be duplicate)...")
        
        original_data = test_signup_data.copy()
        original_data["email"] = "suguanu24@gmail.com"
        
        response2 = requests.post(f"{frontend_url}/api/auth/signup", json=original_data, timeout=30)
        print(f"📊 Original Email Response Status: {response2.status_code}")
        
        try:
            result2 = response2.json()
            print(f"📋 Original Email Response: {json.dumps(result2, indent=2)}")
        except:
            print(f"📋 Original Email Raw Response: {response2.text}")
                    
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_user_signup_debug()
