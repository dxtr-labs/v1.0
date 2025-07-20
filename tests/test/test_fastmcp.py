#!/usr/bin/env python3
"""Test FastMCP LLM capabilities"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from fastmcp import FastMCP
    from fastmcp.client import Client
    print("✅ FastMCP imports successful")
    
    # Check available methods
    print("FastMCP methods:", [m for m in dir(FastMCP) if not m.startswith('_')])
    print("Client methods:", [m for m in dir(Client) if not m.startswith('_')])
    
    # Try to test LLM completion
    print("\n=== Testing FastMCP LLM Completion ===")
    
    # Test simple completion
    app = FastMCP()
    
    # Check if we can use it for completions
    print("FastMCP app created")
    print("App methods:", [m for m in dir(app) if not m.startswith('_')])
    
    # Try to find completion capabilities
    if hasattr(app, 'complete'):
        print("✅ FastMCP has complete method")
    if hasattr(app, 'chat'):
        print("✅ FastMCP has chat method")
    if hasattr(app, 'generate'):
        print("✅ FastMCP has generate method")
        
    # Test message completion with Client
    try:
        # Simple test message
        test_prompt = "Generate a professional sales email for a transportation company called PRR TRAVELS"
        print(f"\nTesting with prompt: {test_prompt}")
        
        # Try using Client for completion
        print("\n🔄 Testing FastMCP Client completion...")
        client = Client()
        
        # Check if client can be used for completion
        if hasattr(client, 'complete'):
            print("✅ Client has complete method")
            # Try completion
            try:
                result = client.complete(test_prompt)
                print(f"✅ Completion successful: {result[:100]}...")
            except Exception as e:
                print(f"❌ Completion failed: {e}")
        
        # Try different approaches
        print("Available FastMCP attributes:", [attr for attr in dir(app) if 'complete' in attr.lower() or 'chat' in attr.lower() or 'generate' in attr.lower()])
        
    except Exception as e:
        print(f"Error testing completion: {e}")
    
except Exception as e:
    print(f"Error with FastMCP: {e}")
    
try:
    import fastmcp
    print(f"\nFastMCP version: {fastmcp.__version__}")
    
    # Check if there's an LLM or chat method
    if hasattr(fastmcp, 'chat'):
        print("FastMCP module has chat method")
    if hasattr(fastmcp, 'llm'):
        print("FastMCP module has llm method")
    if hasattr(fastmcp, 'complete'):
        print("FastMCP module has complete method")
    if hasattr(fastmcp, 'Client'):
        print("FastMCP module has Client class")
        
    # Check all available functions
    print("All FastMCP module contents:", [item for item in dir(fastmcp) if not item.startswith('_')])
        
except Exception as e:
    print(f"Error checking FastMCP features: {e}")
