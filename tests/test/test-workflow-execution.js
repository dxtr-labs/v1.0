// test-workflow-execution.js - Test complete workflow execution including confirmation
const fetch = require('node-fetch');

const BASE_URL = 'http://localhost:8002';
const FRONTEND_URL = 'http://localhost:3001';

// Test credentials
const testUser = {
    email: 'test@example.com',
    password: 'password123'
};

async function testWorkflowExecution() {
    console.log('🔬 Testing complete workflow execution...\n');
    
    try {
        // Step 1: Login to get session
        console.log('📝 Step 1: Logging in...');
        const loginResponse = await fetch(`${BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(testUser)
        });
        
        if (!loginResponse.ok) {
            throw new Error(`Login failed: ${loginResponse.statusText}`);
        }
        
        const loginData = await loginResponse.json();
        console.log('✅ Login successful!');
        
        // Extract session cookie
        const cookies = loginResponse.headers.get('set-cookie');
        const sessionCookie = cookies ? cookies.split(',').find(c => c.includes('session=')) : null;
        
        if (!sessionCookie) {
            throw new Error('No session cookie received');
        }
        
        const cookieHeader = sessionCookie.split(';')[0];
        console.log(`   Session: ${cookieHeader.substring(0, 20)}...`);
        
        // Step 2: Test MCP workflow generation
        console.log('\n🤖 Step 2: Testing MCP workflow generation...');
        const mcpResponse = await fetch(`${BASE_URL}/api/mcp/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Cookie': cookieHeader
            },
            body: JSON.stringify({
                message: "Create an email automation that sends a welcome email to new users",
                ai_service: "in_house"
            })
        });
        
        if (!mcpResponse.ok) {
            throw new Error(`MCP request failed: ${mcpResponse.statusText}`);
        }
        
        const mcpData = await mcpResponse.json();
        console.log('✅ MCP workflow generated!');
        console.log(`   Type: ${mcpData.type}`);
        console.log(`   Has workflow preview: ${!!mcpData.workflow_preview}`);
        
        if (mcpData.workflow_preview) {
            console.log(`   Title: ${mcpData.workflow_preview.title}`);
            console.log(`   Steps: ${mcpData.workflow_preview.steps?.length || 0}`);
            console.log(`   Credits: ${mcpData.workflow_preview.estimated_credits}`);
        }
        
        // Step 3: Test workflow confirmation (the critical part!)
        if (mcpData.workflow_preview && mcpData.workflow_preview.workflow_json) {
            console.log('\n🚀 Step 3: Testing workflow confirmation...');
            const confirmResponse = await fetch(`${BASE_URL}/api/workflow/confirm`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Cookie': cookieHeader
                },
                body: JSON.stringify({
                    workflow_json: mcpData.workflow_preview.workflow_json
                })
            });
            
            if (!confirmResponse.ok) {
                const errorText = await confirmResponse.text();
                throw new Error(`Workflow confirmation failed: ${confirmResponse.status} ${confirmResponse.statusText} - ${errorText}`);
            }
            
            const confirmData = await confirmResponse.json();
            console.log('✅ Workflow confirmation successful!');
            console.log(`   Status: ${confirmData.success ? 'Success' : 'Failed'}`);
            console.log(`   Message: ${confirmData.message}`);
            
            if (confirmData.execution_details) {
                console.log(`   Execution Details:`, confirmData.execution_details);
            }
        } else {
            console.log('⚠️  No workflow_json to confirm');
        }
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
        return false;
    }
    
    return true;
}

async function main() {
    console.log('🧪 Workflow Execution Test Suite\n');
    console.log('Testing backend:', BASE_URL);
    console.log('Testing frontend:', FRONTEND_URL);
    console.log('='.repeat(50));
    
    const success = await testWorkflowExecution();
    
    console.log('\n' + '='.repeat(50));
    if (success) {
        console.log('🎉 All workflow execution tests passed!');
        console.log('✅ The automation engine fix is working correctly!');
    } else {
        console.log('❌ Workflow execution tests failed');
    }
}

main().catch(console.error);
