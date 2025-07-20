#!/usr/bin/env python3
"""
Demo script showing flexible email parameter extraction
This script demonstrates the email parameter extraction functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.mcp.simple_mcp_llm import MCP_LLM_Orchestrator

def demo_email_parameter_extraction():
    print("🧪 FLEXIBLE EMAIL PARAMETER EXTRACTION DEMO")
    print("=" * 60)
    
    # Create MCP orchestrator instance
    orchestrator = MCP_LLM_Orchestrator()
    
    # Test cases demonstrating flexible parameter space
    test_cases = [
        {
            "name": "📧 Standard Email Format",
            "input": "send email to john@company.com with subject 'Project Update' and message 'The project is on track'",
            "description": "Classic email format with standard parameters"
        },
        {
            "name": "🤖 AI-Generated Sales Pitch", 
            "input": "service:inhouse generate sales pitch for healthy ice cream send to customer@restaurant.com",
            "description": "AI content generation with email delivery"
        },
        {
            "name": "📮 Flexible Parameter Names",
            "input": "email recipient: alex@startup.com title: Meeting Reminder content: Don't forget our 3pm meeting cc: team@startup.com",
            "description": "Alternative parameter names (recipient, title, content, cc)"
        },
        {
            "name": "🚨 Priority Email",
            "input": "urgent email to boss@company.com subject: Server Down saying: The main server is experiencing issues priority: high",
            "description": "Priority handling with flexible content specification"
        },
        {
            "name": "📢 Marketing Blast",
            "input": "send marketing email to list@customers.com with bcc: analytics@company.com about our new product launch using professional template",
            "description": "Marketing email with BCC and template style"
        },
        {
            "name": "🎯 AI Service Selection",
            "input": "service:openai create email to client@enterprise.com with subject titled 'Proposal Ready' telling them the proposal is complete",
            "description": "OpenAI service with flexible subject and content parameters"
        }
    ]
    
    print("Testing email parameter extraction from various input formats:")
    print("-" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"Input: {test_case['input']}")
        print(f"Description: {test_case['description']}")
        
        try:
            # Extract email parameters using the flexible system
            email_params = orchestrator._extract_email_parameters(
                test_case['input'], 
                {"extracted_emails": ["extracted@example.com"]}
            )
            
            print("✅ Extracted Parameters:")
            for key, value in email_params.items():
                if value:  # Only show non-empty values
                    display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                    print(f"   📌 {key}: {display_value}")
            
        except Exception as e:
            print(f"❌ Error extracting parameters: {e}")
        
        print("-" * 60)
    
    print("\n🎯 FLEXIBLE PARAMETER SYSTEM FEATURES:")
    print("=" * 60)
    print("✅ Multiple Email Address Parameters:")
    print("   • toEmail, to, recipient, email")
    print("✅ Subject Line Variations:")
    print("   • subject, title, subjectLine, 'with subject', 'titled'")
    print("✅ Content Parameters:")
    print("   • content, text, body, message, 'saying', 'telling them'")
    print("✅ Advanced Features:")
    print("   • CC/BCC support (cc, bcc, carbonCopy, blindCarbonCopy)")
    print("   • Priority detection (urgent, high, low, asap)")
    print("   • Template styles (professional, marketing, sales)")
    print("   • Auto-subject generation from content")
    print("   • AI service integration (inhouse, openai, claude)")
    
    print("\n🚀 SYSTEM BENEFITS:")
    print("=" * 60)
    print("• 🔄 Works with both direct email requests AND AI-generated content")
    print("• 🎨 Supports multiple input formats and natural language")
    print("• 🤖 Seamlessly integrates with AI services for content generation")
    print("• 📧 Handles complex email scenarios (CC, BCC, priority, templates)")
    print("• 🛠️ Flexible parameter space adapts to user preferences")
    
    print("\n✨ Ready for production use with comprehensive email automation!")

if __name__ == "__main__":
    demo_email_parameter_extraction()
