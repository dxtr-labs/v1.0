// test-complete-workflow.js - Final comprehensive test of the entire workflow system

const fetch = require('node-fetch');
const readline = require('readline');

const BASE_URL = 'http://localhost:8002';

// Test credentials
const testUser = {
    email: 'test@example.com',
    password: 'password123'
};

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function ask(question) {
    return new Promise((resolve) => {
        rl.question(question, (answer) => {
            resolve(answer);
        });
    });
}

async function testCompleteWorkflow() {
    console.log('🔬 Testing COMPLETE workflow with manual confirmation...\n');
    
    try {
        // Step 1: Login
        console.log('📝 Step 1: Logging in...');
        const loginResponse = await fetch(`${BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(testUser)
        });
        
        if (!loginResponse.ok) {
            throw new Error(`Login failed: ${loginResponse.statusText}`);
        }
        
        const cookies = loginResponse.headers.get('set-cookie');
        const sessionCookie = cookies ? cookies.split(',').find(c => c.includes('session=')) : null;
        
        if (!sessionCookie) {
            throw new Error('No session cookie received');
        }
        
        const cookieHeader = sessionCookie.split(';')[0];
        console.log('✅ Login successful!\n');
        
        // Step 2: Generate workflow preview
        console.log('🤖 Step 2: Generating workflow preview...');
        const mcpResponse = await fetch(`${BASE_URL}/api/mcp/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Cookie': cookieHeader
            },
            body: JSON.stringify({
                message: "Create a marketing email for our new fitness app and send it to slakshanand1105@gmail.com",
                ai_service: "in_house"
            })
        });
        
        if (!mcpResponse.ok) {
            throw new Error(`MCP request failed: ${mcpResponse.statusText}`);
        }
        
        const mcpData = await mcpResponse.json();
        console.log('✅ Workflow preview generated!');
        console.log(`   Type: ${mcpData.type}`);
        console.log(`   Status: ${mcpData.status}`);
        console.log(`   Has workflow preview: ${!!mcpData.workflow_preview}`);
        
        if (mcpData.workflow_preview) {
            console.log(`   Title: ${mcpData.workflow_preview.title}`);
            console.log(`   Description: ${mcpData.workflow_preview.description}`);
            console.log(`   Steps: ${mcpData.workflow_preview.steps?.length || 0}`);
            console.log(`   Credits: ${mcpData.workflow_preview.estimated_credits}`);
            console.log(`   Recipient: ${mcpData.workflow_preview.recipient}`);
            
            if (mcpData.workflow_preview.workflow_json) {
                console.log('\\n📋 WORKFLOW DETAILS:');
                console.log(`   Type: ${mcpData.workflow_preview.workflow_json.type}`);
                console.log(`   Recipient: ${mcpData.workflow_preview.workflow_json.recipient}`);
                console.log(`   Content Type: ${mcpData.workflow_preview.workflow_json.content_type}`);
                
                // Step 3: Manual confirmation test
                console.log('\\n🎯 Step 3: Testing Manual Confirmation...');
                console.log('In the frontend, you should see a dialog with:');
                console.log('- Workflow title and description');
                console.log('- Step details');
                console.log('- Credit cost');
                console.log('- CANCEL and CONFIRM & EXECUTE buttons');
                console.log('');
                
                const userDecision = await ask('Did you see the workflow preview dialog? (y/n): ');
                
                if (userDecision.toLowerCase() === 'y') {
                    console.log('✅ Dialog display working correctly!');
                    
                    const confirmChoice = await ask('Do you want to test workflow execution? (y/n): ');
                    
                    if (confirmChoice.toLowerCase() === 'y') {
                        console.log('\\n🚀 Step 4: Testing workflow execution...');
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
                            console.log(`❌ Workflow execution failed: ${confirmResponse.status} - ${errorText}`);
                        } else {
                            const confirmData = await confirmResponse.json();
                            console.log('✅ Workflow execution completed!');
                            console.log(`   Success: ${confirmData.success}`);
                            console.log(`   Message: ${confirmData.message}`);
                            
                            if (confirmData.execution_details) {
                                console.log(`   Details: ${JSON.stringify(confirmData.execution_details, null, 2)}`);
                            }
                        }
                    } else {
                        console.log('⏭️  Skipping execution test');
                    }
                } else {
                    console.log('❌ Dialog not displaying - there may be a frontend issue');
                }
            } else {
                console.log('⚠️  No workflow_json found');
            }
        } else {
            console.log('❌ No workflow preview generated');
        }
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
    } finally {
        rl.close();
    }
}

async function main() {
    console.log('🧪 COMPLETE WORKFLOW TEST SUITE\\n');
    console.log('This test will check:');
    console.log('✓ Backend workflow generation');
    console.log('✓ Frontend dialog display');
    console.log('✓ Manual user confirmation');
    console.log('✓ Real automation execution');
    console.log('='.repeat(60));
    console.log('');
    
    console.log('📋 INSTRUCTIONS:');
    console.log('1. Make sure both servers are running:');
    console.log('   - Backend: http://localhost:8002');
    console.log('   - Frontend: http://localhost:3001');
    console.log('2. Open the frontend at: http://localhost:3001/dashboard/agents/sam/chat');
    console.log('3. Type this message: "Create a marketing email for our new fitness app and send it to slakshanand1105@gmail.com"');
    console.log('4. Watch for the workflow preview dialog');
    console.log('5. Answer the prompts in this terminal');
    console.log('='.repeat(60));
    console.log('');
    
    const ready = await ask('Are you ready to start the test? (y/n): ');
    
    if (ready.toLowerCase() === 'y') {
        await testCompleteWorkflow();
    } else {
        console.log('Test cancelled');
        rl.close();
    }
}

main().catch(console.error);
