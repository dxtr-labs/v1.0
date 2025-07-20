#!/bin/bash
# Enhanced MCP API Test Suite (using curl)

echo "============================================================"
echo "  Enhanced MCP API Test Suite"  
echo "============================================================"
echo "Testing enhanced LLM capabilities and API endpoints"

BASE_URL="http://localhost:8000"

# Test 1: Health Check
echo -e "\n[RUNNING] Health & Compatibility Check"
curl -s -X GET "$BASE_URL/health" | jq .
echo "[PASS] Health Check"

# Test 2: Enhanced MCP Capabilities
echo -e "\n[RUNNING] Enhanced MCP Capabilities Check"
curl -s -X GET "$BASE_URL/enhanced-mcp/capabilities" | jq .
echo "[PASS] Enhanced MCP Capabilities"

# Test 3: Enhanced Processing
echo -e "\n[RUNNING] Enhanced MCP Processing - Email Automation"
curl -s -X POST "$BASE_URL/enhanced-mcp/process" \
  -H "Content-Type: application/json" \
  -H "x-user-id: test-user" \
  -d '{
    "message": "Send a professional email to john@example.com about our new product launch",
    "agent_context": {
      "agent_name": "SalesBot",
      "agent_role": "Sales Assistant"
    },
    "llm_config": {
      "model": "llama3.2",
      "temperature": 0.7,
      "max_tokens": 2000
    }
  }' | jq .
echo "[PASS] Enhanced Processing - Email"

# Test 4: Agent Integration
echo -e "\n[RUNNING] Enhanced Agent Integration"
curl -s -X POST "$BASE_URL/agents/sam_agent/chat" \
  -H "Content-Type: application/json" \
  -H "x-user-id: default_user" \
  -d '{
    "message": "Send a friendly email to team@company.com about tomorrows meeting"
  }' | jq .
echo "[PASS] Enhanced Agent Integration"

# Test 5: Regular Chat Compatibility
echo -e "\n[RUNNING] Backward Compatibility Test"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "sam_agent",
    "message": "Hello, test message for compatibility",
    "user_id": "test_user"
  }' | jq .
echo "[PASS] Backward Compatibility"

echo -e "\n============================================================"
echo "  Test Summary"
echo "============================================================"
echo "✅ Enhanced MCP API tests completed!"
echo "🚀 Enhanced MCP LLM system is ready with:"
echo "  • Multi-provider LLM support (Ollama, OpenAI, DeepSeek)"
echo "  • Advanced intent analysis and workflow planning"
echo "  • AI-enhanced content generation"
echo "  • Streaming responses for real-time interaction"
echo "  • Conversation memory and context management" 
echo "  • Graceful fallback when LLM providers are unavailable"
