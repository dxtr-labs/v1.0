// src/app/api/nodes/available/route.ts
// API endpoint to fetch available node types from the backend

import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    // For now, return a predefined set of node types
    // In production, this would fetch from the n8n backend
    const nodeDefinitions = getAvailableNodeDefinitions();

    return NextResponse.json({
      success: true,
      nodes: nodeDefinitions,
      totalNodes: nodeDefinitions.length,
      stats: {
        total: nodeDefinitions.length,
        byCategory: getNodesByCategory(nodeDefinitions)
      }
    });

  } catch (error) {
    console.error('Error fetching available nodes:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error',
        nodes: [],
        totalNodes: 0
      },
      { status: 500 }
    );
  }
}

function getAvailableNodeDefinitions() {
  return [
    // Trigger Nodes
    {
      id: 'manual-trigger',
      name: 'Manual Trigger',
      type: 'manual',
      category: 'triggers',
      description: 'Manually start the workflow',
      icon: '▶️',
      parameters: [
        {
          name: 'name',
          type: 'string',
          required: false,
          description: 'Trigger name',
          defaultValue: 'Manual Trigger'
        }
      ],
      inputs: [],
      outputs: ['trigger'],
      examples: [{
        name: 'Start workflow',
        description: 'Basic manual trigger to start any workflow',
        configuration: {}
      }]
    },
    {
      id: 'schedule-trigger',
      name: 'Schedule Trigger',
      type: 'schedule',
      category: 'triggers',
      description: 'Trigger workflow on a schedule',
      icon: '⏰',
      parameters: [
        {
          name: 'schedule',
          type: 'string',
          required: true,
          description: 'Cron expression for schedule',
          defaultValue: '0 9 * * *'
        },
        {
          name: 'timezone',
          type: 'string',
          required: false,
          description: 'Timezone for schedule',
          defaultValue: 'UTC'
        }
      ],
      inputs: [],
      outputs: ['trigger'],
      examples: [{
        name: 'Daily 9 AM',
        description: 'Trigger every day at 9 AM',
        configuration: { schedule: '0 9 * * *' }
      }]
    },
    {
      id: 'webhook-trigger',
      name: 'Webhook Trigger',
      type: 'webhook',
      category: 'triggers',
      description: 'Trigger workflow via HTTP webhook',
      icon: '🌐',
      parameters: [
        {
          name: 'path',
          type: 'string',
          required: true,
          description: 'Webhook path',
          defaultValue: '/webhook'
        },
        {
          name: 'method',
          type: 'string',
          required: false,
          description: 'HTTP method',
          defaultValue: 'POST',
          options: ['GET', 'POST', 'PUT', 'DELETE']
        }
      ],
      inputs: [],
      outputs: ['data'],
      examples: [{
        name: 'Basic webhook',
        description: 'Simple webhook trigger',
        configuration: { path: '/webhook', method: 'POST' }
      }]
    },
    
    // Communication Nodes
    {
      id: 'email-send',
      name: 'Email Send',
      type: 'email',
      category: 'communication',
      description: 'Send email messages',
      icon: '📧',
      parameters: [
        {
          name: 'to',
          type: 'string',
          required: true,
          description: 'Recipient email address'
        },
        {
          name: 'subject',
          type: 'string',
          required: true,
          description: 'Email subject'
        },
        {
          name: 'body',
          type: 'string',
          required: true,
          description: 'Email content'
        },
        {
          name: 'from',
          type: 'string',
          required: false,
          description: 'Sender email address'
        }
      ],
      inputs: ['input'],
      outputs: ['output'],
      examples: [{
        name: 'Basic email',
        description: 'Send a simple email',
        configuration: {
          to: 'user@example.com',
          subject: 'Hello',
          body: 'Hello World!'
        }
      }]
    },
    {
      id: 'slack-send',
      name: 'Slack Send',
      type: 'slack',
      category: 'communication',
      description: 'Send messages to Slack',
      icon: '💬',
      parameters: [
        {
          name: 'channel',
          type: 'string',
          required: true,
          description: 'Slack channel or user'
        },
        {
          name: 'message',
          type: 'string',
          required: true,
          description: 'Message content'
        },
        {
          name: 'token',
          type: 'string',
          required: true,
          description: 'Slack bot token'
        }
      ],
      inputs: ['input'],
      outputs: ['output'],
      examples: [{
        name: 'Channel message',
        description: 'Send message to Slack channel',
        configuration: {
          channel: '#general',
          message: 'Hello from automation!'
        }
      }]
    },
    
    // Data Nodes
    {
      id: 'json-transform',
      name: 'JSON Transform',
      type: 'json',
      category: 'data',
      description: 'Transform JSON data',
      icon: '📊',
      parameters: [
        {
          name: 'operation',
          type: 'string',
          required: true,
          description: 'JSON operation',
          defaultValue: 'parse',
          options: ['parse', 'stringify', 'transform']
        },
        {
          name: 'path',
          type: 'string',
          required: false,
          description: 'JSON path to transform'
        }
      ],
      inputs: ['input'],
      outputs: ['output'],
      examples: [{
        name: 'Parse JSON',
        description: 'Parse JSON string to object',
        configuration: { operation: 'parse' }
      }]
    },
    
    // Logic Nodes
    {
      id: 'if-condition',
      name: 'IF Condition',
      type: 'if',
      category: 'logic',
      description: 'Conditional logic branching',
      icon: '🧠',
      parameters: [
        {
          name: 'condition',
          type: 'string',
          required: true,
          description: 'Condition to evaluate'
        },
        {
          name: 'operator',
          type: 'string',
          required: true,
          description: 'Comparison operator',
          defaultValue: 'equals',
          options: ['equals', 'not_equals', 'greater', 'less', 'contains']
        },
        {
          name: 'value',
          type: 'string',
          required: true,
          description: 'Value to compare against'
        }
      ],
      inputs: ['input'],
      outputs: ['true', 'false'],
      examples: [{
        name: 'Simple condition',
        description: 'Check if value equals something',
        configuration: { condition: 'status', operator: 'equals', value: 'active' }
      }]
    },
    
    // Action Nodes
    {
      id: 'http-request',
      name: 'HTTP Request',
      type: 'http',
      category: 'actions',
      description: 'Make HTTP requests',
      icon: '🔧',
      parameters: [
        {
          name: 'url',
          type: 'string',
          required: true,
          description: 'Request URL'
        },
        {
          name: 'method',
          type: 'string',
          required: true,
          description: 'HTTP method',
          defaultValue: 'GET',
          options: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        },
        {
          name: 'headers',
          type: 'string',
          required: false,
          description: 'Request headers (JSON)'
        },
        {
          name: 'body',
          type: 'string',
          required: false,
          description: 'Request body'
        }
      ],
      inputs: ['input'],
      outputs: ['output'],
      examples: [{
        name: 'GET request',
        description: 'Simple GET request',
        configuration: { url: 'https://api.example.com/data', method: 'GET' }
      }]
    },
    
    // Integration Nodes
    {
      id: 'google-sheets',
      name: 'Google Sheets',
      type: 'google-sheets',
      category: 'integrations',
      description: 'Work with Google Sheets',
      icon: '📝',
      parameters: [
        {
          name: 'operation',
          type: 'string',
          required: true,
          description: 'Sheets operation',
          defaultValue: 'read',
          options: ['read', 'write', 'update', 'delete']
        },
        {
          name: 'spreadsheet_id',
          type: 'string',
          required: true,
          description: 'Google Sheets ID'
        },
        {
          name: 'range',
          type: 'string',
          required: true,
          description: 'Cell range (e.g., A1:B10)'
        }
      ],
      inputs: ['input'],
      outputs: ['output'],
      examples: [{
        name: 'Read sheet',
        description: 'Read data from Google Sheets',
        configuration: { operation: 'read', range: 'A1:B10' }
      }]
    }
  ];
}

function getNodesByCategory(nodes: any[]) {
  const categories: Record<string, number> = {};
  nodes.forEach(node => {
    categories[node.category] = (categories[node.category] || 0) + 1;
  });
  return categories;
}
