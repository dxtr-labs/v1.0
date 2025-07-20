#!/usr/bin/env python3
"""
Multiple User Input Test Suite
Focused testing of various user input scenarios for workflow automation
"""

import requests
import json
import time
import uuid
import re
from typing import Dict, Any, List

class MultipleUserInputTester:
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/automation/load-workflow"
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   📝 {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.time()
        })

    def extract_email_from_input(self, user_input: str) -> str:
        """Extract email address from user input"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, user_input)
        return match.group() if match else "no_email_found"

    def create_workflow_from_input(self, user_input: str, category: str) -> Dict[str, Any]:
        """Create a workflow based on user input"""
        workflow_id = f"input_{category}_{uuid.uuid4().hex[:8]}"
        
        # Base workflow structure
        workflow = {
            "id": workflow_id,
            "name": f"User Request: {user_input[:60]}{'...' if len(user_input) > 60 else ''}",
            "description": f"Workflow generated from user input: {user_input}",
            "filename": f"{workflow_id}.json",
            "user_input": user_input,
            "category": category,
            "created_at": time.time(),
            "nodes": []
        }
        
        # Create nodes based on category
        if category == "email":
            workflow["nodes"] = [
                {
                    "id": "email_trigger",
                    "type": "manualTrigger",
                    "name": "Email Request Trigger",
                    "parameters": {
                        "user_input": user_input,
                        "extracted_email": self.extract_email_from_input(user_input)
                    },
                    "position": {"x": 100, "y": 100}
                },
                {
                    "id": "email_compose",
                    "type": "emailSend",
                    "name": "Compose & Send Email",
                    "parameters": {
                        "recipient": self.extract_email_from_input(user_input),
                        "subject": "Generated from user request",
                        "content_source": "ai_generated"
                    },
                    "position": {"x": 300, "y": 100}
                }
            ]
        elif category == "content":
            workflow["nodes"] = [
                {
                    "id": "content_trigger",
                    "type": "manualTrigger", 
                    "name": "Content Creation Trigger",
                    "parameters": {"user_input": user_input},
                    "position": {"x": 100, "y": 100}
                },
                {
                    "id": "ai_generate",
                    "type": "openaiChat",
                    "name": "AI Content Generator",
                    "parameters": {
                        "prompt": user_input,
                        "model": "gpt-3.5-turbo"
                    },
                    "position": {"x": 300, "y": 100}
                },
                {
                    "id": "format_content",
                    "type": "set",
                    "name": "Format Content",
                    "parameters": {"output_format": "markdown"},
                    "position": {"x": 500, "y": 100}
                }
            ]
        elif category == "data":
            workflow["nodes"] = [
                {
                    "id": "data_source",
                    "type": "httpRequest",
                    "name": "Data Source",
                    "parameters": {"url": "api_endpoint", "method": "GET"},
                    "position": {"x": 100, "y": 100}
                },
                {
                    "id": "process_data",
                    "type": "set",
                    "name": "Process Data",
                    "parameters": {
                        "user_request": user_input,
                        "operation": "transform"
                    },
                    "position": {"x": 300, "y": 100}
                },
                {
                    "id": "save_results",
                    "type": "webhook",
                    "name": "Save Results",
                    "parameters": {"destination": "database"},
                    "position": {"x": 500, "y": 100}
                }
            ]
        else:  # automation
            workflow["nodes"] = [
                {
                    "id": "auto_trigger",
                    "type": "webhook",
                    "name": "Automation Trigger",
                    "parameters": {"event_type": "user_defined"},
                    "position": {"x": 100, "y": 100}
                },
                {
                    "id": "condition_check",
                    "type": "if",
                    "name": "Condition Check",
                    "parameters": {"condition": "evaluate_request"},
                    "position": {"x": 300, "y": 100}
                },
                {
                    "id": "execute_action",
                    "type": "function",
                    "name": "Execute Action",
                    "parameters": {"action": "user_defined"},
                    "position": {"x": 500, "y": 100}
                }
            ]
        
        return workflow

    def test_email_scenarios(self):
        """Test multiple email automation scenarios"""
        print("\n📧 Testing Email Automation Scenarios")
        print("-" * 50)
        
        email_scenarios = [
            "Send a welcome email to john@example.com",
            "Email the quarterly report to all@company.com",
            "Send follow-up to sarah@startup.io about our meeting",
            "Create and send a newsletter to subscribers@list.com",
            "Email invoice to billing@client.org", 
            "Send reminder to team@project.com about deadline",
            "Email product update to customers@shop.com",
            "Send survey to feedback@service.net",
            "Email contract to legal@partner.co",
            "Send thank you note to support@helper.org"
        ]
        
        success_count = 0
        total_scenarios = len(email_scenarios)
        
        for i, scenario in enumerate(email_scenarios, 1):
            print(f"\n📧 Email Test {i}/{total_scenarios}: {scenario}")
            
            workflow = self.create_workflow_from_input(scenario, "email")
            
            try:
                response = requests.post(
                    self.api_url,
                    json={"workflow": workflow, "user_input": scenario},
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print(f"   ✅ SUCCESS: Workflow ID {data.get('workflowId', 'N/A')}")
                        success_count += 1
                        
                        # Validate email extraction
                        extracted_email = self.extract_email_from_input(scenario)
                        if extracted_email != "no_email_found":
                            print(f"   📨 Extracted email: {extracted_email}")
                        else:
                            print(f"   ⚠️  No email found in input")
                    else:
                        print(f"   ❌ API Error: {data.get('error', 'Unknown')}")
                else:
                    print(f"   ❌ HTTP Error: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"   ⏰ TIMEOUT: Request took too long")
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
                
            time.sleep(0.1)  # Small delay between requests
        
        success_rate = (success_count / total_scenarios) * 100
        self.log_result("Email Automation Scenarios", success_count >= total_scenarios * 0.8, 
                       f"{success_count}/{total_scenarios} scenarios passed ({success_rate:.1f}%)")

    def test_content_creation_scenarios(self):
        """Test multiple content creation scenarios"""
        print("\n✍️ Testing Content Creation Scenarios")
        print("-" * 50)
        
        content_scenarios = [
            "Generate a blog post about AI automation trends",
            "Create social media content for product launch",
            "Write API documentation for webhook endpoints", 
            "Generate marketing copy for email campaigns",
            "Create a press release for new feature",
            "Write technical documentation for developers",
            "Generate product descriptions for e-commerce",
            "Create training materials for new employees",
            "Write case study about successful implementation",
            "Generate FAQ content for customer support"
        ]
        
        success_count = 0
        total_scenarios = len(content_scenarios)
        
        for i, scenario in enumerate(content_scenarios, 1):
            print(f"\n✍️ Content Test {i}/{total_scenarios}: {scenario}")
            
            workflow = self.create_workflow_from_input(scenario, "content")
            
            try:
                response = requests.post(
                    self.api_url,
                    json={"workflow": workflow, "user_input": scenario},
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print(f"   ✅ SUCCESS: Content workflow created")
                        success_count += 1
                    else:
                        print(f"   ❌ API Error: {data.get('error', 'Unknown')}")
                else:
                    print(f"   ❌ HTTP Error: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"   ⏰ TIMEOUT: Request took too long")
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
                
            time.sleep(0.1)
        
        success_rate = (success_count / total_scenarios) * 100
        self.log_result("Content Creation Scenarios", success_count >= total_scenarios * 0.8,
                       f"{success_count}/{total_scenarios} scenarios passed ({success_rate:.1f}%)")

    def test_data_processing_scenarios(self):
        """Test multiple data processing scenarios"""
        print("\n📊 Testing Data Processing Scenarios")
        print("-" * 50)
        
        data_scenarios = [
            "Analyze sales data and generate monthly report",
            "Process customer feedback from survey responses",
            "Extract and transform CRM data for analytics",
            "Parse log files and identify error patterns",
            "Convert CSV data to JSON format",
            "Aggregate website analytics and create dashboard",
            "Process inventory data and update stock levels",
            "Analyze user behavior data for insights",
            "Clean and validate customer contact information",
            "Generate performance metrics from application logs"
        ]
        
        success_count = 0
        total_scenarios = len(data_scenarios)
        
        for i, scenario in enumerate(data_scenarios, 1):
            print(f"\n📊 Data Test {i}/{total_scenarios}: {scenario}")
            
            workflow = self.create_workflow_from_input(scenario, "data")
            
            try:
                response = requests.post(
                    self.api_url,
                    json={"workflow": workflow, "user_input": scenario},
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print(f"   ✅ SUCCESS: Data processing workflow created")
                        success_count += 1
                    else:
                        print(f"   ❌ API Error: {data.get('error', 'Unknown')}")
                else:
                    print(f"   ❌ HTTP Error: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"   ⏰ TIMEOUT: Request took too long")
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
                
            time.sleep(0.1)
        
        success_rate = (success_count / total_scenarios) * 100
        self.log_result("Data Processing Scenarios", success_count >= total_scenarios * 0.8,
                       f"{success_count}/{total_scenarios} scenarios passed ({success_rate:.1f}%)")

    def test_complex_automation_scenarios(self):
        """Test multiple complex automation scenarios"""
        print("\n🔄 Testing Complex Automation Scenarios")
        print("-" * 50)
        
        automation_scenarios = [
            "When new user registers, send welcome email and create CRM record",
            "Monitor website uptime and alert team if downtime detected",
            "Automatically backup database every night at 2 AM",
            "When support ticket created, route to appropriate team member",
            "Process incoming invoices and update accounting system",
            "Sync customer data between CRM and marketing platform",
            "Auto-generate reports and email to managers weekly",
            "Monitor social media mentions and respond to customer queries",
            "When inventory low, automatically reorder from suppliers",
            "Process refund requests and update customer accounts"
        ]
        
        success_count = 0
        total_scenarios = len(automation_scenarios)
        
        for i, scenario in enumerate(automation_scenarios, 1):
            print(f"\n🔄 Automation Test {i}/{total_scenarios}: {scenario}")
            
            workflow = self.create_workflow_from_input(scenario, "automation")
            
            try:
                response = requests.post(
                    self.api_url,
                    json={"workflow": workflow, "user_input": scenario},
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print(f"   ✅ SUCCESS: Complex automation workflow created")
                        success_count += 1
                    else:
                        print(f"   ❌ API Error: {data.get('error', 'Unknown')}")
                else:
                    print(f"   ❌ HTTP Error: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"   ⏰ TIMEOUT: Request took too long")
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
                
            time.sleep(0.1)
        
        success_rate = (success_count / total_scenarios) * 100
        self.log_result("Complex Automation Scenarios", success_count >= total_scenarios * 0.6,  # Lower threshold for complex
                       f"{success_count}/{total_scenarios} scenarios passed ({success_rate:.1f}%)")

    def run_all_user_input_tests(self):
        """Run all user input tests"""
        print("🚀 Starting Multiple User Input Tests")
        print("=" * 70)
        print("Testing system's ability to handle diverse user input scenarios")
        print("=" * 70)
        
        start_time = time.time()
        
        # Run all test categories
        self.test_email_scenarios()
        self.test_content_creation_scenarios()
        self.test_data_processing_scenarios()
        self.test_complex_automation_scenarios()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Generate summary report
        print("\n" + "=" * 70)
        print("📊 MULTIPLE USER INPUT TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"📈 Overall Results:")
        print(f"   Total Test Categories: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"   ⏱️  Execution Time: {execution_time:.2f} seconds")
        
        print(f"\n📝 Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {result['test']}: {result['details']}")
        
        print(f"\n🎯 System Assessment:")
        if passed_tests == total_tests:
            print("   🟢 EXCELLENT: All user input scenarios handled perfectly!")
        elif passed_tests >= total_tests * 0.8:
            print("   🔵 GOOD: System handles most user inputs well")
        elif passed_tests >= total_tests * 0.6:
            print("   🟡 FAIR: System needs improvement for better user input handling")
        else:
            print("   🔴 POOR: System requires significant work on user input processing")
        
        # Test coverage summary
        total_scenarios_tested = 40  # 10 per category
        print(f"\n📋 Test Coverage:")
        print(f"   📧 Email scenarios: 10 tested")
        print(f"   ✍️  Content creation: 10 tested")
        print(f"   📊 Data processing: 10 tested") 
        print(f"   🔄 Complex automation: 10 tested")
        print(f"   🎯 Total user inputs tested: {total_scenarios_tested}")
        
        return {
            "total_categories": total_tests,
            "passed_categories": passed_tests,
            "failed_categories": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "total_scenarios": total_scenarios_tested,
            "execution_time": execution_time,
            "results": self.test_results
        }

if __name__ == "__main__":
    print("🎯 Multiple User Input Test Suite")
    print("Testing workflow system with diverse user scenarios")
    print("-" * 50)
    
    # Initialize tester
    tester = MultipleUserInputTester()
    
    # Run all tests
    results = tester.run_all_user_input_tests()
    
    # Save results
    timestamp = int(time.time())
    results_file = f"user_input_test_results_{timestamp}.json"
    
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {results_file}")
    print("🏁 Testing complete!")
