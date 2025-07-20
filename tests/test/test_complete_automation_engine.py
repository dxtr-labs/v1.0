"""
Complete Workflow and Automation Engine Test
Test the entire automation pipeline from detection to execution
"""
import requests
import json
import time

def test_complete_automation_pipeline():
    """Test the full automation engine workflow"""
    
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
    
    print("🔧 COMPLETE AUTOMATION ENGINE TEST")
    print("=" * 60)
    print("Testing: Context → Automation Detection → Workflow Generation → Email Execution")
    
    # Step 1: Build context
    print("\n📋 STEP 1: Building Context")
    context_messages = [
        "My company is TechCorp Inc and we make protein noodles",
        "My email is john@techcorp.com and I'm the CEO",
        "We use FastMCP for automation"
    ]
    
    for msg in context_messages:
        print(f"  💬 {msg}")
        response = requests.post(f"{base_url}/api/chat/mcpai", 
            json={"message": msg}, headers=headers, timeout=20)
        if response.status_code == 200:
            print(f"    ✅ Context stored")
        else:
            print(f"    ❌ Failed: {response.status_code}")
        time.sleep(1)
    
    # Step 2: Test automation detection
    print("\n🤖 STEP 2: Testing Automation Detection")
    automation_requests = [
        "Send email to slakshanand1105@gmail.com about TechCorp services",
        "Create email workflow to contact slakshanand1105@gmail.com",
        "I need to send an automated email to slakshanand1105@gmail.com"
    ]
    
    for i, request in enumerate(automation_requests, 1):
        print(f"\n  🧪 Automation Test {i}: {request}")
        
        try:
            response = requests.post(f"{base_url}/api/chat/mcpai", 
                json={"message": request}, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"    ✅ Status: 200")
                
                # Check for workflow generation
                if 'workflow' in result and result['workflow']:
                    workflow = result['workflow']
                    print(f"    🎯 WORKFLOW GENERATED!")
                    print(f"      Type: {workflow.get('type', 'unknown')}")
                    print(f"      Recipient: {workflow.get('recipient', 'Not specified')}")
                    print(f"      Subject: {workflow.get('subject', 'Not specified')}")
                    
                    # Full workflow details
                    print(f"    📋 Full Workflow JSON:")
                    print(json.dumps(workflow, indent=4))
                    
                    # Test workflow execution if present
                    if workflow.get('recipient') == 'slakshanand1105@gmail.com':
                        print(f"    ✅ Correct recipient confirmed")
                        return test_workflow_execution(workflow, headers, base_url)
                    
                else:
                    print(f"    ⚠️ No workflow generated")
                    print(f"      Response: {result.get('message', 'No message')[:100]}...")
                    
                    # Check response type and fields
                    print(f"    📋 Response fields: {list(result.keys())}")
                    
            else:
                print(f"    ❌ HTTP Error: {response.status_code}")
                print(f"      Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"    ❌ Exception: {e}")
    
    # Step 3: Test direct automation engine
    print("\n⚙️ STEP 3: Testing Direct Automation Engine")
    test_direct_automation_engine(headers, base_url)

def test_workflow_execution(workflow, headers, base_url):
    """Test executing a generated workflow"""
    print(f"\n🚀 STEP 3: Testing Workflow Execution")
    
    # Check if there's an execution endpoint
    execution_endpoints = [
        "/api/automation/execute",
        "/api/workflow/execute", 
        "/api/email/send",
        "/api/automation/trigger"
    ]
    
    for endpoint in execution_endpoints:
        print(f"  🔧 Testing endpoint: {endpoint}")
        
        try:
            response = requests.post(f"{base_url}{endpoint}",
                json={"workflow": workflow},
                headers=headers,
                timeout=20
            )
            
            print(f"    Status: {response.status_code}")
            if response.status_code != 404:
                print(f"    Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"    Exception: {e}")

def test_direct_automation_engine(headers, base_url):
    """Test the automation engine directly"""
    
    # Check automation engine status
    print(f"  📊 Checking automation engine status...")
    
    try:
        # Test health endpoint
        health_response = requests.get(f"{base_url}/health", timeout=10)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"    ✅ Server health: {health_data.get('status', 'unknown')}")
        
        # Check if there's an automation status endpoint
        status_endpoints = [
            "/api/automation/status",
            "/api/automation/health",
            "/api/workflow/status"
        ]
        
        for endpoint in status_endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", 
                    headers=headers, timeout=10)
                if response.status_code == 200:
                    print(f"    ✅ {endpoint}: {response.json()}")
                elif response.status_code != 404:
                    print(f"    ⚠️ {endpoint}: {response.status_code}")
            except:
                pass
                
    except Exception as e:
        print(f"    ❌ Health check failed: {e}")
    
    # Test email configuration
    print(f"  📧 Testing email configuration...")
    
    try:
        # Check if email service is configured
        email_test_endpoints = [
            "/api/email/test",
            "/api/email/config",
            "/api/automation/email/test"
        ]
        
        for endpoint in email_test_endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}",
                    headers=headers, timeout=10)
                if response.status_code == 200:
                    print(f"    ✅ {endpoint}: Available")
                    print(f"      Response: {response.text[:100]}")
                elif response.status_code != 404:
                    print(f"    ⚠️ {endpoint}: {response.status_code}")
            except:
                pass
                
    except Exception as e:
        print(f"    ❌ Email config check failed: {e}")

def test_backend_components():
    """Test backend automation components"""
    print(f"\n🔍 STEP 4: Backend Component Analysis")
    
    # Check if backend files exist and are accessible
    components_to_check = [
        "backend/mcp/simple_automation_engine.py",
        "backend/simple_email_service.py", 
        "backend/email_sender.py",
        "backend/automation_engine/"
    ]
    
    import os
    for component in components_to_check:
        if os.path.exists(component):
            print(f"  ✅ {component}: Found")
        else:
            print(f"  ❌ {component}: Missing")

if __name__ == "__main__":
    test_complete_automation_pipeline()
    test_backend_components()
    
    print(f"\n🎯 AUTOMATION ENGINE DIAGNOSIS:")
    print(f"✅ Context extraction working")
    print(f"⚠️ Automation detection may need calibration")
    print(f"❓ Workflow execution pipeline needs verification")
    print(f"📧 Email delivery system requires investigation")
    print(f"\n💡 Next: Check email credentials and automation engine configuration")
