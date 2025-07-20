// src/lib/ai-memory.ts
// AI memory and context management system

interface ConversationMemory {
  id: string;
  userId: string;
  messages: Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    metadata?: {
      intent?: string;
      extractedParameters?: Record<string, any>;
      workflowGenerated?: any;
      nodeTypes?: string[];
    };
  }>;
  context: {
    currentWorkflow?: any;
    availableNodes: NodeDefinition[];
    userPreferences: {
      defaultSchedule?: string;
      favoriteNodes?: string[];
      emailTemplates?: Array<{name: string, subject: string, content: string}>;
    };
    workflowHistory: Array<{
      id: string;
      name: string;
      createdAt: Date;
      executed: boolean;
      nodes: any[];
    }>;
  };
  createdAt: Date;
  updatedAt: Date;
}

interface NodeDefinition {
  id: string;
  name: string;
  type: string;
  category: 'triggers' | 'actions' | 'logic' | 'data' | 'communication' | 'integrations';
  description: string;
  icon: string;
  parameters: Array<{
    name: string;
    type: 'string' | 'number' | 'boolean' | 'email' | 'url' | 'json' | 'schedule';
    required: boolean;
    description: string;
    defaultValue?: any;
    options?: string[];
  }>;
  inputs?: string[];
  outputs?: string[];
  examples?: Array<{
    name: string;
    description: string;
    configuration: Record<string, any>;
  }>;
}

class AIMemoryManager {
  private memories: Map<string, ConversationMemory> = new Map();
  private nodeDefinitions: NodeDefinition[] = [];

  constructor() {
    this.initializeNodeDefinitions();
    this.loadAvailableNodes();
  }

  public async loadAvailableNodes() {
    try {
      // Only load nodes on client side or provide a full URL
      if (typeof window === 'undefined') {
        console.log('⚠️  Skipping node loading on server side');
        return;
      }
      
      const response = await fetch('/api/nodes/available');
      if (response.ok) {
        const data = await response.json() as {
          success: boolean;
          nodes: NodeDefinition[];
          totalNodes: number;
        };
        if (data.success && data.nodes) {
          this.nodeDefinitions = [...this.nodeDefinitions, ...data.nodes];
          console.log(`✅ Loaded ${data.totalNodes} node definitions from backend`);
        }
      } else {
        console.warn('⚠️  Failed to load nodes from backend, using defaults');
      }
    } catch (error) {
      console.warn('⚠️  Error loading nodes from backend:', error);
    }
  }

  private initializeNodeDefinitions() {
    // Initialize with common node types
    this.nodeDefinitions = [
      // Trigger Nodes
      {
        id: 'manual-trigger',
        name: 'Manual Trigger',
        type: 'manual',
        category: 'triggers',
        description: 'Manually start the workflow',
        icon: '▶️',
        parameters: [],
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
            type: 'schedule',
            required: true,
            description: 'Cron expression or schedule (e.g., "0 9 * * *" for daily at 9 AM)'
          },
          {
            name: 'timezone',
            type: 'string',
            required: false,
            description: 'Timezone for the schedule',
            defaultValue: 'UTC'
          }
        ],
        outputs: ['trigger'],
        examples: [
          {
            name: 'Daily at 9 AM',
            description: 'Trigger every day at 9 AM',
            configuration: { schedule: '0 9 * * *', timezone: 'UTC' }
          },
          {
            name: 'Every Monday',
            description: 'Trigger every Monday at 10 AM',
            configuration: { schedule: '0 10 * * 1', timezone: 'UTC' }
          }
        ]
      },
      {
        id: 'webhook-trigger',
        name: 'Webhook Trigger',
        type: 'webhook',
        category: 'triggers',
        description: 'Trigger workflow from HTTP webhook',
        icon: '🌐',
        parameters: [
          {
            name: 'path',
            type: 'string',
            required: false,
            description: 'Custom webhook path',
            defaultValue: '/webhook'
          }
        ],
        outputs: ['data'],
        examples: [{
          name: 'Form submission',
          description: 'Trigger when a form is submitted',
          configuration: { path: '/form-submit' }
        }]
      },

      // Communication Nodes
      {
        id: 'send-email',
        name: 'Send Email',
        type: 'email',
        category: 'communication',
        description: 'Send an email message',
        icon: '📧',
        parameters: [
          {
            name: 'recipient',
            type: 'email',
            required: true,
            description: 'Email address to send to'
          },
          {
            name: 'subject',
            type: 'string',
            required: true,
            description: 'Email subject line'
          },
          {
            name: 'content',
            type: 'string',
            required: true,
            description: 'Email message content'
          },
          {
            name: 'html',
            type: 'boolean',
            required: false,
            description: 'Send as HTML email',
            defaultValue: false
          }
        ],
        inputs: ['trigger'],
        outputs: ['success', 'error'],
        examples: [
          {
            name: 'Daily reminder',
            description: 'Send a daily reminder email',
            configuration: {
              recipient: 'user@example.com',
              subject: 'Daily Reminder',
              content: 'Don\'t forget your daily tasks!'
            }
          },
          {
            name: 'Welcome email',
            description: 'Send welcome email to new users',
            configuration: {
              recipient: '{{user.email}}',
              subject: 'Welcome to our platform!',
              content: 'Thank you for joining us, {{user.name}}!'
            }
          }
        ]
      },

      // Logic Nodes
      {
        id: 'condition',
        name: 'Condition',
        type: 'if',
        category: 'logic',
        description: 'Add conditional logic to workflow',
        icon: '🤔',
        parameters: [
          {
            name: 'condition',
            type: 'string',
            required: true,
            description: 'Condition to evaluate (e.g., "age > 18")'
          }
        ],
        inputs: ['input'],
        outputs: ['true', 'false'],
        examples: [{
          name: 'Age check',
          description: 'Check if user is over 18',
          configuration: { condition: 'age > 18' }
        }]
      },

      // Data Nodes
      {
        id: 'set-variable',
        name: 'Set Variable',
        type: 'set',
        category: 'data',
        description: 'Set a variable value',
        icon: '📝',
        parameters: [
          {
            name: 'name',
            type: 'string',
            required: true,
            description: 'Variable name'
          },
          {
            name: 'value',
            type: 'string',
            required: true,
            description: 'Variable value'
          }
        ],
        inputs: ['input'],
        outputs: ['output'],
        examples: [{
          name: 'Set timestamp',
          description: 'Set current timestamp',
          configuration: { name: 'timestamp', value: '{{now}}' }
        }]
      },

      // Integration Nodes
      {
        id: 'http-request',
        name: 'HTTP Request',
        type: 'http',
        category: 'integrations',
        description: 'Make HTTP API call',
        icon: '🌍',
        parameters: [
          {
            name: 'url',
            type: 'url',
            required: true,
            description: 'API endpoint URL'
          },
          {
            name: 'method',
            type: 'string',
            required: true,
            description: 'HTTP method',
            options: ['GET', 'POST', 'PUT', 'DELETE'],
            defaultValue: 'GET'
          },
          {
            name: 'headers',
            type: 'json',
            required: false,
            description: 'Request headers as JSON'
          },
          {
            name: 'body',
            type: 'json',
            required: false,
            description: 'Request body as JSON'
          }
        ],
        inputs: ['trigger'],
        outputs: ['success', 'error'],
        examples: [
          {
            name: 'Get weather',
            description: 'Fetch weather data from API',
            configuration: {
              url: 'https://api.weather.com/current',
              method: 'GET',
              headers: { 'Authorization': 'Bearer {{api_key}}' }
            }
          }
        ]
      }
    ];
  }

  // Memory Management
  async getMemory(userId: string, conversationId: string): Promise<ConversationMemory | null> {
    const key = `${userId}-${conversationId}`;
    return this.memories.get(key) || null;
  }

  async createMemory(userId: string, conversationId: string): Promise<ConversationMemory> {
    const memory: ConversationMemory = {
      id: conversationId,
      userId,
      messages: [],
      context: {
        availableNodes: this.nodeDefinitions,
        userPreferences: {},
        workflowHistory: []
      },
      createdAt: new Date(),
      updatedAt: new Date()
    };
    
    const key = `${userId}-${conversationId}`;
    this.memories.set(key, memory);
    return memory;
  }

  async addMessage(
    userId: string, 
    conversationId: string, 
    role: 'user' | 'assistant', 
    content: string, 
    metadata?: any
  ): Promise<void> {
    const key = `${userId}-${conversationId}`;
    let memory = this.memories.get(key);
    
    if (!memory) {
      memory = await this.createMemory(userId, conversationId);
    }

    memory.messages.push({
      role,
      content,
      timestamp: new Date(),
      metadata
    });
    
    memory.updatedAt = new Date();
    this.memories.set(key, memory);
  }

  async updateContext(
    userId: string, 
    conversationId: string, 
    updates: Partial<ConversationMemory['context']>
  ): Promise<void> {
    const key = `${userId}-${conversationId}`;
    const memory = this.memories.get(key);
    
    if (memory) {
      memory.context = { ...memory.context, ...updates };
      memory.updatedAt = new Date();
      this.memories.set(key, memory);
    }
  }

  // Node Discovery and Understanding
  findNodesByIntent(intent: string): NodeDefinition[] {
    const lowerIntent = intent.toLowerCase();
    
    return this.nodeDefinitions.filter(node => {
      return (
        node.name.toLowerCase().includes(lowerIntent) ||
        node.description.toLowerCase().includes(lowerIntent) ||
        node.type.toLowerCase().includes(lowerIntent) ||
        node.examples?.some(example => 
          example.name.toLowerCase().includes(lowerIntent) ||
          example.description.toLowerCase().includes(lowerIntent)
        )
      );
    });
  }

  getNodesByCategory(category: string): NodeDefinition[] {
    return this.nodeDefinitions.filter(node => node.category === category);
  }

  getNodeById(id: string): NodeDefinition | null {
    return this.nodeDefinitions.find(node => node.id === id) || null;
  }

  // Workflow Generation
  generateWorkflowFromIntent(intent: string, parameters: Record<string, any> = {}): any {
    const lowerIntent = intent.toLowerCase();
    
    if (lowerIntent.includes('email') || lowerIntent.includes('send')) {
      return this.generateEmailWorkflow(parameters);
    }
    
    if (lowerIntent.includes('schedule') || lowerIntent.includes('daily') || lowerIntent.includes('every')) {
      return this.generateScheduledWorkflow(intent, parameters);
    }
    
    if (lowerIntent.includes('webhook') || lowerIntent.includes('api')) {
      return this.generateWebhookWorkflow(parameters);
    }
    
    return this.generateGenericWorkflow(intent, parameters);
  }

  private generateEmailWorkflow(parameters: Record<string, any>) {
    // Find appropriate nodes from available definitions
    const triggerNode = this.getNodesByCategory('triggers').find((n: NodeDefinition) => n.type === 'manual') || this.getNodeById('manual-trigger');
    const emailNode = this.getNodesByCategory('communication').find((n: NodeDefinition) => n.type === 'email') || this.getNodeById('email-send');
    
    const nodes = [
      {
        id: 'trigger-1',
        type: triggerNode?.type || 'manual',
        name: triggerNode?.name || 'Start',
        position: { x: 50, y: 100 },
        parameters: {},
        category: 'triggers',
        icon: triggerNode?.icon || '▶️',
        outputs: triggerNode?.outputs || ['trigger'],
        description: triggerNode?.description || 'Manually start the workflow'
      },
      {
        id: 'email-1',
        type: emailNode?.type || 'email',
        name: emailNode?.name || 'Send Email',
        position: { x: 250, y: 100 },
        parameters: {
          to: parameters.recipient || '',
          subject: parameters.subject || 'Automated Email',
          body: parameters.content || 'This is an automated email.',
          from: parameters.from || ''
        },
        category: 'communication',
        icon: emailNode?.icon || '📧',
        inputs: emailNode?.inputs || ['input'],
        outputs: emailNode?.outputs || ['output'],
        description: emailNode?.description || 'Send an email message'
      }
    ];

    const connections = [
      {
        id: 'conn-1',
        source: 'trigger-1',
        target: 'email-1',
        sourceOutput: 'trigger',
        targetInput: 'input'
      }
    ];

    return {
      id: `workflow-${Date.now()}`,
      name: 'Email Automation',
      description: 'Send an automated email',
      nodes,
      connections,
      createdAt: new Date()
    };
  }

  private generateScheduledWorkflow(intent: string, parameters: Record<string, any>) {
    const nodes = [
      {
        id: 'schedule-1',
        type: 'schedule',
        name: 'Schedule Trigger',
        position: { x: 50, y: 100 },
        parameters: {
          schedule: parameters.schedule || '0 9 * * *',
          timezone: parameters.timezone || 'UTC'
        },
        category: 'triggers',
        icon: '⏰',
        outputs: ['trigger']
      }
    ];

    // Add appropriate action based on intent
    if (intent.includes('email')) {
      nodes.push({
        id: 'email-1',
        type: 'email',
        name: 'Send Scheduled Email',
        position: { x: 250, y: 100 },
        parameters: {
          recipient: parameters.recipient || '',
          subject: parameters.subject || 'Scheduled Reminder',
          content: parameters.content || 'This is your scheduled reminder.',
          html: false
        },
        category: 'communication',
        icon: '📧',
        inputs: ['trigger'],
        outputs: ['success', 'error']
      } as any);
    }

    const connections = nodes.length > 1 ? [
      {
        id: 'conn-1',
        source: 'schedule-1',
        target: nodes[1].id,
        sourceOutput: 'trigger',
        targetInput: 'trigger'
      }
    ] : [];

    return {
      id: `workflow-${Date.now()}`,
      name: 'Scheduled Automation',
      description: 'Automated workflow that runs on a schedule',
      nodes,
      connections,
      createdAt: new Date()
    };
  }

  private generateWebhookWorkflow(parameters: Record<string, any>) {
    const nodes = [
      {
        id: 'webhook-1',
        type: 'webhook',
        name: 'Webhook Trigger',
        position: { x: 50, y: 100 },
        parameters: {
          path: parameters.path || '/webhook'
        },
        category: 'triggers',
        icon: '🌐',
        outputs: ['data']
      },
      {
        id: 'http-1',
        type: 'http',
        name: 'HTTP Response',
        position: { x: 250, y: 100 },
        parameters: {
          url: parameters.responseUrl || 'https://example.com/api',
          method: 'POST',
          body: '{"status": "received"}'
        },
        category: 'integrations',
        icon: '🌍',
        inputs: ['data'],
        outputs: ['success', 'error']
      }
    ];

    const connections = [
      {
        id: 'conn-1',
        source: 'webhook-1',
        target: 'http-1',
        sourceOutput: 'data',
        targetInput: 'data'
      }
    ];

    return {
      id: `workflow-${Date.now()}`,
      name: 'Webhook Automation',
      description: 'Webhook-triggered automation workflow',
      nodes,
      connections,
      createdAt: new Date()
    };
  }

  private generateGenericWorkflow(intent: string, parameters: Record<string, any>) {
    const nodes = [
      {
        id: 'manual-1',
        type: 'manual',
        name: 'Manual Trigger',
        position: { x: 50, y: 100 },
        parameters: {},
        category: 'triggers',
        icon: '▶️',
        outputs: ['trigger']
      }
    ];

    return {
      id: `workflow-${Date.now()}`,
      name: 'Custom Automation',
      description: `Automation workflow for: ${intent}`,
      nodes,
      connections: [],
      createdAt: new Date()
    };
  }

  // Get context for AI responses
  getAIContext(userId: string, conversationId: string): string {
    const key = `${userId}-${conversationId}`;
    const memory = this.memories.get(key);
    
    if (!memory) return '';
    
    const recentMessages = memory.messages.slice(-5);
    const availableNodeTypes = this.nodeDefinitions.map(n => `${n.name} (${n.type})`).join(', ');
    
    return `
Context:
- Available node types: ${availableNodeTypes}
- Recent conversation: ${recentMessages.map(m => `${m.role}: ${m.content}`).join('\n')}
- Current workflow: ${memory.context.currentWorkflow ? memory.context.currentWorkflow.name : 'None'}
- User preferences: ${JSON.stringify(memory.context.userPreferences)}
`;
  }
}

export const aiMemoryManager = new AIMemoryManager();
export type { ConversationMemory, NodeDefinition };
