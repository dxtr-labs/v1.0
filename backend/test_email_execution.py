"""
Test Email Execution with Real Sending
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_email_service import email_service
from mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine

async def test_email_execution():
    """Test email execution with configuration"""
    
    print("🎯 Testing Email Execution")
    print("=" * 50)
    
    # Check if email service is configured
    if not email_service.configured:
        print("❌ Email service not configured")
        print("Please run: python setup_email.py")
        return
    
    # Test email service
    print("🔌 Testing email service...")
    test_result = email_service.test_connection()
    if not test_result["success"]:
        print(f"❌ Email service test failed: {test_result['error']}")
        return
    
    print("✅ Email service is working!")
    
    # Create automation engine
    print("\n🤖 Creating automation engine...")
    engine = CustomMCPLLMIterationEngine("test-agent-email")
    
    # Test email automation with execution
    print("\n📧 Testing email automation with real sending...")
    
    # Create a complete email request
    email_request = "Send email to slakshanand1105@gmail.com with subject 'Test from Automation System' and message 'Hello! This is a test email from your working automation system. The email integration is now functional!'"
    
    print(f"Request: {email_request}")
    
    # Process and execute
    result = await engine.process_with_execution(email_request, auto_execute=True)
    
    print(f"\n📋 Result:")
    print(f"Success: {result.get('success')}")
    print(f"Response: {result.get('response')}")
    
    if "execution" in result:
        execution = result["execution"]
        print(f"Execution Success: {execution.get('success')}")
        if execution.get('success'):
            print("✅ Email was actually sent!")
        else:
            print(f"❌ Email execution failed: {execution.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_email_execution())
