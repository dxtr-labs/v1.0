import { NextRequest, NextResponse } from 'next/server';

// Types
interface ProcessRequest {
  userInput: string;
  nodeType: string;
  nodeName: string;
  currentParameters?: Record<string, any>;
  context?: string;
}

interface ProcessResponse {
  success: boolean;
  suggestedParameters: Record<string, any>;
  explanation: string;
  confidence: number;
  needsMoreInfo?: boolean;
  followUpQuestions?: string[];
}

export async function POST(request: NextRequest) {
  try {
    const body: ProcessRequest = await request.json();
    const { userInput, nodeType, nodeName, currentParameters = {}, context = '' } = body;

    if (!userInput || !nodeType) {
      return NextResponse.json(
        { error: 'Missing required fields: userInput and nodeType' },
        { status: 400 }
      );
    }

    // Enhanced AI parameter extraction
    const result = await processWithAI(userInput, nodeType, nodeName, currentParameters, context);

    return NextResponse.json(result);
  } catch (error) {
    console.error('Error in agent processing:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

async function processWithAI(
  userInput: string,
  nodeType: string,
  nodeName: string,
  currentParameters: Record<string, any>,
  context: string
): Promise<ProcessResponse> {
  const input = userInput.toLowerCase();
  
  // Enhanced parameter extraction with confidence scoring
  let suggestedParameters: Record<string, any> = {};
  let explanation = '';
  let confidence = 0.7; // Default confidence
  let needsMoreInfo = false;
  let followUpQuestions: string[] = [];

  switch (nodeType) {
    case 'n8n-nodes-base.httpRequest':
    case 'n8n-nodes-base.webhook':
      const httpResult = processHttpNode(input, userInput);
      suggestedParameters = httpResult.parameters;
      explanation = httpResult.explanation;
      confidence = httpResult.confidence;
      needsMoreInfo = httpResult.needsMoreInfo;
      followUpQuestions = httpResult.followUpQuestions;
      break;

    case 'n8n-nodes-base.gmail':
    case 'n8n-nodes-base.email':
      const emailResult = processEmailNode(input, userInput);
      suggestedParameters = emailResult.parameters;
      explanation = emailResult.explanation;
      confidence = emailResult.confidence;
      needsMoreInfo = emailResult.needsMoreInfo;
      followUpQuestions = emailResult.followUpQuestions;
      break;

    case 'n8n-nodes-base.set':
      const setResult = processSetNode(input, userInput);
      suggestedParameters = setResult.parameters;
      explanation = setResult.explanation;
      confidence = setResult.confidence;
      break;

    case 'n8n-nodes-base.function':
      const functionResult = processFunctionNode(input, userInput);
      suggestedParameters = functionResult.parameters;
      explanation = functionResult.explanation;
      confidence = functionResult.confidence;
      break;

    case 'n8n-nodes-base.manualTrigger':
      suggestedParameters = { configured: true };
      explanation = `Manual trigger configured. This node will start the workflow when executed manually.`;
      confidence = 1.0;
      break;

    case 'n8n-nodes-base.noOp':
      const noOpResult = processNoOpNode(input, userInput);
      suggestedParameters = noOpResult.parameters;
      explanation = noOpResult.explanation;
      confidence = noOpResult.confidence;
      needsMoreInfo = noOpResult.needsMoreInfo;
      followUpQuestions = noOpResult.followUpQuestions;
      break;

    case 'n8n-nodes-base.googleSheets':
    case 'n8n-nodes-base.airtable':
      const spreadsheetResult = processSpreadsheetNode(input, userInput, nodeType);
      suggestedParameters = spreadsheetResult.parameters;
      explanation = spreadsheetResult.explanation;
      confidence = spreadsheetResult.confidence;
      needsMoreInfo = spreadsheetResult.needsMoreInfo;
      followUpQuestions = spreadsheetResult.followUpQuestions;
      break;

    default:
      const genericResult = processGenericNode(input, userInput, nodeType, nodeName);
      suggestedParameters = genericResult.parameters;
      explanation = genericResult.explanation;
      confidence = genericResult.confidence;
  }

  return {
    success: true,
    suggestedParameters,
    explanation,
    confidence,
    needsMoreInfo,
    followUpQuestions
  };
}

function processHttpNode(input: string, originalInput: string) {
  let parameters: Record<string, any> = {};
  let explanation = '';
  let confidence = 0.8;
  let needsMoreInfo = false;
  let followUpQuestions: string[] = [];

  // Extract HTTP method
  if (input.includes('get') || input.includes('fetch') || input.includes('retrieve')) {
    parameters.method = 'GET';
  } else if (input.includes('post') || input.includes('send') || input.includes('create')) {
    parameters.method = 'POST';
  } else if (input.includes('put') || input.includes('update')) {
    parameters.method = 'PUT';
  } else if (input.includes('delete') || input.includes('remove')) {
    parameters.method = 'DELETE';
  }

  // Extract URL with improved regex
  const urlRegex = /https?:\/\/[^\s]+/g;
  const urlMatch = originalInput.match(urlRegex);
  if (urlMatch && urlMatch.length > 0) {
    parameters.url = urlMatch[0];
    confidence += 0.2;
  }

  // Extract API endpoints
  const apiPatterns = [
    /api\.([a-zA-Z0-9.-]+)/g,
    /\/api\/([a-zA-Z0-9\/.-]+)/g,
    /([a-zA-Z0-9.-]+)\.com\/([a-zA-Z0-9\/.-]+)/g
  ];

  apiPatterns.forEach(pattern => {
    const match = originalInput.match(pattern);
    if (match && !parameters.url) {
      parameters.url = match[0].startsWith('http') ? match[0] : `https://${match[0]}`;
    }
  });

  // Extract headers
  if (input.includes('authorization') || input.includes('bearer') || input.includes('token')) {
    parameters.headers = {
      'Authorization': 'Bearer YOUR_TOKEN_HERE',
      'Content-Type': 'application/json'
    };
    followUpQuestions.push('What is your API token or authentication method?');
    needsMoreInfo = true;
  }

  // Extract query parameters
  const queryPattern = /[?&]([a-zA-Z0-9_]+)=([a-zA-Z0-9_.-]+)/g;
  const queryMatches = [...originalInput.matchAll(queryPattern)];
  if (queryMatches.length > 0) {
    parameters.qs = {};
    queryMatches.forEach(match => {
      parameters.qs[match[1]] = match[2];
    });
  }

  // Generate explanation
  if (parameters.method && parameters.url) {
    explanation = `HTTP Request configured: ${parameters.method} ${parameters.url}`;
    if (parameters.headers) {
      explanation += ' with authentication headers';
    }
    if (parameters.qs) {
      explanation += ` and query parameters: ${Object.keys(parameters.qs).join(', ')}`;
    }
  } else {
    explanation = 'HTTP Request node configured with basic settings';
    if (!parameters.url) {
      followUpQuestions.push('What URL should this request call?');
      needsMoreInfo = true;
      confidence = 0.4;
    }
    if (!parameters.method) {
      parameters.method = 'GET'; // Default
      followUpQuestions.push('What HTTP method should be used? (GET, POST, PUT, DELETE)');
    }
  }

  return { parameters, explanation, confidence, needsMoreInfo, followUpQuestions };
}

function processEmailNode(input: string, originalInput: string) {
  let parameters: Record<string, any> = {};
  let explanation = '';
  let confidence = 0.7;
  let needsMoreInfo = false;
  let followUpQuestions: string[] = [];

  // Extract email addresses
  const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
  const emailMatches = originalInput.match(emailRegex);
  if (emailMatches && emailMatches.length > 0) {
    parameters.to = emailMatches[0];
    confidence += 0.2;
  }

  // Extract subject
  const subjectPatterns = [
    /subject:\s*(.+?)(\n|$|\.)/i,
    /title:\s*(.+?)(\n|$|\.)/i,
    /"([^"]+)"/g // Quoted strings might be subjects
  ];

  subjectPatterns.forEach(pattern => {
    const match = originalInput.match(pattern);
    if (match && match[1]) {
      parameters.subject = match[1].trim();
      confidence += 0.1;
    }
  });

  // Extract body content
  const bodyPatterns = [
    /body:\s*(.+?)(\n|$)/i,
    /message:\s*(.+?)(\n|$)/i,
    /content:\s*(.+?)(\n|$)/i
  ];

  bodyPatterns.forEach(pattern => {
    const match = originalInput.match(pattern);
    if (match && match[1]) {
      parameters.message = match[1].trim();
      confidence += 0.1;
    }
  });

  // Detect email purpose
  if (input.includes('alert') || input.includes('notification') || input.includes('notify')) {
    if (!parameters.subject) parameters.subject = 'Alert Notification';
    if (!parameters.message) parameters.message = 'This is an automated alert from your workflow.';
  } else if (input.includes('report') || input.includes('summary')) {
    if (!parameters.subject) parameters.subject = 'Automated Report';
    if (!parameters.message) parameters.message = 'Please find the automated report attached.';
  } else if (input.includes('welcome') || input.includes('greeting')) {
    if (!parameters.subject) parameters.subject = 'Welcome!';
    if (!parameters.message) parameters.message = 'Welcome to our service!';
  }

  // Check what's missing
  if (!parameters.to) {
    followUpQuestions.push('What email address should receive this email?');
    needsMoreInfo = true;
  }
  if (!parameters.subject) {
    followUpQuestions.push('What should the email subject be?');
    needsMoreInfo = true;
  }
  if (!parameters.message) {
    followUpQuestions.push('What should the email message say?');
    needsMoreInfo = true;
  }

  explanation = `Email configured: `;
  if (parameters.to) explanation += `To: ${parameters.to}, `;
  if (parameters.subject) explanation += `Subject: "${parameters.subject}", `;
  if (parameters.message) explanation += `Message: "${parameters.message.substring(0, 50)}..."`;

  if (needsMoreInfo) {
    explanation += ' (Some details still needed)';
    confidence = 0.4;
  }

  return { parameters, explanation, confidence, needsMoreInfo, followUpQuestions };
}

function processSetNode(input: string, originalInput: string) {
  let parameters: Record<string, any> = {
    values: {
      string: [],
      number: [],
      boolean: []
    },
    options: {},
    keepOnlySet: true
  };
  let explanation = '';
  let confidence = 0.6;

  // Extract variable assignments
  const assignmentPatterns = [
    /set\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+to\s+(.+)/gi,
    /([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)/g,
    /variable\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+(.+)/gi
  ];

  assignmentPatterns.forEach(pattern => {
    const matches = [...originalInput.matchAll(pattern)];
    matches.forEach(match => {
      const [, varName, varValue] = match;
      if (varName && varValue) {
        const cleanValue = varValue.trim().replace(/['"]/g, '');
        
        // Determine type and add to appropriate array
        if (!isNaN(Number(cleanValue))) {
          parameters.values.number.push({
            name: varName.trim(),
            value: Number(cleanValue)
          });
        } else if (cleanValue.toLowerCase() === 'true' || cleanValue.toLowerCase() === 'false') {
          parameters.values.boolean.push({
            name: varName.trim(),
            value: cleanValue.toLowerCase() === 'true'
          });
        } else {
          parameters.values.string.push({
            name: varName.trim(),
            value: cleanValue
          });
        }
        confidence += 0.2;
      }
    });
  });

  // If no specific assignments found, create generic data transformation
  if (parameters.values.string.length === 0 && parameters.values.number.length === 0 && parameters.values.boolean.length === 0) {
    if (input.includes('name') || input.includes('fullname') || input.includes('contact')) {
      parameters.values.string.push({
        name: 'Name',
        value: '{{$json["properties"]["firstname"]["value"]}} {{$json["properties"]["lastname"]["value"]}}'
      });
    }
    if (input.includes('email')) {
      parameters.values.string.push({
        name: 'Email',
        value: '{{$json["identity-profiles"][0]["identities"][0]["value"]}}'
      });
    }
    if (input.includes('status')) {
      parameters.values.string.push({
        name: 'Status',
        value: 'processed'
      });
    }
  }

  const totalFields = parameters.values.string.length + parameters.values.number.length + parameters.values.boolean.length;
  explanation = `Set node configured with ${totalFields} field(s): `;
  explanation += parameters.values.string.map((s: any) => s.name).join(', ');
  explanation += parameters.values.number.map((n: any) => n.name).join(', ');
  explanation += parameters.values.boolean.map((b: any) => b.name).join(', ');

  return { parameters, explanation, confidence };
}

function processFunctionNode(input: string, originalInput: string) {
  let parameters: Record<string, any> = {};
  let explanation = '';
  let confidence = 0.5;

  // Detect programming language
  if (input.includes('javascript') || input.includes('js')) {
    parameters.functionCode = `// JavaScript function
const items = $input.all();
const processedItems = items.map(item => {
  // Process your data here
  return {
    ...item.json,
    processed: true,
    timestamp: new Date().toISOString()
  };
});
return processedItems.map(item => ({ json: item }));`;
  } else if (input.includes('python')) {
    parameters.functionCode = `# Python function
def main():
    items = $input.all()
    processed_items = []
    for item in items:
        # Process your data here
        processed_item = {
            **item['json'],
            'processed': True,
            'timestamp': datetime.now().isoformat()
        }
        processed_items.append({'json': processed_item})
    return processed_items`;
  } else {
    // Default JavaScript
    if (input.includes('transform') || input.includes('process') || input.includes('modify')) {
      parameters.functionCode = `// Data transformation function
const items = $input.all();
return items.map(item => ({
  json: {
    ...item.json,
    processed: true,
    processedAt: new Date().toISOString()
  }
}));`;
    } else if (input.includes('filter')) {
      parameters.functionCode = `// Data filtering function
const items = $input.all();
return items.filter(item => {
  // Add your filter conditions here
  return item.json.status === 'active';
});`;
    } else {
      parameters.functionCode = `// Custom function
const items = $input.all();
// Add your custom logic here
return items;`;
    }
  }

  explanation = `Function node configured with ${input.includes('javascript') || input.includes('js') ? 'JavaScript' : input.includes('python') ? 'Python' : 'JavaScript'} code for data processing`;
  confidence = 0.7;

  return { parameters, explanation, confidence };
}

function processNoOpNode(input: string, originalInput: string) {
  let parameters: Record<string, any> = {};
  let explanation = '';
  let confidence = 0.8;
  let needsMoreInfo = true;
  let followUpQuestions: string[] = [];

  // NoOp is typically a placeholder that should be replaced
  if (input.includes('replace') || input.includes('substitute') || input.includes('change')) {
    explanation = 'This NoOp node is a placeholder. ';
    followUpQuestions.push('What type of node should replace this placeholder?');
    followUpQuestions.push('What action should this step perform?');
  } else if (input.includes('database') || input.includes('db')) {
    explanation = 'Placeholder for database operation. ';
    followUpQuestions.push('What database operation do you need? (INSERT, UPDATE, SELECT, DELETE)');
    followUpQuestions.push('What table or collection should be accessed?');
  } else if (input.includes('spreadsheet') || input.includes('sheet') || input.includes('excel')) {
    explanation = 'Placeholder for spreadsheet operation. ';
    followUpQuestions.push('Which spreadsheet service? (Google Sheets, Excel, Airtable)');
    followUpQuestions.push('What operation? (Add row, Update row, Read data)');
  } else if (input.includes('api') || input.includes('service')) {
    explanation = 'Placeholder for API or service integration. ';
    followUpQuestions.push('What API or service should be integrated?');
    followUpQuestions.push('What operation should be performed?');
  } else {
    explanation = 'NoOp placeholder node configured. ';
    followUpQuestions.push('What should this step do in your workflow?');
    followUpQuestions.push('What type of action or integration do you need here?');
  }

  parameters.configured = true;
  parameters.placeholder = true;

  return { parameters, explanation, confidence, needsMoreInfo, followUpQuestions };
}

function processSpreadsheetNode(input: string, originalInput: string, nodeType: string) {
  let parameters: Record<string, any> = {};
  let explanation = '';
  let confidence = 0.6;
  let needsMoreInfo = false;
  let followUpQuestions: string[] = [];

  const isGoogleSheets = nodeType.includes('googleSheets');
  const serviceName = isGoogleSheets ? 'Google Sheets' : 'Airtable';

  // Detect operation
  if (input.includes('add') || input.includes('append') || input.includes('insert') || input.includes('create')) {
    parameters.operation = 'append';
    parameters.resource = 'spreadsheet';
  } else if (input.includes('update') || input.includes('modify') || input.includes('edit')) {
    parameters.operation = 'update';
    parameters.resource = 'spreadsheet';
  } else if (input.includes('read') || input.includes('get') || input.includes('fetch')) {
    parameters.operation = 'read';
    parameters.resource = 'spreadsheet';
  } else {
    parameters.operation = 'append'; // Default
    parameters.resource = 'spreadsheet';
  }

  // Extract spreadsheet ID or URL
  const spreadsheetPatterns = [
    /spreadsheets\/d\/([a-zA-Z0-9-_]+)/,
    /docs\.google\.com\/spreadsheets\/d\/([a-zA-Z0-9-_]+)/,
    /spreadsheet[_\s]*id[:\s]*([a-zA-Z0-9-_]+)/i
  ];

  spreadsheetPatterns.forEach(pattern => {
    const match = originalInput.match(pattern);
    if (match && match[1]) {
      parameters.documentId = match[1];
      confidence += 0.2;
    }
  });

  // Extract sheet name
  const sheetPatterns = [
    /sheet[_\s]*name[:\s]*['"]?([^'"\\n]+)['"]?/i,
    /tab[_\s]*name[:\s]*['"]?([^'"\\n]+)['"]?/i,
    /worksheet[:\s]*['"]?([^'"\\n]+)['"]?/i
  ];

  sheetPatterns.forEach(pattern => {
    const match = originalInput.match(pattern);
    if (match && match[1]) {
      parameters.sheetName = match[1].trim();
      confidence += 0.1;
    }
  });

  // Set default values
  if (!parameters.sheetName) {
    parameters.sheetName = 'Sheet1';
  }

  // Check what's needed
  if (!parameters.documentId) {
    followUpQuestions.push(`What is the ${serviceName} ID or URL?`);
    needsMoreInfo = true;
    confidence = 0.3;
  }

  if (parameters.operation === 'append') {
    followUpQuestions.push('What data columns should be added to the spreadsheet?');
    needsMoreInfo = true;
  }

  explanation = `${serviceName} ${parameters.operation} operation configured`;
  if (parameters.documentId) {
    explanation += ` for document ${parameters.documentId}`;
  }
  if (parameters.sheetName) {
    explanation += ` on sheet "${parameters.sheetName}"`;
  }

  return { parameters, explanation, confidence, needsMoreInfo, followUpQuestions };
}

function processGenericNode(input: string, originalInput: string, nodeType: string, nodeName: string) {
  let parameters: Record<string, any> = { configured: true };
  let explanation = `${nodeName} node configured based on your description: "${originalInput.substring(0, 100)}${originalInput.length > 100 ? '...' : ''}"`;
  let confidence = 0.5;

  // Extract common parameters based on node type patterns
  if (nodeType.includes('trigger')) {
    parameters.active = true;
    explanation = `Trigger node "${nodeName}" configured and activated`;
    confidence = 0.8;
  } else if (nodeType.includes('webhook')) {
    parameters.httpMethod = 'POST';
    parameters.path = `/${nodeName.toLowerCase().replace(/\s+/g, '-')}`;
    explanation = `Webhook "${nodeName}" configured with POST method`;
    confidence = 0.7;
  } else if (nodeType.includes('schedule')) {
    parameters.rule = {
      interval: [{ field: 'cronExpression', expression: '0 9 * * *' }] // Daily at 9 AM
    };
    explanation = `Scheduler "${nodeName}" configured to run daily at 9 AM`;
    confidence = 0.6;
  }

  return { parameters, explanation, confidence };
}
