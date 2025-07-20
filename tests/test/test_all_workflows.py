#!/usr/bin/env python3
"""
DXTR AutoFlow - Comprehensive Workflow Testing System
Tests all workflows and validates their connectivity requirements
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from enhanced_agent_workflow_system import EnhancedAgentWorkflowSystem

class WorkflowTestingSuite:
    """Comprehensive testing suite for all workflows"""
    
    def __init__(self):
        self.agent_system = EnhancedAgentWorkflowSystem()
        self.test_scenarios = [
            # Technical Lead Scenarios
            {
                "agent": "technical_lead",
                "category": "Bug Fixes & Incidents",
                "scenarios": [
                    "Create a critical bug fix task in Asana and alert the dev team immediately",
                    "Report a production incident and notify stakeholders via Slack and email",
                    "Set up monitoring for database performance issues",
                    "Create a security patch deployment workflow"
                ]
            },
            # Marketing Manager Scenarios  
            {
                "agent": "marketing_manager",
                "category": "Marketing & Social Media",
                "scenarios": [
                    "Launch our new AI product announcement on Twitter and track engagement",
                    "Create a social media campaign for Black Friday with analytics tracking",
                    "Send email newsletter to subscribers about product updates",
                    "Post LinkedIn article about industry trends and monitor metrics"
                ]
            },
            # Customer Success Scenarios
            {
                "agent": "customer_success", 
                "category": "Customer Management",
                "scenarios": [
                    "Set up complete onboarding for new enterprise client Microsoft",
                    "Process customer refund request and notify relevant teams",
                    "Create support ticket for customer escalation with priority handling",
                    "Send personalized thank you email to premium customers"
                ]
            },
            # Sales Executive Scenarios
            {
                "agent": "sales_executive",
                "category": "Sales & Revenue",
                "scenarios": [
                    "Process payment for new customer subscription and send confirmation",
                    "Create sales pipeline task for high-value prospect follow-up", 
                    "Generate invoice for enterprise client and track payment status",
                    "Set up automated billing for recurring subscriptions"
                ]
            }
        ]
        
        self.workflow_results = []
        self.connectivity_report = {}
    
    async def run_comprehensive_tests(self):
        """Run all workflow tests and generate comprehensive report"""
        
        print("🧪 DXTR AutoFlow - Comprehensive Workflow Testing Suite")
        print("=" * 80)
        print("Testing all workflows with agent personalities and connectivity validation\n")
        
        total_tests = 0
        successful_tests = 0
        connectivity_issues = 0
        
        for agent_group in self.test_scenarios:
            agent_type = agent_group["agent"]
            category = agent_group["category"]
            
            print(f"\n🎯 Testing Agent: {agent_type.replace('_', ' ').title()}")
            print(f"📋 Category: {category}")
            print("─" * 60)
            
            for i, scenario in enumerate(agent_group["scenarios"], 1):
                total_tests += 1
                print(f"\n🔧 Test {i}: {scenario}")
                
                result = await self.agent_system.process_agent_request(scenario, agent_type)
                
                if result["success"]:
                    successful_tests += 1
                    print(f"✅ Success - Workflow generated and ready for execution")
                    print(f"   📊 Steps: {len(result['workflow']['steps'])}")
                    print(f"   ⏱️ Estimated time: {result['estimated_time']}s")
                    print(f"   🔗 Required connections: {', '.join(result['required_connections'])}")
                else:
                    connectivity_issues += 1
                    print(f"❌ Failed - {result['error']}")
                    if result.get("missing_connections"):
                        print(f"   🔌 Missing: {', '.join(result['missing_connections'])}")
                
                # Store result for report
                self.workflow_results.append({
                    "agent": agent_type,
                    "category": category,
                    "scenario": scenario,
                    "success": result["success"],
                    "error": result.get("error"),
                    "missing_connections": result.get("missing_connections", []),
                    "required_connections": result.get("required_connections", []),
                    "template_used": result.get("template_id") is not None,
                    "execution_time": result.get("estimated_time", 0)
                })
        
        # Generate connectivity report
        await self.generate_connectivity_report()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🏆 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 80)
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Successful Workflows: {successful_tests}")
        print(f"🔌 Connectivity Issues: {connectivity_issues}")
        print(f"📈 Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "connectivity_issues": connectivity_issues,
            "success_rate": (successful_tests/total_tests)*100,
            "detailed_results": self.workflow_results,
            "connectivity_report": self.connectivity_report
        }
    
    async def generate_connectivity_report(self):
        """Generate detailed connectivity requirements report"""
        
        print("\n🔌 CONNECTIVITY REQUIREMENTS ANALYSIS")
        print("=" * 80)
        
        # Analyze all connection requirements
        all_connections = set()
        connection_usage = {}
        
        for result in self.workflow_results:
            for conn in result["required_connections"]:
                all_connections.add(conn)
                connection_usage[conn] = connection_usage.get(conn, 0) + 1
        
        # Get connectivity manager data
        dashboard_data = self.agent_system.connectivity_manager.get_connectivity_dashboard_data()
        
        print(f"📈 Total Unique Connections Required: {len(all_connections)}")
        print(f"🔗 Currently Connected: {dashboard_data['connected']}")
        print(f"❌ Currently Disconnected: {dashboard_data['disconnected']}")
        
        print(f"\n📊 Most Required Connections:")
        sorted_usage = sorted(connection_usage.items(), key=lambda x: x[1], reverse=True)
        for conn, count in sorted_usage[:5]:
            status = dashboard_data['connections'][conn]['status']
            status_icon = "✅" if status == "connected" else "❌"
            print(f"   {status_icon} {conn}: {count} workflows require this")
        
        print(f"\n🔧 Setup Priority Recommendations:")
        priority_connections = [conn for conn, count in sorted_usage if count >= 3]
        for conn in priority_connections:
            connection_info = dashboard_data['connections'][conn]
            if connection_info['status'] != 'connected':
                print(f"   🔴 HIGH PRIORITY: {connection_info['name']}")
                print(f"      Required fields: {', '.join(connection_info['required_fields'])}")
        
        self.connectivity_report = {
            "total_connections_needed": len(all_connections),
            "currently_connected": dashboard_data['connected'],
            "connection_usage": connection_usage,
            "priority_setup": priority_connections,
            "dashboard_data": dashboard_data
        }
    
    def generate_setup_instructions(self):
        """Generate step-by-step setup instructions for each connection"""
        
        setup_instructions = {
            "asana": {
                "steps": [
                    "1. Go to https://app.asana.com/0/my-apps",
                    "2. Click 'Create new token'", 
                    "3. Copy your Personal Access Token",
                    "4. Find your Workspace ID in the URL when viewing your workspace"
                ],
                "documentation": "https://developers.asana.com/docs/authentication"
            },
            "slack": {
                "steps": [
                    "1. Go to https://api.slack.com/apps",
                    "2. Create a new app for your workspace",
                    "3. Add Bot Token Scopes: chat:write, channels:read",
                    "4. Install app to workspace and copy Bot User OAuth Token",
                    "5. Create incoming webhook for notifications"
                ],
                "documentation": "https://api.slack.com/start/building"
            },
            "stripe": {
                "steps": [
                    "1. Log into your Stripe Dashboard",
                    "2. Go to Developers > API Keys",
                    "3. Copy your Secret Key (starts with sk_)",
                    "4. Copy your Publishable Key (starts with pk_)",
                    "5. Optional: Set up webhooks for payment notifications"
                ],
                "documentation": "https://stripe.com/docs/keys"
            },
            "twitter": {
                "steps": [
                    "1. Apply for Twitter Developer Account at https://developer.twitter.com",
                    "2. Create a new Twitter App",
                    "3. Generate API Key and Secret",
                    "4. Generate Access Token and Secret",
                    "5. Optional: Get Bearer Token for API v2"
                ],
                "documentation": "https://developer.twitter.com/en/docs/authentication"
            },
            "openai": {
                "steps": [
                    "1. Sign up at https://platform.openai.com",
                    "2. Go to API Keys section",
                    "3. Create new secret key",
                    "4. Copy and securely store your API key",
                    "5. Set usage limits and billing preferences"
                ],
                "documentation": "https://platform.openai.com/docs/api-reference/authentication"
            }
        }
        
        return setup_instructions

async def main():
    """Main testing function"""
    
    test_suite = WorkflowTestingSuite()
    results = await test_suite.run_comprehensive_tests()
    
    # Generate setup instructions
    setup_instructions = test_suite.generate_setup_instructions()
    
    print("\n🔧 QUICK SETUP GUIDE FOR TOP CONNECTIONS")
    print("=" * 80)
    
    # Show setup for most needed connections
    for conn, count in sorted(results["connectivity_report"]["connection_usage"].items(), 
                             key=lambda x: x[1], reverse=True)[:3]:
        if conn in setup_instructions:
            print(f"\n📋 {conn.upper()} Setup ({count} workflows need this):")
            for step in setup_instructions[conn]["steps"]:
                print(f"   {step}")
            print(f"   📖 Docs: {setup_instructions[conn]['documentation']}")
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. Open the Connectivity Dashboard: file:///c:/Users/sugua/Desktop/redo/connectivity_dashboard.html")
    print("2. Click 'Setup' on each disconnected service")
    print("3. Follow the setup guide above for API credentials")
    print("4. Test connections using the 'Test' button")
    print("5. Re-run workflows once connections are established")
    
    print(f"\n✨ Once all connections are setup, you'll have {results['total_tests']} fully automated workflows ready!")

if __name__ == "__main__":
    asyncio.run(main())
