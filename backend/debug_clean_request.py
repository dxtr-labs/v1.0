#!/usr/bin/env python3
"""
Debug the clean_request processing
"""

import re

def debug_clean_request():
    """Test the clean_request processing"""
    
    user_message = "service:inhouse Using AI generate a sales pitch to sell healthy mango ice cream and send email to slakshanand1105@gmail.com"
    
    print(f"Original message: {user_message}")
    
    # This is the same regex used in the code
    clean_request = re.sub(r'service:\s*\w+\s*', '', user_message, flags=re.IGNORECASE).strip()
    
    print(f"Clean request: '{clean_request}'")
    print(f"Clean request repr: {repr(clean_request)}")
    
    # Test if there are any quotes
    if '"' in clean_request:
        print("❌ Contains double quotes!")
    else:
        print("✅ No double quotes")
        
    if "'" in clean_request:
        print("❌ Contains single quotes!")
    else:
        print("✅ No single quotes")

if __name__ == "__main__":
    debug_clean_request()
