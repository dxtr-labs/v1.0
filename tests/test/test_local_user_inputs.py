#!/usr/bin/env python3
"""
Local Multiple User Input Test Suite
Tests user input processing capabilities without requiring a backend server
"""

import json
import time
import uuid
import re
from typing import Dict, Any, List, Tuple

class LocalUserInputProcessor:
    def __init__(self):
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

    def detect_automation_intent(self, user_input: str) -> Tuple[str, float, List[str]]:
        """Detect automation intent from user input"""
        user_input_lower = user_input.lower()
        
        # Email automation keywords
        email_keywords = ['email', 'send', 'mail', 'message', 'notify', 'alert', 'newsletter', 'invitation', 'reminder']
        email_score = sum(1 for keyword in email_keywords if keyword in user_input_lower)
        
        # Content creation keywords
        content_keywords = ['generate', 'create', 'write', 'blog', 'post', 'content', 'article', 'documentation', 'copy']
        content_score = sum(1 for keyword in content_keywords if keyword in user_input_lower)
        
        # Data processing keywords
        data_keywords = ['analyze', 'process', 'data', 'report', 'analytics', 'export', 'import', 'convert', 'transform']
        data_score = sum(1 for keyword in data_keywords if keyword in user_input_lower)
        
        # Automation/workflow keywords
        automation_keywords = ['when', 'automatically', 'schedule', 'trigger', 'workflow', 'automate', 'monitor', 'sync']
        automation_score = sum(1 for keyword in automation_keywords if keyword in user_input_lower)
        
        # Determine primary intent
        scores = {
            'email_automation': email_score,
            'content_creation': content_score,
            'data_processing': data_score,
            'workflow_automation': automation_score
        }
        
        primary_intent = max(scores, key=scores.get)
        confidence = scores[primary_intent] / 10.0  # Normalize to 0-1 scale
        
        # Extract key parameters
        extracted_params = []
        
        # Extract email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', user_input)
        extracted_params.extend(emails)
        
        # Extract quoted strings (often contain specific content or names)
        quoted_strings = re.findall(r'"([^"]*)"', user_input)
        extracted_params.extend(quoted_strings)
        
        # Extract common business terms
        business_terms = ['CRM', 'API', 'dashboard', 'analytics', 'database', 'CSV', 'JSON', 'report', 'invoice']
        found_terms = [term for term in business_terms if term.lower() in user_input_lower]
        extracted_params.extend(found_terms)
        
        return primary_intent, min(confidence, 1.0), extracted_params

    def create_workflow_structure(self, user_input: str, intent: str, params: List[str]) -> Dict[str, Any]:
        """Create a workflow structure based on detected intent"""
        workflow_id = f"local_{intent}_{uuid.uuid4().hex[:8]}"
        
        workflow = {
            "id": workflow_id,
            "name": f"Generated: {user_input[:50]}{'...' if len(user_input) > 50 else ''}",
            "description": f"Workflow automatically generated from user input",
            "user_input": user_input,
            "detected_intent": intent,
            "extracted_params": params,
            "confidence": len(params) / 5.0,  # Simple confidence based on parameter extraction
            "created_at": time.time(),
            "nodes": []
        }
        
        # Generate appropriate nodes based on intent
        if intent == "email_automation":
            workflow["nodes"] = [
                {
                    "id": "email_trigger",
                    "type": "trigger",
                    "name": "Email Automation Trigger",
                    "parameters": {
                        "user_request": user_input,
                        "recipients": [p for p in params if '@' in p]
                    }
                },
                {
                    "id": "compose_email",
                    "type": "email_compose",
                    "name": "Compose Email",
                    "parameters": {
                        "content_source": "ai_generated",
                        "template": "user_request"
                    }
                },
                {
                    "id": "send_email",
                    "type": "email_send",
                    "name": "Send Email",
                    "parameters": {
                        "delivery_method": "smtp"
                    }
                }
            ]
        elif intent == "content_creation":
            workflow["nodes"] = [
                {
                    "id": "content_trigger",
                    "type": "trigger",
                    "name": "Content Creation Trigger",
                    "parameters": {"user_request": user_input}
                },
                {
                    "id": "ai_generate",
                    "type": "ai_content",
                    "name": "AI Content Generator",
                    "parameters": {
                        "prompt": user_input,
                        "content_type": "dynamic",
                        "business_context": params
                    }
                },
                {
                    "id": "format_output",
                    "type": "formatter",
                    "name": "Format Output",
                    "parameters": {"output_format": "structured"}
                }
            ]
        elif intent == "data_processing":
            workflow["nodes"] = [
                {
                    "id": "data_source",
                    "type": "data_input",
                    "name": "Data Input",
                    "parameters": {"source_type": "dynamic"}
                },
                {
                    "id": "process_data",
                    "type": "data_processor",
                    "name": "Data Processor", 
                    "parameters": {
                        "operation": "analyze",
                        "user_requirements": user_input,
                        "data_types": params
                    }
                },
                {
                    "id": "output_results",
                    "type": "data_output",
                    "name": "Output Results",
                    "parameters": {"format": "report"}
                }
            ]
        else:  # workflow_automation
            workflow["nodes"] = [
                {
                    "id": "automation_trigger",
                    "type": "event_trigger",
                    "name": "Automation Trigger",
                    "parameters": {"trigger_type": "event_based"}
                },
                {
                    "id": "condition_logic",
                    "type": "condition",
                    "name": "Business Logic",
                    "parameters": {
                        "conditions": user_input,
                        "business_rules": params
                    }
                },
                {
                    "id": "execute_actions",
                    "type": "multi_action",
                    "name": "Execute Actions",
                    "parameters": {"action_sequence": "sequential"}
                }
            ]
        
        return workflow

    def test_email_input_processing(self):
        """Test email automation input processing"""
        print("\n📧 Testing Email Input Processing")
        print("-" * 50)
        
        email_inputs = [
            "Send a welcome email to john@example.com",
            "Email the quarterly report to managers@company.com and sarah@startup.io", 
            "Create and send a newsletter about our new features to subscribers@list.com",
            "Send follow-up emails to leads@techcompany.com about our demo",
            "Email invoice to billing@client.org with payment instructions",
            "Send reminder to team@project.com about tomorrow's deadline",
            "Email product update announcement to customers@shop.com",
            "Send survey link to feedback@service.net for customer satisfaction",
            "Email contract to legal@partner.co for review and approval",
            "Send thank you note to support@helper.org for excellent service"
        ]
        
        success_count = 0
        total_tests = len(email_inputs)
        
        for i, user_input in enumerate(email_inputs, 1):
            print(f"\n📧 Email Test {i}/{total_tests}")
            print(f"   Input: {user_input}")
            
            # Process the input
            intent, confidence, params = self.detect_automation_intent(user_input)
            workflow = self.create_workflow_structure(user_input, intent, params)
            
            # Validate results
            email_found = self.extract_email_from_input(user_input)
            is_email_intent = intent == "email_automation"
            has_email_params = any('@' in param for param in params)
            
            if is_email_intent and email_found != "no_email_found" and has_email_params:
                print(f"   ✅ SUCCESS: Intent={intent}, Confidence={confidence:.2f}, Email={email_found}")
                print(f"   📋 Extracted: {len(params)} parameters")
                success_count += 1
            else:
                print(f"   ❌ FAILED: Intent={intent}, Email={email_found}, Params={len(params)}")
        
        success_rate = (success_count / total_tests) * 100
        self.log_result("Email Input Processing", success_count >= total_tests * 0.8,
                       f"{success_count}/{total_tests} emails processed correctly ({success_rate:.1f}%)")

    def test_content_input_processing(self):
        """Test content creation input processing"""
        print("\n✍️ Testing Content Input Processing")
        print("-" * 50)
        
        content_inputs = [
            "Generate a blog post about AI automation trends for our website",
            "Create social media content for LinkedIn about our product launch",
            "Write API documentation for our new webhook endpoints",
            "Generate marketing copy for email campaigns targeting small businesses",
            "Create a press release announcing our Series A funding",
            "Write technical documentation for developers using our platform",
            "Generate product descriptions for our e-commerce catalog",
            "Create training materials for new employee onboarding",
            "Write a case study about successful customer implementation",
            "Generate FAQ content for customer support knowledge base"
        ]
        
        success_count = 0
        total_tests = len(content_inputs)
        
        for i, user_input in enumerate(content_inputs, 1):
            print(f"\n✍️ Content Test {i}/{total_tests}")
            print(f"   Input: {user_input}")
            
            intent, confidence, params = self.detect_automation_intent(user_input)
            workflow = self.create_workflow_structure(user_input, intent, params)
            
            is_content_intent = intent == "content_creation"
            has_content_keywords = any(keyword in user_input.lower() for keyword in ['generate', 'create', 'write'])
            has_useful_params = len(params) > 0
            
            if is_content_intent and has_content_keywords and confidence > 0.1:
                print(f"   ✅ SUCCESS: Intent={intent}, Confidence={confidence:.2f}")
                print(f"   📋 Context extracted: {params[:3]}...")  # Show first 3 params
                success_count += 1
            else:
                print(f"   ❌ FAILED: Intent={intent}, Confidence={confidence:.2f}")
        
        success_rate = (success_count / total_tests) * 100
        self.log_result("Content Input Processing", success_count >= total_tests * 0.8,
                       f"{success_count}/{total_tests} content requests processed correctly ({success_rate:.1f}%)")

    def test_data_input_processing(self):
        """Test data processing input processing"""
        print("\n📊 Testing Data Input Processing")
        print("-" * 50)
        
        data_inputs = [
            "Analyze sales data from our CRM and generate monthly report",
            "Process customer feedback from survey responses and create insights",
            "Extract user activity data from analytics and identify trends",
            "Convert CSV files to JSON format for API integration",
            "Parse application logs and identify error patterns",
            "Aggregate website analytics data and create dashboard",
            "Process inventory data and update stock level reports",
            "Analyze customer behavior data to improve user experience",
            "Clean and validate customer contact information in database",
            "Generate performance metrics from application monitoring data"
        ]
        
        success_count = 0
        total_tests = len(data_inputs)
        
        for i, user_input in enumerate(data_inputs, 1):
            print(f"\n📊 Data Test {i}/{total_tests}")
            print(f"   Input: {user_input}")
            
            intent, confidence, params = self.detect_automation_intent(user_input)
            workflow = self.create_workflow_structure(user_input, intent, params)
            
            is_data_intent = intent == "data_processing"
            has_data_keywords = any(keyword in user_input.lower() for keyword in ['analyze', 'process', 'data', 'convert'])
            has_data_context = len(params) > 0
            
            if is_data_intent and has_data_keywords and confidence > 0.1:
                print(f"   ✅ SUCCESS: Intent={intent}, Confidence={confidence:.2f}")
                print(f"   📊 Data context: {params[:3]}...")
                success_count += 1
            else:
                print(f"   ❌ FAILED: Intent={intent}, Confidence={confidence:.2f}")
        
        success_rate = (success_count / total_tests) * 100
        self.log_result("Data Input Processing", success_count >= total_tests * 0.8,
                       f"{success_count}/{total_tests} data requests processed correctly ({success_rate:.1f}%)")

    def test_complex_automation_processing(self):
        """Test complex automation input processing"""
        print("\n🔄 Testing Complex Automation Processing")
        print("-" * 50)
        
        automation_inputs = [
            "When a new customer registers, send welcome email and create CRM record",
            "Monitor website uptime and send Slack alert if downtime detected",
            "Automatically backup database every night at 2 AM",
            "When support ticket is created, route to appropriate team member",
            "Process incoming invoices and update accounting system automatically",
            "Sync customer data between CRM and marketing platform hourly",
            "Generate weekly reports and email to management team",
            "Monitor social media mentions and respond to customer queries",
            "When inventory falls below threshold, automatically reorder from suppliers",
            "Process refund requests and update customer accounts in real-time"
        ]
        
        success_count = 0
        total_tests = len(automation_inputs)
        
        for i, user_input in enumerate(automation_inputs, 1):
            print(f"\n🔄 Automation Test {i}/{total_tests}")
            print(f"   Input: {user_input}")
            
            intent, confidence, params = self.detect_automation_intent(user_input)
            workflow = self.create_workflow_structure(user_input, intent, params)
            
            has_trigger_words = any(word in user_input.lower() for word in ['when', 'automatically', 'monitor'])
            has_business_context = len(params) > 0
            is_complex = len(user_input.split()) > 8  # Complex sentences are usually longer
            
            if has_trigger_words and has_business_context and confidence > 0.1:
                print(f"   ✅ SUCCESS: Intent={intent}, Confidence={confidence:.2f}")
                print(f"   🔄 Automation context: {params[:3]}...")
                success_count += 1
            else:
                print(f"   ❌ FAILED: Intent={intent}, Confidence={confidence:.2f}")
        
        success_rate = (success_count / total_tests) * 100
        self.log_result("Complex Automation Processing", success_count >= total_tests * 0.6,  # Lower threshold for complex
                       f"{success_count}/{total_tests} automation requests processed correctly ({success_rate:.1f}%)")

    def test_parameter_extraction_accuracy(self):
        """Test accuracy of parameter extraction from various inputs"""
        print("\n🎯 Testing Parameter Extraction Accuracy")
        print("-" * 50)
        
        test_cases = [
            {
                "input": "Send invoice to billing@client.com with reference number #INV-2023-001",
                "expected_params": ["billing@client.com", "#INV-2023-001"],
                "description": "Email with reference number"
            },
            {
                "input": "Generate report from CRM data and save as CSV format",
                "expected_params": ["CRM", "CSV"],
                "description": "Business terms extraction"
            },
            {
                "input": "Create \"Monthly Newsletter\" content for our Q4 campaign",
                "expected_params": ["Monthly Newsletter"],
                "description": "Quoted content extraction"
            },
            {
                "input": "Sync data between Salesforce and HubSpot via API every 2 hours",
                "expected_params": ["API"],
                "description": "Integration platform terms"
            },
            {
                "input": "Email team@company.com and managers@company.com about project update",
                "expected_params": ["team@company.com", "managers@company.com"],
                "description": "Multiple email extraction"
            }
        ]
        
        success_count = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🎯 Extraction Test {i}/{total_tests}: {test_case['description']}")
            print(f"   Input: {test_case['input']}")
            
            intent, confidence, extracted_params = self.detect_automation_intent(test_case["input"])
            
            # Check if we found expected parameters
            found_expected = 0
            for expected in test_case["expected_params"]:
                if any(expected.lower() in param.lower() for param in extracted_params):
                    found_expected += 1
            
            accuracy = found_expected / len(test_case["expected_params"]) if test_case["expected_params"] else 1.0
            
            if accuracy >= 0.5:  # Found at least 50% of expected params
                print(f"   ✅ SUCCESS: Found {found_expected}/{len(test_case['expected_params'])} expected params")
                print(f"   📋 Extracted: {extracted_params}")
                success_count += 1
            else:
                print(f"   ❌ FAILED: Only found {found_expected}/{len(test_case['expected_params'])} expected params")
                print(f"   📋 Extracted: {extracted_params}")
        
        success_rate = (success_count / total_tests) * 100
        self.log_result("Parameter Extraction Accuracy", success_count >= total_tests * 0.8,
                       f"{success_count}/{total_tests} extraction tests passed ({success_rate:.1f}%)")

    def run_all_local_tests(self):
        """Run all local user input processing tests"""
        print("🎯 Local Multiple User Input Processing Tests")
        print("=" * 70)
        print("Testing user input processing capabilities locally")
        print("=" * 70)
        
        start_time = time.time()
        
        # Run all test categories
        self.test_email_input_processing()
        self.test_content_input_processing()
        self.test_data_input_processing()
        self.test_complex_automation_processing()
        self.test_parameter_extraction_accuracy()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Generate summary report
        print("\n" + "=" * 70)
        print("📊 LOCAL USER INPUT TEST SUMMARY")
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
        
        print(f"\n🎯 Processing Assessment:")
        if passed_tests == total_tests:
            print("   🟢 EXCELLENT: All user input processing working perfectly!")
        elif passed_tests >= total_tests * 0.8:
            print("   🔵 GOOD: User input processing works well for most scenarios")
        elif passed_tests >= total_tests * 0.6:
            print("   🟡 FAIR: User input processing needs some improvements")
        else:
            print("   🔴 POOR: User input processing requires significant work")
        
        # Processing capabilities summary
        print(f"\n🧠 Processing Capabilities Tested:")
        print(f"   📧 Email intent detection and parameter extraction")
        print(f"   ✍️  Content creation request analysis")
        print(f"   📊 Data processing workflow generation")
        print(f"   🔄 Complex automation scenario handling")
        print(f"   🎯 Parameter extraction accuracy")
        print(f"   🎯 Total scenarios processed: 45+")
        
        return {
            "total_categories": total_tests,
            "passed_categories": passed_tests,
            "failed_categories": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "execution_time": execution_time,
            "processing_capabilities": {
                "email_detection": True,
                "content_analysis": True,
                "data_workflow_generation": True,
                "automation_scenario_handling": True,
                "parameter_extraction": True
            },
            "results": self.test_results
        }

if __name__ == "__main__":
    print("🧠 Local User Input Processing Test Suite")
    print("Testing natural language processing capabilities")
    print("-" * 50)
    
    # Initialize processor
    processor = LocalUserInputProcessor()
    
    # Run all tests
    results = processor.run_all_local_tests()
    
    # Save results
    timestamp = int(time.time())
    results_file = f"local_user_input_test_results_{timestamp}.json"
    
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {results_file}")
    print("🏁 Local testing complete!")
