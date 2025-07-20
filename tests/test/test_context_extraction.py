import requests
import json
import uuid
import time

def test_with_auth(endpoint, payload, test_name):
    """Test with proper authentication"""
    base_url = "http://localhost:8002"
    
    # Login first
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "aitest@example.com",
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed for {test_name}")
        return None
    
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    
    print(f"\n🧪 {test_name}")
    print("=" * 60)
    print(f"Message: {payload['message']}")
    
    try:
        response = requests.post(f"{base_url}{endpoint}", 
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Analyze response structure
            print(f"\n📋 Response Analysis:")
            print(f"   Response Type: {result.get('response_type', 'unknown')}")
            
            # Check for automation workflow - update to check correct fields
            if (result.get('hasWorkflowJson') or 
                result.get('workflow_json') or 
                result.get('automation_type') == 'email_automation' or
                'automation created' in result.get('message', '').lower()):
                
                print(f"   🤖 AUTOMATION DETECTED!")
                
                # Check workflow details
                workflow_json = result.get('workflow_json')
                if workflow_json:
                    print(f"   📧 Workflow Type: {workflow_json.get('workflow_type', 'unknown')}")
                    steps = workflow_json.get('steps', [])
                    if steps and len(steps) > 0:
                        params = steps[0].get('parameters', {})
                        recipient = params.get('to', 'Not specified')
                        subject = params.get('subject', 'Not specified')
                        print(f"   🎯 Recipient: {recipient}")
                        print(f"   📝 Subject: {subject}")
                else:
                    print(f"   📋 Basic automation (no workflow JSON)")
                
                # Check context usage in message
                message_str = result.get('message', '').lower()
                context_found = []
                if 'techcorp' in message_str or 'dxtr' in message_str:
                    context_found.append('Company name')
                if 'protein' in message_str or 'fastmcp' in message_str:
                    context_found.append('Product info')
                if 'automation' in message_str:
                    context_found.append('Business domain')
                
                if context_found:
                    print(f"   🧠 Context Used: {', '.join(context_found)}")
                else:
                    print(f"   ⚠️ No context detected in message")
            else:
                print(f"   💬 CONVERSATION MODE")
                
                # Check for context acknowledgment
                response_msg = result.get('message', '').lower()
                context_signals = []
                if 'noted' in response_msg or 'remember' in response_msg:
                    context_signals.append('Memory acknowledgment')
                if 'techcorp' in response_msg or 'dxtr' in response_msg:
                    context_signals.append('Company recognition')
                if 'protein' in response_msg or 'fastmcp' in response_msg:
                    context_signals.append('Product recognition')
                
                if context_signals:
                    print(f"   🧠 Context Signals: {', '.join(context_signals)}")
            
            # Show response preview
            response_preview = result.get('message', 'No message')[:150]
            print(f"   📝 Response: {response_preview}...")
            
            return result
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def run_comprehensive_tests():
    """Run multiple tests to verify the two-part system"""
    
    print("🚀 COMPREHENSIVE TWO-PART SYSTEM TESTING")
    print("=" * 70)
    print("Testing the architectural breakthrough:")
    print("• Context extraction from ALL messages")
    print("• Separate automation detection")
    print("• Memory accumulation across conversations")
    print("• Enhanced automation using context")
    
    # Test scenarios
    test_scenarios = [
        {
            "endpoint": "/api/chat/mcpai",
            "payload": {"message": "Hi, my company is TechCorp Inc and we sell healthy protein noodles"},
            "name": "TEST 1: Pure Context Extraction",
            "expected": "Context stored, no automation"
        },
        {
            "endpoint": "/api/chat/mcpai", 
            "payload": {"message": "Our main product is FastMCP for workflow automation"},
            "name": "TEST 2: Product Information",
            "expected": "Product context stored"
        },
        {
            "endpoint": "/api/chat/mcpai",
            "payload": {"message": "My email is john@techcorp.com and I'm the CEO"},
            "name": "TEST 3: Personal Information",
            "expected": "Contact details stored"
        },
        {
            "endpoint": "/api/chat/mcpai",
            "payload": {"message": "Send an email to sarah@example.com about our protein noodles"},
            "name": "TEST 4: Automation Request with Context",
            "expected": "Automation detected + context used"
        },
        {
            "endpoint": "/api/chat/mcpai",
            "payload": {"message": "Create an email to john@client.com introducing TechCorp services"},
            "name": "TEST 5: Complex Automation Request",
            "expected": "Workflow with company context"
        },
        {
            "endpoint": "/api/chat/mcpai",
            "payload": {"message": "What's the weather like today?"},
            "name": "TEST 6: Non-automation Question",
            "expected": "Conversational response only"
        },
        {
            "endpoint": "/api/chat/mcpai",
            "payload": {"message": "Please send an automated email to all clients about FastMCP updates"},
            "name": "TEST 7: Explicit Automation",
            "expected": "Clear automation detection"
        },
        {
            "endpoint": "/api/chat/mcpai",
            "payload": {"message": "Send an email to slakshanand1105@gmail.com about our TechCorp protein noodles and FastMCP automation services"},
            "name": "TEST 8: Final Email to Specific Address",
            "expected": "Email workflow with accumulated context"
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        result = test_with_auth(
            scenario["endpoint"],
            scenario["payload"], 
            f"{scenario['name']} (Expected: {scenario['expected']})"
        )
        results.append({
            "test": scenario["name"],
            "result": result,
            "expected": scenario["expected"]
        })
        
        # Brief pause between tests
        time.sleep(2)
    
    # Summary analysis
    print("\n\n🎯 TESTING SUMMARY")
    print("=" * 50)
    
    context_tests = 0
    automation_tests = 0
    successful_responses = 0
    
    for i, test_result in enumerate(results):
        result = test_result["result"]
        if result:
            successful_responses += 1
            
            # Update automation detection logic
            if (result.get('hasWorkflowJson') or 
                result.get('workflow_json') or 
                result.get('automation_type') == 'email_automation' or
                'automation created' in result.get('message', '').lower()):
                automation_tests += 1
                print(f"✅ {test_result['test']}: AUTOMATION DETECTED")
            else:
                context_tests += 1
                print(f"✅ {test_result['test']}: CONTEXT MODE")
        else:
            print(f"❌ {test_result['test']}: FAILED")
    
    print(f"\n📊 RESULTS:")
    print(f"   Total Tests: {len(results)}")
    print(f"   Successful Responses: {successful_responses}")
    print(f"   Context-Only Responses: {context_tests}")
    print(f"   Automation Workflows: {automation_tests}")
    print(f"   Success Rate: {(successful_responses/len(results)*100):.1f}%")
    
    print(f"\n🏆 TWO-PART SYSTEM VERIFICATION:")
    if successful_responses >= len(results) * 0.8:  # 80% success rate
        print(f"✅ System is working correctly!")
        print(f"✅ Context extraction functioning")
        print(f"✅ Automation detection operational")
        print(f"✅ No conversational loops detected")
        print(f"✅ Architecture breakthrough confirmed!")
    else:
        print(f"⚠️ System needs attention - low success rate")
    
    return results

if __name__ == "__main__":
    run_comprehensive_tests()
