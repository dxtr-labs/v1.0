#!/usr/bin/env python3
"""
Production Readiness Test Suite
Tests multiple scenarios to validate system stability
"""

import requests
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import uuid

BASE_URL = "http://localhost:8002"

class ProductionTester:
    def __init__(self):
        self.test_results = {}
        
    def log_test(self, test_name, status, details=""):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {test_name}: {status}")
        if details:
            print(f"    └─ {details}")
        self.test_results[test_name] = {"status": status, "details": details}
    
    def test_concurrent_users(self, num_users=5):
        """Test system with multiple concurrent users"""
        print(f"\n🔄 Testing {num_users} concurrent users...")
        
        def create_user_session(user_id):
            try:
                # Create unique user
                user_data = {
                    "username": f"testuser{user_id}",
                    "email": f"test{user_id}@example.com", 
                    "password": "testpass123"
                }
                
                requests.post(f"{BASE_URL}/api/auth/signup", json=user_data, timeout=10)
                
                # Login
                login_response = requests.post(
                    f"{BASE_URL}/api/auth/login",
                    json={"email": user_data["email"], "password": user_data["password"]},
                    timeout=10
                )
                
                if login_response.status_code == 200:
                    return {"user_id": user_id, "status": "success"}
                else:
                    return {"user_id": user_id, "status": "failed", "code": login_response.status_code}
                    
            except Exception as e:
                return {"user_id": user_id, "status": "error", "error": str(e)}
        
        # Execute concurrent logins
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            results = list(executor.map(create_user_session, range(num_users)))
        
        successful = sum(1 for r in results if r["status"] == "success")
        self.log_test("Concurrent User Test", 
                     f"✅ PASSED" if successful >= num_users * 0.8 else "❌ FAILED",
                     f"{successful}/{num_users} users authenticated successfully")
    
    def test_ai_service_variety(self):
        """Test different AI services"""
        print(f"\n🤖 Testing AI service variety...")
        
        # First authenticate
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "aitest@example.com", "password": "testpass123"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            self.log_test("AI Service Variety", "❌ FAILED", "Authentication failed")
            return
        
        ai_services = ["inhouse", "openai", "claude"]
        results = {}
        
        for service in ai_services:
            try:
                test_payload = {
                    "message": f"service:{service} write a short greeting",
                    "service": service
                }
                
                response = requests.post(
                    f"{BASE_URL}/api/chat/mcpai",
                    json=test_payload,
                    timeout=30
                )
                
                results[service] = response.status_code == 200
                
            except Exception as e:
                results[service] = False
        
        passed_services = sum(results.values())
        self.log_test("AI Service Variety",
                     f"✅ PASSED" if passed_services >= 1 else "❌ FAILED", 
                     f"{passed_services}/3 AI services working")
    
    def test_workflow_complexity(self):
        """Test complex workflow scenarios"""
        print(f"\n⚙️ Testing complex workflows...")
        
        # Test multi-step workflow
        complex_workflow = {
            "user_input": "service:inhouse Generate a business proposal and send it to multiple recipients",
            "ai_service": "inhouse"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/workflow/generate",
                json=complex_workflow,
                timeout=45
            )
            
            if response.status_code == 200:
                workflow_data = response.json()
                nodes = workflow_data.get("workflow", {}).get("nodes", [])
                
                if len(nodes) >= 2:  # Should have AI + Email nodes
                    self.log_test("Complex Workflow", "✅ PASSED", 
                                f"Generated workflow with {len(nodes)} nodes")
                else:
                    self.log_test("Complex Workflow", "⚠️ PARTIAL", 
                                f"Basic workflow with {len(nodes)} nodes")
            else:
                self.log_test("Complex Workflow", "❌ FAILED", 
                            f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Complex Workflow", "❌ FAILED", f"Error: {str(e)}")
    
    def test_error_handling(self):
        """Test system error handling"""
        print(f"\n🛡️ Testing error handling...")
        
        error_tests = [
            {
                "name": "Invalid Endpoint",
                "url": f"{BASE_URL}/api/nonexistent",
                "expected": 404
            },
            {
                "name": "Malformed JSON",
                "url": f"{BASE_URL}/api/auth/login",
                "data": "invalid json",
                "expected": 400
            },
            {
                "name": "Missing Required Fields",
                "url": f"{BASE_URL}/api/auth/login", 
                "data": {"email": "test@example.com"},  # Missing password
                "expected": 400
            }
        ]
        
        passed_tests = 0
        for test in error_tests:
            try:
                if "data" in test:
                    if isinstance(test["data"], str):
                        response = requests.post(test["url"], data=test["data"], timeout=10)
                    else:
                        response = requests.post(test["url"], json=test["data"], timeout=10)
                else:
                    response = requests.get(test["url"], timeout=10)
                
                if response.status_code == test["expected"]:
                    passed_tests += 1
                    print(f"    ✅ {test['name']}: Handled correctly")
                else:
                    print(f"    ❌ {test['name']}: Expected {test['expected']}, got {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ {test['name']}: Exception - {str(e)}")
        
        self.log_test("Error Handling", 
                     f"✅ PASSED" if passed_tests == len(error_tests) else "⚠️ PARTIAL",
                     f"{passed_tests}/{len(error_tests)} error cases handled correctly")
    
    def test_system_stability(self):
        """Test system stability over time"""
        print(f"\n⏱️ Testing system stability (quick test)...")
        
        start_time = time.time()
        successful_requests = 0
        total_requests = 10
        
        for i in range(total_requests):
            try:
                response = requests.get(f"{BASE_URL}/health", timeout=5)
                if response.status_code == 200:
                    successful_requests += 1
                time.sleep(0.5)  # Small delay between requests
            except:
                pass
        
        duration = time.time() - start_time
        success_rate = (successful_requests / total_requests) * 100
        
        self.log_test("System Stability",
                     f"✅ PASSED" if success_rate >= 90 else "❌ FAILED",
                     f"{success_rate:.1f}% uptime over {duration:.1f}s")
    
    def run_production_tests(self):
        """Run comprehensive production readiness tests"""
        print("🚀 PRODUCTION READINESS TEST SUITE")
        print("=" * 60)
        
        # Test 1: System Health
        try:
            health_response = requests.get(f"{BASE_URL}/health", timeout=10)
            if health_response.status_code == 200:
                self.log_test("System Health", "✅ PASSED", "Backend responding")
            else:
                self.log_test("System Health", "❌ FAILED", f"Status: {health_response.status_code}")
                return
        except:
            self.log_test("System Health", "❌ FAILED", "Backend not accessible")
            return
        
        # Test 2: Concurrent Users
        self.test_concurrent_users(3)
        
        # Test 3: AI Service Variety  
        self.test_ai_service_variety()
        
        # Test 4: Complex Workflows
        self.test_workflow_complexity()
        
        # Test 5: Error Handling
        self.test_error_handling()
        
        # Test 6: System Stability
        self.test_system_stability()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 PRODUCTION READINESS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() 
                          if "✅ PASSED" in result["status"])
        partial_tests = sum(1 for result in self.test_results.values() 
                           if "⚠️ PARTIAL" in result["status"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Partial: {partial_tests}")
        print(f"Failed: {total_tests - passed_tests - partial_tests}")
        
        success_rate = ((passed_tests + partial_tests * 0.5) / total_tests) * 100
        
        if success_rate >= 80:
            print(f"\n🎉 PRODUCTION READY: {success_rate:.1f}% success rate")
            print("✅ System is stable enough for production deployment")
        elif success_rate >= 60:
            print(f"\n⚠️ NEEDS IMPROVEMENT: {success_rate:.1f}% success rate")
            print("🔧 Address failing tests before production")
        else:
            print(f"\n❌ NOT READY: {success_rate:.1f}% success rate")
            print("🛠️ Significant issues need resolution")

if __name__ == "__main__":
    tester = ProductionTester()
    tester.run_production_tests()
