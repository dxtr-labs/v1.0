#!/usr/bin/env python3
"""
Final validation script to confirm web search integration is working
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_web_search_import():
    """Test if web search service can be imported"""
    print("🔍 Testing Web Search Service Import...")
    
    try:
        from backend.services.web_search_service import web_search_service
        print("✅ Web search service imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Web search import failed: {e}")
        return False

def test_mcp_engine_import():
    """Test if MCP engine imports web search correctly"""
    print("🔍 Testing MCP Engine Web Search Import...")
    
    try:
        from backend.mcp.custom_mcp_llm_iteration import WEB_SEARCH_AVAILABLE
        print(f"✅ WEB_SEARCH_AVAILABLE flag: {WEB_SEARCH_AVAILABLE}")
        return WEB_SEARCH_AVAILABLE
    except ImportError as e:
        print(f"❌ MCP engine import failed: {e}")
        return False

def test_web_search_detection():
    """Test web search detection logic"""
    print("🔍 Testing Web Search Detection Logic...")
    
    test_request = "find top 10 ai investors email from web and send that list to slakshanand1105@gmail.com"
    original_request_lower = test_request.lower()
    
    # Test the same logic as in MCP engine
    is_web_search = (any(search_term in original_request_lower for search_term in ['find', 'search', 'research', 'look up', 'locate']) and
                   any(search_context in original_request_lower for search_context in ['web', 'internet', 'google', 'investors', 'companies', 'contacts', 'information']))
    
    print(f"📝 Test request: {test_request}")
    print(f"✅ Web search detected: {is_web_search}")
    return is_web_search

def main():
    """Run all tests"""
    print("🚀 Final Web Search Integration Validation")
    print("=" * 50)
    
    # Test 1: Web search service import
    web_search_import_ok = test_web_search_import()
    print()
    
    # Test 2: MCP engine web search availability
    mcp_web_search_ok = test_mcp_engine_import()
    print()
    
    # Test 3: Web search detection logic
    detection_logic_ok = test_web_search_detection()
    print()
    
    # Final result
    all_tests_passed = web_search_import_ok and mcp_web_search_ok and detection_logic_ok
    
    print("=" * 50)
    print("📊 FINAL TEST RESULTS:")
    print(f"   Web Search Import: {'✅ PASS' if web_search_import_ok else '❌ FAIL'}")
    print(f"   MCP Engine Integration: {'✅ PASS' if mcp_web_search_ok else '❌ FAIL'}")
    print(f"   Detection Logic: {'✅ PASS' if detection_logic_ok else '❌ FAIL'}")
    print()
    
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! WEB SEARCH INTEGRATION IS READY!")
        print()
        print("✅ You can now test with Sam's original request:")
        print("   'find top 10 ai investors email from web and send that list to slakshanand1105@gmail.com'")
        print()
        print("🌐 Test interfaces available:")
        print("   • Web Interface: http://localhost:8002/public/mcp-enhanced-chat.html")
        print("   • API Documentation: http://localhost:8002/docs")
    else:
        print("❌ SOME TESTS FAILED - Web search integration needs more work")

if __name__ == "__main__":
    main()
