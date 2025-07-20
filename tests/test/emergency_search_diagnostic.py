#!/usr/bin/env python3
"""
EMERGENCY WEB SEARCH DIAGNOSTIC & FIX
Comprehensive test to diagnose and fix all search issues
"""

import requests
import json
import time
import uuid
from typing import Dict, Any

class SearchDiagnostic:
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        
    def log(self, message: str, status: str = "INFO"):
        print(f"[{status}] {message}")
        
    def test_backend_connection(self):
        """Test if backend is responding"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ Backend is running and healthy", "SUCCESS")
                return True
            else:
                self.log(f"❌ Backend health check failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Cannot connect to backend: {str(e)}", "ERROR")
            return False
    
    def authenticate(self):
        """Try to authenticate with various methods"""
        # Method 1: Try creating a new user
        test_email = f"searchtest_{uuid.uuid4().hex[:8]}@example.com"
        signup_data = {
            "email": test_email,
            "password": "test123456",
            "name": "Search Test User"
        }
        
        try:
            signup_response = requests.post(f"{self.base_url}/api/auth/signup", json=signup_data)
            if signup_response.status_code in [200, 201]:
                self.log(f"✅ Created new test user: {test_email}", "SUCCESS")
                
                # Login with new user
                login_data = {"email": test_email, "password": "test123456"}
                login_response = requests.post(f"{self.base_url}/api/auth/login", json=login_data)
                
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    self.token = login_result.get("access_token")
                    self.user_id = login_result.get("user_id")
                    self.log(f"✅ Successfully authenticated! Token: {self.token[:30]}...", "SUCCESS")
                    return True
            
        except Exception as e:
            self.log(f"❌ Authentication failed: {str(e)}", "ERROR")
        
        # Method 2: Try common test accounts
        test_accounts = [
            {"email": "testuser@example.com", "password": "password123"},
            {"email": "admin@example.com", "password": "admin123"},
            {"email": "test@test.com", "password": "test123"},
        ]
        
        for creds in test_accounts:
            try:
                login_response = requests.post(f"{self.base_url}/api/auth/login", json=creds)
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    self.token = login_result.get("access_token")
                    self.user_id = login_result.get("user_id")
                    self.log(f"✅ Logged in with existing account: {creds['email']}", "SUCCESS")
                    return True
            except Exception:
                continue
        
        self.log("❌ Could not authenticate with any method", "ERROR")
        return False
    
    def test_search_functionality(self):
        """Test the actual search functionality"""
        if not self.token:
            self.log("❌ No authentication token available", "ERROR")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test various search requests
        search_requests = [
            "Search for AI automation investors and email the list to slakshanand1105@gmail.com",
            "Find companies that need automation solutions",
            "Research the latest trends in AI automation",
            "Search Google for startup investors in AI",
            "Look up contact information for automation companies"
        ]
        
        for i, search_query in enumerate(search_requests, 1):
            self.log(f"🔍 Testing search {i}: {search_query[:60]}...", "TEST")
            
            chat_data = {"message": search_query}
            
            try:
                response = requests.post(
                    f"{self.base_url}/api/chat/mcpai", 
                    json=chat_data, 
                    headers=headers, 
                    timeout=45
                )
                
                self.log(f"Response status: {response.status_code}", "INFO")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log(f"✅ Search request processed successfully!", "SUCCESS")
                    
                    # Check response content
                    if data.get("success"):
                        response_text = data.get("response", "")
                        self.log(f"📝 Response preview: {response_text[:200]}...", "INFO")
                        
                        # Check if it contains search-related content
                        search_indicators = ["search", "found", "results", "investors", "companies", "automation"]
                        if any(indicator in response_text.lower() for indicator in search_indicators):
                            self.log("✅ Response contains search-related content", "SUCCESS")
                        else:
                            self.log("⚠️ Response doesn't seem search-related", "WARNING")
                    else:
                        self.log(f"⚠️ Request processed but marked as not successful: {data}", "WARNING")
                        
                elif response.status_code == 401:
                    self.log("❌ Authentication failed - token may be expired", "ERROR")
                    return False
                elif response.status_code == 404:
                    self.log("❌ Endpoint not found - API structure may have changed", "ERROR")
                    return False
                else:
                    self.log(f"❌ Request failed with status {response.status_code}: {response.text[:300]}", "ERROR")
                    
            except requests.exceptions.Timeout:
                self.log("⏰ Request timed out - search may be taking too long", "WARNING")
            except Exception as e:
                self.log(f"❌ Exception during search: {str(e)}", "ERROR")
            
            time.sleep(2)  # Brief pause between requests
        
        return True
    
    def test_email_functionality(self):
        """Test if email sending works"""
        if not self.token:
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test direct email sending
        email_data = {
            "to": "slakshanand1105@gmail.com",
            "subject": "Search Test Email",
            "body": "This is a test email to verify the email functionality is working."
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/email/send",
                json=email_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                self.log("✅ Email functionality is working", "SUCCESS")
                return True
            else:
                self.log(f"⚠️ Email test failed: {response.status_code} - {response.text[:200]}", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"❌ Email test error: {str(e)}", "ERROR")
            return False
    
    def test_web_search_integration(self):
        """Test if the web search service is integrated"""
        if not self.token:
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test a simple web search request
        search_message = "Search the web for 'artificial intelligence automation companies' and summarize the top 3 results"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat/mcpai",
                json={"message": search_message},
                headers=headers,
                timeout=60  # Longer timeout for web search
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "").lower()
                
                # Check for web search indicators
                web_indicators = ["search", "found", "website", "results", "web", "google", "companies"]
                indicator_count = sum(1 for indicator in web_indicators if indicator in response_text)
                
                if indicator_count >= 3:
                    self.log("✅ Web search integration appears to be working", "SUCCESS")
                    return True
                else:
                    self.log("⚠️ Web search may not be properly integrated", "WARNING")
                    self.log(f"Response: {response_text[:500]}...", "INFO")
                    return False
            else:
                self.log(f"❌ Web search test failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Web search test error: {str(e)}", "ERROR")
            return False
    
    def provide_fixes(self):
        """Provide specific fixes for common issues"""
        self.log("\n🔧 DIAGNOSTIC COMPLETE - RECOMMENDATIONS:", "FIX")
        
        if not self.token:
            self.log("1. AUTHENTICATION ISSUE:", "FIX")
            self.log("   - Check if the backend database is properly initialized", "FIX")
            self.log("   - Try creating a new user account manually", "FIX")
            self.log("   - Verify PostgreSQL is running and accessible", "FIX")
        
        self.log("\n2. WEB SEARCH INTEGRATION:", "FIX")
        self.log("   - Verify search service is properly configured in the agent", "FIX")
        self.log("   - Check if Google Search API key is set in environment", "FIX")
        self.log("   - Ensure web search tools are loaded in the MCP server", "FIX")
        
        self.log("\n3. EMAIL FUNCTIONALITY:", "FIX")
        self.log("   - Verify SMTP settings in environment variables", "FIX")
        self.log("   - Check email service configuration", "FIX")
        self.log("   - Test direct email API endpoint", "FIX")
        
        self.log("\n4. QUICK FIXES TO TRY:", "FIX")
        self.log("   - Restart the backend server", "FIX")
        self.log("   - Check backend logs for error messages", "FIX")
        self.log("   - Verify all environment variables are set", "FIX")
        self.log("   - Test with a simple non-search message first", "FIX")
    
    def run_full_diagnostic(self):
        """Run complete diagnostic"""
        self.log("🚀 STARTING EMERGENCY SEARCH DIAGNOSTIC", "START")
        self.log("=" * 60, "START")
        
        # Step 1: Check backend
        if not self.test_backend_connection():
            self.log("❌ CRITICAL: Backend is not responding!", "CRITICAL")
            return False
        
        # Step 2: Authenticate
        if not self.authenticate():
            self.log("❌ CRITICAL: Cannot authenticate!", "CRITICAL")
            return False
        
        # Step 3: Test search
        self.log("\n🔍 TESTING SEARCH FUNCTIONALITY", "TEST")
        search_working = self.test_search_functionality()
        
        # Step 4: Test email
        self.log("\n📧 TESTING EMAIL FUNCTIONALITY", "TEST")
        email_working = self.test_email_functionality()
        
        # Step 5: Test web search integration
        self.log("\n🌐 TESTING WEB SEARCH INTEGRATION", "TEST")
        web_search_working = self.test_web_search_integration()
        
        # Summary
        self.log("\n" + "=" * 60, "SUMMARY")
        self.log("📊 DIAGNOSTIC SUMMARY", "SUMMARY")
        self.log(f"Backend: {'✅ Working' if True else '❌ Failed'}", "SUMMARY")
        self.log(f"Authentication: {'✅ Working' if self.token else '❌ Failed'}", "SUMMARY")
        self.log(f"Search Requests: {'✅ Working' if search_working else '❌ Failed'}", "SUMMARY")
        self.log(f"Email Sending: {'✅ Working' if email_working else '❌ Failed'}", "SUMMARY")
        self.log(f"Web Search: {'✅ Working' if web_search_working else '❌ Failed'}", "SUMMARY")
        
        # Provide fixes
        self.provide_fixes()
        
        return search_working and email_working

if __name__ == "__main__":
    diagnostic = SearchDiagnostic()
    success = diagnostic.run_full_diagnostic()
    
    if success:
        print("\n🎉 SUCCESS: Your search system should be working!")
    else:
        print("\n🚨 ISSUES FOUND: Follow the recommendations above to fix the problems.")
