import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';
import fs from 'fs';
import path from 'path';

// Initialize OpenAI
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

interface WorkflowSearchRequest {
  query: string;
  limit?: number;
}

interface WorkflowSearchResult {
  filename: string;
  name: string;
  description: string;
  nodes: any[];
  relevanceScore: number;
  explanation: string;
  suggestedParameters: Record<string, any>;
}

interface SearchResponse {
  success: boolean;
  results: WorkflowSearchResult[];
  totalFound: number;
  searchQuery: string;
  aiExplanation: string;
}

export async function POST(request: NextRequest) {
  try {
    const body: WorkflowSearchRequest = await request.json();
    const { query, limit = 5 } = body;

    if (!query || query.trim().length === 0) {
      return NextResponse.json(
        { error: 'Search query is required' },
        { status: 400 }
      );
    }

    if (!process.env.OPENAI_API_KEY) {
      return NextResponse.json(
        { error: 'OpenAI API key not configured' },
        { status: 500 }
      );
    }

    // Search for relevant workflows
    const searchResults = await searchWorkflows(query, limit);

    return NextResponse.json(searchResults);
  } catch (error) {
    console.error('Error in workflow search:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

async function searchWorkflows(query: string, limit: number): Promise<SearchResponse> {
  const workflowsDir = path.join(process.cwd(), 'src', 'app', 'dashboard', 'automation', 'workflows');
  
  try {
    // Get all workflow files
    const files = fs.readdirSync(workflowsDir)
      .filter(file => file.endsWith('.json'))
      .slice(0, 100); // Limit to first 100 for performance

    // Load and parse workflows
    const workflows = [];
    for (const file of files) {
      try {
        const filePath = path.join(workflowsDir, file);
        const content = fs.readFileSync(filePath, 'utf-8');
        const workflow = JSON.parse(content);
        workflows.push({
          filename: file,
          ...workflow
        });
      } catch (parseError) {
        console.warn(`Failed to parse workflow ${file}:`, parseError);
        continue;
      }
    }

    // Use OpenAI to find relevant workflows
    const relevantWorkflows = await findRelevantWorkflows(query, workflows, limit);

    // Generate AI explanation
    const aiExplanation = await generateSearchExplanation(query, relevantWorkflows);

    return {
      success: true,
      results: relevantWorkflows,
      totalFound: relevantWorkflows.length,
      searchQuery: query,
      aiExplanation
    };

  } catch (error) {
    console.error('Error searching workflows:', error);
    return {
      success: false,
      results: [],
      totalFound: 0,
      searchQuery: query,
      aiExplanation: 'An error occurred while searching workflows.'
    };
  }
}

async function findRelevantWorkflows(
  query: string, 
  workflows: any[], 
  limit: number
): Promise<WorkflowSearchResult[]> {
  
  // Create a prompt for OpenAI to analyze workflows
  const workflowSummaries = workflows.map(w => ({
    filename: w.filename,
    name: w.name || 'Unnamed Workflow',
    nodeCount: w.nodes?.length || 0,
    nodeTypes: w.nodes?.map((n: any) => n.type).join(', ') || '',
    firstNodeName: w.nodes?.[0]?.name || '',
    description: generateWorkflowDescription(w)
  }));

  const prompt = `
You are an expert automation workflow analyst. A user is searching for workflows with this query: "${query}"

Here are available workflows to analyze:
${workflowSummaries.map((w, i) => `
${i + 1}. Filename: ${w.filename}
   Name: ${w.name}
   Description: ${w.description}
   Nodes: ${w.nodeCount} (${w.nodeTypes})
`).join('\n')}

Your task:
1. Identify the top ${limit} most relevant workflows for the user's query
2. For each relevant workflow, provide:
   - A relevance score (0-100)
   - An explanation of why it matches
   - Suggested parameters the user might need

Return your response as a JSON array of objects with this structure:
[
  {
    "filename": "workflow_file.json",
    "relevanceScore": 85,
    "explanation": "This workflow matches because...",
    "suggestedParameters": {
      "param1": "value1",
      "param2": "value2"
    }
  }
]

Focus on workflows that actually solve the user's problem or are closely related to their intent.
`;

  try {
    const completion = await openai.chat.completions.create({
      model: process.env.OPENAI_MODEL || 'gpt-4-turbo-preview',
      messages: [
        {
          role: 'system',
          content: 'You are a helpful assistant that analyzes automation workflows and finds the most relevant ones for user queries. Always respond with valid JSON.'
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      max_tokens: parseInt(process.env.OPENAI_MAX_TOKENS || '2000'),
      temperature: 0.3,
    });

    const aiResponse = completion.choices[0]?.message?.content;
    if (!aiResponse) {
      throw new Error('No response from OpenAI');
    }

    // Parse AI response
    let aiResults;
    try {
      // Clean the response in case it has markdown formatting
      const cleanResponse = aiResponse.replace(/```json\n?/g, '').replace(/```\n?/g, '');
      aiResults = JSON.parse(cleanResponse);
    } catch (parseError) {
      console.error('Failed to parse AI response:', aiResponse);
      // Fallback to simple text matching
      return simpleTextSearch(query, workflows, limit);
    }

    // Combine AI results with actual workflow data
    const results: WorkflowSearchResult[] = [];
    
    for (const aiResult of aiResults) {
      const workflow = workflows.find(w => w.filename === aiResult.filename);
      if (workflow && results.length < limit) {
        results.push({
          filename: workflow.filename,
          name: workflow.name || 'Unnamed Workflow',
          description: generateWorkflowDescription(workflow),
          nodes: workflow.nodes || [],
          relevanceScore: aiResult.relevanceScore || 50,
          explanation: aiResult.explanation || 'AI identified this as relevant',
          suggestedParameters: aiResult.suggestedParameters || {}
        });
      }
    }

    return results.sort((a, b) => b.relevanceScore - a.relevanceScore);

  } catch (error) {
    console.error('Error with OpenAI analysis:', error);
    // Fallback to simple search
    return simpleTextSearch(query, workflows, limit);
  }
}

function simpleTextSearch(query: string, workflows: any[], limit: number): WorkflowSearchResult[] {
  const queryLower = query.toLowerCase();
  const results: WorkflowSearchResult[] = [];

  for (const workflow of workflows) {
    const name = (workflow.name || '').toLowerCase();
    const description = generateWorkflowDescription(workflow).toLowerCase();
    const nodeNames = (workflow.nodes || []).map((n: any) => (n.name || '').toLowerCase()).join(' ');
    
    let score = 0;
    
    // Name match (highest weight)
    if (name.includes(queryLower)) score += 50;
    
    // Description match
    if (description.includes(queryLower)) score += 30;
    
    // Node name match
    if (nodeNames.includes(queryLower)) score += 20;
    
    // Keyword matching
    const keywords = queryLower.split(' ');
    for (const keyword of keywords) {
      if (name.includes(keyword)) score += 10;
      if (description.includes(keyword)) score += 5;
      if (nodeNames.includes(keyword)) score += 5;
    }

    if (score > 0) {
      results.push({
        filename: workflow.filename,
        name: workflow.name || 'Unnamed Workflow',
        description: generateWorkflowDescription(workflow),
        nodes: workflow.nodes || [],
        relevanceScore: Math.min(score, 100),
        explanation: `Matches based on content similarity (score: ${score})`,
        suggestedParameters: {}
      });
    }
  }

  return results
    .sort((a, b) => b.relevanceScore - a.relevanceScore)
    .slice(0, limit);
}

function generateWorkflowDescription(workflow: any): string {
  if (!workflow.nodes || workflow.nodes.length === 0) {
    return 'Empty workflow with no nodes';
  }

  const nodeTypes = workflow.nodes.map((n: any) => {
    const type = n.type || 'unknown';
    const name = n.name || 'unnamed';
    return `${name} (${type.replace('n8n-nodes-base.', '')})`;
  });

  const triggerNodes = workflow.nodes.filter((n: any) => 
    n.type?.includes('trigger') || n.type?.includes('webhook') || n.type?.includes('manual')
  );

  const actionNodes = workflow.nodes.filter((n: any) => 
    !n.type?.includes('trigger') && !n.type?.includes('webhook') && !n.type?.includes('manual')
  );

  let description = `Workflow with ${workflow.nodes.length} nodes: `;
  
  if (triggerNodes.length > 0) {
    description += `Triggered by ${triggerNodes[0].name || 'trigger'}, `;
  }
  
  if (actionNodes.length > 0) {
    const actions = actionNodes.slice(0, 3).map(n => n.name || 'action').join(', ');
    description += `performs: ${actions}`;
    if (actionNodes.length > 3) {
      description += ` and ${actionNodes.length - 3} more actions`;
    }
  }

  return description;
}

async function generateSearchExplanation(query: string, results: WorkflowSearchResult[]): Promise<string> {
  if (results.length === 0) {
    return `I couldn't find any workflows that match "${query}". You might want to try different keywords or create a custom workflow for your specific needs.`;
  }

  try {
    const prompt = `
A user searched for workflows with the query: "${query}"

I found ${results.length} relevant workflows:
${results.map((r, i) => `${i + 1}. ${r.name} (Score: ${r.relevanceScore}) - ${r.explanation}`).join('\n')}

Write a helpful, conversational explanation (2-3 sentences) that:
1. Acknowledges what the user was looking for
2. Briefly explains what workflows were found and why they're relevant
3. Encourages the user to explore the results

Keep it friendly and concise.
`;

    const completion = await openai.chat.completions.create({
      model: process.env.OPENAI_MODEL || 'gpt-4-turbo-preview',
      messages: [
        {
          role: 'system',
          content: 'You are a helpful AI assistant that explains search results in a friendly, conversational way.'
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      max_tokens: 200,
      temperature: 0.7,
    });

    return completion.choices[0]?.message?.content || 
           `I found ${results.length} workflows that match your search for "${query}". These workflows should help you get started with your automation needs.`;

  } catch (error) {
    console.error('Error generating explanation:', error);
    return `I found ${results.length} workflows that match your search for "${query}". These workflows should help you get started with your automation needs.`;
  }
}
