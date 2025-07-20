import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def show_ai_generated_emails():
    """Show the AI-generated email content without sending"""
    
    print("📧 AI Email Content Generator - Preview Mode")
    print("=" * 60)
    
    from backend.mcp.simple_mcp_llm import MCP_LLM_Orchestrator
    
    orchestrator = MCP_LLM_Orchestrator()
    
    # Test various business types
    test_businesses = [
        "CodeMaster - a revolutionary IDE for developers",
        "Roomify - one stop place for college students to find roommates", 
        "PizzaExpress - fastest pizza delivery in town",
        "FitPro - 24/7 smart gym with AI trainers",
        "StyleHub - trendy fashion for young professionals",
        "EcoClean - sustainable cleaning products for modern homes",
        "TechTutor - personalized online coding education platform"
    ]
    
    for i, business in enumerate(test_businesses, 1):
        print(f"\n{i}. Testing: {business}")
        print("-" * 50)
        
        message = f"service:inhouse Using AI generate a sales pitch for {business} and send to slakshanand1105@gmail.com"
        
        try:
            result = await orchestrator.process_user_input("test_user", "test_agent", message)
            
            if result.get('workflow_preview') and result['workflow_preview'].get('email_preview'):
                email_preview = result['workflow_preview']['email_preview']
                
                # Extract email details
                to_email = email_preview.get('to')
                subject = email_preview.get('subject', 'AI-Generated Content')
                
                # Extract the actual content from the preview
                preview_content = email_preview.get('preview_content', '')
                
                # Parse the content between the --- markers
                content_lines = preview_content.split('\n')
                email_content = []
                in_content_section = False
                
                for line in content_lines:
                    if '---' in line and not in_content_section:
                        in_content_section = True
                        continue
                    elif '---' in line and in_content_section:
                        break
                    elif in_content_section:
                        email_content.append(line)
                
                # Clean up the content
                final_content = '\n'.join(email_content).strip()
                
                # Remove the "Note: Final content will be generated..." line
                if "Note: Final content will be generated" in final_content:
                    final_content = final_content.split("Note: Final content will be generated")[0].strip()
                
                print(f"📧 TO: {to_email}")
                print(f"📧 SUBJECT: {subject}")
                print(f"📧 CONTENT:")
                print("-" * 30)
                print(final_content[:300] + "..." if len(final_content) > 300 else final_content)
                print("-" * 30)
                print(f"✅ Generated {len(final_content)} characters of custom content")
            else:
                print("❌ No email preview generated")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    asyncio.run(show_ai_generated_emails())
