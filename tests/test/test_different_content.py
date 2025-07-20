import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.mcp.simple_mcp_llm import MCP_LLM_Orchestrator

async def test_different_content():
    """Test various AI content generation scenarios and send emails"""
    
    orchestrator = MCP_LLM_Orchestrator()
    
    # Different test scenarios
    test_scenarios = [
        {
            "name": "Tech Startup - DevTools",
            "message": "service:inhouse Using AI generate a sales pitch for CodeMaster - a revolutionary IDE for developers and send to slakshanand1105@gmail.com"
        },
        {
            "name": "Food Business - Pizza Delivery", 
            "message": "service:inhouse Using AI generate a marketing email for PizzaExpress - fastest pizza delivery in town and send to slakshanand1105@gmail.com"
        },
        {
            "name": "Education - Online Courses",
            "message": "service:inhouse Using AI generate a promotional email for LearnHub - online coding bootcamp and send to slakshanand1105@gmail.com"
        },
        {
            "name": "Health & Fitness - Gym",
            "message": "service:inhouse Using AI generate a sales pitch for FitPro - 24/7 smart gym with AI trainers and send to slakshanand1105@gmail.com"
        },
        {
            "name": "E-commerce - Fashion",
            "message": "service:inhouse Using AI generate a marketing email for StyleHub - trendy fashion for young professionals and send to slakshanand1105@gmail.com"
        }
    ]
    
    print("🧪 Testing Different AI Content Generation Scenarios...")
    print("=" * 60)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. Testing: {scenario['name']}")
        print(f"Request: {scenario['message']}")
        print("-" * 50)
        
        try:
            result = await orchestrator.process_user_input("test_user", "test_agent", scenario['message'])
            
            print(f"Status: {result.get('status', 'Unknown')}")
            
            if result.get('workflow_preview') and result['workflow_preview'].get('email_preview'):
                preview = result['workflow_preview']['email_preview']
                
                print(f"✅ EMAIL GENERATED:")
                print(f"   TO: {preview.get('to', 'Unknown')}")
                print(f"   SUBJECT: {preview.get('subject', 'Unknown')}")
                print(f"   AI SERVICE: {preview.get('ai_service', 'Unknown')}")
                
                # Show first few lines of content
                content = preview.get('preview_content', '')
                content_lines = content.split('\n')
                preview_lines = []
                in_content_section = False
                
                for line in content_lines:
                    if '---' in line and not in_content_section:
                        in_content_section = True
                        continue
                    elif '---' in line and in_content_section:
                        break
                    elif in_content_section and line.strip():
                        preview_lines.append(line.strip())
                        if len(preview_lines) >= 5:  # Show first 5 lines
                            break
                
                print(f"   CONTENT PREVIEW:")
                for line in preview_lines:
                    print(f"   {line}")
                if len(preview_lines) >= 5:
                    print("   ...")
                
                print(f"   ESTIMATED CREDITS: {result.get('estimated_credits', 'Unknown')}")
            else:
                print(f"❌ No email preview generated")
                print(f"   Full result: {result}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print()

if __name__ == "__main__":
    asyncio.run(test_different_content())
