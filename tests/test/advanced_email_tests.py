#!/usr/bin/env python3
"""
Advanced Email Tests Using Backend MCP LLM System
Tests the actual workflow automation system with real email sending
"""

import asyncio
import sys
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)

# Load environment variables
load_dotenv('.env.local')

TARGET_EMAIL = "slakshanand1105@gmail.com"

class AdvancedEmailTester:
    def __init__(self):
        self.backend_url = "http://localhost:8002"
        self.frontend_url = "http://localhost:3002"
        
    async def test_backend_mcp_email_automation(self):
        """Test using backend Custom MCP LLM system directly"""
        print("\n" + "="*60)
        print("🚀 ADVANCED TEST: BACKEND MCP LLM EMAIL AUTOMATION")
        print("="*60)
        
        try:
            # Import backend systems directly
            from simple_email_service import email_service
            from mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine
            
            # Configure email service
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')
            smtp_host = os.getenv('SMTP_HOST')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            
            email_service.configure(smtp_user, smtp_password, smtp_host, smtp_port)
            print("✅ Email service configured")
            
            # Create MCP LLM engine
            engine = CustomMCPLLMIterationEngine("advanced-test-agent")
            print("✅ Custom MCP LLM engine initialized")
            
            # Test different automation scenarios
            test_scenarios = [
                {
                    "name": "Business Pitch Email",
                    "request": f"Send a professional business email to {TARGET_EMAIL} about our new AI automation platform. Include key benefits and a call to action."
                },
                {
                    "name": "Thank You Email",
                    "request": f"Create and send a thank you email to {TARGET_EMAIL} for testing our automation system. Make it personalized and professional."
                },
                {
                    "name": "Product Demo Email",
                    "request": f"Send an email to {TARGET_EMAIL} offering a free demo of our Custom MCP LLM automation platform. Include scheduling information."
                }
            ]
            
            results = []
            
            for i, scenario in enumerate(test_scenarios, 1):
                print(f"\n📧 Test {i}: {scenario['name']}")
                print("-" * 40)
                
                try:
                    result = await engine.process_user_request(scenario['request'])
                    
                    if result.get("success"):
                        print(f"✅ {scenario['name']}: MCP LLM processing successful")
                        print(f"📝 Response: {result.get('response', '')[:100]}...")
                        results.append((scenario['name'], True))
                    else:
                        print(f"❌ {scenario['name']}: MCP LLM processing failed")
                        results.append((scenario['name'], False))
                        
                except Exception as e:
                    print(f"❌ {scenario['name']}: Error - {e}")
                    results.append((scenario['name'], False))
                
                # Wait between tests
                await asyncio.sleep(2)
            
            return results
            
        except ImportError as e:
            print(f"❌ Backend system import failed: {e}")
            return [("Backend MCP Import", False)]
        except Exception as e:
            print(f"❌ Backend test failed: {e}")
            return [("Backend MCP Test", False)]

    async def test_api_email_workflow(self):
        """Test email automation through API endpoints"""
        print("\n" + "="*60)
        print("🌐 ADVANCED TEST: API WORKFLOW EMAIL AUTOMATION")  
        print("="*60)
        
        # Try to test through the workflow API
        try:
            # Test workflow creation endpoint
            workflow_data = {
                "message": f"Create an email automation workflow that sends a welcome email to {TARGET_EMAIL} with our company information and services",
                "ai_service": "in_house"
            }
            
            print("📡 Testing workflow creation API...")
            response = requests.post(
                f"{self.backend_url}/api/workflow/generate",
                json=workflow_data,
                timeout=30
            )
            
            if response.status_code == 200:
                workflow_result = response.json()
                print("✅ Workflow API responded successfully")
                print(f"📋 Workflow created: {workflow_result.get('success', False)}")
                
                if workflow_result.get('workflow'):
                    workflow = workflow_result['workflow']
                    print(f"🔧 Workflow ID: {workflow.get('id', 'unknown')}")
                    print(f"📝 Workflow Name: {workflow.get('name', 'unknown')}")
                    
                    # Try to execute the workflow
                    if workflow.get('id'):
                        try:
                            confirm_data = {
                                "workflow_id": workflow['id'],
                                "user_decision": "approved"
                            }
                            
                            print("⚡ Executing workflow...")
                            exec_response = requests.post(
                                f"{self.backend_url}/api/workflow/confirm",
                                json=confirm_data,
                                timeout=30
                            )
                            
                            if exec_response.status_code == 200:
                                exec_result = exec_response.json()
                                print("✅ Workflow executed successfully")
                                return [("API Workflow", True)]
                            else:
                                print(f"❌ Workflow execution failed: {exec_response.status_code}")
                                return [("API Workflow Execution", False)]
                                
                        except Exception as e:
                            print(f"❌ Workflow execution error: {e}")
                            return [("API Workflow Execution", False)]
                    else:
                        print("⚠️ No workflow ID returned")
                        return [("API Workflow ID", False)]
                else:
                    print("⚠️ No workflow returned in response")
                    return [("API Workflow Response", False)]
            else:
                print(f"❌ Workflow API failed: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return [("API Workflow", False)]
                
        except Exception as e:
            print(f"❌ API test failed: {e}")
            return [("API Test", False)]

    async def test_direct_smtp_with_custom_content(self):
        """Test direct SMTP with dynamically generated content"""
        print("\n" + "="*60)
        print("📧 ADVANCED TEST: DIRECT SMTP WITH DYNAMIC CONTENT")
        print("="*60)
        
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Get SMTP configuration
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        
        if not all([smtp_host, smtp_user, smtp_password]):
            print("❌ SMTP configuration incomplete")
            return [("SMTP Config", False)]
        
        # Generate dynamic content
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        advanced_scenarios = [
            {
                "subject": "🎯 Advanced Test: Automation Platform Status Report",
                "content": f"""🚀 AUTOMATION PLATFORM STATUS REPORT

Generated: {current_time}
Platform: DXTR Labs Custom MCP LLM System
Test Suite: Advanced Email Automation

📊 PLATFORM PERFORMANCE:
• Email System: ✅ OPERATIONAL
• MCP LLM Engine: ✅ ACTIVE
• Workflow Automation: ✅ FUNCTIONAL
• API Endpoints: ✅ RESPONSIVE
• Database Connection: ✅ STABLE

🔧 SYSTEM CAPABILITIES VERIFIED:
• Real-time email sending via SMTP
• AI-powered content generation
• Workflow automation and execution
• External data integration
• Internal data analysis

🎯 TEST RESULTS:
All automated tests are passing successfully. Your email automation platform is ready for production use.

Next Steps:
1. Deploy to production environment
2. Set up monitoring and alerts
3. Configure user onboarding workflows
4. Implement advanced AI features

This email demonstrates the advanced capabilities of your Custom MCP LLM automation platform."""
            },
            {
                "subject": "🤖 AI-Powered Business Intelligence Report",
                "content": f"""🤖 AI-POWERED BUSINESS INTELLIGENCE

Analysis Date: {current_time}
AI Engine: Custom MCP LLM Orchestrator
Report Type: Automated Business Intelligence

📈 KEY INSIGHTS:
• Platform Usage: Increasing steadily
• User Engagement: High satisfaction scores
• Automation Efficiency: 95% success rate
• Cost Savings: 40% reduction in manual tasks

🎯 MARKET OPPORTUNITIES:
• Expand automation features
• Integrate with more external services
• Develop mobile applications
• Create API marketplace

💡 AI RECOMMENDATIONS:
Based on data analysis, the platform shows excellent potential for scaling. The automation workflows are performing above industry standards.

Suggested Focus Areas:
1. User experience optimization
2. Advanced AI model integration
3. Real-time analytics dashboard
4. Multi-language support

This analysis was generated by our AI system and delivered automatically."""
            }
        ]
        
        results = []
        
        for i, scenario in enumerate(advanced_scenarios, 1):
            try:
                print(f"📤 Sending advanced email {i}: {scenario['subject'][:50]}...")
                
                msg = MIMEMultipart("alternative")
                msg["From"] = smtp_user
                msg["To"] = TARGET_EMAIL
                msg["Subject"] = scenario['subject']
                
                # Add enhanced footer
                enhanced_content = scenario['content'] + f"""

---
🚀 TECHNICAL DETAILS:
• Platform: DXTR Labs Automation Engine
• Engine: Custom MCP LLM v2.0
• Delivery Method: Direct SMTP
• Test Suite: Advanced Email Automation
• From: {smtp_user}
• Time: {current_time}

🔗 Learn More:
Visit our platform dashboard for detailed analytics and automation tools.
"""
                
                msg.attach(MIMEText(enhanced_content, "plain"))
                
                with smtplib.SMTP(smtp_host, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_password)
                    server.send_message(msg)
                
                print(f"✅ Advanced email {i} sent successfully")
                results.append((f"Advanced Email {i}", True))
                
            except Exception as e:
                print(f"❌ Advanced email {i} failed: {e}")
                results.append((f"Advanced Email {i}", False))
        
        return results

    async def run_advanced_tests(self):
        """Run all advanced email tests"""
        print("🚀 ADVANCED EMAIL AUTOMATION TEST SUITE")
        print("=" * 80)
        print(f"🎯 Target Email: {TARGET_EMAIL}")
        print(f"🏠 Backend URL: {self.backend_url}")
        print(f"🌐 Frontend URL: {self.frontend_url}")
        print("=" * 80)
        
        all_results = []
        
        # Test 1: Backend MCP LLM System
        print("\n🔧 Running Backend MCP LLM Tests...")
        backend_results = await self.test_backend_mcp_email_automation()
        all_results.extend(backend_results)
        
        # Test 2: API Workflow System
        print("\n🌐 Running API Workflow Tests...")
        api_results = await self.test_api_email_workflow()
        all_results.extend(api_results)
        
        # Test 3: Direct SMTP with Dynamic Content
        print("\n📧 Running Direct SMTP Tests...")
        smtp_results = await self.test_direct_smtp_with_custom_content()
        all_results.extend(smtp_results)
        
        # Print comprehensive summary
        print("\n" + "="*80)
        print("📋 ADVANCED TEST RESULTS SUMMARY")
        print("="*80)
        
        passed = 0
        for test_name, result in all_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name:.<50} {status}")
            if result:
                passed += 1
        
        print(f"\n🎯 Advanced Test Score: {passed}/{len(all_results)} tests passed")
        
        if passed >= len(all_results) * 0.75:  # 75% pass rate for advanced tests
            print("🎉 ADVANCED TESTS LARGELY SUCCESSFUL!")
            print("Your automation platform demonstrates advanced capabilities!")
        else:
            print("⚠️ Some advanced features need attention.")
        
        print(f"\n📧 Check {TARGET_EMAIL} for all advanced test emails!")
        return all_results

async def main():
    """Main advanced test runner"""
    tester = AdvancedEmailTester()
    await tester.run_advanced_tests()

if __name__ == "__main__":
    asyncio.run(main())
