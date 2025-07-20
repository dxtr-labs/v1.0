// Test Enhanced MCP LLM API with JSON Script Detection
const testInputs = [
  {
    input: "Send an email to john@example.com about the project update",
    expectedWorkflow: "email-automation",
    expectedScript: "gmail-send"
  },
  {
    input: "Create a new task in Asana for design review",
    expectedWorkflow: "task-creation", 
    expectedScript: "asana-task"
  },
  {
    input: "Post to Twitter about our product launch",
    expectedWorkflow: "social-media-post",
    expectedScript: "twitter-post"
  },
  {
    input: "Schedule a Zoom meeting for tomorrow",
    expectedWorkflow: "calendly-meeting",
    expectedScript: "zoom-meeting"
  },
  {
    input: "Export data to Excel spreadsheet",
    expectedWorkflow: "data-fetch",
    expectedScript: "excel-export"
  },
  {
    input: "Send notification to Slack channel",
    expectedWorkflow: "webhook-trigger",
    expectedScript: "slack-webhook"
  }
];

const candidateWorkflows = [
  { id: 'email-automation', name: 'Email Automation', description: 'Send emails and manage communication' },
  { id: 'task-creation', name: 'Task Creation', description: 'Create tasks in project management tools' },
  { id: 'social-media-post', name: 'Social Media Post', description: 'Post content to social platforms' },
  { id: 'calendly-meeting', name: 'Meeting Scheduling', description: 'Schedule meetings and appointments' },
  { id: 'data-fetch', name: 'Data Processing', description: 'Process and export data' },
  { id: 'webhook-trigger', name: 'Webhook Integration', description: 'Trigger webhooks and API calls' }
];

async function testEnhancedMCPAPI() {
  console.log('🧪 Testing Enhanced MCP LLM API with JSON Script Detection');
  console.log('='.repeat(70));
  
  for (const test of testInputs) {
    console.log(`\\n📝 Testing: "${test.input}"`);
    
    try {
      const response = await fetch('http://localhost:3000/api/mcp/llm/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userInput: test.input,
          candidateWorkflows: candidateWorkflows
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        const topMatch = result.enhancedMatches[0];
        
        console.log(`   🎯 Predicted Workflow: ${topMatch.id}`);
        console.log(`   📊 Confidence: ${(topMatch.confidence * 100).toFixed(1)}%`);
        console.log(`   🔧 Selected Script: ${topMatch.jsonScript?.script || 'N/A'}`);
        console.log(`   📈 Script Confidence: ${(topMatch.jsonScript?.confidence * 100).toFixed(1)}%`);
        console.log(`   🎯 Expected: ${test.expectedWorkflow} → ${test.expectedScript}`);
        
        const workflowMatch = topMatch.id === test.expectedWorkflow;
        const scriptMatch = topMatch.jsonScript?.script === test.expectedScript;
        
        console.log(`   ✅ Workflow Match: ${workflowMatch ? 'PASS' : 'FAIL'}`);
        console.log(`   ✅ Script Match: ${scriptMatch ? 'PASS' : 'FAIL'}`);
        
        if (topMatch.extractedParameters && Object.keys(topMatch.extractedParameters).length > 0) {
          console.log(`   📋 Parameters: ${JSON.stringify(topMatch.extractedParameters)}`);
        }
        
      } else {
        console.log(`   ❌ API Error: ${response.status}`);
      }
      
    } catch (error) {
      console.log(`   ❌ Network Error: ${error.message}`);
    }
  }
  
  console.log('\\n🚀 Enhanced MCP LLM API Test Complete!');
}

// Check if running in Node.js environment
if (typeof window === 'undefined') {
  // Node.js environment - use fetch polyfill
  const fetch = require('node-fetch');
  testEnhancedMCPAPI();
} else {
  // Browser environment
  console.log('Run this test with the Next.js server running on localhost:3000');
  console.log('Copy and paste this function into the browser console:');
  console.log(testEnhancedMCPAPI.toString());
}
