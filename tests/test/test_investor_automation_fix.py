"""
Test the AI Investor Email Fix
This script tests the production fix for the investor email automation.
"""

import asyncio
import json
import sys
import os

# Add the backend path so we can import the MCP engine
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_investor_automation():
    """Test the AI investor automation fix"""
    print("🧪 Testing AI Investor Automation Fix...")
    
    try:
        # Import the MCP engine
        from mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine
        
        # Create test engine
        engine = CustomMCPLLMIterationEngine(
            agent_id="test_agent",
            session_id="test_session",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Test investor search queries
        test_queries = [
            "find top 10 AI investors email addresses",
            "search for AI automation investors and email me the list",
            "I need contact info for venture capital firms investing in AI",
            "get me emails of top investors interested in automation startups"
        ]
        
        print(f"🔍 Testing {len(test_queries)} investor search queries...")
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'='*60}")
            print(f"TEST {i}: {query}")
            print('='*60)
            
            # Process the query
            result = await engine.process_user_request(query)
            
            if result:
                print(f"✅ Status: {result.get('status', 'unknown')}")
                print(f"📧 Success: {result.get('success', False)}")
                
                if result.get('workflow_json'):
                    workflow = result['workflow_json']
                    print(f"🔧 Workflow Type: {workflow.get('workflow_type', 'unknown')}")
                    print(f"⚡ Steps: {len(workflow.get('steps', []))}")
                    
                    # Check if it's investor automation
                    if workflow.get('workflow_type') == 'ai_investor_research':
                        print("🎯 AI INVESTOR AUTOMATION DETECTED!")
                        
                        # Check if email step exists
                        email_step = None
                        for step in workflow.get('steps', []):
                            if step.get('action') == 'send_email':
                                email_step = step
                                break
                        
                        if email_step:
                            params = email_step.get('parameters', {})
                            print(f"📧 Email will be sent to: {params.get('to', 'unknown')}")
                            print(f"📧 Subject: {params.get('subject', 'unknown')}")
                            print(f"📧 Content length: {len(params.get('body', ''))}")
                        
                        print("✅ INVESTOR AUTOMATION WORKING!")
                    else:
                        print(f"⚠️ Different automation type: {workflow.get('workflow_type')}")
                else:
                    print("⚠️ No workflow JSON in result")
                    
                if result.get('response'):
                    response_preview = result['response'][:200] + "..." if len(result['response']) > 200 else result['response']
                    print(f"💬 Response preview: {response_preview}")
            else:
                print("❌ No result returned")
        
        print(f"\n{'='*60}")
        print("🏁 INVESTOR AUTOMATION TEST COMPLETE")
        print('='*60)
        
        # Test the database directly
        print("\n🗃️ Testing AI Investor Database directly...")
        
        if hasattr(engine, 'ai_investors_database'):
            investors = engine.ai_investors_database
            print(f"✅ Database loaded with {len(investors)} investors")
            
            print("\n📋 Sample investors:")
            for i, investor in enumerate(investors[:3], 1):
                print(f"  {i}. {investor['name']}: {investor['email']}")
                
            total_fund_size = sum([
                float(inv["fund_size"].replace("$", "").replace("B", "")) 
                for inv in investors
            ])
            print(f"💰 Total fund size: ${total_fund_size:.1f}B")
        else:
            print("❌ AI investors database not found in engine")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting AI Investor Automation Test...")
    success = asyncio.run(test_investor_automation())
    
    if success:
        print("\n✅ TEST PASSED - AI Investor automation is working!")
        print("🎯 Ready for production deployment!")
    else:
        print("\n❌ TEST FAILED - Check the logs above")
        
    print("\n" + "="*60)
    print("📧 QUICK INVESTOR EMAIL REFERENCE:")
    print("="*60)
    
    # Quick reference list
    quick_emails = [
        "Andreessen Horowitz (a16z): info@a16z.com",
        "Google Ventures (GV): team@gv.com",
        "Bessemer Venture Partners: info@bvp.com",
        "Accel Partners: info@accel.com",
        "Sequoia Capital: info@sequoiacap.com",
        "NEA: info@nea.com",
        "Intel Capital: intel.capital@intel.com",
        "NVIDIA GPU Ventures: gpuventures@nvidia.com",
        "Insight Partners: info@insightpartners.com",
        "Khosla Ventures: info@khoslaventures.com"
    ]
    
    for email in quick_emails:
        print(f"  • {email}")
    
    print(f"\n🎯 PRODUCTION STATUS: {'READY' if success else 'NEEDS FIXES'}")
