#!/usr/bin/env python3
"""
Authenticated User Input Prompt Testing
Handles authentication and tests user prompts
"""

import requests
import json
from test_prompts_collection import PROMPT_CATEGORIES

class AuthenticatedTester:
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
    
    def register_test_user(self):
        """Register a test user"""
        url = f"{self.base_url}/api/auth/signup"
        payload = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        try:
            response = self.session.post(url, json=payload)
            if response.status_code == 200:
                return True, "✅ Test user registered"
            elif response.status_code == 400 and "already exists" in response.text:
                return True, "✅ Test user already exists"
            else:
                return False, f"❌ Registration failed: {response.status_code} - {response.text[:100]}"
        except Exception as e:
            return False, f"❌ Registration error: {str(e)}"
    
    def login_test_user(self):
        """Login with test user"""
        url = f"{self.base_url}/api/auth/login"
        payload = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        try:
            response = self.session.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                session_token = data.get("session_token")
                if session_token:
                    self.session.headers.update({"X-User-ID": str(data.get("user", {}).get("user_id"))})
                    return True, "✅ Login successful"
                else:
                    return False, "❌ No session token received"
            else:
                return False, f"❌ Login failed: {response.status_code} - {response.text[:100]}"
        except Exception as e:
            return False, f"❌ Login error: {str(e)}"
    
    def authenticate(self):
        """Complete authentication process"""
        print("🔐 Authenticating...")
        
        # Try to register (in case user doesn't exist)
        reg_success, reg_msg = self.register_test_user()
        print(f"Registration: {reg_msg}")
        
        # Login
        login_success, login_msg = self.login_test_user()
        print(f"Login: {login_msg}")
        
        return login_success
    
    def test_workflow_generation(self, prompt, category="Test"):
        """Test workflow generation with authenticated session"""
        url = f"{self.base_url}/api/workflow/generate"
        payload = {
            "user_input": prompt,
            "category": category
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                nodes_count = len(data.get('nodes', []))
                return True, f"✅ Generated workflow with {nodes_count} nodes"
            else:
                return False, f"❌ HTTP {response.status_code}: {response.text[:150]}"
        except Exception as e:
            return False, f"❌ Exception: {str(e)}"
    
    def test_chat_endpoint(self, prompt):
        """Test chat endpoint"""
        url = f"{self.base_url}/api/chat/mcpai"
        payload = {"message": prompt}
        
        try:
            response = self.session.post(url, json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                return True, f"✅ Chat response: {response_text[:100]}..."
            else:
                return False, f"❌ HTTP {response.status_code}: {response.text[:150]}"
        except Exception as e:
            return False, f"❌ Exception: {str(e)}"
    
    def run_authenticated_prompt_tests(self):
        """Run authenticated prompt tests"""
        print("🎯 Authenticated User Input Prompt Testing")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot run tests")
            return
        
        print("\n✅ Authentication successful - running prompt tests...")
        print("=" * 70)
        
        # Test prompts
        test_prompts = [
            ("📧 Email", "Send a welcome email to john@example.com"),
            ("✍️ Content", "Generate a blog post about AI automation"),
            ("📊 Data", "Analyze sales data and create monthly report"),
            ("🔄 Complex", "When customer registers, send email and notify team"),
            ("🎯 Simple", "Create an email automation workflow"),
            ("🌍 International", "Send email to user@company.de with pricing")
        ]
        
        results = []
        
        for category, prompt in test_prompts:
            print(f"\n{category}: {prompt}")
            print("-" * 50)
            
            # Test workflow generation
            wf_success, wf_msg = self.test_workflow_generation(prompt, category)
            print(f"Workflow: {wf_msg}")
            
            # Test chat
            chat_success, chat_msg = self.test_chat_endpoint(prompt)
            print(f"Chat: {chat_msg}")
            
            results.append((category, prompt, wf_success, chat_success))
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 AUTHENTICATED TEST RESULTS")
        print("=" * 70)
        
        total_prompts = len(results)
        workflow_successes = sum(1 for _, _, wf, _ in results if wf)
        chat_successes = sum(1 for _, _, _, chat in results if chat)
        
        print(f"Total Prompts: {total_prompts}")
        print(f"✅ Workflow Generation: {workflow_successes}/{total_prompts} ({(workflow_successes/total_prompts)*100:.1f}%)")
        print(f"✅ Chat Processing: {chat_successes}/{total_prompts} ({(chat_successes/total_prompts)*100:.1f}%)")
        
        if workflow_successes > 0 or chat_successes > 0:
            print(f"\n🎉 SUCCESS! The system can process user inputs!")
            print(f"\n📝 Working capabilities:")
            if workflow_successes > 0:
                print(f"   ✅ Workflow Generation: {workflow_successes} prompts succeeded")
            if chat_successes > 0:
                print(f"   ✅ Chat Processing: {chat_successes} prompts succeeded")
            
            print(f"\n🧪 You can now test these {len(PROMPT_CATEGORIES)} categories:")
            for category_name, prompts in PROMPT_CATEGORIES.items():
                print(f"   {category_name}: {len(prompts)} prompts")
        
        return results

def show_all_test_prompts():
    """Show all available test prompts"""
    print(f"\n📚 ALL AVAILABLE TEST PROMPTS:")
    print("=" * 50)
    
    total_prompts = 0
    for category_name, prompts in PROMPT_CATEGORIES.items():
        print(f"\n{category_name} ({len(prompts)} prompts):")
        for i, prompt in enumerate(prompts[:3], 1):  # Show first 3 of each
            print(f"  {i}. {prompt}")
        if len(prompts) > 3:
            print(f"  ... and {len(prompts) - 3} more")
        total_prompts += len(prompts)
    
    print(f"\n💡 Total: {total_prompts} prompts available for testing")
    print(f"📋 Categories: {len(PROMPT_CATEGORIES)} different automation types")

if __name__ == "__main__":
    # Run authenticated tests
    tester = AuthenticatedTester()
    results = tester.run_authenticated_prompt_tests()
    
    # Show available prompts
    show_all_test_prompts()
    
    print(f"\n🎯 MANUAL TESTING INSTRUCTIONS:")
    print("1. Use the working endpoints identified above")
    print("2. Test with prompts from test_prompts_collection.py")
    print("3. Verify the system correctly:")
    print("   - Identifies automation intent (email, content, data, etc.)")
    print("   - Extracts parameters (emails, dates, requirements)")
    print("   - Generates appropriate workflow structures")
    print("4. Check response quality and accuracy")
    
    print(f"\n🔗 Resources:")
    print(f"   - API Documentation: http://localhost:8002/docs")
    print(f"   - All test prompts: python test_prompts_collection.py")
    print(f"   - Local processing test: python test_local_user_inputs.py")
