#!/usr/bin/env python3
"""
Quick test of Zoom OAuth endpoint
"""

import requests

def test_zoom_oauth():
    """Quick test of Zoom OAuth authorization"""
    print("🔗 Testing Zoom OAuth Authorization")
    
    try:
        response = requests.get("http://localhost:8002/api/oauth/zoom/authorize", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ OAuth endpoint working!")
            print(f"OAuth URL available: {'oauth_url' in result}")
            if 'oauth_url' in result:
                print(f"URL preview: {result['oauth_url'][:80]}...")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_zoom_oauth()
