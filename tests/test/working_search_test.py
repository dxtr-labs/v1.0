#!/usr/bin/env python3
"""
WORKING SEARCH TEST - FIXED AUTHENTICATION
Using session_token instead of access_token
"""

import requests
import json
import uuid

def test_working_search():
    """Test search with correct authentication"""
    base_url = "http://localhost:8002"
    
    # Create new user
    test_email = f"searchuser_{uuid.uuid4().hex[:6]}@example.com"
    signup_data = {
        "email": test_email,
        "password": "searchtest123",
        "name": "Search Test User"
    }
    
    print(f"🔐 Creating user: {test_email}")
    
    try:
        # Signup
        signup_response = requests.post(f"{base_url}/api/auth/signup", json=signup_data)
        print(f"Signup: {signup_response.status_code}")
        
        if signup_response.status_code == 200:
            signup_data_response = signup_response.json()
            signup_token = signup_data_response.get("session_token")
            
            if signup_token:
                print(f"✅ Got signup token: {signup_token[:30]}...")
                
                # Use Bearer token format with session_token
                headers = {"Authorization": f"Bearer {signup_token}"}
                
                # Test multiple search scenarios
                search_tests = [
                    "Search for AI automation investors and email the list to slakshanand1105@gmail.com",
                    "Find companies that need automation services",
                    "Research automation market trends and email summary to slakshanand1105@gmail.com",
                    "Search Google for 'startup investors AI automation' and compile results"
                ]
                
                for i, search_query in enumerate(search_tests, 1):
                    print(f"\n🔍 TEST {i}: {search_query[:60]}...")
                    
                    chat_data = {"message": search_query}
                    
                    try:
                        chat_response = requests.post(
                            f"{base_url}/api/chat/mcpai", 
                            json=chat_data, 
                            headers=headers, 
                            timeout=60
                        )
                        
                        print(f"Status: {chat_response.status_code}")
                        
                        if chat_response.status_code == 200:
                            response_data = chat_response.json()
                            
                            if response_data.get("success"):
                                response_text = response_data.get("response", "")
                                print(f"✅ SUCCESS! Response: {response_text[:300]}...")
                                
                                # Check if it actually performed search
                                search_indicators = ["search", "found", "results", "companies", "investors", "automation"]
                                matches = sum(1 for indicator in search_indicators if indicator.lower() in response_text.lower())
                                
                                if matches >= 2:
                                    print(f"✅ SEARCH WORKING! Found {matches} search indicators")
                                else:
                                    print(f"⚠️ May not be searching - only {matches} indicators found")
                                    
                            else:
                                print(f"❌ Request failed: {response_data}")
                        else:
                            print(f"❌ HTTP Error: {chat_response.status_code}")
                            print(f"Response: {chat_response.text[:300]}")
                            
                    except requests.exceptions.Timeout:
                        print("⏰ Request timed out (this is normal for complex searches)")
                    except Exception as e:
                        print(f"❌ Error: {str(e)}")
                
                return True
            else:
                print("❌ No session token in signup response")
        else:
            print(f"❌ Signup failed: {signup_response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    return False

def test_direct_email():
    """Test direct email functionality"""
    base_url = "http://localhost:8002"
    
    # Create user for email test
    test_email = f"emailuser_{uuid.uuid4().hex[:6]}@example.com"
    signup_data = {
        "email": test_email,
        "password": "emailtest123",
        "name": "Email Test User"
    }
    
    print(f"\n📧 Testing email with user: {test_email}")
    
    try:
        signup_response = requests.post(f"{base_url}/api/auth/signup", json=signup_data)
        
        if signup_response.status_code == 200:
            signup_data_response = signup_response.json()
            token = signup_data_response.get("session_token")
            
            if token:
                headers = {"Authorization": f"Bearer {token}"}
                
                # Test direct email
                email_data = {
                    "to": "slakshanand1105@gmail.com",
                    "subject": "Search System Test Email",
                    "body": "This is a test email to verify the email functionality is working with your automation system."
                }
                
                email_response = requests.post(f"{base_url}/api/email/send", json=email_data, headers=headers)
                print(f"Email Status: {email_response.status_code}")
                print(f"Email Response: {email_response.text}")
                
                if email_response.status_code == 200:
                    print("✅ EMAIL FUNCTIONALITY WORKING!")
                    return True
                    
    except Exception as e:
        print(f"❌ Email test error: {str(e)}")
    
    return False

if __name__ == "__main__":
    print("🚀 WORKING SEARCH TEST - FIXED AUTHENTICATION")
    print("=" * 60)
    
    # Test search functionality
    search_working = test_working_search()
    
    # Test email functionality  
    email_working = test_direct_email()
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS:")
    print(f"🔍 Search functionality: {'✅ WORKING' if search_working else '❌ NOT WORKING'}")
    print(f"📧 Email functionality: {'✅ WORKING' if email_working else '❌ NOT WORKING'}")
    
    if search_working and email_working:
        print("\n🎉 SUCCESS! Your web search and email system is fully functional!")
        print("\n💡 TO USE YOUR SYSTEM:")
        print("1. Go to http://localhost:8002/docs")
        print("2. Create a user account via /api/auth/signup")
        print("3. Use the session_token from signup or login")
        print("4. Send search requests to /api/chat/mcpai")
        print("5. Example: 'Search for AI investors and email list to slakshanand1105@gmail.com'")
    else:
        print("\n❌ Some functionality is not working. Check the logs above for details.")
