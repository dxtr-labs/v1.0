#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced MCP LLM with Conversational Flow
Tests: Normal Conversation → Automation Detection → Prebuilt Workflows → Custom Building → Parameter Collection → Execution
"""

import requests
import json
import time
import uuid

class EnhancedMCPTester:
    def __init__(self):
        self.base_url = "http://localhost:8002"
        self.test_results = []
        
    def test_conversational_flow(self):
        """Test the complete conversational flow"""
        
        print("🚀 Enhanced MCP LLM Conversational Flow Test Suite")
        print("=" * 70)
        
        # Test 1: Normal Conversation
        print("\n1️⃣ Testing Normal Conversation Mode...")
        self._test_normal_conversation()
        
        # Test 2: Automation Detection  
        print("\n2️⃣ Testing Automation Detection...")
        self._test_automation_detection()
        
        # Test 3: Prebuilt Workflow Search
        print("\n3️⃣ Testing Prebuilt Workflow Search...")
        self._test_prebuilt_workflows()
        
        # Test 4: Custom Workflow Building
        print("\n4️⃣ Testing Custom Workflow Building...")
        self._test_custom_workflow_building()
        
        # Test 5: Parameter Collection
        print("\n5️⃣ Testing Parameter Collection...")
        self._test_parameter_collection()
        
        # Test 6: Enhanced ASU Bus Automation
        print("\n6️⃣ Testing Enhanced ASU Bus Automation...")
        self._test_asu_bus_automation()
        
        # Test 7: Driver Integration Testing
        print("\n7️⃣ Testing Available Drivers...")
        self._test_driver_integration()
        
        # Summary
        self._print_summary()
    
    def _make_request(self, message: str, endpoint: str = "/api/chat/mcpai") -> dict:
        """Make a request to the MCP API"""
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                json={"message": message},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"error": f"Request failed: {e}"}
    
    def _test_normal_conversation(self):
        """Test normal conversational responses"""
        
        conversational_inputs = [
            "Hi there! How are you doing today?",
            "What can you help me with?", 
            "Nice to meet you!",
            "Thank you for your help",
            "Can you explain what automation is?"
        ]
        
        for i, message in enumerate(conversational_inputs, 1):
            print(f"   Test 1.{i}: '{message[:30]}...'")
            
            result = self._make_request(message)
            
            if "error" in result:
                print(f"      ❌ Error: {result['error']}")
                self.test_results.append(f"Conversation Test {i}: FAILED - {result['error']}")
            else:
                status = result.get('status', 'unknown')
                response = result.get('response', '')
                
                if status == 'conversational':
                    print(f"      ✅ Conversational response: {response[:100]}...")
                    self.test_results.append(f"Conversation Test {i}: PASSED")
                else:
                    print(f"      ⚠️ Unexpected status: {status}")
                    self.test_results.append(f"Conversation Test {i}: PARTIAL - wrong status")
            
            time.sleep(1)
    
    def _test_automation_detection(self):
        """Test automation detection capabilities"""
        
        automation_inputs = [
            "Send an email to john@example.com about the meeting",
            "Search for competitor prices online",
            "Create a workflow to process customer data",
            "Schedule a reminder email for tomorrow",
            "Find ASU bus schedules and email them to me"
        ]
        
        for i, message in enumerate(automation_inputs, 1):
            print(f"   Test 2.{i}: '{message[:40]}...'")
            
            result = self._make_request(message)
            
            if "error" in result:
                print(f"      ❌ Error: {result['error']}")
                self.test_results.append(f"Automation Detection {i}: FAILED - {result['error']}")
            else:
                status = result.get('status', 'unknown')
                has_workflow = result.get('hasWorkflowJson', False)
                
                if status in ['automation_ready', 'workflow_selection', 'parameter_collection', 'workflow_confirmation']:
                    print(f"      ✅ Automation detected: {status}")
                    if has_workflow:
                        print(f"         🔧 Workflow generated")
                    self.test_results.append(f"Automation Detection {i}: PASSED")
                else:
                    print(f"      ❌ Not detected as automation: {status}")
                    self.test_results.append(f"Automation Detection {i}: FAILED - not detected")
            
            time.sleep(1)
    
    def _test_prebuilt_workflows(self):
        """Test prebuilt workflow search and presentation"""
        
        workflow_requests = [
            "I want to send welcome emails to new customers",
            "Help me monitor competitor prices",
            "Create a reminder system for my tasks",
            "Set up ASU bus tracking for students"
        ]
        
        for i, message in enumerate(workflow_requests, 1):
            print(f"   Test 3.{i}: '{message[:40]}...'")
            
            result = self._make_request(message)
            
            if "error" in result:
                print(f"      ❌ Error: {result['error']}")
                self.test_results.append(f"Prebuilt Workflow {i}: FAILED - {result['error']}")
            else:
                status = result.get('status', 'unknown')
                workflow_options = result.get('workflow_options', [])
                awaiting_choice = result.get('awaiting_user_choice', False)
                
                if status == 'workflow_selection' and workflow_options:
                    print(f"      ✅ Found {len(workflow_options)} prebuilt workflows")
                    for j, workflow in enumerate(workflow_options):
                        print(f"         {j+1}. {workflow.get('name', 'Unknown')}")
                    self.test_results.append(f"Prebuilt Workflow {i}: PASSED")
                elif status in ['automation_ready', 'workflow_confirmation']:
                    print(f"      ✅ Custom workflow created directly: {status}")
                    self.test_results.append(f"Prebuilt Workflow {i}: PASSED (custom)")
                else:
                    print(f"      ❌ Unexpected response: {status}")
                    self.test_results.append(f"Prebuilt Workflow {i}: FAILED - unexpected response")
            
            time.sleep(1)
    
    def _test_custom_workflow_building(self):
        """Test custom workflow creation"""
        
        custom_requests = [
            "Create a custom automation to fetch weather data and email it daily",
            "Build a workflow to analyze social media mentions",
            "I need to automate my inventory management process",
            "Help me create a customer feedback collection system"
        ]
        
        for i, message in enumerate(custom_requests, 1):
            print(f"   Test 4.{i}: '{message[:40]}...'")
            
            result = self._make_request(message)
            
            if "error" in result:
                print(f"      ❌ Error: {result['error']}")
                self.test_results.append(f"Custom Workflow {i}: FAILED - {result['error']}")
            else:
                status = result.get('status', 'unknown')
                has_workflow = result.get('hasWorkflowJson', False)
                workflow_json = result.get('workflow_json', {})
                
                if status in ['automation_ready', 'workflow_confirmation', 'parameter_collection']:
                    print(f"      ✅ Custom workflow created: {status}")
                    if has_workflow:
                        workflow_type = workflow_json.get('workflow_type', 'unknown')
                        steps = len(workflow_json.get('steps', []))
                        print(f"         🔧 Type: {workflow_type}, Steps: {steps}")
                    self.test_results.append(f"Custom Workflow {i}: PASSED")
                else:
                    print(f"      ❌ Failed to create custom workflow: {status}")
                    self.test_results.append(f"Custom Workflow {i}: FAILED")
            
            time.sleep(1)
    
    def _test_parameter_collection(self):
        """Test parameter collection flow"""
        
        print(f"   Test 5.1: Email automation with missing parameters...")
        
        # Step 1: Request automation with missing parameters
        result = self._make_request("Send an email about our new product")
        
        if "error" in result:
            print(f"      ❌ Error: {result['error']}")
            self.test_results.append("Parameter Collection: FAILED - initial error")
            return
        
        status = result.get('status', 'unknown')
        missing_params = result.get('missing_parameters', [])
        
        if status == 'parameter_collection' and missing_params:
            print(f"      ✅ Parameter collection initiated")
            print(f"         📝 Missing: {', '.join(missing_params)}")
            
            # Step 2: Provide parameters
            print(f"   Test 5.2: Providing missing parameters...")
            
            param_response = self._make_request("Send to alice@company.com with subject: New Product Launch")
            
            if "error" in param_response:
                print(f"      ❌ Parameter response error: {param_response['error']}")
                self.test_results.append("Parameter Collection: FAILED - parameter response error")
            else:
                param_status = param_response.get('status', 'unknown')
                if param_status in ['workflow_confirmation', 'automation_ready']:
                    print(f"      ✅ Parameters collected successfully: {param_status}")
                    self.test_results.append("Parameter Collection: PASSED")
                else:
                    print(f"      ❌ Parameter collection incomplete: {param_status}")
                    self.test_results.append("Parameter Collection: PARTIAL")
        else:
            print(f"      ⚠️ No parameter collection needed: {status}")
            self.test_results.append("Parameter Collection: SKIPPED - no params needed")
        
        time.sleep(1)
    
    def _test_asu_bus_automation(self):
        """Test the enhanced ASU bus automation"""
        
        bus_requests = [
            "search asu bus shuttle website and fetch bus data from there and send email to test@asu.edu when is the next bus",
            "asu bus schedule information",
            "when is the next shuttle to tempe campus",
            "track ASU transportation for me"
        ]
        
        for i, message in enumerate(bus_requests, 1):
            print(f"   Test 6.{i}: '{message[:50]}...'")
            
            result = self._make_request(message)
            
            if "error" in result:
                print(f"      ❌ Error: {result['error']}")
                self.test_results.append(f"ASU Bus {i}: FAILED - {result['error']}")
            else:
                status = result.get('status', 'unknown')
                workflow_json = result.get('workflow_json', {})
                automation_type = workflow_json.get('workflow_type', '')
                
                if automation_type == 'asu_bus_automation':
                    print(f"      ✅ ASU Bus automation detected: {status}")
                    steps = workflow_json.get('steps', [])
                    print(f"         🚌 Steps: {len(steps)} (search, AI analysis, email)")
                    
                    # Check for required steps
                    has_search = any(step.get('action') == 'web_search_asu_bus' for step in steps)
                    has_ai = any(step.get('action') == 'ai_bus_analysis' for step in steps)
                    has_email = any(step.get('action') == 'send_email' for step in steps)
                    
                    if has_search and has_ai and has_email:
                        print(f"         ✅ All required steps present")
                        self.test_results.append(f"ASU Bus {i}: PASSED")
                    else:
                        print(f"         ⚠️ Missing steps: search={has_search}, ai={has_ai}, email={has_email}")
                        self.test_results.append(f"ASU Bus {i}: PARTIAL")
                else:
                    print(f"      ❌ Not detected as ASU bus automation: {automation_type}")
                    self.test_results.append(f"ASU Bus {i}: FAILED - wrong detection")
            
            time.sleep(1)
    
    def _test_driver_integration(self):
        """Test that various drivers are available and working"""
        
        driver_test_requests = [
            ("email_send", "Send email to test@example.com"),
            ("web_search", "Search for AI automation tools"),
            ("openai_driver", "Generate content using AI"),
            ("data_processor", "Process CSV data file"),
            ("scheduler", "Schedule a daily reminder")
        ]
        
        for i, (driver_name, test_request) in enumerate(driver_test_requests, 1):
            print(f"   Test 7.{i}: {driver_name} - '{test_request[:30]}...'")
            
            result = self._make_request(test_request)
            
            if "error" in result:
                print(f"      ❌ Error: {result['error']}")
                self.test_results.append(f"Driver {driver_name}: FAILED - {result['error']}")
            else:
                status = result.get('status', 'unknown')
                has_workflow = result.get('hasWorkflowJson', False)
                
                if status in ['automation_ready', 'workflow_confirmation', 'parameter_collection'] and has_workflow:
                    workflow_json = result.get('workflow_json', {})
                    steps = workflow_json.get('steps', [])
                    
                    # Check if any step uses related drivers
                    driver_found = False
                    for step in steps:
                        step_driver = step.get('driver', '')
                        if driver_name.replace('_', '') in step_driver.replace('_', '') or driver_name in step.get('action', ''):
                            driver_found = True
                            break
                    
                    if driver_found:
                        print(f"      ✅ Driver integration working")
                        self.test_results.append(f"Driver {driver_name}: PASSED")
                    else:
                        print(f"      ⚠️ Driver not explicitly used but workflow created")
                        self.test_results.append(f"Driver {driver_name}: PARTIAL")
                else:
                    print(f"      ❌ No workflow generated: {status}")
                    self.test_results.append(f"Driver {driver_name}: FAILED - no workflow")
            
            time.sleep(1)
    
    def _print_summary(self):
        """Print test summary"""
        
        print("\n" + "=" * 70)
        print("📊 ENHANCED MCP LLM TEST SUMMARY")
        print("=" * 70)
        
        passed = len([r for r in self.test_results if "PASSED" in r])
        partial = len([r for r in self.test_results if "PARTIAL" in r])
        failed = len([r for r in self.test_results if "FAILED" in r])
        skipped = len([r for r in self.test_results if "SKIPPED" in r])
        total = len(self.test_results)
        
        print(f"✅ PASSED:  {passed}/{total}")
        print(f"⚠️  PARTIAL: {partial}/{total}")
        print(f"❌ FAILED:  {failed}/{total}")
        print(f"⏭️  SKIPPED: {skipped}/{total}")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            if "PASSED" in result:
                print(f"   ✅ {result}")
            elif "PARTIAL" in result:
                print(f"   ⚠️  {result}")
            elif "FAILED" in result:
                print(f"   ❌ {result}")
            else:
                print(f"   ⏭️  {result}")
        
        print(f"\n🎉 ENHANCED CONVERSATIONAL FLOW TESTING COMPLETE!")
        
        if passed >= total * 0.8:
            print("🚀 EXCELLENT: Most features working correctly!")
        elif passed >= total * 0.6:
            print("👍 GOOD: Majority of features functional!")
        else:
            print("🔧 NEEDS WORK: Some features need attention!")

def main():
    """Run the comprehensive test suite"""
    
    print("🧪 Enhanced MCP LLM Comprehensive Test Suite")
    print("Testing: Conversation → Automation Detection → Workflows → Parameters → Execution")
    print()
    
    tester = EnhancedMCPTester()
    tester.test_conversational_flow()

if __name__ == "__main__":
    main()
