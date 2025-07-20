#!/usr/bin/env python3
"""
Agent Interface Integration Test
Tests the complete flow from workflow loading to agent interaction
"""

import requests
import json
import time
from typing import Dict, Any

class AgentInterfaceTest:
    def __init__(self, base_url: str = "http://localhost:3001"):
        self.base_url = base_url
        self.load_api = f"{base_url}/api/automation/load-workflow"
        
    def print_test_header(self, test_name: str):
        print(f"\n{'='*60}")
        print(f"🧪 {test_name}")
        print(f"{'='*60}")
        
    def test_workflow_retrieval(self, workflow_id: str):
        """Test workflow retrieval from the API"""
        print(f"\n🔍 Testing workflow retrieval for ID: {workflow_id}")
        
        try:
            response = requests.get(f"{self.load_api}?workflowId={workflow_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("workflow"):
                    workflow = data["workflow"]
                    print(f"✅ Retrieved workflow: '{workflow.get('name', 'Unknown')}'")
                    print(f"   📋 Description: {workflow.get('description', 'No description')}")
                    print(f"   🔧 Nodes: {len(workflow.get('nodes', []))}")
                    
                    # Print node details
                    for i, node in enumerate(workflow.get('nodes', []), 1):
                        print(f"      {i}. {node.get('name', 'Unnamed')} ({node.get('type', 'unknown')})")
                    
                    return workflow
                else:
                    print(f"❌ Failed to retrieve workflow: {data}")
                    return None
            else:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Exception during retrieval: {str(e)}")
            return None
    
    def test_agent_url_generation(self, workflow_id: str):
        """Test agent URL generation and access"""
        print(f"\n🔗 Testing agent URL generation for workflow: {workflow_id}")
        
        agent_url = f"{self.base_url}/dashboard/automation/agent?workflowId={workflow_id}&mode=configure"
        print(f"   Generated URL: {agent_url}")
        
        # Test if the URL is accessible (just check if it returns HTML)
        try:
            response = requests.get(agent_url, timeout=10)
            if response.status_code == 200 and "html" in response.headers.get("content-type", "").lower():
                print(f"✅ Agent interface accessible")
                print(f"   📄 Response size: {len(response.text)} characters")
                
                # Check if the page contains expected elements
                page_content = response.text.lower()
                checks = [
                    ("automation agent", "🤖 Agent title found"),
                    ("workflow", "📋 Workflow context found"),
                    ("react", "⚛️ React framework detected"),
                    ("next", "▲ Next.js framework detected")
                ]
                
                for check_text, success_msg in checks:
                    if check_text in page_content:
                        print(f"   {success_msg}")
                
                return True
            else:
                print(f"❌ Agent interface not accessible: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error accessing agent interface: {str(e)}")
            return False
    
    def test_workflow_complexity_handling(self):
        """Test handling of workflows with different complexity levels"""
        self.print_test_header("WORKFLOW COMPLEXITY TESTING")
        
        test_workflows = [
            {
                "name": "Simple 1-Node Workflow",
                "workflow": {
                    "id": "simple_test",
                    "name": "Simple Test",
                    "description": "Basic single-node workflow",
                    "filename": "simple.json",
                    "nodes": [{
                        "id": "node1",
                        "type": "http",
                        "name": "Simple HTTP Request",
                        "parameters": {"url": "https://api.example.com"}
                    }]
                }
            },
            {
                "name": "Medium 5-Node Workflow", 
                "workflow": {
                    "id": "medium_test",
                    "name": "Medium Complexity Test",
                    "description": "Multi-step workflow with various node types",
                    "filename": "medium.json",
                    "nodes": [
                        {"id": "trigger", "type": "webhook", "name": "Webhook Trigger"},
                        {"id": "transform", "type": "transform", "name": "Data Transform"},
                        {"id": "condition", "type": "conditional", "name": "Condition Check"},
                        {"id": "action1", "type": "email", "name": "Send Email"},
                        {"id": "action2", "type": "database", "name": "Update Database"}
                    ]
                }
            },
            {
                "name": "Complex 10-Node Workflow",
                "workflow": {
                    "id": "complex_test",
                    "name": "Complex Multi-Step Process",
                    "description": "Complex workflow with many interconnected nodes",
                    "filename": "complex.json",
                    "nodes": [
                        {"id": f"node_{i}", "type": ["webhook", "http", "ai", "email", "database"][i % 5], 
                         "name": f"Step {i+1}", "parameters": {"step": i+1}} 
                        for i in range(10)
                    ]
                }
            }
        ]
        
        results = []
        for test_case in test_workflows:
            print(f"\n📊 Testing: {test_case['name']}")
            
            # Store workflow
            response = requests.post(self.load_api, json={"workflow": test_case["workflow"]})
            
            if response.status_code == 200:
                data = response.json()
                workflow_id = data.get("workflowId")
                
                if workflow_id:
                    print(f"   ✅ Stored successfully: {workflow_id}")
                    
                    # Test retrieval
                    retrieved = self.test_workflow_retrieval(workflow_id)
                    if retrieved:
                        # Test agent access
                        agent_accessible = self.test_agent_url_generation(workflow_id)
                        results.append({
                            "name": test_case["name"],
                            "stored": True,
                            "retrieved": True,
                            "agent_accessible": agent_accessible,
                            "workflow_id": workflow_id
                        })
                    else:
                        results.append({
                            "name": test_case["name"],
                            "stored": True,
                            "retrieved": False,
                            "agent_accessible": False
                        })
                else:
                    print(f"   ❌ No workflow ID returned")
                    results.append({"name": test_case["name"], "stored": False})
            else:
                print(f"   ❌ Storage failed: {response.status_code}")
                results.append({"name": test_case["name"], "stored": False})
        
        return results
    
    def test_edge_cases(self):
        """Test various edge cases and error conditions"""
        self.print_test_header("EDGE CASE TESTING")
        
        edge_cases = [
            {
                "name": "Empty Workflow",
                "test": lambda: requests.post(self.load_api, json={"workflow": {}}),
                "expected": "Should handle empty workflow gracefully"
            },
            {
                "name": "Missing Nodes Array",
                "test": lambda: requests.post(self.load_api, json={"workflow": {"id": "test", "name": "Test"}}),
                "expected": "Should handle missing nodes"
            },
            {
                "name": "Invalid JSON Structure",
                "test": lambda: requests.post(self.load_api, json={"invalid": "data"}),
                "expected": "Should reject invalid structure"
            },
            {
                "name": "Null Workflow",
                "test": lambda: requests.post(self.load_api, json={"workflow": None}),
                "expected": "Should reject null workflow"
            },
            {
                "name": "Very Large Workflow",
                "test": lambda: requests.post(self.load_api, json={
                    "workflow": {
                        "id": "large_test",
                        "name": "Large Workflow Test",
                        "description": "X" * 10000,  # Large description
                        "nodes": [{"id": f"node_{i}", "type": "http", "name": f"Node {i}", 
                                  "parameters": {"data": "X" * 1000}} for i in range(50)]
                    }
                }),
                "expected": "Should handle large workflows"
            }
        ]
        
        results = []
        for case in edge_cases:
            print(f"\n🔍 Testing: {case['name']}")
            print(f"   Expected: {case['expected']}")
            
            try:
                response = case["test"]()
                print(f"   Response: {response.status_code}")
                
                if response.status_code in [200, 400, 422]:  # Acceptable responses
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            print(f"   ✅ Handled successfully")
                            results.append({"case": case["name"], "result": "success"})
                        else:
                            print(f"   ⚠️ Returned error as expected: {data.get('error', 'Unknown error')}")
                            results.append({"case": case["name"], "result": "expected_error"})
                    else:
                        print(f"   ⚠️ Properly rejected with {response.status_code}")
                        results.append({"case": case["name"], "result": "properly_rejected"})
                else:
                    print(f"   ❌ Unexpected response: {response.status_code}")
                    results.append({"case": case["name"], "result": "unexpected_response"})
                    
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
                results.append({"case": case["name"], "result": "exception"})
        
        return results
    
    def test_url_length_simulation(self):
        """Simulate the original URL length problem and verify solution"""
        self.print_test_header("URL LENGTH PROBLEM SIMULATION")
        
        # Create a workflow that would cause URL length issues
        large_workflow = {
            "id": "url_length_test",
            "name": "URL Length Test Workflow",
            "description": "This workflow simulates the scenario where the URL would be too long",
            "filename": "url_length_test.json",
            "nodes": []
        }
        
        # Add many nodes with complex parameters to simulate large URL
        for i in range(20):
            large_workflow["nodes"].append({
                "id": f"complex_node_{i}",
                "type": ["webhook", "http", "ai", "email", "database", "transform"][i % 6],
                "name": f"Complex Node {i+1}",
                "parameters": {
                    "complex_config": {
                        "nested_data": {
                            "array_items": [f"item_{j}" for j in range(20)],
                            "metadata": {
                                "description": f"Very long description for node {i} that would contribute to URL length issues " * 5,
                                "tags": [f"tag_{j}" for j in range(10)],
                                "configuration": {
                                    "setting_1": "value_with_long_string_" * 10,
                                    "setting_2": [{"nested": f"value_{k}"} for k in range(15)],
                                    "setting_3": "another_very_long_configuration_string_" * 8
                                }
                            }
                        }
                    },
                    "additional_params": {f"param_{k}": f"value_{k}_with_long_text" * 3 for k in range(10)}
                },
                "position": {"x": i * 100, "y": 50 + (i % 5) * 100}
            })
        
        workflow_json = json.dumps(large_workflow)
        encoded_workflow = requests.utils.quote(workflow_json)
        
        # Calculate what the old URL would have been
        old_url = f"/dashboard/automation/agent?workflow={encoded_workflow}"
        old_url_length = len(old_url)
        
        print(f"📏 Simulated original URL length: {old_url_length:,} characters")
        print(f"🚨 HTTP 414 limit is typically around 8,192 characters")
        
        if old_url_length > 8192:
            print(f"✅ This would definitely cause 'URI Too Long' error")
        else:
            print(f"⚠️ Might cause issues depending on server configuration")
        
        # Now test our solution
        print(f"\n🔧 Testing POST-based solution...")
        
        response = requests.post(self.load_api, json={"workflow": large_workflow})
        
        if response.status_code == 200:
            data = response.json()
            workflow_id = data.get("workflowId")
            new_url = data.get("redirectUrl")
            
            print(f"✅ POST solution successful!")
            print(f"   📋 Workflow ID: {workflow_id}")
            print(f"   🔗 New URL: {new_url}")
            print(f"   📏 New URL length: {len(new_url)} characters")
            print(f"   💾 Data reduction: {old_url_length - len(new_url):,} characters saved")
            print(f"   📈 Compression ratio: {((old_url_length - len(new_url)) / old_url_length * 100):.1f}% reduction")
            
            # Test that the new URL works
            if self.test_agent_url_generation(workflow_id):
                print(f"✅ Complete solution verified!")
                return True
            else:
                print(f"❌ Agent interface not accessible")
                return False
        else:
            print(f"❌ POST solution failed: {response.status_code}")
            return False
    
    def run_full_integration_test(self):
        """Run complete integration test suite"""
        print("🎬 STARTING AGENT INTERFACE INTEGRATION TESTS")
        print(f"Testing complete workflow loading and agent interaction flow")
        
        # Test 1: Workflow complexity handling
        complexity_results = self.test_workflow_complexity_handling()
        
        # Test 2: Edge cases
        edge_case_results = self.test_edge_cases()
        
        # Test 3: URL length simulation
        url_solution_works = self.test_url_length_simulation()
        
        # Generate summary report
        self.print_test_header("INTEGRATION TEST SUMMARY")
        
        print("📊 COMPLEXITY TEST RESULTS:")
        for result in complexity_results:
            status = "✅" if result.get("agent_accessible", False) else "❌"
            print(f"   {status} {result['name']}")
            if result.get("workflow_id"):
                print(f"      ID: {result['workflow_id']}")
        
        print(f"\n🔍 EDGE CASE TEST RESULTS:")
        for result in edge_case_results:
            status = "✅" if result["result"] in ["success", "expected_error", "properly_rejected"] else "❌"
            print(f"   {status} {result['case']}: {result['result']}")
        
        print(f"\n🎯 URL LENGTH SOLUTION:")
        status = "✅" if url_solution_works else "❌"
        print(f"   {status} Long URL problem solution")
        
        # Overall assessment
        successful_complexity = sum(1 for r in complexity_results if r.get("agent_accessible", False))
        successful_edge_cases = sum(1 for r in edge_case_results if r["result"] in ["success", "expected_error", "properly_rejected"])
        
        total_complexity = len(complexity_results)
        total_edge_cases = len(edge_case_results)
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   Complexity Tests: {successful_complexity}/{total_complexity} passed")
        print(f"   Edge Case Tests: {successful_edge_cases}/{total_edge_cases} handled properly")
        print(f"   URL Solution: {'Working' if url_solution_works else 'Failed'}")
        
        overall_success_rate = ((successful_complexity + successful_edge_cases + (1 if url_solution_works else 0)) / 
                               (total_complexity + total_edge_cases + 1)) * 100
        
        print(f"   Overall Success Rate: {overall_success_rate:.1f}%")
        
        if overall_success_rate >= 90:
            print(f"\n🎉 EXCELLENT: System is production-ready!")
        elif overall_success_rate >= 75:
            print(f"\n✅ GOOD: System is working well with minor issues")
        elif overall_success_rate >= 60:
            print(f"\n⚠️ FAIR: System needs some improvements")
        else:
            print(f"\n🚨 POOR: System needs significant work")

if __name__ == "__main__":
    tester = AgentInterfaceTest()
    tester.run_full_integration_test()
