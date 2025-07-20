#!/usr/bin/env python3
"""
Test AI confirmation logic
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from mcp.ai_content_generator import ai_content_generator
except ImportError:
    print("❌ Could not import ai_content_generator")
    print("Current working directory:", os.getcwd())
    print("Python path:", sys.path)
    exit(1)

def test_ai_confirmation():
    print("🧪 Testing AI confirmation logic")
    
    test_cases = [
        "generate cold email idea to sell product- arithect company and send to slakshanand1105@gmail.com",
        "generate ai ideas for selling product and send email to slakshanand1105@gmail.com",
        "send email to user@example.com saying hello",
        "create beautiful email template for user@example.com"
    ]
    
    for test_input in test_cases:
        should_ask = ai_content_generator.should_ask_for_ai_generation(test_input)
        print(f"Input: {test_input[:50]}...")
        print(f"Should ask for AI generation: {should_ask}")
        
        if should_ask:
            prompt = ai_content_generator.create_confirmation_prompt(test_input, "slakshanand1105@gmail.com")
            print(f"Confirmation prompt: {prompt}")
        
        print("-" * 60)

if __name__ == "__main__":
    test_ai_confirmation()
