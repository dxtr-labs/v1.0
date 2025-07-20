#!/usr/bin/env python3
"""
Simple test showing Roomify-specific content generation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.mcp.fastmcp_content_generator import FastMCPContentGenerator

def test_roomify_content():
    """Test Roomify-specific content generation"""
    print("=== Testing Roomify Content Generation ===\n")
    
    content_generator = FastMCPContentGenerator()
    
    # Test 1: Generic prompt that should trigger default content
    print("🧪 Test 1: Generic sales email")
    result1 = content_generator.generate_content(
        prompt="Generate a sales email",
        custom_prompt="Make it professional"
    )
    print(f"Subject: {result1.get('subject', 'No subject')}")
    print(f"Contains 'Roomify': {'roomify' in result1.get('main_content', '').lower()}\n")
    
    # Test 2: Roomify-specific prompt
    print("🧪 Test 2: Roomify-specific sales email")
    result2 = content_generator.generate_content(
        prompt="Generate a sales email for Roomify",
        custom_prompt="Focus on college roommate matching platform"
    )
    print(f"Subject: {result2.get('subject', 'No subject')}")
    print(f"Contains 'Roomify': {'roomify' in result2.get('main_content', '').lower()}")
    print(f"Contains 'roommate': {'roommate' in result2.get('main_content', '').lower()}")
    print(f"Contains 'college': {'college' in result2.get('main_content', '').lower()}")
    
    # Show content preview
    content = result2.get('main_content', '')
    if content:
        print(f"\nContent Preview: {content[:300]}...")
    
    print(f"\n✅ Template: {result2.get('template_used', 'Unknown')}")

if __name__ == "__main__":
    test_roomify_content()
