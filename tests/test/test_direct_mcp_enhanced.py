#!/usr/bin/env python3
"""
Simple Enhanced MCP Test - Direct Backend Testing
Test the enhanced conversational flow by calling MCP methods directly
"""

import sys
import os
import asyncio
import logging

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from mcp.custom_mcp_llm_iteration import CustomMCPLLMIteration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DirectMCPTester:
    def __init__(self):
        """Initialize the MCP tester with direct backend access"""
        self.mcp_instance = None
        
    async def setup_mcp(self):
        """Setup MCP instance"""
        try:
            # Create MCP instance
            self.mcp_instance = CustomMCPLLMIteration(
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                agent_data={
                    'agent_name': 'Test Assistant',
                    'agent_role': 'Automation Expert',
                    'agent_id': 'test_123'
                }
            )
            print("✅ MCP Instance created successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to create MCP instance: {e}")
            return False
    
    async def test_conversational_flow(self):
        """Test the enhanced conversational flow"""
        
        print("🚀 Direct Enhanced MCP Testing")
        print("=" * 50)
        
        if not await self.setup_mcp():
            print("❌ Setup failed, cannot proceed with tests")
            return
        
        # Test 1: Normal Conversation
        print("\n1️⃣ Testing Normal Conversation...")
        await self._test_conversation()
        
        # Test 2: Automation Detection
        print("\n2️⃣ Testing Automation Detection...")
        await self._test_automation_detection()
        
        # Test 3: ASU Bus Automation
        print("\n3️⃣ Testing ASU Bus Automation...")
        await self._test_asu_bus_automation()
        
        # Test 4: Enhanced Pattern Detection
        print("\n4️⃣ Testing Enhanced Pattern Detection...")
        await self._test_pattern_detection()
        
        print("\n✅ Direct MCP Testing Complete!")
    
    async def _test_conversation(self):
        """Test normal conversational responses"""
        
        conversational_inputs = [
            "Hi there! How are you doing today?",
            "What can you help me with?",
            "Nice to meet you!"
        ]
        
        for i, message in enumerate(conversational_inputs, 1):
            print(f"   Test 1.{i}: '{message}'")
            
            try:
                result = await self.mcp_instance.process_user_request(message)
                
                status = result.get('status', 'unknown')
                response = result.get('response', '')
                
                if status == 'conversational':
                    print(f"      ✅ Conversational: {response[:100]}...")
                else:
                    print(f"      ⚠️ Status: {status}")
                    print(f"         Response: {response[:100]}...")
                    
            except Exception as e:
                print(f"      ❌ Error: {e}")
    
    async def _test_automation_detection(self):
        """Test automation detection"""
        
        automation_inputs = [
            "Send an email to john@example.com about the meeting",
            "Search for competitor prices online",
            "Create a workflow to process data"
        ]
        
        for i, message in enumerate(automation_inputs, 1):
            print(f"   Test 2.{i}: '{message}'")
            
            try:
                result = await self.mcp_instance.process_user_request(message)
                
                status = result.get('status', 'unknown')
                has_workflow = result.get('hasWorkflowJson', False)
                workflow_type = ''
                
                if has_workflow:
                    workflow_json = result.get('workflow_json', {})
                    workflow_type = workflow_json.get('workflow_type', 'unknown')
                
                if status in ['automation_ready', 'workflow_confirmation', 'parameter_collection']:
                    print(f"      ✅ Automation detected: {status}")
                    if has_workflow:
                        print(f"         🔧 Workflow: {workflow_type}")
                else:
                    print(f"      ⚠️ Status: {status}")
                    
            except Exception as e:
                print(f"      ❌ Error: {e}")
    
    async def _test_asu_bus_automation(self):
        """Test ASU bus automation specifically"""
        
        bus_inputs = [
            "search asu bus shuttle website and fetch bus data from there and send email to test@asu.edu when is the next bus",
            "asu bus schedule information",
            "when is the next shuttle to tempe campus"
        ]
        
        for i, message in enumerate(bus_inputs, 1):
            print(f"   Test 3.{i}: '{message[:50]}...'")
            
            try:
                result = await self.mcp_instance.process_user_request(message)
                
                status = result.get('status', 'unknown')
                workflow_json = result.get('workflow_json', {})
                workflow_type = workflow_json.get('workflow_type', '')
                
                if workflow_type == 'asu_bus_automation':
                    print(f"      ✅ ASU Bus automation detected!")
                    steps = workflow_json.get('steps', [])
                    print(f"         🚌 Steps: {len(steps)}")
                    
                    # Check for required steps
                    actions = [step.get('action') for step in steps]
                    print(f"         🔧 Actions: {actions}")
                    
                elif status in ['automation_ready', 'workflow_confirmation']:
                    print(f"      ✅ Automation created: {workflow_type or 'generic'}")
                else:
                    print(f"      ⚠️ Status: {status}")
                    
            except Exception as e:
                print(f"      ❌ Error: {e}")
    
    async def _test_pattern_detection(self):
        """Test enhanced pattern detection"""
        
        pattern_inputs = [
            "email automation test",
            "web search for information",
            "schedule a meeting",
            "data processing task"
        ]
        
        for i, message in enumerate(pattern_inputs, 1):
            print(f"   Test 4.{i}: '{message}'")
            
            try:
                # Test the pattern detection method directly
                if hasattr(self.mcp_instance, '_enhanced_pattern_detection'):
                    pattern_result = await self.mcp_instance._enhanced_pattern_detection(message)
                    
                    is_automation = pattern_result.get('is_automation', False)
                    automation_type = pattern_result.get('automation_type', 'none')
                    confidence = pattern_result.get('confidence', 0.0)
                    
                    if is_automation:
                        print(f"      ✅ Pattern detected: {automation_type} (confidence: {confidence})")
                    else:
                        print(f"      ❌ No automation pattern detected")
                else:
                    print(f"      ⚠️ Pattern detection method not found")
                    
            except Exception as e:
                print(f"      ❌ Error: {e}")

async def main():
    """Run the direct MCP tests"""
    
    print("🧪 Direct Enhanced MCP Testing Suite")
    print("Testing enhanced conversational flow without API authentication")
    print()
    
    tester = DirectMCPTester()
    await tester.test_conversational_flow()

if __name__ == "__main__":
    asyncio.run(main())
