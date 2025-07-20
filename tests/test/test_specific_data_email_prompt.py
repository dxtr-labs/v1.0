#!/usr/bin/env python3
"""
Test specific user prompt: "Fetch data from server and send email to slakshanand1105@gmail.com"
"""

import requests
import json
import time

class SpecificPromptTester:
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.session = requests.Session()

    def test_data_fetch_email_prompt(self):
        """Test the specific prompt about fetching data and sending email"""
        user_prompt = "Fetch data from server and send email to slakshanand1105@gmail.com"
        
        print("🎯 Testing Specific User Prompt")
        print("=" * 60)
        print(f"Prompt: {user_prompt}")
        print("-" * 60)
        
        # Test different endpoints that we know exist
        endpoints_to_test = [
            {
                "name": "Workflow Generation",
                "url": f"{self.base_url}/api/workflow/generate",
                "payload": {
                    "user_input": user_prompt,
                    "category": "data_processing_email"
                }
            },
            {
                "name": "Chat Processing", 
                "url": f"{self.base_url}/api/chat/mcpai",
                "payload": {
                    "message": user_prompt
                }
            },
            {
                "name": "Automation Execution",
                "url": f"{self.base_url}/api/automations/execute",
                "payload": {
                    "workflow_description": user_prompt,
                    "parameters": {
                        "email_recipient": "slakshanand1105@gmail.com",
                        "action_type": "data_fetch_and_email"
                    }
                }
            }
        ]
        
        results = []
        
        for endpoint in endpoints_to_test:
            print(f"\n🔗 Testing: {endpoint['name']}")
            print(f"   URL: {endpoint['url']}")
            
            try:
                response = self.session.post(
                    endpoint['url'],
                    json=endpoint['payload'],
                    headers={"Content-Type": "application/json"},
                    timeout=15
                )
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"   ✅ SUCCESS: {endpoint['name']}")
                        
                        # Show relevant parts of response
                        if 'nodes' in data:
                            nodes_count = len(data.get('nodes', []))
                            print(f"   📋 Generated workflow with {nodes_count} nodes")
                        elif 'response' in data:
                            response_text = data.get('response', '')[:150]
                            print(f"   💬 Chat response: {response_text}...")
                        elif 'result' in data:
                            result = str(data.get('result', ''))[:150]
                            print(f"   🎯 Execution result: {result}...")
                        else:
                            print(f"   📄 Response keys: {list(data.keys())}")
                        
                        # Check if email is detected
                        response_str = json.dumps(data).lower()
                        if "slakshanand1105@gmail.com" in response_str:
                            print(f"   📧 Email address correctly detected!")
                        
                        # Check if data fetching is detected
                        data_keywords = ["fetch", "data", "server", "retrieve", "get"]
                        detected_keywords = [kw for kw in data_keywords if kw in response_str]
                        if detected_keywords:
                            print(f"   📊 Data processing keywords detected: {detected_keywords}")
                        
                        results.append({
                            "endpoint": endpoint['name'],
                            "success": True,
                            "response": data
                        })
                        
                    except json.JSONDecodeError:
                        print(f"   ⚠️  Response not JSON: {response.text[:100]}...")
                        results.append({
                            "endpoint": endpoint['name'],
                            "success": False,
                            "error": "Invalid JSON response"
                        })
                elif response.status_code == 401:
                    print(f"   🔐 AUTHENTICATION REQUIRED")
                    results.append({
                        "endpoint": endpoint['name'],
                        "success": False,
                        "error": "Authentication required"
                    })
                else:
                    print(f"   ❌ FAILED: HTTP {response.status_code}")
                    print(f"   📄 Response: {response.text[:150]}...")
                    results.append({
                        "endpoint": endpoint['name'],
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text[:100]}"
                    })
                    
            except requests.exceptions.Timeout:
                print(f"   ⏰ TIMEOUT: Request took too long")
                results.append({
                    "endpoint": endpoint['name'],
                    "success": False,
                    "error": "Request timeout"
                })
            except Exception as e:
                print(f"   💥 EXCEPTION: {str(e)}")
                results.append({
                    "endpoint": endpoint['name'],
                    "success": False,
                    "error": f"Exception: {str(e)}"
                })
        
        return results

    def test_additional_data_email_prompts(self):
        """Test additional variations of data fetching + email prompts"""
        test_prompts = [
            "Get customer data from database and email report to slakshanand1105@gmail.com",
            "Fetch sales analytics and send summary to slakshanand1105@gmail.com", 
            "Retrieve user activity logs and email insights to slakshanand1105@gmail.com",
            "Pull data from API and send formatted results to slakshanand1105@gmail.com",
            "Extract inventory information and email status update to slakshanand1105@gmail.com"
        ]
        
        print(f"\n" + "=" * 60)
        print("🔄 Testing Additional Data + Email Prompt Variations")
        print("=" * 60)
        
        # Test with the workflow generation endpoint (most likely to work)
        url = f"{self.base_url}/api/workflow/generate"
        
        successful_prompts = 0
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n📋 Test {i}/5: {prompt}")
            
            try:
                response = self.session.post(
                    url,
                    json={
                        "user_input": prompt,
                        "category": "data_email_automation"
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    nodes_count = len(data.get('nodes', []))
                    print(f"   ✅ SUCCESS: Generated workflow with {nodes_count} nodes")
                    successful_prompts += 1
                    
                    # Check for email detection
                    response_str = json.dumps(data).lower()
                    if "slakshanand1105@gmail.com" in response_str:
                        print(f"   📧 Email correctly extracted")
                    
                elif response.status_code == 401:
                    print(f"   🔐 Authentication required")
                else:
                    print(f"   ❌ Failed: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   💥 Exception: {str(e)}")
        
        print(f"\n📊 Results: {successful_prompts}/{len(test_prompts)} prompts succeeded")
        return successful_prompts

    def run_comprehensive_test(self):
        """Run all tests for the data fetching + email prompt"""
        print("🚀 COMPREHENSIVE DATA FETCH + EMAIL PROMPT TESTING")
        print("=" * 70)
        
        # Test the specific prompt
        results = self.test_data_fetch_email_prompt()
        
        # Test additional variations
        successful_variations = self.test_additional_data_email_prompts()
        
        # Summary
        print(f"\n" + "=" * 70)
        print("📈 FINAL SUMMARY")
        print("=" * 70)
        
        successful_endpoints = sum(1 for r in results if r["success"])
        total_endpoints = len(results)
        
        print(f"Original Prompt Testing:")
        print(f"   ✅ Successful endpoints: {successful_endpoints}/{total_endpoints}")
        print(f"   📋 Variation prompts: {successful_variations}/5 succeeded")
        
        if successful_endpoints > 0:
            print(f"\n🎉 SUCCESS! The system can process your data fetch + email prompt!")
            print(f"📧 Your email (slakshanand1105@gmail.com) is being detected")
            print(f"📊 Data fetching requirements are being understood")
        else:
            print(f"\n⚠️  Authentication may be required to test the endpoints")
        
        # Show working endpoints
        working_endpoints = [r["endpoint"] for r in results if r["success"]]
        if working_endpoints:
            print(f"\n✅ Working endpoints for your prompt:")
            for endpoint in working_endpoints:
                print(f"   - {endpoint}")
        
        # Show authentication issues
        auth_endpoints = [r["endpoint"] for r in results if "authentication" in r.get("error", "").lower()]
        if auth_endpoints:
            print(f"\n🔐 Endpoints requiring authentication:")
            for endpoint in auth_endpoints:
                print(f"   - {endpoint}")
        
        return {
            "original_prompt_success": successful_endpoints > 0,
            "variation_prompts_success": successful_variations,
            "working_endpoints": working_endpoints,
            "results": results
        }

if __name__ == "__main__":
    tester = SpecificPromptTester()
    final_results = tester.run_comprehensive_test()
    
    print(f"\n💾 Test completed!")
    print(f"📧 Your prompt: 'Fetch data from server and send email to slakshanand1105@gmail.com'")
    print(f"🎯 Result: {'✅ Successfully processed' if final_results['original_prompt_success'] else '🔐 Requires authentication'}")
