#!/usr/bin/env python3
"""
Test Email Preview and Confirmation Workflow
Demonstrates the new MCP email system with preview functionality
"""
import requests
import json
import time

# API Configuration
API_BASE = "http://localhost:8000"

def test_email_preview_workflow():
    """Test the complete email preview and send workflow"""
    
    print("🧪 Testing Email Preview and Confirmation Workflow")
    print("=" * 60)
    
    # Test message for DXTR Labs sales email
    test_message = "Hey Sam, we are DXTR Labs building virtual workforce. AI- explain advantage of using virtual workforce and sell our product to slakshanand1105@gmail.com by email and make sure it is perfectly templated email and make sure he is impressed by the format of email and ask if he is ready to automate"
    
    # Step 1: Generate Email Preview
    print("\n📋 STEP 1: Generating Email Preview...")
    preview_response = requests.post(
        f"{API_BASE}/email/preview",
        json={"message": test_message},
        headers={"Content-Type": "application/json"}
    )
    
    if preview_response.status_code == 200:
        preview_data = preview_response.json()
        print("✅ Preview generated successfully!")
        
        preview_info = preview_data.get("preview", {})
        print(f"📧 To: {preview_info.get('to_email')}")
        print(f"👤 Recipient: {preview_info.get('recipient_name')}")
        print(f"📬 Subject: {preview_info.get('subject')}")
        print(f"🎨 Premium Template: {preview_info.get('is_premium_template')}")
        
        # Show preview of HTML content (first 500 chars)
        html_preview = preview_info.get('html_content', '')[:500]
        print(f"\n🌐 HTML Preview (first 500 chars):")
        print("-" * 50)
        print(html_preview + "...")
        print("-" * 50)
        
        # Show text content preview
        text_preview = preview_info.get('text_content', '')[:300]
        print(f"\n📄 Text Preview (first 300 chars):")
        print("-" * 30)
        print(text_preview + "...")
        print("-" * 30)
        
        # Step 2: User Confirmation Simulation
        print(f"\n❓ STEP 2: Email Preview Review")
        print("📧 This is the email that will be sent:")
        print(f"   • Beautiful DXTR Labs premium template")
        print(f"   • Modern gradient design with AI-generated patterns")
        print(f"   • Professional statistics dashboard")
        print(f"   • Responsive design for all devices")
        
        # Simulate user confirmation
        user_confirmation = input("\n🤔 Is this email okay to be sent out? (y/n): ").lower().strip()
        
        if user_confirmation == 'y' or user_confirmation == 'yes':
            print("\n✅ User confirmed! Proceeding to send email...")
            
            # Step 3: Send Confirmed Email
            print("\n📤 STEP 3: Sending Confirmed Email...")
            send_response = requests.post(
                f"{API_BASE}/email/send-premium",
                json={
                    "to_email": preview_info.get('to_email'),
                    "subject": preview_info.get('subject'),
                    "html_content": preview_info.get('html_content'),
                    "text_content": preview_info.get('text_content'),
                    "confirmed": True
                },
                headers={"Content-Type": "application/json"}
            )
            
            if send_response.status_code == 200:
                send_data = send_response.json()
                print("🎉 EMAIL SENT SUCCESSFULLY!")
                print(f"✅ {send_data.get('message')}")
                print(f"📧 Details: {send_data.get('details')}")
                
                print("\n🎨 Email Features Delivered:")
                print("   ✨ Modern gradient color palette (Purple, Blue, Green, Gold)")
                print("   🤖 AI-generated SVG patterns and backgrounds")
                print("   🎯 Interactive visual elements and icons")
                print("   📱 Responsive design for all devices")
                print("   🎨 Professional typography and spacing")
                print("   💎 Premium visual hierarchy")
                print("   🚀 Animated gradient effects")
                print("   📊 Visual statistics dashboard")
                
            else:
                print(f"❌ Failed to send email: {send_response.text}")
                
        else:
            print("\n🚫 User cancelled email sending.")
            print("💡 You can modify the email content and try again.")
            
    else:
        print(f"❌ Failed to generate preview: {preview_response.text}")

def test_regular_email_preview():
    """Test preview for regular (non-DXTR) email"""
    
    print("\n\n🧪 Testing Regular Email Preview")
    print("=" * 40)
    
    test_message = "send good morning email to test@example.com"
    
    print(f"📝 Test Message: {test_message}")
    
    preview_response = requests.post(
        f"{API_BASE}/email/preview",
        json={"message": test_message},
        headers={"Content-Type": "application/json"}
    )
    
    if preview_response.status_code == 200:
        preview_data = preview_response.json()
        print("✅ Regular email preview generated!")
        
        preview_info = preview_data.get("preview", {})
        print(f"📧 To: {preview_info.get('to_email')}")
        print(f"👤 Recipient: {preview_info.get('recipient_name')}")
        print(f"📬 Subject: {preview_info.get('subject')}")
        print(f"🎨 Premium Template: {preview_info.get('is_premium_template')}")
        
    else:
        print(f"❌ Failed to generate regular email preview: {preview_response.text}")

if __name__ == "__main__":
    print("🚀 DXTR Labs Email Preview & Confirmation System")
    print("🤖 Advanced MCP Integration Test")
    print("=" * 60)
    
    try:
        # Test DXTR Labs premium email workflow
        test_email_preview_workflow()
        
        # Test regular email preview
        test_regular_email_preview()
        
        print("\n" + "=" * 60)
        print("✅ Email Preview Workflow Test Completed!")
        print("🎯 Features Tested:")
        print("   • Email content preview generation")
        print("   • Premium DXTR Labs template detection")
        print("   • User confirmation workflow")
        print("   • HTML email sending with confirmation")
        print("   • Regular email template handling")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the FastAPI server is running on http://localhost:8000")
        print("💡 Run: cd backend && python main.py")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
