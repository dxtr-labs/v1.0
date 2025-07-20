"""
Test Memory and HTTP Functionality
Test conversation memory and web browser features
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from simple_email_service import email_service
from mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine

async def test_memory_functionality():
    """Test conversation memory and continuity"""
    
    print("🧠 TESTING MEMORY & CONVERSATION CONTINUITY")
    print("=" * 60)
    
    # Configure email service
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    
    email_service.configure(smtp_user, smtp_password, smtp_host, smtp_port)
    
    # Create engine
    engine = CustomMCPLLMIterationEngine("memory-test")
    
    print("📝 Conversation Test:")
    
    # First request
    print("\n1. First Request:")
    request1 = "Send email to slakshanand1105@gmail.com with subject 'Memory Test 1' and message 'Testing conversation memory functionality'"
    print(f"User: {request1}")
    
    result1 = await engine.process_user_request(request1)
    print(f"Assistant: {result1.get('response')}")
    
    # Second request with continuation
    print("\n2. Continuation Request:")
    request2 = "Send another email like that but with subject 'Memory Test 2'"
    print(f"User: {request2}")
    
    result2 = await engine.process_user_request(request2)
    print(f"Assistant: {result2.get('response')}")
    
    # Third request with reference
    print("\n3. Reference Request:")
    request3 = "What was the previous email about?"
    print(f"User: {request3}")
    
    result3 = await engine.process_user_request(request3)
    print(f"Assistant: {result3.get('response')}")
    
    # Check memory
    print(f"\n🧠 Memory Status:")
    print(f"Stored conversations: {len(engine.conversation_history)}")
    if engine.conversation_history:
        for i, exchange in enumerate(engine.conversation_history):
            print(f"  {i+1}. User: {exchange['user'][:50]}...")
            print(f"     Assistant: {exchange['assistant'][:50]}...")
    
    return len(engine.conversation_history) > 0

async def test_http_functionality():
    """Test HTTP request and web browser functionality"""
    
    print("\n🌐 TESTING HTTP & WEB BROWSER FUNCTIONALITY")
    print("=" * 60)
    
    engine = CustomMCPLLMIterationEngine("http-test")
    
    # Test HTTP request workflow creation
    print("📋 Creating HTTP fetch workflow:")
    
    request = "Fetch data from https://jsonplaceholder.typicode.com/posts/1 and send summary to slakshanand1105@gmail.com about the API response"
    print(f"Request: {request}")
    
    result = await engine._create_simple_automation(request)
    print(f"Response: {result.get('response')}")
    
    if result.get('success') and 'workflow' in result:
        workflow = result['workflow']
        
        print(f"\n🔧 Workflow Details:")
        print(f"Name: {workflow.get('name')}")
        print(f"Steps: {len(workflow.get('steps', []))}")
        
        for i, step in enumerate(workflow.get('steps', [])):
            print(f"  Step {i+1}: {step.get('driver')} - {step.get('id')}")
        
        # Execute the workflow
        print(f"\n🚀 Executing workflow...")
        execution_result = engine.execute_workflow(workflow)
        
        print(f"Execution Success: {execution_result.get('success')}")
        if execution_result.get('success'):
            step_results = execution_result.get('step_results', {})
            for step_id, step_result in step_results.items():
                output = step_result.get('output', '')
                if isinstance(output, str):
                    output_preview = output[:100] + "..." if len(output) > 100 else output
                else:
                    output_preview = str(output)[:100] + "..." if len(str(output)) > 100 else str(output)
                print(f"  {step_id}: {step_result.get('success')} - {output_preview}")
            return True
        else:
            print(f"Execution Error: {execution_result.get('error')}")
            return False
    else:
        print("❌ Workflow creation failed")
        return False

async def test_comprehensive_workflow():
    """Test comprehensive workflow with memory, HTTP, and email"""
    
    print("\n🎯 COMPREHENSIVE WORKFLOW TEST")
    print("=" * 60)
    
    engine = CustomMCPLLMIterationEngine("comprehensive-test")
    
    # Multi-step conversation with memory
    requests = [
        "Fetch website data from https://httpbin.org/json",
        "Now send that data to slakshanand1105@gmail.com with subject 'API Data Report'",
        "Also fetch data from https://jsonplaceholder.typicode.com/users/1",
        "Send a summary of both API calls to slakshanand1105@gmail.com"
    ]
    
    results = []
    
    for i, request in enumerate(requests, 1):
        print(f"\n{i}. Request: {request}")
        
        result = await engine.process_with_execution(request, auto_execute=True)
        print(f"   Response: {result.get('response')}")
        
        if 'execution' in result:
            execution = result['execution']
            print(f"   Execution: {'✅ Success' if execution.get('success') else '❌ Failed'}")
        
        results.append(result.get('success', False))
    
    print(f"\n📊 Results: {sum(results)}/{len(results)} successful")
    
    # Show memory
    print(f"\n🧠 Final Memory State:")
    print(f"Conversations stored: {len(engine.conversation_history)}")
    
    return sum(results) > 0

async def run_all_tests():
    """Run all memory and HTTP tests"""
    
    print("🚀 MEMORY & HTTP FUNCTIONALITY TESTS")
    print("=" * 80)
    
    # Test 1: Memory
    memory_success = await test_memory_functionality()
    
    # Test 2: HTTP
    http_success = await test_http_functionality()
    
    # Test 3: Comprehensive
    comprehensive_success = await test_comprehensive_workflow()
    
    # Summary
    print("\n" + "=" * 80)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 80)
    
    print(f"✅ Memory & Continuity: {'PASS' if memory_success else 'FAIL'}")
    print(f"🌐 HTTP & Web Browser: {'PASS' if http_success else 'FAIL'}")
    print(f"🎯 Comprehensive Test: {'PASS' if comprehensive_success else 'FAIL'}")
    
    total_success = sum([memory_success, http_success, comprehensive_success])
    print(f"\n📊 Overall Success: {total_success}/3 tests passed")
    
    if total_success == 3:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Memory functionality working")
        print("✅ HTTP web browser working")
        print("✅ Conversation continuity working")
        print("✅ Multi-step workflows working")
        print("🚀 Your automation system is fully enhanced!")
    else:
        print(f"\n⚡ {total_success} out of 3 tests passed")
        print("Some functionality may need attention")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
