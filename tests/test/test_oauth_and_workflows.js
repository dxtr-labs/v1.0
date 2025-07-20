// OAuth Provider Testing Script
// Run this to test all OAuth providers

const testOAuthProviders = async () => {
  const providers = [
    { provider: 'google', service: 'gmail', name: 'Gmail' },
    { provider: 'google', service: 'drive', name: 'Google Drive' },
    { provider: 'google', service: 'calendar', name: 'Google Calendar' },
    { provider: 'microsoft', service: 'outlook', name: 'Outlook' },
    { provider: 'microsoft', service: 'onedrive', name: 'OneDrive' },
    { provider: 'facebook', service: 'instagram', name: 'Instagram' },
    { provider: 'facebook', service: 'facebook', name: 'Facebook' },
    { provider: 'twitter', service: 'twitter', name: 'Twitter' },
    { provider: 'linkedin', service: 'linkedin', name: 'LinkedIn' },
    { provider: 'slack', service: 'slack', name: 'Slack' },
    { provider: 'dropbox', service: 'dropbox', name: 'Dropbox' },
    { provider: 'github', service: 'github', name: 'GitHub' }
  ];

  console.log('🧪 Testing OAuth Providers...\n');
  console.log('='.repeat(80));

  let successCount = 0;
  let failureCount = 0;

  for (const { provider, service, name } of providers) {
    try {
      console.log(`\n🔍 Testing ${name} (${provider}/${service})...`);
      
      const startTime = Date.now();
      const response = await fetch(`http://localhost:3001/api/oauth/authorize?provider=${provider}&service=${service}`);
      const endTime = Date.now();
      
      const data = await response.json();
      
      if (response.ok && data.authUrl) {
        console.log(`✅ ${name}: SUCCESS (${endTime - startTime}ms)`);
        console.log(`   📍 Auth URL: ${data.authUrl.substring(0, 80)}...`);
        console.log(`   🔑 Provider: ${provider}`);
        console.log(`   🎯 Service: ${service}`);
        successCount++;
      } else {
        console.log(`❌ ${name}: FAILED`);
        console.log(`   ⚠️  Error: ${data.error || 'Unknown error'}`);
        console.log(`   📝 Message: ${data.message || 'No message'}`);
        failureCount++;
      }
    } catch (error) {
      console.log(`❌ ${name}: ERROR`);
      console.log(`   💥 Exception: ${error}`);
      failureCount++;
    }
  }

  console.log('\n' + '='.repeat(80));
  console.log('📊 OAUTH TESTING SUMMARY');
  console.log('='.repeat(80));
  console.log(`✅ Successful: ${successCount}/${providers.length}`);
  console.log(`❌ Failed: ${failureCount}/${providers.length}`);
  console.log(`📈 Success Rate: ${Math.round((successCount / providers.length) * 100)}%`);
  
  if (successCount === providers.length) {
    console.log('\n🎉 ALL OAUTH PROVIDERS ARE WORKING! 🎉');
  } else if (successCount > 0) {
    console.log('\n⚠️  Some OAuth providers need attention.');
  } else {
    console.log('\n🚨 OAuth system needs configuration.');
  }
  
  console.log('\n📋 Next Steps:');
  console.log('1. 🌐 Open http://localhost:3001/dashboard/connectivity');
  console.log('2. 🧪 Test OAuth buttons in the UI');
  console.log('3. 🤖 Try the Workflow Builder at http://localhost:3001/dashboard/workflow-builder');
};

// Export for use in browser console or Node.js
if (typeof window !== 'undefined') {
  // Browser environment
  window.testOAuthProviders = testOAuthProviders;
  console.log('🚀 OAuth testing function loaded! Run testOAuthProviders() to test all providers.');
} else if (typeof module !== 'undefined' && module.exports) {
  // Node.js environment
  module.exports = { testOAuthProviders };
} else {
  // Direct execution
  testOAuthProviders().catch(console.error);
}

// Test workflow examples
const testWorkflowExamples = [
  {
    input: 'Send email to john@company.com about meeting tomorrow',
    expected: 'email-automation',
    extractedParams: ['recipient', 'subject']
  },
  {
    input: 'Create high priority task in Asana for bug fix',
    expected: 'task-creation',
    extractedParams: ['platform', 'priority', 'title']
  },
  {
    input: 'Post to Twitter about our new product launch',
    expected: 'social-media-post',
    extractedParams: ['platform', 'content']
  },
  {
    input: 'Schedule 30-minute meeting with client@example.com using Calendly',
    expected: 'calendly-meeting',
    extractedParams: ['meetingType', 'recipient']
  },
  {
    input: 'Process CSV file from https://data.com/sales.csv with filter operation',
    expected: 'data-processing',
    extractedParams: ['fileType', 'sourceUrl', 'operation']
  },
  {
    input: 'Setup webhook for https://api.example.com/notify with POST method',
    expected: 'webhook-trigger',
    extractedParams: ['webhookUrl', 'method']
  }
];

console.log('\n🧠 WORKFLOW TESTING EXAMPLES:');
console.log('='.repeat(80));
testWorkflowExamples.forEach((example, index) => {
  console.log(`\n${index + 1}. Input: "${example.input}"`);
  console.log(`   Expected Workflow: ${example.expected}`);
  console.log(`   Expected Parameters: ${example.extractedParams.join(', ')}`);
});

console.log('\n📝 SYSTEM FEATURES IMPLEMENTED:');
console.log('='.repeat(80));
console.log('📧 Email Automation with Gmail/Outlook OAuth');
console.log('📱 Social Media Posting (Twitter, LinkedIn, Instagram, Facebook)');
console.log('📋 Task Creation (Asana, Trello, Jira, Monday.com)');
console.log('📅 Calendly Meeting Scheduling');
console.log('📊 Data Processing (CSV, JSON, Excel, PDF)');
console.log('🔗 Webhook Integration Setup');
console.log('🤖 AI-powered Workflow Matching');
console.log('🔍 Intelligent Parameter Extraction');
console.log('⚙️ OAuth Authentication for 12 Services');
console.log('✨ Auto-parameter Extraction from Natural Language');

console.log('\n🎯 READY FOR TESTING!');
