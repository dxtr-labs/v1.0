#!/usr/bin/env python3
"""
DXTR AutoFlow - Prompt Testing Demo
Quick demonstration of prompt testing capabilities
"""

import asyncio
import time
from datetime import datetime

async def demo_prompt_testing():
    """Demonstrate prompt testing with sample prompts"""
    
    print("🎯 DXTR AutoFlow - Prompt Testing Demonstration")
    print("=" * 60)
    print("Demonstrating various prompt types and responses...")
    print()
    
    # Sample prompts to demonstrate
    demo_prompts = [
        {
            "category": "AI Chat",
            "prompt": "Generate a professional email announcing our new AI automation platform launch",
            "expected": "Professional email content with business tone"
        },
        {
            "category": "Workflow Automation", 
            "prompt": "Create a task in Asana, post to Slack, and send email notification for project completion",
            "expected": "Multi-step workflow execution"
        },
        {
            "category": "Customer Support Agent",
            "prompt": "A customer is asking about refund policy for their subscription",
            "expected": "Helpful customer service response"
        },
        {
            "category": "Integration Testing",
            "prompt": "Process a Stripe payment for $99.99 and create invoice for customer John Smith",
            "expected": "Payment processing confirmation"
        },
        {
            "category": "Complex Workflow",
            "prompt": "New enterprise customer onboarding: setup Asana workspace, Slack channels, Stripe billing, and analytics tracking",
            "expected": "Complete onboarding automation"
        }
    ]
    
    for i, demo in enumerate(demo_prompts, 1):
        print(f"📝 Demo {i}: {demo['category']}")
        print(f"Prompt: {demo['prompt']}")
        print("Processing...", end="", flush=True)
        
        # Simulate processing time
        for _ in range(3):
            await asyncio.sleep(0.5)
            print(".", end="", flush=True)
        
        print(" ✅")
        
        # Generate realistic response based on category
        if demo['category'] == "AI Chat":
            response = f"""📧 Generated Email Content:

Subject: Introducing DXTR AutoFlow - Revolutionary AI Automation Platform

Dear Valued Customers,

We're excited to announce the launch of DXTR AutoFlow, our groundbreaking AI-powered automation platform that will transform how you manage workflows.

Key Features:
• 31 production-ready automation drivers
• AI-powered task processing and decision making  
• Seamless integration with Asana, Slack, Stripe, Twitter, and more
• Real-time analytics and monitoring
• Enterprise-grade security and reliability

Ready to boost your productivity by 300%? 

Get started today: https://dxtrautoflow.com

Best regards,
The DXTR Team

Generated in {time.time():.2f}s by DXTR AutoFlow AI"""

        elif demo['category'] == "Workflow Automation":
            response = f"""⚙️ Workflow Execution Complete:

✅ Step 1: Asana Task Created
   - Task: "Project Completion Notification"
   - Project: Current Active Project
   - Assignee: Project Manager
   - Due Date: Today
   - Status: Completed

✅ Step 2: Slack Notification Posted
   - Channel: #project-updates
   - Message: "🎉 Project completed successfully! All deliverables ready."
   - Mentions: @team @project-manager
   - Reactions: 👍 ✅ 🎉

✅ Step 3: Email Notification Sent
   - Recipients: Stakeholders list
   - Subject: "Project Completion - Success!"
   - Template: Professional notification template
   - Delivery: Confirmed

Workflow ID: WF-{int(time.time())}
Total Execution Time: {time.time():.2f}s
Status: SUCCESS ✅"""

        elif demo['category'] == "Customer Support Agent":
            response = f"""👋 Customer Support Response:

Hello! Thank you for contacting us about our refund policy.

I'm happy to help clarify our refund terms for you:

**Subscription Refund Policy:**
• 30-day money-back guarantee for all new subscriptions
• Pro-rated refunds available for annual plans  
• Instant processing for refunds within first 7 days
• Enterprise customers: Custom refund terms available

**How to Request a Refund:**
1. Log into your account dashboard
2. Go to Billing & Subscriptions  
3. Click "Request Refund"
4. Select reason and submit

**Processing Time:**
• Credit card refunds: 3-5 business days
• Bank transfers: 5-7 business days
• PayPal: 1-2 business days

Is there anything specific about your subscription I can help you with today?

Agent: Sarah | Support Ticket: #{int(time.time())}
Response Time: {time.time():.2f}s"""

        elif demo['category'] == "Integration Testing":
            response = f"""💳 Stripe Payment Processing Complete:

✅ Payment Successfully Processed:
   - Amount: $99.99 USD
   - Customer: John Smith (john.smith@email.com)
   - Payment Method: **** **** **** 4242 (Visa)
   - Transaction ID: pi_{int(time.time())}
   - Status: Succeeded
   - Processing Fee: $3.19

✅ Invoice Generated:
   - Invoice #: INV-{int(time.time())}
   - Date: {datetime.now().strftime('%Y-%m-%d')}
   - Due Date: {datetime.now().strftime('%Y-%m-%d')} (Paid)
   - PDF Generated: ✅
   - Email Sent: ✅

✅ Customer Notifications:
   - Payment confirmation email sent
   - Invoice delivered to customer
   - Receipt generated and archived

Next Actions:
• Product/service activation: Automatic
• Customer onboarding: Initiated
• Accounting sync: Completed

Processing Time: {time.time():.2f}s
Integration Status: SUCCESS ✅"""

        else:  # Complex Workflow
            response = f"""🚀 Enterprise Customer Onboarding - Complete:

Customer: TechCorp Inc. | Enterprise Plan | ID: CUST-{int(time.time())}

✅ ASANA WORKSPACE SETUP:
   - Workspace: "TechCorp Inc - DXTR AutoFlow"
   - Projects: 3 template projects created
   - Teams: Engineering, Marketing, Operations
   - Members: 5 initial users invited
   - Templates: Enterprise workflow templates installed

✅ SLACK INTEGRATION:
   - Workspace: techcorp-dxtr.slack.com
   - Channels: #general, #automation, #support, #alerts
   - Bot installed: DXTR AutoFlow Assistant
   - Webhooks: Configured for all workflow notifications
   - Team: 12 members added

✅ STRIPE BILLING SETUP:
   - Subscription: Enterprise Plan ($299/month)
   - Payment Method: Corporate card ending 4567
   - Billing Cycle: Monthly on 17th
   - Next Billing: {datetime.now().strftime('%Y-%m-%d')}
   - Invoice: Auto-generated and sent

✅ ANALYTICS TRACKING:
   - Dashboard: Created custom enterprise dashboard
   - Metrics: 15 KPIs configured
   - Reports: Weekly automation summary scheduled
   - Alerts: Performance thresholds set
   - Integration: Google Analytics connected

✅ ONBOARDING COMPLETE:
   - Welcome email sequence: Initiated
   - Training materials: Delivered
   - Account manager: Assigned (Sarah Johnson)
   - Success metrics: Baseline established

Customer Status: ACTIVE ✅
Onboarding Time: {time.time():.2f}s
Success Rate: 100%"""

        print(f"Response Preview:")
        print("─" * 40)
        print(response[:300] + "..." if len(response) > 300 else response)
        print("─" * 40)
        print()
    
    print("🎉 Demo Complete!")
    print("\nTo run interactive testing, use:")
    print("   python test_prompts_realtime.py")
    print("\nTo run comprehensive testing, use:")
    print("   python test_prompts_interactive.py")

if __name__ == "__main__":
    asyncio.run(demo_prompt_testing())
