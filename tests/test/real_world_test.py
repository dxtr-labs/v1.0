#!/usr/bin/env python3
"""
🌍 REAL-WORLD AUTOMATION SCENARIOS
Test the system with realistic business automation requests
"""

import requests
import json
import time

def test_with_auth(endpoint, payload, test_name):
    """Test with proper authentication"""
    base_url = "http://localhost:8002"
    
    # Login first
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "aitest@example.com",
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed for {test_name}")
        return None
    
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    
    print(f"\n🌍 {test_name}")
    print("=" * 80)
    print(f"💬 Request: {payload['message']}")
    
    try:
        response = requests.post(f"{base_url}{endpoint}", 
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Analyze response
            automation_detected = (
                result.get('hasWorkflowJson') or 
                result.get('workflow_json') or 
                result.get('automation_type') == 'email_automation' or
                'automation created' in result.get('message', '').lower()
            )
            
            email_sent = result.get('email_sent', False)
            message = result.get('message', '')
            
            if automation_detected:
                print(f"🤖 AUTOMATION: DETECTED")
                
                # Check for email execution
                if 'executed' in message:
                    print(f"⚡ EXECUTION: COMPLETED")
                    if email_sent:
                        print(f"📧 EMAIL: SENT SUCCESSFULLY")
                    else:
                        print(f"📧 EMAIL: ATTEMPTED (status unclear)")
                elif 'queued' in message:
                    print(f"⏳ EXECUTION: QUEUED")
                else:
                    print(f"📋 EXECUTION: PREPARED")
                
                # Check workflow details
                workflow_json = result.get('workflow_json')
                if workflow_json:
                    steps = workflow_json.get('steps', [])
                    if steps:
                        params = steps[0].get('parameters', {})
                        recipient = params.get('to', 'Unknown')
                        subject = params.get('subject', 'Unknown')
                        print(f"📧 RECIPIENT: {recipient}")
                        print(f"📝 SUBJECT: {subject}")
                
                # Check context usage
                context_signals = []
                if any(word in message.lower() for word in ['techcorp', 'dxtr']):
                    context_signals.append('Company')
                if any(word in message.lower() for word in ['protein', 'fastmcp']):
                    context_signals.append('Products')
                if 'automation' in message.lower():
                    context_signals.append('Services')
                
                if context_signals:
                    print(f"🧠 CONTEXT: {', '.join(context_signals)}")
            else:
                print(f"💬 MODE: CONVERSATIONAL")
                
                # Check for context acknowledgment
                if any(word in message.lower() for word in ['noted', 'remember', 'stored']):
                    print(f"🧠 CONTEXT: ACKNOWLEDGED")
            
            # Show response preview
            print(f"💭 RESPONSE: {message[:200]}...")
            
            return {
                'automation_detected': automation_detected,
                'email_sent': email_sent,
                'message': message,
                'result': result
            }
        else:
            print(f"❌ Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def run_real_world_scenarios():
    """Test real-world business automation scenarios"""
    
    print("🌍 REAL-WORLD AUTOMATION TESTING")
    print("=" * 80)
    print("Testing comprehensive business automation scenarios")
    print("Simulating actual customer interactions and use cases")
    print()
    
    # Real-world test scenarios
    scenarios = [
        {
            "name": "SCENARIO 1: New Customer Onboarding",
            "setup_message": "Hi! I'm Sarah Johnson, CEO of GreenTech Solutions. We're a renewable energy startup based in Austin, Texas. Our main products are solar panel optimization software and energy monitoring systems. My email is sarah@greentech-solutions.com",
            "automation_message": "Please send an introduction email to our new client john.martinez@ecoenergy.com telling them about our solar optimization software and how it can help their business"
        },
        {
            "name": "SCENARIO 2: Product Launch Announcement", 
            "setup_message": "I'm the Marketing Director at TechFlow Inc. We just launched our new AI-powered data analytics platform called DataVision Pro. It helps businesses automate their reporting workflows.",
            "automation_message": "Send an email to our investor contacts at investors@venturecap.com announcing our new DataVision Pro launch and requesting a meeting to discuss investment opportunities"
        },
        {
            "name": "SCENARIO 3: Customer Support Follow-up",
            "setup_message": "I work at CloudSecure, a cybersecurity company. We provide threat detection and incident response services. Our main contact email is support@cloudsecure.io",
            "automation_message": "Create an email to customer alex.thompson@techstartup.com following up on their recent security incident and offering our premium threat monitoring package"
        },
        {
            "name": "SCENARIO 4: Sales Lead Outreach",
            "setup_message": "I'm a sales rep at AutoFlow Logistics. We specialize in supply chain automation and warehouse management systems. Our flagship product is the SmartWarehouse platform.",
            "automation_message": "Send a professional outreach email to procurement@manufacturing-corp.com introducing our SmartWarehouse solution and proposing a demo meeting"
        },
        {
            "name": "SCENARIO 5: Partnership Proposal",
            "setup_message": "I represent FinTech Innovations, a company that develops payment processing solutions and digital banking platforms. We're looking to expand our partnership network.",
            "automation_message": "Draft an email to partnerships@retailtech.com proposing a strategic partnership to integrate our payment solutions with their e-commerce platform"
        },
        {
            "name": "SCENARIO 6: Event Invitation",
            "setup_message": "I'm organizing a tech conference called 'AI Future Summit 2025' for our company NextGen Events. It focuses on artificial intelligence trends and business applications.",
            "automation_message": "Send an invitation email to speakers@ai-research.org inviting them to be keynote speakers at our AI Future Summit and provide details about the speaking opportunity"
        },
        {
            "name": "SCENARIO 7: Customer Feedback Request",
            "setup_message": "I work at UserExperience Labs, where we create UX design tools and user research platforms. Our main product is called InsightBuilder.",
            "automation_message": "Create an email to beta-users@designstudio.com asking for feedback on our new InsightBuilder features and offering a discount for their continued participation"
        },
        {
            "name": "SCENARIO 8: Final Test - Original Request",
            "setup_message": "I'm back to our original TechCorp scenario. We're TechCorp Inc, selling healthy protein noodles and FastMCP automation services.",
            "automation_message": "Send a comprehensive email to slakshanand1105@gmail.com about our complete product line including TechCorp protein noodles and FastMCP automation services, with a personalized touch"
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n" + "="*80)
        print(f"🎬 STARTING {scenario['name']}")
        print("="*80)
        
        # Step 1: Setup company context
        print(f"📋 STEP 1: Setting up business context...")
        setup_result = test_with_auth(
            "/api/chat/mcpai",
            {"message": scenario['setup_message']},
            f"Context Setup - {scenario['name']}"
        )
        
        if not setup_result:
            print(f"❌ Setup failed for {scenario['name']}")
            continue
        
        # Brief pause to ensure context is stored
        time.sleep(3)
        
        # Step 2: Execute automation
        print(f"\n⚡ STEP 2: Executing automation request...")
        automation_result = test_with_auth(
            "/api/chat/mcpai", 
            {"message": scenario['automation_message']},
            f"Automation Execution - {scenario['name']}"
        )
        
        # Analyze results
        if automation_result:
            results.append({
                'scenario': scenario['name'],
                'setup_success': setup_result is not None,
                'automation_detected': automation_result.get('automation_detected', False),
                'email_sent': automation_result.get('email_sent', False),
                'full_success': automation_result.get('automation_detected', False) and 'executed' in automation_result.get('message', '').lower()
            })
        else:
            results.append({
                'scenario': scenario['name'],
                'setup_success': setup_result is not None,
                'automation_detected': False,
                'email_sent': False,
                'full_success': False
            })
        
        # Pause between scenarios
        time.sleep(5)
    
    # Final Analysis
    print(f"\n" + "="*80)
    print(f"📊 REAL-WORLD TESTING ANALYSIS")
    print("="*80)
    
    total_scenarios = len(results)
    setup_successes = sum(1 for r in results if r['setup_success'])
    automation_detections = sum(1 for r in results if r['automation_detected'])
    email_executions = sum(1 for r in results if r['email_sent'])
    full_successes = sum(1 for r in results if r['full_success'])
    
    print(f"📈 OVERALL PERFORMANCE:")
    print(f"   Total Scenarios: {total_scenarios}")
    print(f"   Context Setup Success: {setup_successes}/{total_scenarios} ({setup_successes/total_scenarios*100:.1f}%)")
    print(f"   Automation Detection: {automation_detections}/{total_scenarios} ({automation_detections/total_scenarios*100:.1f}%)")
    print(f"   Email Execution: {email_executions}/{total_scenarios} ({email_executions/total_scenarios*100:.1f}%)")
    print(f"   Complete Success: {full_successes}/{total_scenarios} ({full_successes/total_scenarios*100:.1f}%)")
    
    print(f"\n📋 SCENARIO BREAKDOWN:")
    for result in results:
        status = "✅ COMPLETE" if result['full_success'] else "⚡ PARTIAL" if result['automation_detected'] else "💬 CONTEXT"
        print(f"   {result['scenario']}: {status}")
    
    print(f"\n🎯 REAL-WORLD READINESS:")
    if full_successes >= total_scenarios * 0.75:  # 75% full success rate
        print(f"🚀 SYSTEM IS PRODUCTION READY!")
        print(f"✅ Excellent performance across diverse business scenarios")
        print(f"✅ Context extraction and automation detection working reliably")
        print(f"✅ Email automation executing successfully")
        print(f"✅ Ready for real customer deployments")
    elif automation_detections >= total_scenarios * 0.8:  # 80% automation detection
        print(f"⚡ SYSTEM IS NEARLY PRODUCTION READY!")
        print(f"✅ Strong automation detection capabilities")
        print(f"✅ Context handling working well")
        print(f"⚠️ Minor issues with email execution consistency")
    else:
        print(f"🔧 SYSTEM NEEDS REFINEMENT")
        print(f"⚠️ Automation detection needs improvement")
        print(f"📝 Review context extraction and automation triggers")
    
    return results

if __name__ == "__main__":
    run_real_world_scenarios()
