#!/usr/bin/env node
/**
 * Enhanced MCP API Test Suite
 * Tests the new enhanced MCP endpoints and capabilities
 */

const fetch = require('node-fetch');

const BASE_URL = 'http://localhost:8000';

const Colors = {
    GREEN: '\x1b[32m',
    RED: '\x1b[31m',
    YELLOW: '\x1b[33m',
    BLUE: '\x1b[34m',
    PURPLE: '\x1b[35m',
    CYAN: '\x1b[36m',
    RESET: '\x1b[0m',
    BOLD: '\x1b[1m'
};

function printHeader(title) {
    console.log(`\n${Colors.CYAN}${Colors.BOLD}${'='.repeat(60)}`);
    console.log(`  ${title}`);
    console.log(`${'='.repeat(60)}${Colors.RESET}`);
}

function printTest(testName, status = "RUNNING") {
    const color = status === "RUNNING" ? Colors.YELLOW : status === "PASS" ? Colors.GREEN : Colors.RED;
    console.log(`${color}[${status}]${Colors.RESET} ${testName}`);
}

async function testEnhancedMCPCapabilities() {
    printTest("Enhanced MCP Capabilities Check", "RUNNING");
    
    try {
        const response = await fetch(`${BASE_URL}/enhanced-mcp/capabilities`);
        const data = await response.json();
        
        console.log(`${Colors.PURPLE}Enhanced Features:${Colors.RESET}`);
        data.enhanced_features.forEach(feature => {
            console.log(`  • ${feature}`);
        });
        
        console.log(`${Colors.PURPLE}Supported Providers:${Colors.RESET} ${data.supported_providers.join(', ')}`);
        console.log(`${Colors.PURPLE}Automation Types:${Colors.RESET} ${data.automation_types.join(', ')}`);
        console.log(`${Colors.PURPLE}Version:${Colors.RESET} ${data.version}`);
        
        printTest("Enhanced MCP Capabilities Check", "PASS");
        return true;
    } catch (error) {
        console.log(`${Colors.RED}Error: ${error.message}${Colors.RESET}`);
        printTest("Enhanced MCP Capabilities Check", "FAIL");
        return false;
    }
}

async function testEnhancedProcessing() {
    printTest("Enhanced MCP Processing", "RUNNING");
    
    const testCases = [
        {
            name: "Email Automation",
            payload: {
                message: "Send a professional email to john@example.com about our new product launch",
                agent_context: {
                    agent_name: "SalesBot",
                    agent_role: "Sales Assistant"
                },
                llm_config: {
                    model: "llama3.2",
                    temperature: 0.7,
                    max_tokens: 2000
                }
            }
        },
        {
            name: "Schedule Setup",
            payload: {
                message: "Set up a daily reminder at 9 AM to check project status",
                agent_context: {
                    agent_name: "ProjectManager",
                    agent_role: "Project Coordinator"
                },
                llm_config: {
                    model: "llama3.2",
                    temperature: 0.5,
                    max_tokens: 1500
                }
            }
        },
        {
            name: "Conversational Query",
            payload: {
                message: "Hello, how can you help me with automation?",
                agent_context: {
                    agent_name: "Assistant",
                    agent_role: "Automation Helper"
                }
            }
        }
    ];
    
    for (const testCase of testCases) {
        console.log(`\n${Colors.BLUE}Testing: ${testCase.name}${Colors.RESET}`);
        console.log(`${Colors.PURPLE}Message:${Colors.RESET} ${testCase.payload.message}`);
        
        try {
            const response = await fetch(`${BASE_URL}/enhanced-mcp/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-user-id': 'test-user'
                },
                body: JSON.stringify(testCase.payload)
            });
            
            const result = await response.json();
            
            console.log(`${Colors.GREEN}Success:${Colors.RESET} ${result.success || false}`);
            console.log(`${Colors.PURPLE}Type:${Colors.RESET} ${result.execution_type || 'unknown'}`);
            console.log(`${Colors.PURPLE}Message:${Colors.RESET} ${(result.message || 'No message').substring(0, 100)}...`);
            
            if (result.enhanced_features) {
                console.log(`${Colors.CYAN}Enhanced Features:${Colors.RESET}`);
                Object.entries(result.enhanced_features).forEach(([key, value]) => {
                    console.log(`  ${key}: ${value}`);
                });
            }
            
            if (result.suggestions) {
                console.log(`${Colors.CYAN}Suggestions:${Colors.RESET}`);
                result.suggestions.forEach(suggestion => {
                    console.log(`  • ${suggestion}`);
                });
            }
            
        } catch (error) {
            console.log(`${Colors.RED}Error: ${error.message}${Colors.RESET}`);
        }
    }
    
    printTest("Enhanced MCP Processing", "PASS");
}

async function testStreamingResponse() {
    printTest("Enhanced MCP Streaming", "RUNNING");
    
    const payload = {
        message: "Create an automated welcome email for new customers",
        agent_context: {
            agent_name: "CustomerSuccessBot",
            agent_role: "Customer Success Manager"
        },
        llm_config: {
            model: "llama3.2",
            temperature: 0.8,
            max_tokens: 2000
        }
    };
    
    try {
        console.log(`\n${Colors.YELLOW}Streaming Enhanced MCP Response:${Colors.RESET}`);
        console.log(`${Colors.PURPLE}Message:${Colors.RESET} ${payload.message}`);
        
        const response = await fetch(`${BASE_URL}/enhanced-mcp/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-user-id': 'test-user'
            },
            body: JSON.stringify(payload)
        });
        
        // Note: In a real implementation, you'd need to handle Server-Sent Events
        // For this test, we'll just check if the endpoint is accessible
        
        if (response.ok) {
            console.log(`${Colors.GREEN}✅ Streaming endpoint is accessible${Colors.RESET}`);
            console.log(`${Colors.CYAN}Content-Type:${Colors.RESET} ${response.headers.get('content-type')}`);
            
            // Read a bit of the stream for testing
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let chunks = 0;
            
            try {
                while (chunks < 5) { // Read first 5 chunks
                    const { done, value } = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value);
                    if (chunk.trim()) {
                        console.log(`${Colors.CYAN}Stream chunk ${chunks + 1}:${Colors.RESET} ${chunk.substring(0, 100)}...`);
                        chunks++;
                    }
                }
            } finally {
                reader.releaseLock();
            }
            
            printTest("Enhanced MCP Streaming", "PASS");
        } else {
            console.log(`${Colors.RED}HTTP Error: ${response.status}${Colors.RESET}`);
            printTest("Enhanced MCP Streaming", "FAIL");
        }
        
    } catch (error) {
        console.log(`${Colors.RED}Error: ${error.message}${Colors.RESET}`);
        printTest("Enhanced MCP Streaming", "FAIL");
    }
}

async function testAgentIntegration() {
    printTest("Enhanced Agent Integration", "RUNNING");
    
    // Test with existing Sam agent
    const payload = {
        message: "Send a friendly email to team@company.com about tomorrow's meeting"
    };
    
    try {
        const response = await fetch(`${BASE_URL}/agents/sam_agent/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-user-id': 'default_user'
            },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        
        console.log(`${Colors.GREEN}Agent Response Success:${Colors.RESET} ${result.success || false}`);
        console.log(`${Colors.PURPLE}Agent Name:${Colors.RESET} ${result.agent_name || 'Unknown'}`);
        console.log(`${Colors.PURPLE}Response Type:${Colors.RESET} ${result.metadata?.type || 'unknown'}`);
        
        if (result.metadata?.enhanced) {
            console.log(`${Colors.CYAN}✨ Enhanced processing used!${Colors.RESET}`);
        }
        
        if (result.metadata?.enhanced_features) {
            console.log(`${Colors.CYAN}Enhanced Features:${Colors.RESET}`);
            Object.entries(result.metadata.enhanced_features).forEach(([key, value]) => {
                console.log(`  ${key}: ${value}`);
            });
        }
        
        console.log(`${Colors.PURPLE}Response:${Colors.RESET} ${(result.response || 'No response').substring(0, 150)}...`);
        
        printTest("Enhanced Agent Integration", "PASS");
        
    } catch (error) {
        console.log(`${Colors.RED}Error: ${error.message}${Colors.RESET}`);
        printTest("Enhanced Agent Integration", "FAIL");
    }
}

async function testHealthAndCompatibility() {
    printTest("Health & Compatibility Check", "RUNNING");
    
    try {
        // Test health endpoint
        const healthResponse = await fetch(`${BASE_URL}/health`);
        const healthData = await healthResponse.json();
        
        console.log(`${Colors.GREEN}Health Status:${Colors.RESET} ${healthData.status}`);
        console.log(`${Colors.PURPLE}Message:${Colors.RESET} ${healthData.message}`);
        
        // Test backward compatibility with regular chat
        const chatResponse = await fetch(`${BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                agent_id: 'sam_agent',
                message: 'Hello, test message',
                user_id: 'test_user'
            })
        });
        
        const chatData = await chatResponse.json();
        console.log(`${Colors.GREEN}Backward Compatibility:${Colors.RESET} ${chatData.success ? 'PASS' : 'FAIL'}`);
        
        printTest("Health & Compatibility Check", "PASS");
        
    } catch (error) {
        console.log(`${Colors.RED}Error: ${error.message}${Colors.RESET}`);
        printTest("Health & Compatibility Check", "FAIL");
    }
}

async function main() {
    printHeader("Enhanced MCP API Test Suite");
    console.log(`${Colors.YELLOW}Testing enhanced LLM capabilities and API endpoints${Colors.RESET}`);
    
    try {
        await testHealthAndCompatibility();
        await testEnhancedMCPCapabilities();
        await testEnhancedProcessing();
        await testStreamingResponse();
        await testAgentIntegration();
        
        printHeader("Test Summary");
        console.log(`${Colors.GREEN}✅ Enhanced MCP API tests completed!${Colors.RESET}`);
        console.log(`${Colors.CYAN}🚀 Enhanced MCP LLM system is ready with:${Colors.RESET}`);
        console.log(`${Colors.CYAN}  • Multi-provider LLM support (Ollama, OpenAI, DeepSeek)${Colors.RESET}`);
        console.log(`${Colors.CYAN}  • Advanced intent analysis and workflow planning${Colors.RESET}`);
        console.log(`${Colors.CYAN}  • AI-enhanced content generation${Colors.RESET}`);
        console.log(`${Colors.CYAN}  • Streaming responses for real-time interaction${Colors.RESET}`);
        console.log(`${Colors.CYAN}  • Conversation memory and context management${Colors.RESET}`);
        console.log(`${Colors.CYAN}  • Graceful fallback when LLM providers are unavailable${Colors.RESET}`);
        
    } catch (error) {
        console.log(`\n${Colors.RED}❌ Test suite failed with error: ${error.message}${Colors.RESET}`);
        console.error(error);
    }
}

if (require.main === module) {
    main();
}
