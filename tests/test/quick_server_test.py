#!/usr/bin/env python3
"""
Quick Server Test
"""

import requests
import time

def test_current_server():
    base_url = "http://localhost:8002"
    
    print("Testing current server...")
    
    # Test different endpoints
    endpoints = [
        "/docs",
        "/api/chat/mcpai", 
        "/api/auth/login"
    ]
    
    for endpoint in endpoints:
        try:
            if endpoint == "/api/chat/mcpai":
                # POST request for chat
                response = requests.post(
                    f"{base_url}{endpoint}",
                    json={"message": "Hello"},
                    timeout=5
                )
            elif endpoint == "/api/auth/login":
                # POST request for login
                response = requests.post(
                    f"{base_url}{endpoint}",
                    json={"email": "test@test.com", "password": "test"},
                    timeout=5
                )
            else:
                # GET request
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            print(f"✅ {endpoint}: {response.status_code}")
            if response.status_code >= 400:
                print(f"   Error: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint}: Connection refused")
        except requests.exceptions.Timeout:
            print(f"⏰ {endpoint}: Timeout")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

if __name__ == "__main__":
    test_current_server()
