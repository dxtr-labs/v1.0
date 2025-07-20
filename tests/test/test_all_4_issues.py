#!/usr/bin/env python3
"""
Comprehensive test for all 4 identified issues:
1. AI box only appearing with specific keywords (not for every prompt)
2. Clean workflow preview (not raw JSON)
3. Better LLM understanding and node selection
4. Automation execution working properly
"""

import asyncio
import aiohttp
import json
import sys

# Test configuration
BASE_URL = "http://localhost:8002"
TEST_EMAIL = "test@example.com"

class TestSuite:
    def __init__(self):
        self.session = None
        self.auth_token = None

    async def setup(self):
        """Setup test session and authentication"""
        self.session = aiohttp.ClientSession()
        
        # First try to register a test user
        signup_data = {
            "email": "test@example.com",
            "password": "password123",
            "firstName": "Test",
            "lastName": "User"
        }
        
        async with self.session.post(f"{BASE_URL}/api/auth/signup", json=signup_data) as response:
            if response.status == 200:
                print("✅ Test user created successfully")
            elif response.status == 400:
                print("ℹ️ Test user already exists")
            else:
                print(f"⚠️ User creation status: {response.status}")
        
        # Now login to get auth token
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        async with self.session.post(f"{BASE_URL}/api/auth/login", json=login_data) as response:
            if response.status == 200:
                result = await response.json()
                self.auth_token = result.get("token")
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status}")
                result = await response.text()
                print(f"Response: {result}")
                return False

    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()

    async def test_issue_1_ai_keyword_specificity(self):
        """Test Issue 1: AI box should only appear for specific AI + automation keywords"""
        print("\n🔍 Testing Issue 1: AI Keyword Specificity")
        
        test_cases = [
            {
                "message": "Hello, how are you?",
                "should_trigger_ai_selection": False,
                "description": "General greeting"
            },
            {
                "message": "What's the weather like?",
                "should_trigger_ai_selection": False,
                "description": "Simple question"
            },
            {
                "message": "Can you help me with something?",
                "should_trigger_ai_selection": False,
                "description": "General help request"
            },
            {
                "message": "Using AI, send an email to test@example.com",
                "should_trigger_ai_selection": True,
                "description": "AI + email automation"
            },
            {
                "message": "Use AI to generate content and email it to john@company.com",
                "should_trigger_ai_selection": True,
                "description": "AI content generation + email"
            }
        ]
        
        for case in test_cases:
            print(f"  Testing: {case['description']}")
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "message": case["message"],
                "agentId": "test-agent",
                "agentConfig": {
                    "name": "Test Agent",
                    "role": "assistant",
                    "personality": {},
                    "llm_config": {}
                }
            }
            
            async with self.session.post(f"{BASE_URL}/api/mcpai/chat", headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    has_ai_selection = result.get("status") == "ai_service_selection"
                    
                    if has_ai_selection == case["should_trigger_ai_selection"]:
                        print(f"    ✅ Correct behavior: {'AI selection triggered' if has_ai_selection else 'No AI selection'}")
                    else:
                        print(f"    ❌ Wrong behavior: Expected {'AI selection' if case['should_trigger_ai_selection'] else 'no AI selection'}, got {'AI selection' if has_ai_selection else 'no AI selection'}")
                else:
                    print(f"    ❌ Request failed: {response.status}")

    async def test_issue_2_clean_workflow_preview(self):
        """Test Issue 2: Clean workflow preview instead of raw JSON"""
        print("\n🔍 Testing Issue 2: Clean Workflow Preview")
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test with service selection to get workflow preview
        data = {
            "message": f"service:inhouse Using AI, send an email to {TEST_EMAIL} with a welcome message",
            "agentId": "test-agent",
            "agentConfig": {
                "name": "Test Agent",
                "role": "assistant",
                "personality": {},
                "llm_config": {}
            }
        }
        
        async with self.session.post(f"{BASE_URL}/api/mcpai/chat", headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                
                if result.get("status") == "workflow_preview":
                    workflow_preview = result.get("workflow_preview", {})
                    
                    # Check for clean preview structure
                    has_title = "title" in workflow_preview
                    has_description = "description" in workflow_preview
                    has_steps = "steps" in workflow_preview and isinstance(workflow_preview["steps"], list)
                    has_estimated_credits = "estimated_credits" in workflow_preview
                    
                    # Check that steps have proper structure
                    steps_valid = True
                    if has_steps:
                        for step in workflow_preview["steps"]:
                            if not all(key in step for key in ["step", "action", "details", "icon"]):
                                steps_valid = False
                                break
                    
                    if has_title and has_description and has_steps and has_estimated_credits and steps_valid:
                        print("    ✅ Clean workflow preview structure detected")
                        print(f"    ✅ Title: {workflow_preview.get('title')}")
                        print(f"    ✅ Steps: {len(workflow_preview.get('steps', []))} steps")
                        print(f"    ✅ Credits: {workflow_preview.get('estimated_credits')}")
                    else:
                        print("    ❌ Workflow preview structure incomplete")
                        print(f"    Has title: {has_title}")
                        print(f"    Has description: {has_description}")
                        print(f"    Has steps: {has_steps}")
                        print(f"    Steps valid: {steps_valid}")
                else:
                    print(f"    ❌ Expected workflow_preview status, got: {result.get('status')}")
            else:
                print(f"    ❌ Request failed: {response.status}")

    async def test_issue_3_llm_understanding(self):
        """Test Issue 3: Better LLM understanding and node selection"""
        print("\n🔍 Testing Issue 3: Enhanced LLM Understanding")
        
        test_cases = [
            {
                "message": f"service:inhouse Generate a marketing email using AI and send it to {TEST_EMAIL}",
                "expected_nodes": ["mcpLLM", "emailSend"],
                "description": "AI content + email automation"
            },
            {
                "message": f"service:openai Create promotional content with AI and email to {TEST_EMAIL}",
                "expected_nodes": ["openai", "emailSend"],
                "description": "OpenAI content + email"
            },
            {
                "message": f"service:claude Write a professional message using AI and send to {TEST_EMAIL}",
                "expected_nodes": ["claude", "emailSend"],
                "description": "Claude content + email"
            }
        ]
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        for case in test_cases:
            print(f"  Testing: {case['description']}")
            
            data = {
                "message": case["message"],
                "agentId": "test-agent",
                "agentConfig": {
                    "name": "Test Agent",
                    "role": "assistant", 
                    "personality": {},
                    "llm_config": {}
                }
            }
            
            async with self.session.post(f"{BASE_URL}/api/mcpai/chat", headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    if result.get("status") == "workflow_preview":
                        workflow_json = result.get("workflow_json", {})
                        actions = workflow_json.get("workflow", {}).get("actions", [])
                        
                        detected_nodes = [action.get("node") for action in actions]
                        
                        # Check if expected nodes are present
                        nodes_match = all(node in detected_nodes for node in case["expected_nodes"])
                        
                        if nodes_match:
                            print(f"    ✅ Correct nodes selected: {detected_nodes}")
                        else:
                            print(f"    ❌ Wrong nodes: Expected {case['expected_nodes']}, got {detected_nodes}")
                    else:
                        print(f"    ❌ Unexpected status: {result.get('status')}")
                else:
                    print(f"    ❌ Request failed: {response.status}")

    async def test_issue_4_automation_execution(self):
        """Test Issue 4: Automation execution actually works"""
        print("\n🔍 Testing Issue 4: Automation Execution")
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # First, create a workflow
        workflow_json = {
            "workflow": {
                "trigger": {
                    "node": "manual",
                    "parameters": {}
                },
                "logic": [],
                "actions": [
                    {
                        "node": "mcpLLM",
                        "parameters": {
                            "user_input": "Write a brief welcome message",
                            "context": "ai_content_generation"
                        }
                    },
                    {
                        "node": "emailSend",
                        "parameters": {
                            "toEmail": TEST_EMAIL,
                            "subject": "Test Email from DXTR Labs (MCP LLM)",
                            "text": "{ai_generated_content}"
                        }
                    }
                ]
            }
        }
        
        # Test workflow confirmation endpoint
        confirm_data = {
            "workflow_json": workflow_json,
            "agentId": "test-agent",
            "confirmed": True
        }
        
        print("  Attempting to execute workflow via confirmation endpoint...")
        
        async with self.session.post(f"{BASE_URL}/api/workflow/confirm", headers=headers, json=confirm_data) as response:
            print(f"  Response status: {response.status}")
            
            if response.status == 200:
                result = await response.json()
                
                if result.get("success"):
                    print("    ✅ Workflow execution successful!")
                    print(f"    ✅ Message: {result.get('message')}")
                    
                    execution_details = result.get("execution_details", {})
                    if execution_details.get("status") == "success":
                        print("    ✅ Automation engine reported success")
                    else:
                        print(f"    ⚠️ Automation engine status: {execution_details.get('status')}")
                else:
                    print(f"    ❌ Workflow execution failed: {result}")
            else:
                response_text = await response.text()
                print(f"    ❌ Request failed: {response.status} - {response_text}")

    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting comprehensive test suite for all 4 issues")
        
        if not await self.setup():
            print("❌ Setup failed, aborting tests")
            return
        
        try:
            await self.test_issue_1_ai_keyword_specificity()
            await self.test_issue_2_clean_workflow_preview()
            await self.test_issue_3_llm_understanding()
            await self.test_issue_4_automation_execution()
            
            print("\n🏁 Test suite completed!")
            
        except Exception as e:
            print(f"❌ Test suite failed with error: {e}")
        finally:
            await self.cleanup()

async def main():
    test_suite = TestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
