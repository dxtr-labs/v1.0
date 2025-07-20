#!/usr/bin/env python3
"""
Comprehensive test of the enhanced MCP LLM system with web access
"""

import asyncio
import time
import requests
import json

def test_endpoint(endpoint, data, description):
    """Test a specific endpoint"""
    print(f"\n🔧 {description}")
    print("-" * 50)
    
    try:
        url = f"http://127.0.0.1:8000{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result}")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Run comprehensive tests"""
    print("🚀 Enhanced MCP LLM System - Comprehensive Test Suite")
    print("=" * 70)
    print("Testing the AI system that now has:")
    print("✨ Internet access and web search capabilities")
    print("🤖 Advanced AI content generation")
    print("📧 Professional email automation with HTML templates")
    print("🔄 Multi-provider LLM support with fallback")
    print("🌐 HTTP request capabilities for external APIs")
    print("📚 Wikipedia integration for knowledge lookup")
    print("=" * 70)
    
    # Test 1: Basic health check
    try:
        response = requests.get("http://127.0.0.1:8000/health")
        if response.status_code == 200:
            print("✅ Server is running and healthy")
        else:
            print("❌ Server health check failed")
            return
    except:
        print("❌ Cannot connect to server")
        return
    
    # Test 2: AI Personal Assistant Email
    test_endpoint(
        "/send-email",
        {"message": "Send a personalized AI assistant email to slakshanand1105@gmail.com with productivity tips, latest tech news, and motivational content"},
        "AI Personal Assistant Email Generation"
    )
    
    time.sleep(2)
    
    # Test 3: Enhanced MCP with Web Search
    test_endpoint(
        "/enhanced-mcp/stream", 
        {"message": "Research the latest developments in artificial intelligence and machine learning for 2024, then create a comprehensive summary"},
        "Enhanced MCP with Web Search Capabilities"
    )
    
    time.sleep(2)
    
    # Test 4: Professional Newsletter
    test_endpoint(
        "/send-email",
        {"message": "Create a professional newsletter about emerging technologies including AI, blockchain, and quantum computing for slakshanand1105@gmail.com"},
        "Professional Newsletter Generation"
    )
    
    time.sleep(2)
    
    # Test 5: Technical Documentation
    test_endpoint(
        "/send-email",
        {"message": "Generate technical documentation about Python best practices and send it to slakshanand1105@gmail.com with code examples"},
        "Technical Documentation Creation"
    )
    
    time.sleep(2)
    
    # Test 6: Smart Email with Web Research
    test_endpoint(
        "/send-email",
        {"message": "Research current market trends in renewable energy and create an informative report email for slakshanand1105@gmail.com"},
        "Smart Email with Web Research"
    )
    
    print("\n" + "=" * 70)
    print("🎉 Comprehensive testing completed!")
    print("\n📧 Check slakshanand1105@gmail.com for:")
    print("   • AI Personal Assistant emails")
    print("   • Professional newsletters") 
    print("   • Technical documentation")
    print("   • Research-based reports")
    print("\n✨ Features demonstrated:")
    print("   🔍 Web search integration")
    print("   🤖 Advanced AI content generation")
    print("   📧 Professional email templates")
    print("   🎨 HTML formatting with styling")
    print("   🔄 Multi-round MCP processing")
    print("   🌐 Internet-powered content creation")
    print("\n🚀 Your MCP LLM system is now significantly smarter with internet access!")

if __name__ == "__main__":
    main()
