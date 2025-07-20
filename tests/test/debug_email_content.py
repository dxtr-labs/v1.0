#!/usr/bin/env python3
"""
Debug email content generation issue
"""

import requests
import json

def debug_email_content_generation():
    """Debug the email content generation issue"""
    print("🔍 DEBUGGING EMAIL CONTENT GENERATION")
    print("=" * 60)
    
    base_url = "http://localhost:8002"
    
    # Login
    print("🔐 Authenticating...")
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "aitest@example.com",
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    print("✅ Authentication successful")
    
    # Test the exact message from the screenshot
    test_message = """I am ceo and my name is Lakshanand Sugumar.We are proteinramen INC and we sell high protein ramen noodles. this is healthy.
Draft a sales pitch email about our company and send to slakshanand1105@gmail.com"""
    
    print(f"\n📧 Testing email content generation...")
    print(f"Request: {test_message}")
    
    try:
        response = requests.post(f"{base_url}/api/chat/mcpai",
            json={"message": test_message},
            headers=headers,
            timeout=30
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"Response Analysis:")
            print(f"   Response Type: {result.get('response_type', 'unknown')}")
            print(f"   Has Workflow JSON: {result.get('hasWorkflowJson', False)}")
            print(f"   Workflow JSON: {result.get('workflow_json', 'None')}")
            print(f"   Automation Type: {result.get('automation_type', 'None')}")
            print(f"   Message Length: {len(result.get('message', ''))}")
            
            print(f"\n📝 Full Response Message:")
            print("-" * 40)
            print(result.get('message', 'No message'))
            print("-" * 40)
            
            # Check if this looks like a proper sales pitch
            message_content = result.get('message', '').lower()
            
            # Look for sales pitch elements
            sales_indicators = [
                'protein', 'ramen', 'noodles', 'healthy', 
                'proteinramen', 'inc', 'lakshanand', 'sugumar',
                'sales', 'pitch', 'company', 'business'
            ]
            
            found_indicators = []
            for indicator in sales_indicators:
                if indicator in message_content:
                    found_indicators.append(indicator)
            
            print(f"\n🔍 Content Analysis:")
            print(f"   Sales indicators found: {found_indicators}")
            print(f"   Proper content generation: {'✅' if len(found_indicators) >= 4 else '❌'}")
            
            # Check if it's just a template response
            template_phrases = [
                'this is regarding',
                'context: no context available',
                'best regards, sam - personal assistant'
            ]
            
            is_template = any(phrase in message_content for phrase in template_phrases)
            print(f"   Template response detected: {'❌ YES' if is_template else '✅ NO'}")
            
            if is_template:
                print(f"\n⚠️ ISSUE IDENTIFIED: Template response instead of custom content")
                return False
            elif len(found_indicators) >= 4:
                print(f"\n✅ Email content generation working properly")
                return True
            else:
                print(f"\n⚠️ Email content may need improvement")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_improved_email_generation():
    """Test with more explicit instructions for better content generation"""
    print(f"\n🔧 TESTING IMPROVED EMAIL GENERATION")
    print("=" * 60)
    
    base_url = "http://localhost:8002"
    
    # Login
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "aitest@example.com",
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    
    # More detailed request
    improved_message = """Please create and send a professional sales pitch email with the following details:

Company: ProteinRamen INC
CEO: Lakshanand Sugumar  
Product: High protein ramen noodles (healthy option)
Recipient: slakshanand1105@gmail.com

The email should include:
- Professional introduction
- Company background and mission
- Product benefits and unique value proposition
- Call to action
- Professional closing

Generate compelling sales content and send the email."""
    
    print(f"📧 Testing improved email generation...")
    print(f"Request: {improved_message[:100]}...")
    
    try:
        response = requests.post(f"{base_url}/api/chat/mcpai",
            json={"message": improved_message},
            headers=headers,
            timeout=35
        )
        
        if response.status_code == 200:
            result = response.json()
            message_content = result.get('message', '')
            
            print(f"\n📝 Improved Response:")
            print("-" * 40)
            print(message_content[:500])
            print("..." if len(message_content) > 500 else "")
            print("-" * 40)
            
            # Check for improvement
            has_company_info = 'proteinramen' in message_content.lower()
            has_ceo_name = 'lakshanand' in message_content.lower()
            has_product_info = 'protein' in message_content.lower() and 'noodles' in message_content.lower()
            has_professional_tone = len(message_content) > 200
            
            print(f"\n✅ Content Quality Check:")
            print(f"   Company info: {'✅' if has_company_info else '❌'}")
            print(f"   CEO name: {'✅' if has_ceo_name else '❌'}")
            print(f"   Product info: {'✅' if has_product_info else '❌'}")
            print(f"   Professional length: {'✅' if has_professional_tone else '❌'}")
            
            improvement_score = sum([has_company_info, has_ceo_name, has_product_info, has_professional_tone])
            print(f"   Overall score: {improvement_score}/4")
            
            return improvement_score >= 3
        else:
            print(f"❌ Improved test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Improved test error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 EMAIL CONTENT GENERATION DEBUG SESSION")
    print("=" * 70)
    
    # Test 1: Debug current issue
    issue_result = debug_email_content_generation()
    
    # Test 2: Try improved approach
    improvement_result = test_improved_email_generation()
    
    print(f"\n🏁 DEBUG RESULTS:")
    print(f"Current email generation: {'✅ WORKING' if issue_result else '❌ NEEDS FIX'}")
    print(f"Improved email generation: {'✅ WORKING' if improvement_result else '❌ NEEDS FIX'}")
    
    if not issue_result:
        print(f"\n🔧 RECOMMENDED FIXES:")
        print(f"1. Check OpenAI prompt engineering for email content")
        print(f"2. Verify context extraction and usage")
        print(f"3. Ensure proper email template generation")
        print(f"4. Test with more detailed instructions")
    else:
        print(f"\n✅ Email content generation is working correctly!")
