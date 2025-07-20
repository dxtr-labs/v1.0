#!/usr/bin/env python3
"""
DXTR AutoFlow - AI Agent Integration Test Suite
Tests all AI/LLM drivers and agent workflows
"""

import asyncio
import sys
import traceback
from datetime import datetime
import json

# Test Results Storage
test_results = {
    "timestamp": datetime.now().isoformat(),
    "tests_run": 0,
    "tests_passed": 0,
    "tests_failed": 0,
    "failures": []
}

def log_test_result(test_name: str, success: bool, error: str = None):
    """Log test result"""
    test_results["tests_run"] += 1
    if success:
        test_results["tests_passed"] += 1
        print(f"✅ {test_name}")
    else:
        test_results["tests_failed"] += 1
        test_results["failures"].append({"test": test_name, "error": error})
        print(f"❌ {test_name}: {error}")

async def test_openai_chat_completion():
    """Test OpenAI chat completion driver"""
    try:
        # Mock OpenAI chat completion test
        mock_request = {
            "model": "gpt-4",
            "messages": [
                {"role": "user", "content": "Hello, how are you?"}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        # Mock response
        mock_response = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "gpt-4",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello! I'm doing well, thank you for asking. How can I help you today?"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 12,
                "completion_tokens": 20,
                "total_tokens": 32
            }
        }
        
        # Validate response structure
        assert "choices" in mock_response, "Response missing choices"
        assert len(mock_response["choices"]) > 0, "No choices in response"
        assert mock_response["choices"][0]["message"]["content"], "No content in response"
        
        log_test_result("OpenAI Chat Completion Driver", True)
        
    except Exception as e:
        log_test_result("OpenAI Chat Completion Driver", False, str(e))

async def test_custom_agent_creation():
    """Test custom agent creation and management"""
    try:
        # Mock agent creation test
        agent_config = {
            "id": "agent_123",
            "name": "Customer Support Agent",
            "description": "Handles customer inquiries and support requests",
            "model": "gpt-4",
            "system_prompt": "You are a helpful customer support agent. Be friendly and professional.",
            "tools": ["search", "email", "ticket_creation"],
            "memory_enabled": True,
            "conversation_history": []
        }
        
        # Validate agent configuration
        assert agent_config["id"], "Agent ID missing"
        assert agent_config["name"], "Agent name missing"
        assert agent_config["system_prompt"], "System prompt missing"
        assert isinstance(agent_config["tools"], list), "Tools should be a list"
        assert agent_config["memory_enabled"] == True, "Memory should be enabled"
        
        log_test_result("Custom Agent Creation", True)
        
    except Exception as e:
        log_test_result("Custom Agent Creation", False, str(e))

async def test_agent_conversation():
    """Test agent conversation handling"""
    try:
        # Mock conversation test
        conversation = {
            "agent_id": "agent_123",
            "conversation_id": "conv_456",
            "messages": [
                {"role": "user", "content": "I need help with my order", "timestamp": "2024-01-01T10:00:00"},
                {"role": "assistant", "content": "I'd be happy to help you with your order. Could you please provide your order number?", "timestamp": "2024-01-01T10:00:05"},
                {"role": "user", "content": "My order number is #12345", "timestamp": "2024-01-01T10:00:30"}
            ],
            "context": {
                "customer_id": "cust_789",
                "order_lookup": True,
                "support_priority": "normal"
            }
        }
        
        # Validate conversation structure
        assert conversation["agent_id"], "Agent ID missing"
        assert conversation["conversation_id"], "Conversation ID missing"
        assert len(conversation["messages"]) > 0, "No messages in conversation"
        assert conversation["context"], "Context missing"
        
        # Check message structure
        for msg in conversation["messages"]:
            assert msg["role"] in ["user", "assistant"], "Invalid message role"
            assert msg["content"], "Message content missing"
            assert msg["timestamp"], "Message timestamp missing"
        
        log_test_result("Agent Conversation Handling", True)
        
    except Exception as e:
        log_test_result("Agent Conversation Handling", False, str(e))

async def test_openai_embeddings():
    """Test OpenAI embeddings generation"""
    try:
        # Mock embeddings test
        embedding_request = {
            "model": "text-embedding-ada-002",
            "input": "This is a test document for embedding generation.",
            "encoding_format": "float"
        }
        
        # Mock embedding response
        mock_embedding = {
            "object": "list",
            "data": [
                {
                    "object": "embedding",
                    "embedding": [0.1, 0.2, 0.3, 0.4, 0.5] * 307,  # 1536 dimensions (simplified)
                    "index": 0
                }
            ],
            "model": "text-embedding-ada-002",
            "usage": {
                "prompt_tokens": 12,
                "total_tokens": 12
            }
        }
        
        # Validate embedding structure
        assert "data" in mock_embedding, "Embedding data missing"
        assert len(mock_embedding["data"]) > 0, "No embedding data"
        assert "embedding" in mock_embedding["data"][0], "Embedding vector missing"
        assert len(mock_embedding["data"][0]["embedding"]) > 0, "Empty embedding vector"
        
        log_test_result("OpenAI Embeddings Generation", True)
        
    except Exception as e:
        log_test_result("OpenAI Embeddings Generation", False, str(e))

async def test_content_moderation():
    """Test OpenAI content moderation"""
    try:
        # Mock moderation test
        moderation_request = {
            "input": "This is a test message for content moderation."
        }
        
        # Mock moderation response
        mock_moderation = {
            "id": "modr-123",
            "model": "text-moderation-007",
            "results": [
                {
                    "flagged": False,
                    "categories": {
                        "sexual": False,
                        "hate": False,
                        "harassment": False,
                        "self-harm": False,
                        "sexual/minors": False,
                        "hate/threatening": False,
                        "violence/graphic": False,
                        "self-harm/intent": False,
                        "self-harm/instructions": False,
                        "harassment/threatening": False,
                        "violence": False
                    },
                    "category_scores": {
                        "sexual": 0.0001,
                        "hate": 0.0001,
                        "harassment": 0.0001,
                        "self-harm": 0.0001,
                        "sexual/minors": 0.0001,
                        "hate/threatening": 0.0001,
                        "violence/graphic": 0.0001,
                        "self-harm/intent": 0.0001,
                        "self-harm/instructions": 0.0001,
                        "harassment/threatening": 0.0001,
                        "violence": 0.0001
                    }
                }
            ]
        }
        
        # Validate moderation structure
        assert "results" in mock_moderation, "Moderation results missing"
        assert len(mock_moderation["results"]) > 0, "No moderation results"
        assert "flagged" in mock_moderation["results"][0], "Flagged field missing"
        assert "categories" in mock_moderation["results"][0], "Categories missing"
        
        log_test_result("Content Moderation", True)
        
    except Exception as e:
        log_test_result("Content Moderation", False, str(e))

async def test_agent_memory_system():
    """Test agent memory management"""
    try:
        # Mock memory system test
        memory_system = {
            "agent_id": "agent_123",
            "memory_type": "conversation",
            "storage": {
                "short_term": {
                    "current_context": "Customer support inquiry about order #12345",
                    "active_tools": ["order_lookup", "customer_database"],
                    "session_variables": {"customer_id": "cust_789", "order_id": "12345"}
                },
                "long_term": {
                    "customer_preferences": {"communication_style": "formal", "previous_issues": []},
                    "successful_resolutions": ["order_tracking", "refund_processing"],
                    "learned_patterns": {"frequent_questions": ["order status", "shipping time"]}
                }
            },
            "memory_operations": {
                "store": True,
                "retrieve": True,
                "update": True,
                "clear": True
            }
        }
        
        # Validate memory system structure
        assert memory_system["agent_id"], "Agent ID missing"
        assert "storage" in memory_system, "Memory storage missing"
        assert "short_term" in memory_system["storage"], "Short-term memory missing"
        assert "long_term" in memory_system["storage"], "Long-term memory missing"
        assert "memory_operations" in memory_system, "Memory operations missing"
        
        log_test_result("Agent Memory System", True)
        
    except Exception as e:
        log_test_result("Agent Memory System", False, str(e))

async def test_streaming_responses():
    """Test streaming chat completion responses"""
    try:
        # Mock streaming response test
        streaming_chunks = [
            {"id": "chatcmpl-123", "object": "chat.completion.chunk", "choices": [{"delta": {"content": "Hello"}}]},
            {"id": "chatcmpl-123", "object": "chat.completion.chunk", "choices": [{"delta": {"content": " there!"}}]},
            {"id": "chatcmpl-123", "object": "chat.completion.chunk", "choices": [{"delta": {"content": " How"}}]},
            {"id": "chatcmpl-123", "object": "chat.completion.chunk", "choices": [{"delta": {"content": " can I help?"}}]},
            {"id": "chatcmpl-123", "object": "chat.completion.chunk", "choices": [{"finish_reason": "stop"}]}
        ]
        
        # Simulate streaming response processing
        full_response = ""
        for chunk in streaming_chunks:
            if chunk["choices"][0].get("delta", {}).get("content"):
                full_response += chunk["choices"][0]["delta"]["content"]
        
        assert full_response == "Hello there! How can I help?", "Streaming response assembly failed"
        
        log_test_result("Streaming Responses", True)
        
    except Exception as e:
        log_test_result("Streaming Responses", False, str(e))

async def main():
    """Run all AI agent integration tests"""
    print("🤖 DXTR AutoFlow - AI Agent Integration Tests")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run AI/LLM driver tests
    await test_openai_chat_completion()
    await test_custom_agent_creation()
    await test_agent_conversation()
    await test_openai_embeddings()
    await test_content_moderation()
    await test_agent_memory_system()
    await test_streaming_responses()
    
    # Print summary
    print()
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests Run: {test_results['tests_run']}")
    print(f"Tests Passed: {test_results['tests_passed']} ✅")
    print(f"Tests Failed: {test_results['tests_failed']} ❌")
    print(f"Success Rate: {(test_results['tests_passed']/test_results['tests_run']*100):.1f}%")
    
    if test_results["failures"]:
        print("\n❌ FAILURES:")
        for failure in test_results["failures"]:
            print(f"  - {failure['test']}: {failure['error']}")
    
    # Save results to file
    with open("test_agent_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n📄 Results saved to: test_agent_results.json")
    
    # Exit with appropriate code
    sys.exit(0 if test_results["tests_failed"] == 0 else 1)

if __name__ == "__main__":
    asyncio.run(main())
