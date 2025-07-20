#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/backend")

async def test_direct_email_automation():
    """Test the email automation directly without going through the API"""
    
    try:
        # Import the automation engine directly
        from mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine
        
        print("🧪 Testing Direct Email Automation")
        print("=" * 50)
        
        # Create automation engine
        print("1️⃣ Creating automation engine...")
        automation_engine = AutomationEngine()
        print("✅ Automation engine created")
        
        # Create MCP engine with automation engine
        print("2️⃣ Creating MCP engine with automation...")
        mcp_engine = CustomMCPLLMIterationEngine(
            agent_id="test_agent_123",
            automation_engine=automation_engine
        )
        print("✅ MCP engine created with automation engine")
        
        # Test the workflow execution directly
        print("3️⃣ Testing workflow execution...")
        user_input = "send email to slakshanand1105@gmail.com"
        
        workflow_result = await mcp_engine.execute_workflow(
            "test_email_workflow_123", 
            user_input
        )
        
        print("📊 Workflow execution result:")
        print(f"  - Status: {workflow_result.get('status')}")
        print(f"  - Success: {workflow_result.get('success')}")
        print(f"  - Email sent: {workflow_result.get('email_sent')}")
        print(f"  - Message: {workflow_result.get('message')}")
        
        if workflow_result.get('email_sent'):
            print("🎉 SUCCESS: Email automation is working!")
        else:
            print("❌ ISSUE: Email not sent")
            print(f"Error: {workflow_result.get('error', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct_email_automation())
