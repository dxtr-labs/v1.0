import requests
import json
import uuid

def test_two_part_system():
    """Test the complete OpenAI-powered two-part system"""
    
    # Test cases to demonstrate the system
    test_cases = [
        {
            'name': '🧠 CONTEXT EXTRACTION ONLY',
            'message': 'Hello, my company name is TechCorp Inc and we sell healthy protein noodles. My email is john@techcorp.com. We are a food technology company.',
            'expected': 'Should extract context but no automation'
        },
        {
            'name': '🤖 AUTOMATION + CONTEXT',
            'message': 'Hi, my company name is TechCorp Inc. Please send an email to customer@example.com about our new protein noodle product launch.',
            'expected': 'Should extract context AND create email automation'
        },
        {
            'name': '💭 GENERAL CONVERSATION',
            'message': 'Hello, how are you today? What can you help me with?',
            'expected': 'Should be conversational with no context or automation'
        }
    ]
    
    print("🚀 TESTING COMPLETE TWO-PART SYSTEM")
    print("=" * 60)
    
    # Generate agent ID for testing
    agent_id = str(uuid.uuid4())
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['name']}")
        print(f"📝 Message: {test['message']}")
        print(f"🎯 Expected: {test['expected']}")
        
        try:
            response = requests.post(
                f'http://localhost:8002/api/test/agents/{agent_id}/chat', 
                json={'message': test['message']}, 
                timeout=25
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ Status: {response.status_code}")
                print(f"🔄 Response Type: {result.get('status', 'unknown')}")
                print(f"📄 Response: {result.get('response', 'No response')[:120]}...")
                print(f"💾 Context Stored: {result.get('context_stored', False)}")
                print(f"📋 Context Summary: {result.get('context_summary', 'None')}")
                print(f"⚙️ Has Workflow: {result.get('hasWorkflowJson', False)}")
                
                if result.get('hasWorkflowJson'):
                    workflow = result.get('workflow_json', {})
                    print(f"🎯 Workflow Type: {workflow.get('workflow_type', 'unknown')}")
                    print(f"📧 Automation Summary: {workflow.get('automation_summary', 'None')}")
                
            else:
                print(f"❌ Error {response.status_code}: {response.text[:100]}...")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        print("-" * 60)
    
    print(f"\n🔍 Check server logs for detailed debug information!")

if __name__ == "__main__":
    test_two_part_system()
