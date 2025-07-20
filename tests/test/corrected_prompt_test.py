#!/usr/bin/env python3
"""
Corrected User Input Prompt Testing
Using the correct backend endpoints
"""

import requests
import json
from test_prompts_collection import PROMPT_CATEGORIES

def test_workflow_generation(prompt, category="Test"):
    """Test workflow generation with user prompt"""
    url = "http://localhost:8002/api/workflow/generate"
    
    payload = {
        "user_input": prompt,
        "category": category,
        "context": {
            "prompt_type": "user_request",
            "source": "prompt_testing"
        }
    }
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            return True, f"✅ SUCCESS - Generated workflow with {len(data.get('nodes', []))} nodes"
        else:
            return False, f"❌ HTTP {response.status_code}: {response.text[:150]}"
            
    except Exception as e:
        return False, f"❌ Exception: {str(e)}"

def test_chat_endpoint(prompt):
    """Test the chat endpoint for user input processing"""
    url = "http://localhost:8002/api/chat/mcpai"
    
    payload = {
        "message": prompt,
        "context": "workflow_creation"
    }
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            return True, f"✅ CHAT SUCCESS - Response: {data.get('response', '')[:100]}..."
        else:
            return False, f"❌ HTTP {response.status_code}: {response.text[:150]}"
            
    except Exception as e:
        return False, f"❌ Exception: {str(e)}"

def test_automation_execution(prompt):
    """Test automation execution endpoint"""
    url = "http://localhost:8002/api/automations/execute"
    
    payload = {
        "automation_type": "user_input_workflow",
        "parameters": {
            "user_input": prompt,
            "auto_generate": True
        }
    }
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            return True, f"✅ AUTOMATION SUCCESS - Status: {data.get('status', 'unknown')}"
        else:
            return False, f"❌ HTTP {response.status_code}: {response.text[:150]}"
            
    except Exception as e:
        return False, f"❌ Exception: {str(e)}"

def run_comprehensive_prompt_tests():
    """Run comprehensive tests with multiple endpoints"""
    print("🎯 Comprehensive User Input Prompt Testing")
    print("Testing multiple backend endpoints with user prompts")
    print("=" * 70)
    
    # Select key prompts for testing
    test_prompts = [
        ("📧 Email", "Send a welcome email to john@example.com"),
        ("✍️ Content", "Generate a blog post about AI automation trends"),
        ("📊 Data", "Analyze sales data and create a report"),
        ("🔄 Complex", "When customer registers, send email and create CRM record"),
        ("🎯 Simple", "Create a workflow for sending emails"),
        ("🌍 International", "Send email to müller@test.com")
    ]
    
    all_results = []
    
    for category, prompt in test_prompts:
        print(f"\n{category}: {prompt}")
        print("-" * 60)
        
        # Test 1: Workflow Generation
        success1, msg1 = test_workflow_generation(prompt, category)
        print(f"Workflow Generation: {msg1}")
        
        # Test 2: Chat Endpoint
        success2, msg2 = test_chat_endpoint(prompt)
        print(f"Chat Processing: {msg2}")
        
        # Test 3: Automation Execution
        success3, msg3 = test_automation_execution(prompt)
        print(f"Automation Execution: {msg3}")
        
        # Calculate success for this prompt
        prompt_success = (success1 + success2 + success3) / 3
        all_results.append((category, prompt, prompt_success, (success1, success2, success3)))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 70)
    
    total_prompts = len(all_results)
    total_tests = total_prompts * 3  # 3 endpoints per prompt
    successful_tests = sum(sum(results[3]) for results in all_results)
    
    print(f"Total Prompts Tested: {total_prompts}")
    print(f"Total Endpoint Tests: {total_tests}")
    print(f"✅ Successful Tests: {successful_tests}")
    print(f"❌ Failed Tests: {total_tests - successful_tests}")
    print(f"📈 Overall Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    print(f"\n📋 Per-Prompt Results:")
    for category, prompt, success_rate, (s1, s2, s3) in all_results:
        status = "✅" if success_rate > 0.5 else "⚠️" if success_rate > 0 else "❌"
        print(f"{status} {category}: {success_rate*100:.0f}% success")
        print(f"    Workflow: {'✅' if s1 else '❌'} | Chat: {'✅' if s2 else '❌'} | Automation: {'✅' if s3 else '❌'}")
    
    if successful_tests > 0:
        print(f"\n🎉 System is processing user inputs!")
        print(f"📝 Working endpoints found - you can now test with these prompts:")
        
        # Show which endpoints work
        working_endpoints = []
        endpoint_names = ["Workflow Generation", "Chat Processing", "Automation Execution"]
        endpoint_successes = [0, 0, 0]
        
        for _, _, _, (s1, s2, s3) in all_results:
            endpoint_successes[0] += s1
            endpoint_successes[1] += s2
            endpoint_successes[2] += s3
        
        for i, (name, success_count) in enumerate(zip(endpoint_names, endpoint_successes)):
            if success_count > 0:
                working_endpoints.append(f"{name}: {success_count}/{total_prompts} prompts worked")
        
        for endpoint in working_endpoints:
            print(f"   ✅ {endpoint}")
    else:
        print(f"\n⚠️ No endpoints are processing user inputs correctly.")
        print(f"Check backend logs and API documentation at http://localhost:8002/docs")
    
    return all_results

def show_sample_prompts_for_manual_testing():
    """Show sample prompts for manual testing"""
    print(f"\n🧪 SAMPLE PROMPTS FOR MANUAL TESTING:")
    print("=" * 50)
    print("Copy these prompts and test them manually:")
    print()
    
    # Get sample prompts from each category
    samples = []
    for category_name, prompts in PROMPT_CATEGORIES.items():
        if prompts:  # If category has prompts
            samples.append((category_name, prompts[0]))  # Take first prompt
    
    for i, (category, prompt) in enumerate(samples, 1):
        print(f"{i:2d}. {category}")
        print(f"    \"{prompt}\"")
        print()
    
    print("💡 More prompts available in test_prompts_collection.py (74 total)")
    print("🔗 Backend API docs: http://localhost:8002/docs")

if __name__ == "__main__":
    # Run comprehensive tests
    results = run_comprehensive_prompt_tests()
    
    # Show manual testing samples
    show_sample_prompts_for_manual_testing()
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. Check which endpoints work from the results above")
    print("2. Use working endpoints to test the 74 prompts from test_prompts_collection.py")
    print("3. Test prompt categories: Email, Content, Data, Complex Automation, Edge Cases")
    print("4. Verify the system correctly identifies intent and extracts parameters")
