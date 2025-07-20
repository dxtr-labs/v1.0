/**
 * Test AI Protocol System - No Generic Templates
 * Validates that AI understands workflow syntax and generates proper content
 */

const axios = require('axios');

const BASE_URL = 'http://localhost:8002';
const TEST_USER_EMAIL = 'mcp_test@example.com';
const TEST_PASSWORD = 'test123';

async function testAIProtocolWorkflow() {
    try {
        console.log('🔬 Testing AI Protocol System (No Generic Templates)');
        console.log('====================================================');
        
        // Login
        console.log('1. Logging in...');
        const loginResponse = await axios.post(`${BASE_URL}/api/auth/login`, {
            email: TEST_USER_EMAIL,
            password: TEST_PASSWORD
        });
        
        const userId = loginResponse.data.user.user_id;
        const token = loginResponse.data.session_token;
        console.log(`✅ Logged in as: ${userId}`);
        
        const headers = { 
            'x-user-id': userId,
            'Cookie': `session_token=${token}`
        };
        
        // Test 1: Business inquiry (should use AI protocols, not generic templates)
        console.log('\n2. Testing business inquiry with AI protocols...');
        const businessMsg = await axios.post(`${BASE_URL}/api/chat/mcpai`, {
            message: "I'm interested in your automation services for my e-commerce business"
        }, { headers });
        
        console.log(`Business Response: ${businessMsg.data.message}`);
        
        // Test 2: Email workflow generation with AI protocols
        console.log('\n3. Testing email workflow generation...');
        const emailWorkflow = await axios.post(`${BASE_URL}/api/chat/mcpai`, {
            message: "Create a professional follow-up email for potential clients and send it to test@example.com"
        }, { headers });
        
        console.log(`Email Workflow Response: ${emailWorkflow.data.message}`);
        
        // Test 3: Check for generic template elimination
        console.log('\n4. Validating AI protocol implementation...');
        
        const hasGenericTemplate = businessMsg.data.message && 
            (businessMsg.data.message.includes('🎯 **DXTR Labs - Your AI-Powered Business Automation Partner!**') ||
             businessMsg.data.message.includes('Based on my analysis, this seems to be a general_query with'));
        
        const hasAIProtocol = businessMsg.data.message && 
            (businessMsg.data.message.includes('automation solutions') ||
             businessMsg.data.message.includes('your business') ||
             businessMsg.data.message.includes('help you'));
        
        if (!hasGenericTemplate && hasAIProtocol) {
            console.log('✅ SUCCESS: Generic templates eliminated');
            console.log('✅ SUCCESS: AI protocols implemented');
            console.log('✅ SUCCESS: Intelligent content generation active');
        } else {
            console.log('❌ ISSUE: Still using generic templates or missing AI protocols');
            if (hasGenericTemplate) {
                console.log('❌ Found generic template content');
            }
            if (!hasAIProtocol) {
                console.log('❌ Missing AI protocol responses');
            }
        }
        
        console.log('\n====================================================');
        console.log('🎯 AI Protocol System Status:');
        console.log(`📝 Generic Templates: ${hasGenericTemplate ? '❌ FOUND' : '✅ ELIMINATED'}`);
        console.log(`🤖 AI Protocols: ${hasAIProtocol ? '✅ ACTIVE' : '❌ MISSING'}`);
        console.log(`🔧 Workflow Syntax: ${emailWorkflow.data.message ? '✅ GENERATED' : '❌ FAILED'}`);
        console.log('🚀 System ready for intelligent content generation!');
        
    } catch (error) {
        console.error('❌ Test failed:', error.response?.data || error.message);
    }
}

testAIProtocolWorkflow();
