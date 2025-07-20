// Test JSON Script Detection Enhancement
const fs = require('fs');
const path = require('path');

// Test inputs to validate enhanced script detection
const testInputs = [
  // Email tests
  "Send an email to john@example.com with subject 'Meeting Tomorrow'",
  "Forward this email to the marketing team",
  "Schedule a bulk email campaign for next week",
  "Send a Gmail to my boss about the project update",
  "Compose an Outlook message for the client",
  
  // Task tests
  "Create a new task in Asana for the design review",
  "Add a Trello card to the development board",
  "Open a Jira ticket for the bug report",
  "Make a new GitHub issue for feature request",
  "Set up a Monday.com task for the deadline",
  
  // Social tests
  "Post this to Twitter with #productivity hashtag",
  "Share on LinkedIn about our company update",
  "Upload to Instagram with vacation photos",
  "Post on Facebook about the event",
  "Tweet about the new product launch",
  
  // Meeting tests
  "Schedule a Zoom meeting for tomorrow at 2 PM",
  "Book a Teams call with the development team",
  "Set up a Google Meet for the client presentation",
  "Create a calendar event for the board meeting",
  "Schedule a video conference for training",
  
  // Data tests
  "Export this data to Excel spreadsheet",
  "Create a CSV report of sales data",
  "Generate a PDF document with the analysis",
  "Import data from the Google Sheets",
  "Update the database with new records",
  
  // Webhook tests
  "Send a webhook notification to Slack",
  "Trigger an API call to the payment system",
  "Post data to the external webhook",
  "Send notification to Discord channel",
  "Call the REST API endpoint"
];

// Load the enhanced analysis functions
function loadAnalysisFunctions() {
  // Simplified version of the workflowPatterns with JSON script mappings
  const workflowPatterns = {
    email: {
      json_script_mappings: {
        'gmail-send': ['gmail', 'google mail', 'send gmail'],
        'outlook-send': ['outlook', 'microsoft mail', 'send outlook'],
        'bulk-email': ['bulk', 'campaign', 'mass email'],
        'email-forward': ['forward', 'fwd'],
        'email-reply': ['reply', 'respond']
      }
    },
    task: {
      json_script_mappings: {
        'asana-task': ['asana', 'asana task'],
        'trello-card': ['trello', 'trello card'],
        'jira-ticket': ['jira', 'jira ticket', 'jira issue'],
        'github-issue': ['github', 'github issue'],
        'monday-task': ['monday', 'monday.com']
      }
    },
    social: {
      json_script_mappings: {
        'twitter-post': ['twitter', 'tweet', 'twitter post'],
        'linkedin-post': ['linkedin', 'linkedin post'],
        'instagram-post': ['instagram', 'instagram post'],
        'facebook-post': ['facebook', 'facebook post']
      }
    },
    meeting: {
      json_script_mappings: {
        'zoom-meeting': ['zoom', 'zoom meeting'],
        'teams-meeting': ['teams', 'microsoft teams'],
        'google-meet': ['google meet', 'meet'],
        'calendar-event': ['calendar', 'schedule event']
      }
    },
    data: {
      json_script_mappings: {
        'excel-export': ['excel', 'xlsx', 'spreadsheet'],
        'csv-export': ['csv', 'csv export'],
        'pdf-generate': ['pdf', 'pdf generate'],
        'sheets-import': ['google sheets', 'sheets'],
        'database-update': ['database', 'db update']
      }
    },
    webhook: {
      json_script_mappings: {
        'slack-webhook': ['slack', 'slack notification'],
        'api-call': ['api', 'api call', 'rest api'],
        'discord-webhook': ['discord', 'discord notification'],
        'generic-webhook': ['webhook', 'notify']
      }
    }
  };

  // Script selection function
  function selectJsonScript(input, workflowType) {
    const inputLower = input.toLowerCase();
    const mappings = workflowPatterns[workflowType]?.json_script_mappings || {};
    
    let bestScript = null;
    let bestScore = 0;
    
    for (const [script, keywords] of Object.entries(mappings)) {
      const score = keywords.reduce((sum, keyword) => {
        return sum + (inputLower.includes(keyword.toLowerCase()) ? 1 : 0);
      }, 0);
      
      if (score > bestScore) {
        bestScore = score;
        bestScript = script;
      }
    }
    
    const confidence = bestScore > 0 ? Math.min(bestScore * 0.3, 1.0) : 0.1;
    
    return {
      script: bestScript || `${workflowType}-default`,
      confidence: confidence,
      matchedKeywords: bestScore,
      workflowType: workflowType
    };
  }

  return { selectJsonScript, workflowPatterns };
}

// Test function
function testJsonScriptDetection() {
  console.log('🧪 Testing Enhanced JSON Script Detection');
  console.log('='.repeat(60));
  
  const { selectJsonScript, workflowPatterns } = loadAnalysisFunctions();
  
  const results = [];
  
  testInputs.forEach((input, index) => {
    console.log(`\n${index + 1}. Testing: "${input}"`);
    
    // Determine workflow type (simplified)
    let workflowType = 'webhook'; // default
    if (input.toLowerCase().includes('email') || input.toLowerCase().includes('gmail') || input.toLowerCase().includes('outlook')) {
      workflowType = 'email';
    } else if (input.toLowerCase().includes('task') || input.toLowerCase().includes('asana') || input.toLowerCase().includes('trello') || input.toLowerCase().includes('jira')) {
      workflowType = 'task';
    } else if (input.toLowerCase().includes('post') || input.toLowerCase().includes('twitter') || input.toLowerCase().includes('linkedin') || input.toLowerCase().includes('instagram') || input.toLowerCase().includes('facebook')) {
      workflowType = 'social';
    } else if (input.toLowerCase().includes('meeting') || input.toLowerCase().includes('zoom') || input.toLowerCase().includes('teams') || input.toLowerCase().includes('schedule')) {
      workflowType = 'meeting';
    } else if (input.toLowerCase().includes('export') || input.toLowerCase().includes('excel') || input.toLowerCase().includes('csv') || input.toLowerCase().includes('pdf') || input.toLowerCase().includes('data')) {
      workflowType = 'data';
    }
    
    const scriptResult = selectJsonScript(input, workflowType);
    
    console.log(`   📋 Workflow: ${workflowType}`);
    console.log(`   🔧 Selected Script: ${scriptResult.script}`);
    console.log(`   📊 Confidence: ${(scriptResult.confidence * 100).toFixed(1)}%`);
    console.log(`   🎯 Matched Keywords: ${scriptResult.matchedKeywords}`);
    
    results.push({
      input,
      workflowType,
      selectedScript: scriptResult.script,
      confidence: scriptResult.confidence,
      matchedKeywords: scriptResult.matchedKeywords
    });
  });
  
  // Generate summary
  console.log('\n📊 DETECTION SUMMARY');
  console.log('='.repeat(60));
  
  const scriptCounts = {};
  const workflowCounts = {};
  let totalConfidence = 0;
  let specificScripts = 0;
  
  results.forEach(result => {
    scriptCounts[result.selectedScript] = (scriptCounts[result.selectedScript] || 0) + 1;
    workflowCounts[result.workflowType] = (workflowCounts[result.workflowType] || 0) + 1;
    totalConfidence += result.confidence;
    
    if (!result.selectedScript.includes('default')) {
      specificScripts++;
    }
  });
  
  console.log(`📈 Total Tests: ${results.length}`);
  console.log(`🎯 Average Confidence: ${(totalConfidence / results.length * 100).toFixed(1)}%`);
  console.log(`🔧 Specific Scripts: ${specificScripts}/${results.length} (${(specificScripts / results.length * 100).toFixed(1)}%)`);
  
  console.log('\n📊 Script Distribution:');
  Object.entries(scriptCounts)
    .sort(([,a], [,b]) => b - a)
    .forEach(([script, count]) => {
      console.log(`   ${script}: ${count} (${(count / results.length * 100).toFixed(1)}%)`);
    });
  
  console.log('\n📋 Workflow Distribution:');
  Object.entries(workflowCounts)
    .sort(([,a], [,b]) => b - a)
    .forEach(([workflow, count]) => {
      console.log(`   ${workflow}: ${count} (${(count / results.length * 100).toFixed(1)}%)`);
    });
  
  // Save results
  fs.writeFileSync(
    path.join(__dirname, 'json_script_test_results.json'),
    JSON.stringify({ results, summary: { scriptCounts, workflowCounts, averageConfidence: totalConfidence / results.length } }, null, 2)
  );
  
  console.log('\n💾 Test results saved to json_script_test_results.json');
  console.log('✅ JSON Script Detection Test Complete!');
}

// Run the test
testJsonScriptDetection();
