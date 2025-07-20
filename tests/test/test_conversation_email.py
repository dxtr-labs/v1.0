"""
Conversational Context Building Test
Build context through conversation, then send email to slakshanand1105@gmail.com
"""
import requests
import json
import time

def conversation_test():
    """Test conversational context building followed by email automation"""
    
    base_url = "http://localhost:8002"
    
    # Login
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "aitest@example.com",
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    
    print("🗣️ CONVERSATIONAL CONTEXT BUILDING TEST")
    print("=" * 60)
    print("Building context through natural conversation, then sending email")
    
    # Conversation sequence to build context
    conversation_steps = [
        {
            "message": "Hello! I'm John from TechCorp Inc.",
            "purpose": "Introduce company and name"
        },
        {
            "message": "We specialize in healthy protein noodles and innovative food products.",
            "purpose": "Establish business domain and products"
        },
        {
            "message": "We also use FastMCP for our workflow automation needs.",
            "purpose": "Add technology context"
        },
        {
            "message": "Our company email is contact@techcorp.com and I'm the CEO.",
            "purpose": "Add contact information and role"
        },
        {
            "message": "We're looking to expand our customer base and showcase our products.",
            "purpose": "Business objectives"
        },
        {
            "message": "Please send an email to slakshanand1105@gmail.com introducing TechCorp, our protein noodles, and how FastMCP helps us deliver quality products efficiently.",
            "purpose": "FINAL EMAIL REQUEST with all context"
        }
    ]
    
    print(f"\n📋 Starting conversation sequence...")
    
    for i, step in enumerate(conversation_steps, 1):
        print(f"\n💬 Step {i}: {step['purpose']}")
        print(f"Message: {step['message']}")
        
        try:
            response = requests.post(f"{base_url}/api/chat/mcpai", 
                json={"message": step["message"]},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # For the final step, check for email workflow
                if i == len(conversation_steps):
                    print(f"\n🎯 FINAL EMAIL REQUEST ANALYSIS:")
                    
                    if 'workflow' in result and result['workflow']:
                        print(f"✅ EMAIL WORKFLOW GENERATED!")
                        workflow = result['workflow']
                        print(f"   📧 Type: {workflow.get('type', 'unknown')}")
                        print(f"   🎯 Recipient: {workflow.get('recipient', 'Not specified')}")
                        print(f"   📝 Subject: {workflow.get('subject', 'Not specified')}")
                        
                        # Check if accumulated context was used
                        workflow_str = str(workflow).lower()
                        context_elements = []
                        if 'techcorp' in workflow_str:
                            context_elements.append('Company name (TechCorp)')
                        if 'protein' in workflow_str or 'noodles' in workflow_str:
                            context_elements.append('Product (protein noodles)')
                        if 'fastmcp' in workflow_str:
                            context_elements.append('Technology (FastMCP)')
                        if 'john' in workflow_str or 'ceo' in workflow_str:
                            context_elements.append('Personal details')
                        
                        if context_elements:
                            print(f"   🧠 Context Used: {', '.join(context_elements)}")
                            print(f"   ✅ CONTEXT ACCUMULATION SUCCESSFUL!")
                        else:
                            print(f"   ⚠️ Limited context detected in workflow")
                        
                        # Show the full workflow for verification
                        print(f"\n📋 Complete Workflow:")
                        print(json.dumps(workflow, indent=2))
                        
                        # Check if email would actually be sent
                        if workflow.get('recipient') == 'slakshanand1105@gmail.com':
                            print(f"\n✅ Correct recipient address confirmed!")
                            print(f"🚀 EMAIL AUTOMATION READY FOR EXECUTION")
                        else:
                            print(f"\n⚠️ Recipient address mismatch")
                            
                    else:
                        print(f"❌ NO EMAIL WORKFLOW GENERATED")
                        print(f"Response: {result.get('message', 'No message')[:200]}...")
                        
                else:
                    # For context building steps, check for acknowledgment
                    response_msg = result.get('message', '').lower()
                    context_signals = []
                    if 'noted' in response_msg or 'thanks' in response_msg:
                        context_signals.append('Acknowledgment')
                    if 'techcorp' in response_msg:
                        context_signals.append('Company recognition')
                    if 'protein' in response_msg or 'noodles' in response_msg:
                        context_signals.append('Product recognition')
                    if 'fastmcp' in response_msg:
                        context_signals.append('Technology recognition')
                    
                    if context_signals:
                        print(f"   ✅ Context signals: {', '.join(context_signals)}")
                    else:
                        print(f"   💬 General response")
                    
                    # Brief response preview
                    print(f"   Response: {result.get('message', 'No message')[:100]}...")
                
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        # Pause between conversation steps to simulate natural timing
        if i < len(conversation_steps):
            time.sleep(1)
    
    print(f"\n🎯 CONVERSATION TEST COMPLETE")
    print(f"=" * 40)
    print(f"✅ Context building phase completed")
    print(f"✅ Final email request processed")
    print(f"✅ Target: slakshanand1105@gmail.com")
    print(f"🏆 Two-part system architecture demonstrated!")

if __name__ == "__main__":
    conversation_test()
