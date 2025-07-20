#!/usr/bin/env python3
"""
Test Automation Engine Integration - Direct test of workflow execution
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_automation_engine_integration():
    """Test if automation engine can execute email workflows"""
    print("🧪 Testing Automation Engine Integration")
    print("=" * 50)
    
    try:
        # Import the automation engine
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from backend.mcp.automation_engine import AutomationEngine
        from backend.core.database_manager import DatabaseManager
        
        # Initialize database manager
        db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'autoflow',
            'user': 'autoflow_user',
            'password': 'autoflow_password123'
        }
        
        print("🔗 Connecting to database...")
        db_manager = DatabaseManager(db_config)
        await db_manager.initialize()
        
        # Initialize automation engine
        print("🚀 Initializing automation engine...")
        automation_engine = AutomationEngine(db_config)
        
        # Create a test email workflow
        test_workflow = {
            "workflow": {
                "trigger": {
                    "node": "immediate",
                    "parameters": {
                        "trigger_type": "manual",
                        "user_input": "test email automation"
                    }
                },
                "actions": [
                    {
                        "node": "emailSend",
                        "parameters": {
                            "to": "slakshanand1105@gmail.com",
                            "subject": "🧪 Test Email from Automation Engine",
                            "body": "This is a test email sent directly through the automation engine to verify integration works.",
                            "from": "automation-engine@dxtr-labs.com"
                        }
                    }
                ],
                "logic": []
            }
        }
        
        print("📧 Executing test email workflow...")
        print(f"Target: slakshanand1105@gmail.com")
        print(f"Subject: 🧪 Test Email from Automation Engine")
        
        # Execute the workflow
        result = await automation_engine.execute_workflow(test_workflow, "test_user_123")
        
        print("\n📊 Execution Result:")
        print(f"Status: {result.get('status', 'UNKNOWN')}")
        print(f"Message: {result.get('message', 'No message')}")
        print(f"Success: {result.get('success', False)}")
        
        if result.get('status') == 'success':
            print("✅ SUCCESS: Automation engine executed email workflow successfully!")
            print("📧 Check your email inbox for the test message")
        else:
            print("❌ FAILED: Automation engine execution failed")
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        # Close database connection
        await db_manager.close()
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure all required modules are available")
    except Exception as e:
        print(f"❌ Test Error: {e}")
        print(f"💡 Error details: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_automation_engine_integration())
