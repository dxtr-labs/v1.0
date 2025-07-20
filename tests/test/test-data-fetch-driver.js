/**
 * Data Fetch Driver Test
 * Tests the system's ability to fetch data from external servers and APIs
 */

const axios = require('axios');

const BASE_URL = 'http://localhost:8002';
const TEST_USER_EMAIL = 'mcp_test@example.com';
const TEST_PASSWORD = 'test123';

// Test external APIs
const TEST_APIS = {
    jsonplaceholder: 'https://jsonplaceholder.typicode.com/posts/1',
    httpbin: 'https://httpbin.org/json',
    github: 'https://api.github.com/repos/microsoft/vscode',
    weather: 'https://api.openweathermap.org/data/2.5/weather?q=London&appid=demo'
};

async function testDataFetchDrivers() {
    try {
        console.log('🌐 Testing Data Fetch Drivers');
        console.log('==========================================');
        
        // Step 1: Authentication
        console.log('1. 🔐 Authenticating...');
        const loginResponse = await axios.post(`${BASE_URL}/api/auth/login`, {
            email: TEST_USER_EMAIL,
            password: TEST_PASSWORD
        });
        
        const userId = loginResponse.data.user.user_id;
        const token = loginResponse.data.session_token;
        console.log(`✅ Authenticated as: ${userId}`);
        
        const headers = { 
            'x-user-id': userId,
            'Cookie': `session_token=${token}`
        };
        
        // Step 2: Test direct data fetching capabilities
        console.log('\n2. 🔄 Testing direct API fetch capabilities...');
        
        for (const [apiName, apiUrl] of Object.entries(TEST_APIS)) {
            try {
                console.log(`\n   📡 Fetching from ${apiName}: ${apiUrl}`);
                const startTime = Date.now();
                
                const response = await axios.get(apiUrl, {
                    timeout: 5000,
                    headers: {
                        'User-Agent': 'DXTR-Labs-Test-Driver/1.0'
                    }
                });
                
                const duration = Date.now() - startTime;
                console.log(`   ✅ ${apiName}: SUCCESS (${duration}ms)`);
                console.log(`   📊 Status: ${response.status}, Data size: ${JSON.stringify(response.data).length} chars`);
                
                // Show sample data
                if (response.data) {
                    const sampleData = JSON.stringify(response.data).substring(0, 100) + '...';
                    console.log(`   📝 Sample: ${sampleData}`);
                }
                
            } catch (error) {
                console.log(`   ❌ ${apiName}: FAILED - ${error.message}`);
            }
        }
        
        // Step 3: Test MCP LLM's ability to understand and process fetched data
        console.log('\n3. 🤖 Testing MCP LLM data processing capabilities...');
        
        const dataProcessingRequest = "I need you to fetch data from an API and process it. Can you help me understand how to get user information from jsonplaceholder.typicode.com?";
        
        const mcpResponse = await axios.post(`${BASE_URL}/api/chat/mcpai`, {
            message: dataProcessingRequest
        }, { headers });
        
        console.log(`MCP Response: ${mcpResponse.data.message}`);
        
        // Step 4: Test workflow generation for data fetching
        console.log('\n4. 🔧 Testing data fetch workflow generation...');
        
        const workflowRequest = "Create a workflow that fetches user data from an API and sends a personalized email based on that data";
        
        const workflowResponse = await axios.post(`${BASE_URL}/api/chat/mcpai`, {
            message: workflowRequest
        }, { headers });
        
        console.log(`Workflow Response: ${workflowResponse.data.message}`);
        
        // Step 5: Test data integration workflow execution
        console.log('\n5. ⚙️ Testing data integration workflow...');
        
        const dataIntegrationWorkflow = {
            type: "data_integration_automation",
            recipient: "test@example.com",
            data_source: "https://jsonplaceholder.typicode.com/users/1",
            content_type: "personalized email with fetched data",
            ai_service: "inhouse",
            needs_ai_generation: true,
            needs_data_fetch: true,
            user_request: "Fetch user data and create personalized email"
        };
        
        try {
            const executionResponse = await axios.post(`${BASE_URL}/api/workflow/confirm`, {
                workflow_json: dataIntegrationWorkflow
            }, { headers });
            
            console.log(`Data Integration Execution: ${JSON.stringify(executionResponse.data, null, 2)}`);
            
        } catch (error) {
            console.log(`Data Integration Test: ${error.response?.status} - ${error.response?.data?.detail || error.message}`);
            console.log('ℹ️  This indicates we need to add data fetching capabilities to the automation engine');
        }
        
        // Step 6: Test custom data fetch simulation
        console.log('\n6. 📊 Testing custom data fetch simulation...');
        
        try {
            // Simulate what our system would do with fetched data
            const simulatedFetchedData = {
                user: {
                    name: "John Doe",
                    email: "john@example.com",
                    company: "Tech Corp",
                    position: "Developer"
                },
                source: "jsonplaceholder.typicode.com"
            };
            
            const customWorkflow = {
                type: "email_automation",
                recipient: "test@example.com",
                content_type: "data-driven email",
                ai_service: "inhouse", 
                needs_ai_generation: true,
                user_request: `Create a personalized email for ${simulatedFetchedData.user.name} from ${simulatedFetchedData.user.company}`,
                fetched_data: simulatedFetchedData
            };
            
            const customResponse = await axios.post(`${BASE_URL}/api/workflow/confirm`, {
                workflow_json: customWorkflow
            }, { headers });
            
            console.log(`Custom Data Workflow: SUCCESS`);
            console.log(`Result: ${customResponse.data.message}`);
            
        } catch (error) {
            console.log(`Custom Data Test: ${error.response?.status} - ${error.message}`);
        }
        
        // Summary
        console.log('\n==========================================');
        console.log('🎯 DATA FETCH DRIVER TEST SUMMARY');
        console.log('==========================================');
        
        // Check which APIs were accessible
        let accessibleApis = 0;
        for (const apiName of Object.keys(TEST_APIS)) {
            // This is a simple check - in a real test we'd track results
            accessibleApis++; // Placeholder
        }
        
        console.log(`🌐 External API Access: Testing ${Object.keys(TEST_APIS).length} APIs`);
        console.log(`🤖 MCP LLM Data Processing: ${mcpResponse.data.message ? '✅ ACTIVE' : '❌ NEEDS ATTENTION'}`);
        console.log(`🔧 Workflow Generation: ${workflowResponse.data.message ? '✅ ACTIVE' : '❌ NEEDS ATTENTION'}`);
        console.log(`⚙️ Data Integration: Requires enhancement in automation engine`);
        console.log(`📊 Custom Data Processing: Testing custom data workflows`);
        
        console.log('\n🎯 RECOMMENDATIONS:');
        console.log('1. Add data fetching capabilities to automation engine');
        console.log('2. Implement API authentication handling');
        console.log('3. Add data transformation and validation');
        console.log('4. Create data-driven email templates');
        console.log('5. Add error handling for failed API calls');
        
        console.log('\n🚀 System ready for data integration enhancement!');
        
    } catch (error) {
        console.error('❌ Data fetch driver test failed:', error.response?.data || error.message);
    }
}

testDataFetchDrivers();
