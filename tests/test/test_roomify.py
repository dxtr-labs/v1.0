import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.mcp.simple_mcp_llm import MCP_LLM_Orchestrator

async def test_roomify_request():
    """Test the Roomify AI request that should now work correctly"""
    
    # Initialize the orchestrator
    orchestrator = MCP_LLM_Orchestrator()
    
    print("🏠 Testing Roomify AI request...")
    
    # Test the exact Roomify request
    user_message_with_service = "service:inhouse Using AI generate a sales pitch for roomify- one stop place for college students to find roommates and send to slakshanand1105@gmail.com"
    result = await orchestrator.process_user_input("test_user", "test_agent", user_message_with_service)
    
    print(f"Result Status: {result.get('status', 'Unknown')}")
    
    # Debug: Print all result keys and some values
    print(f"\n🔍 Debug - All result keys: {list(result.keys())}")
    
    if result.get('workflow_preview'):
        print(f"\n📧 WORKFLOW PREVIEW:")
        print(result['workflow_preview'])
    
    if result.get('workflow_preview') and result['workflow_preview'].get('email_preview'):
        preview = result['workflow_preview']['email_preview']
        print("\n📧 EMAIL PREVIEW DETAILS:")
        print(f"TO: {preview.get('to', 'Unknown')}")
        print(f"SUBJECT: {preview.get('subject', 'Unknown')}")
        print(f"AI SERVICE: {preview.get('ai_service', 'Unknown')}")
        print("\nGENERATED CONTENT:")
        print(preview.get('preview_content', 'No content'))
    
    if result.get('workflow_steps'):
        print(f"\n✅ Workflow generated with {len(result['workflow_steps'])} steps:")
        for i, step in enumerate(result['workflow_steps'], 1):
            print(f"  Step {i}: {step.get('action', 'Unknown action')}")

if __name__ == "__main__":
    asyncio.run(test_roomify_request())
