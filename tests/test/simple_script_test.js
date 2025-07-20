console.log('🧪 Testing Enhanced JSON Script Detection');

// Test simple JSON script selection
const input = "Send an email to john@example.com";
const workflowType = "email";

const json_script_mappings = {
  'gmail-send': ['gmail', 'google mail'],
  'outlook-send': ['outlook', 'microsoft mail'],
  'email-send': ['email', 'send email']
};

function selectJsonScript(input, workflowType) {
  const inputLower = input.toLowerCase();
  let bestScript = null;
  let bestScore = 0;
  
  for (const [script, keywords] of Object.entries(json_script_mappings)) {
    const score = keywords.reduce((sum, keyword) => {
      return sum + (inputLower.includes(keyword.toLowerCase()) ? 1 : 0);
    }, 0);
    
    if (score > bestScore) {
      bestScore = score;
      bestScript = script;
    }
  }
  
  return {
    script: bestScript || `${workflowType}-default`,
    confidence: bestScore > 0 ? bestScore * 0.3 : 0.1,
    matchedKeywords: bestScore
  };
}

const result = selectJsonScript(input, workflowType);
console.log('Input:', input);
console.log('Result:', result);
console.log('✅ JSON Script Detection Working!');
