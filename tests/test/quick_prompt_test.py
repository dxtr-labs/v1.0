#!/usr/bin/env python3
"""
Quick Test Script for User Input Prompts
Tests a few key prompts to verify the system is working
"""

import requests
import json
from test_prompts_collection import PROMPT_CATEGORIES

def test_prompt(prompt, category="Test"):
    """Test a single prompt with the backend"""
    url = "http://localhost:8002/api/automation/load-workflow"
    
    # Create a simple workflow structure for testing
    workflow = {
        "id": f"test_{hash(prompt) % 10000}",
        "name": f"Test: {prompt[:30]}...",
        "description": f"Testing user input: {prompt}",
        "user_input": prompt,
        "category": category,
        "nodes": [
            {
                "id": "input_node",
                "type": "manualTrigger",
                "name": "User Input",
                "parameters": {"user_input": prompt}
            }
        ]
    }
    
    try:
        response = requests.post(
            url,
            json={"workflow": workflow, "user_input": prompt},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return True, f"✅ SUCCESS - Workflow ID: {data.get('workflowId', 'N/A')}"
            else:
                return False, f"❌ API Error: {data.get('error', 'Unknown error')}"
        else:
            return False, f"❌ HTTP {response.status_code}: {response.text[:100]}"
            
    except Exception as e:
        return False, f"❌ Exception: {str(e)}"

def run_quick_tests():
    """Run quick tests with sample prompts from each category"""
    print("🚀 Quick User Input Prompt Testing")
    print("=" * 60)
    
    # Select a few key prompts to test
    test_prompts = [
        ("📧 Email", "Send a welcome email to john@example.com"),
        ("✍️ Content", "Generate a blog post about AI automation trends for 2025"),
        ("📊 Data", "Analyze sales data from our CRM and generate a monthly performance report"),
        ("🔄 Complex", "When a new customer registers, send them a welcome email, create a CRM record, and notify the sales team"),
        ("🎯 Edge Case", "Help me with email stuff for our customers"),
        ("🌍 International", "Send email to müller@österreich.at with special pricing")
    ]
    
    results = []
    
    for category, prompt in test_prompts:
        print(f"\n{category}")
        print(f"Prompt: {prompt}")
        print("-" * 50)
        
        success, message = test_prompt(prompt, category)
        results.append((category, success, message))
        print(message)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 QUICK TEST RESULTS")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success, _ in results if success)
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! The system is ready for comprehensive testing.")
        print("\n📋 Next steps:")
        print("1. Run comprehensive tests: python test_workflow_loader_comprehensive.py")
        print("2. Run focused user input tests: python test_multiple_user_inputs.py")
        print("3. Use individual prompts from test_prompts_collection.py")
    else:
        print("\n⚠️ Some tests failed. Check the backend logs for details.")
    
    return results

if __name__ == "__main__":
    results = run_quick_tests()
    
    print(f"\n🎯 SAMPLE PROMPTS TO TEST MANUALLY:")
    print("Copy and paste these into your system:")
    print("-" * 40)
    
    # Show a few more sample prompts for manual testing
    sample_prompts = [
        "Create a newsletter about Q4 updates and send to subscribers@list.com",
        "Convert CSV files from legacy system to JSON format for API integration",
        "When inventory falls below 10 units, automatically reorder from suppliers",
        "Generate FAQ content for customer support knowledge base",
        "Monitor website uptime and send Slack alerts if response time exceeds 5 seconds"
    ]
    
    for i, prompt in enumerate(sample_prompts, 1):
        print(f"{i}. {prompt}")
    
    print(f"\n💡 Total available prompts: 74 (see test_prompts_collection.py)")
