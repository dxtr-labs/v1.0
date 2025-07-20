#!/usr/bin/env python3
"""
Test script for MCP Enhanced Workflow System
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_mcp_workflow():
    """Test the MCP workflow generation"""
    try:
        from mcp.mcp_brain import generate_workflow_with_mcp
        
        print("🧪 Testing MCP Workflow Generation...")
        
        # Test cases
        test_cases = [
            {
                "input": "Send an email to john@example.com about the project update",
                "mcp_prompt": "Always be professional and detailed in emails"
            },
            {
                "input": "Schedule a Zoom meeting with alice@company.com tomorrow at 3pm",
                "mcp_prompt": "Default meetings to 60 minutes duration"
            },
            {
                "input": "Send a Slack message to #general channel saying deployment is complete",
                "mcp_prompt": ""
            }
        ]
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n--- Test Case {i} ---")
            print(f"Input: {test['input']}")
            print(f"MCP Prompt: {test['mcp_prompt'] or 'None'}")
            
            result = await generate_workflow_with_mcp(
                test['input'], 
                test['mcp_prompt']
            )
            
            print(f"Success: {result.get('workflow', {}).get('nodes', [])}")
            print(f"Preview nodes: {len(result.get('preview', {}).get('nodes', []))}")
            
            if result.get('error'):
                print(f"Error: {result['error']}")
        
        print("\n✅ MCP Workflow tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_node_specs():
    """Test node specifications"""
    try:
        from mcp.node_spec import NODE_SPECS
        
        print("\n🔧 Testing Node Specifications...")
        print(f"Total node types available: {len(NODE_SPECS)}")
        
        for node_type, spec in NODE_SPECS.items():
            required = spec.get('required', [])
            optional = spec.get('optional', [])
            print(f"- {node_type}: {len(required)} required, {len(optional)} optional fields")
        
        print("✅ Node specs test completed!")
        
    except Exception as e:
        print(f"❌ Node specs test failed: {e}")

def test_preview_generation():
    """Test preview generation for different node types"""
    try:
        from mcp.mcp_brain import generate_workflow_preview
        
        print("\n👁️ Testing Preview Generation...")
        
        # Sample workflow with different node types
        sample_workflow = {
            "nodes": [
                {
                    "id": "email_1",
                    "type": "emailSend",
                    "parameters": {
                        "to": "test@example.com",
                        "subject": "Test Email",
                        "body": "This is a test email."
                    }
                },
                {
                    "id": "zoom_1",
                    "type": "zoomMeeting",
                    "parameters": {
                        "topic": "Test Meeting",
                        "start_time": "2025-07-14T15:00:00",
                        "participants": ["user@example.com"],
                        "duration": 30
                    }
                },
                {
                    "id": "slack_1",
                    "type": "slack",
                    "parameters": {
                        "channel": "#test",
                        "message": "Test message"
                    }
                }
            ],
            "connections": []
        }
        
        preview = generate_workflow_preview(sample_workflow)
        preview_nodes = preview.get('nodes', [])
        
        print(f"Generated preview for {len(preview_nodes)} nodes:")
        for node in preview_nodes:
            print(f"- {node['type']}: {node['preview']['title']}")
        
        print("✅ Preview generation test completed!")
        
    except Exception as e:
        print(f"❌ Preview generation test failed: {e}")

async def main():
    """Run all tests"""
    print("🚀 Starting MCP Enhanced Workflow System Tests")
    print("=" * 50)
    
    # Test node specifications
    test_node_specs()
    
    # Test preview generation
    test_preview_generation()
    
    # Test MCP workflow generation
    await test_mcp_workflow()
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")
    print("\n📋 Next steps:")
    print("1. Start the FastAPI server: python backend/main.py")
    print("2. Open mcp-enhanced-chat.html in your browser")
    print("3. Test the MCP prompt injection and workflow preview")

if __name__ == "__main__":
    asyncio.run(main())
