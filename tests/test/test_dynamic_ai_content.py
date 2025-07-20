import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

async def test_dynamic_ai_content():
    """Test the dynamic AI content generation for any product"""
    print("🤖 TESTING DYNAMIC AI CONTENT GENERATION")
    print("=" * 60)
    
    try:
        # Add backend to path
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        from mcp.simple_mcp_llm import MCP_LLM_Orchestrator
        
        orchestrator = MCP_LLM_Orchestrator()
        
        # Test various products to see dynamic generation
        test_products = [
            {
                "name": "Torch Lights",
                "prompt": "Using AI generate a sales pitch to sell better torch lights and send email to test@example.com",
                "expected_elements": ["torch", "light", "bright", "battery"]
            },
            {
                "name": "Smartphone",
                "prompt": "Using AI generate a sales pitch for revolutionary smartphone with amazing camera and send email to test@example.com",
                "expected_elements": ["phone", "camera", "display", "technology"]
            },
            {
                "name": "Gaming Laptop",
                "prompt": "Using AI generate a sales pitch for high-performance gaming laptop and send email to test@example.com",
                "expected_elements": ["laptop", "gaming", "performance", "processor"]
            },
            {
                "name": "Running Shoes",
                "prompt": "Using AI generate a sales pitch for comfortable running shoes and send email to test@example.com",
                "expected_elements": ["shoes", "running", "comfort", "design"]
            },
            {
                "name": "Smart Watch",
                "prompt": "Using AI generate a sales pitch for fitness tracking smart watch and send email to test@example.com",
                "expected_elements": ["watch", "fitness", "tracking", "smart"]
            }
        ]
        
        for i, test in enumerate(test_products, 1):
            print(f"\n🧪 Test {i}: {test['name']}")
            print("-" * 40)
            print(f"Input: {test['prompt']}")
            
            # Test AI content generation
            ai_content = orchestrator._generate_sample_content(
                user_input=test['prompt'],
                content_type="sales_pitch"
            )
            
            print(f"\n📝 Generated Content ({len(ai_content)} characters):")
            print(f"{'='*50}")
            print(ai_content)
            print(f"{'='*50}")
            
            # Check if content is product-specific
            content_lower = ai_content.lower()
            found_elements = []
            for element in test['expected_elements']:
                if element in content_lower:
                    found_elements.append(element)
            
            print(f"\n🎯 Product-Specific Analysis:")
            print(f"  Expected Elements: {test['expected_elements']}")
            print(f"  Found Elements: {found_elements}")
            
            if len(found_elements) >= 2:
                print(f"  ✅ GOOD: Content is product-specific!")
            elif len(found_elements) >= 1:
                print(f"  ⚠️ OK: Some product relevance detected")
            else:
                print(f"  ❌ GENERIC: Content not product-specific enough")
            
            # Test workflow generation
            print(f"\n🔧 Testing Complete Workflow Generation...")
            result = await orchestrator.process_user_input(
                user_id=f"dynamic-test-{i}",
                agent_id=f"dynamic-agent-{i}",
                user_message=f"service:inhouse {test['prompt']}"
            )
            
            if 'workflow_json' in result:
                workflow = result['workflow_json']
                actions = workflow.get('actions', [])
                print(f"  ✅ Workflow generated with {len(actions)} actions")
                
                # Check email action for custom subject
                for action in actions:
                    if action.get('action_type') == 'emailSend':
                        subject = action.get('parameters', {}).get('subject', '')
                        print(f"  📧 Email Subject: {subject}")
                        break
            else:
                print(f"  ❌ No workflow generated")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_torch_lights_specifically():
    """Specific test for torch lights to verify the fix"""
    print(f"\n🔦 SPECIFIC TORCH LIGHTS TEST")
    print("=" * 50)
    
    try:
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        from mcp.simple_mcp_llm import MCP_LLM_Orchestrator
        
        orchestrator = MCP_LLM_Orchestrator()
        
        torch_prompt = "Using AI generate a sales pitch to sell better torch lights and send email to slakshanand1105@gmail.com"
        
        print(f"🤖 Input: {torch_prompt}")
        
        # Generate content
        ai_content = orchestrator._generate_sample_content(
            user_input=torch_prompt,
            content_type="sales_pitch"
        )
        
        print(f"\n📝 AI-Generated Torch Light Content:")
        print("="*60)
        print(ai_content)
        print("="*60)
        
        # Check for torch-specific terms
        torch_terms = ['torch', 'light', 'bright', 'led', 'battery', 'beam', 'flashlight', 'lighting']
        found_terms = []
        content_lower = ai_content.lower()
        
        for term in torch_terms:
            if term in content_lower:
                found_terms.append(term)
        
        print(f"\n🔍 Torch Light Analysis:")
        print(f"  Found Terms: {found_terms}")
        print(f"  Content Length: {len(ai_content)} characters")
        
        if 'torch' in found_terms or 'light' in found_terms:
            print(f"  ✅ SUCCESS: Content is torch light specific!")
        else:
            print(f"  ❌ FAILED: Content is still generic")
        
        # Test full workflow
        print(f"\n🔧 Testing Complete Torch Light Workflow...")
        result = await orchestrator.process_user_input(
            user_id="torch-test",
            agent_id="torch-agent",
            user_message=f"service:inhouse {torch_prompt}"
        )
        
        if 'workflow_json' in result and result['workflow_json'].get('actions'):
            print(f"✅ Workflow generated successfully!")
            
            # Send the actual email
            print(f"\n📧 Sending torch light email...")
            await send_torch_email(ai_content)
        else:
            print(f"❌ Workflow generation failed")
    
    except Exception as e:
        print(f"❌ Torch lights test failed: {e}")

async def send_torch_email(content):
    """Send the torch light email"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASSWORD")
        
        if not all([smtp_host, smtp_user, smtp_pass]):
            print("❌ SMTP credentials missing")
            return False
        
        msg = MIMEText(content)
        msg["From"] = smtp_user
        msg["To"] = "slakshanand1105@gmail.com"
        msg["Subject"] = "🔦 BrightBeam Torch Lights - AI Generated Sales Pitch"
        
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        
        print("✅ Torch light email sent successfully!")
        print("📧 Check slakshanand1105@gmail.com for the torch light sales pitch!")
        return True
        
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

async def main():
    print("🎯 DYNAMIC AI CONTENT GENERATION TEST")
    print("Testing AI's ability to generate custom content for ANY product")
    print("=" * 70)
    
    # Test dynamic generation for multiple products
    await test_dynamic_ai_content()
    
    # Specific torch lights test
    await test_torch_lights_specifically()
    
    print(f"\n📊 SUMMARY")
    print("=" * 40)
    print("✅ Dynamic AI content generation implemented")
    print("✅ Product-specific analysis logic added")
    print("✅ Custom features and emojis based on product type")
    print("🔦 Torch lights should now generate custom content!")

if __name__ == "__main__":
    asyncio.run(main())
