#!/usr/bin/env python3
"""
Quick Connectivity Test and Small Batch Validation
Tests basic connectivity and a small sample before running full load test
"""

import requests
import json
import time
from datetime import datetime

def test_connectivity():
    """Test basic connectivity to the MCP API"""
    
    print("🔍 Testing MCP API Connectivity...")
    
    # Test endpoints
    endpoints = [
        ("docs", "http://localhost:8002/docs"),
        ("health", "http://localhost:8002/health"),
        ("mcpai", "http://localhost:8002/api/chat/mcpai")
    ]
    
    for name, url in endpoints:
        try:
            if name == "mcpai":
                # Test POST request
                response = requests.post(
                    url,
                    json={"message": "Hello, testing connectivity"},
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
            else:
                # Test GET request
                response = requests.get(url, timeout=10)
            
            print(f"   {name}: ✅ Status {response.status_code}")
            
            if name == "mcpai" and response.status_code == 200:
                result = response.json()
                print(f"      Response: {result.get('response', 'No response field')[:100]}...")
            
        except Exception as e:
            print(f"   {name}: ❌ Error - {e}")
    
    print()

def run_small_batch_test():
    """Run a small batch test with 10 automation and 10 conversational requests"""
    
    print("🧪 Running Small Batch Test (20 requests)...")
    
    test_requests = [
        ("automation", "Send welcome email to new customers"),
        ("automation", "Search for AI trends online"),
        ("automation", "Process daily sales data"),
        ("automation", "Schedule weekly team meeting"),
        ("automation", "Create customer onboarding workflow"),
        ("automation", "Monitor website uptime"),
        ("automation", "Generate personalized recommendations"),
        ("automation", "Sync CRM and email data"),
        ("automation", "Analyze customer feedback"),
        ("automation", "Set up automated invoicing"),
        ("conversational", "Hi there! How are you?"),
        ("conversational", "What can you help me with?"),
        ("conversational", "Tell me about AI"),
        ("conversational", "How does automation work?"),
        ("conversational", "What services do you provide?"),
        ("conversational", "I'm interested in learning more"),
        ("conversational", "Can you explain workflows?"),
        ("conversational", "What are your capabilities?"),
        ("conversational", "Thank you for your help"),
        ("conversational", "This is very helpful")
    ]
    
    results = []
    start_time = time.time()
    
    for i, (request_type, message) in enumerate(test_requests):
        print(f"   Request {i+1}/20: {request_type} - {message[:40]}...")
        
        try:
            response = requests.post(
                "http://localhost:8002/api/chat/mcpai",
                json={"message": message},
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                results.append({
                    "request_type": request_type,
                    "message": message,
                    "status": result.get("status", "unknown"),
                    "has_workflow": result.get("hasWorkflowJson", False),
                    "success": True
                })
                print(f"      ✅ Status: {result.get('status', 'unknown')}")
            else:
                results.append({
                    "request_type": request_type,
                    "message": message,
                    "error": f"HTTP {response.status_code}",
                    "success": False
                })
                print(f"      ❌ Error: HTTP {response.status_code}")
        
        except Exception as e:
            results.append({
                "request_type": request_type,
                "message": message,
                "error": str(e),
                "success": False
            })
            print(f"      ❌ Error: {e}")
        
        time.sleep(0.5)  # Small delay between requests
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Analyze results
    successful = len([r for r in results if r.get("success")])
    automation_results = [r for r in results if r.get("request_type") == "automation"]
    conversation_results = [r for r in results if r.get("request_type") == "conversational"]
    
    automation_successful = len([r for r in automation_results if r.get("success")])
    conversation_successful = len([r for r in conversation_results if r.get("success")])
    
    automation_detected = len([r for r in automation_results if r.get("success") and r.get("status") not in ["conversational"]])
    workflows_generated = len([r for r in automation_results if r.get("success") and r.get("has_workflow")])
    
    print(f"\n📊 Small Batch Test Results:")
    print(f"   • Total Requests: 20")
    print(f"   • Successful: {successful}/20 ({(successful/20)*100:.1f}%)")
    print(f"   • Duration: {duration:.2f} seconds")
    print(f"   • Rate: {20/duration:.2f} req/sec")
    print(f"   • Automation Success: {automation_successful}/10")
    print(f"   • Conversation Success: {conversation_successful}/10")
    print(f"   • Automation Detected: {automation_detected}/10")
    print(f"   • Workflows Generated: {workflows_generated}/10")
    print()
    
    if successful >= 18:  # 90% success rate
        print("✅ System appears healthy for mass testing!")
        return True
    else:
        print("❌ System has issues - investigate before mass testing")
        return False

def main():
    """Main test function"""
    
    print("🚀 MCP System Validation Test")
    print("=" * 50)
    
    # Test connectivity
    test_connectivity()
    
    # Run small batch test
    system_healthy = run_small_batch_test()
    
    if system_healthy:
        print("🎯 RECOMMENDATION: System is ready for mass load testing!")
        print("   You can now run: python test_simple_mass_1000.py")
    else:
        print("⚠️ RECOMMENDATION: Fix system issues before mass testing")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
