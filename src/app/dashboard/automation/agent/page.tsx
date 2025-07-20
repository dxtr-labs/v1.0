'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { ArrowLeft, Send, Bot, User, Settings, Save, Download, Play } from 'lucide-react';

// Types
interface WorkflowNode {
  id: string;
  type: string;
  name: string;
  parameters?: Record<string, any>;
  position?: { x: number; y: number };
}

interface WorkflowData {
  id: string;
  name: string;
  description?: string;
  nodes: WorkflowNode[];
  filename: string;
}

interface ChatMessage {
  id: string;
  type: 'user' | 'agent';
  content: string;
  timestamp: Date;
  nodeId?: string;
  parameter?: string;
  suggestedValue?: any;
}

interface AIResponse {
  success: boolean;
  suggestedParameters: Record<string, any>;
  explanation: string;
  confidence: number;
  needsMoreInfo?: boolean;
  followUpQuestions?: string[];
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

export default function AutomationAgent() {
  const searchParams = useSearchParams();
  const [workflowData, setWorkflowData] = useState<WorkflowData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentNodeIndex, setCurrentNodeIndex] = useState(0);
  const [completedParameters, setCompletedParameters] = useState<Record<string, Record<string, any>>>({});
  
  // New states for workflow search
  const [isSearchMode, setIsSearchMode] = useState(true);
  const [searchResults, setSearchResults] = useState<WorkflowSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowSearchResult | null>(null);

  useEffect(() => {
    const loadWorkflowData = async () => {
      try {
        const workflowParam = searchParams?.get('workflow');
        const workflowId = searchParams?.get('workflowId');
        const mode = searchParams?.get('mode');
        
        if (workflowId) {
          // Load workflow from API endpoint
          const response = await fetch(`/api/automation/load-workflow?workflowId=${workflowId}`);
          if (response.ok) {
            const data = await response.json() as { workflow: WorkflowData };
            const { workflow } = data;
            setWorkflowData(workflow);
            setIsSearchMode(mode !== 'configure');
            
            if (mode === 'configure') {
              // Initialize chat with welcome message
              const welcomeMessage: ChatMessage = {
                id: 'welcome',
                type: 'agent',
                content: `Hi! I'm your Automation Agent. I'll help you configure the "${workflow.name}" workflow by asking you questions in natural language. 

This workflow has ${workflow.nodes.length} nodes that need configuration. Let's start with the first one!`,
                timestamp: new Date()
              };
              
              setChatMessages([welcomeMessage]);
              startNodeConfiguration(workflow.nodes, 0);
            }
          } else {
            console.error('Failed to load workflow from API');
            setIsSearchMode(true);
          }
        } else if (workflowParam) {
          // Direct workflow loading (existing functionality)
          const decodedData = JSON.parse(decodeURIComponent(workflowParam));
          setWorkflowData(decodedData);
          setIsSearchMode(false);
          
          // Initialize chat with welcome message
          const welcomeMessage: ChatMessage = {
            id: 'welcome',
            type: 'agent',
            content: `Hi! I'm your Automation Agent. I'll help you configure the "${decodedData.name}" workflow by asking you questions in natural language. 

This workflow has ${decodedData.nodes.length} nodes that need configuration. Let's start with the first one!`,
            timestamp: new Date()
          };
          
          setChatMessages([welcomeMessage]);
          startNodeConfiguration(decodedData.nodes, 0);
        } else {
          // No workflow provided - start in search mode
          setIsSearchMode(true);
          const searchWelcomeMessage: ChatMessage = {
            id: 'search-welcome',
            type: 'agent',
            content: `🤖 Hi! I'm your AI Automation Agent. 

I can help you in two ways:
1. **Search existing workflows**: Tell me what you want to automate, and I'll find relevant workflows from our 2000+ templates
2. **Create custom workflows**: If no existing workflow fits, I'll help you build one from scratch

What would you like to automate today?`,
            timestamp: new Date()
          };
          setChatMessages([searchWelcomeMessage]);
        }
      } catch (error) {
        console.error('Error loading workflow data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadWorkflowData();
  }, [searchParams]);

  const startNodeConfiguration = (nodes: WorkflowNode[], nodeIndex: number) => {
    if (nodeIndex >= nodes.length) {
      // All nodes configured
      const completionMessage: ChatMessage = {
        id: `completion-${Date.now()}`,
        type: 'agent',
        content: `🎉 Great! We've configured all ${nodes.length} nodes in your workflow. You can now review the configuration, save it, or run the workflow.`,
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, completionMessage]);
      return;
    }

    const currentNode = nodes[nodeIndex];
    const nodeMessage: ChatMessage = {
      id: `node-${nodeIndex}`,
      type: 'agent',
      content: `Let's configure Node ${nodeIndex + 1}: "${currentNode.name}" (Type: ${currentNode.type})

What parameters would you like to set for this node? You can describe what you want this node to do in plain English, and I'll help you configure the right parameters.

For example, if this is an HTTP node, you might say: "I want to call the GitHub API to get user information" or "Send a POST request to my webhook URL with form data".`,
      timestamp: new Date(),
      nodeId: currentNode.id
    };
    
    setChatMessages(prev => [...prev, nodeMessage]);
  };

  const processUserInput = async (input: string) => {
    if (!input.trim()) return;

    setIsProcessing(true);
    
    // Add user message
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: input,
      timestamp: new Date()
    };
    setChatMessages(prev => [...prev, userMessage]);

    try {
      if (isSearchMode) {
        // Check if user wants to create an agent from search results
        const createAgentMatch = input.toLowerCase().match(/create agent (\d+)/);
        if (createAgentMatch && searchResults.length > 0) {
          const workflowIndex = parseInt(createAgentMatch[1]) - 1;
          if (workflowIndex >= 0 && workflowIndex < searchResults.length) {
            await createAgentFromWorkflow(searchResults[workflowIndex]);
            return;
          } else {
            const errorMessage: ChatMessage = {
              id: `invalid-index-${Date.now()}`,
              type: 'agent',
              content: `Please specify a valid workflow number (1-${searchResults.length}).`,
              timestamp: new Date()
            };
            setChatMessages(prev => [...prev, errorMessage]);
            return;
          }
        }

        // Check if user is selecting a workflow by number
        const workflowMatch = input.match(/^\d+$/);
        if (workflowMatch && searchResults.length > 0) {
          const workflowIndex = parseInt(workflowMatch[0]) - 1;
          if (workflowIndex >= 0 && workflowIndex < searchResults.length) {
            const selectedWorkflow = searchResults[workflowIndex];
            const confirmMessage: ChatMessage = {
              id: `workflow-selected-${Date.now()}`,
              type: 'agent',
              content: `Great choice! You selected **${selectedWorkflow.name}**. 

${selectedWorkflow.explanation}

What would you like to do:
1. **Configure this workflow** - I'll help you set it up step by step
2. **Create a specialized agent** - Get a dedicated AI assistant for this workflow
3. **Learn more** - Get detailed information about this automation

Type your choice or ask me any questions about this workflow!`,
              timestamp: new Date()
            };
            setChatMessages(prev => [...prev, confirmMessage]);
            return;
          }
        }

        // Default: search for workflows
        await searchWorkflows(input);
      } else if (workflowData) {
        // Configure existing workflow
        await configureWorkflowNode(input);
      }
    } catch (error) {
      console.error('Error processing input:', error);
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        type: 'agent',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const createAgentFromWorkflow = async (workflow: WorkflowSearchResult) => {
    try {
      setIsProcessing(true);
      
      // Extract meaningful information from the workflow for agent creation
      const agentName = `${workflow.name} Assistant`;
      const agentRole = `Automation specialist for ${workflow.name.toLowerCase()}`;
      const agentPersonality = {
        traits: ['helpful', 'efficient', 'detail-oriented'],
        communication_style: 'professional and clear',
        expertise: workflow.description || `Expert in ${workflow.name} automation`
      };
      const agentExpectations = `Specializes in ${workflow.name} workflows. Can help users configure, customize, and troubleshoot this specific automation. Always provides step-by-step guidance and best practices.`;

      // Call the agent creation API
      const response = await fetch('/api/agents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: agentName,
          role: agentRole,
          personality: agentPersonality,
          expectations: agentExpectations,
          operation_mode: 'workflow_specialist',
          workflow_template: workflow,
          trigger_config: {
            type: 'workflow_based',
            workflow_id: workflow.filename,
            auto_suggestions: true
          }
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create agent');
      }

      const agentData = await response.json();
      
      const successMessage: ChatMessage = {
        id: `agent-created-${Date.now()}`,
        type: 'agent',
        content: `🎉 Perfect! I've created a specialized agent "${agentName}" for you! This agent is now available in your Agent Station and can help you with:

📋 **Workflow Configuration**: Step-by-step setup guidance
🔧 **Customization**: Tailoring the workflow to your specific needs  
🚀 **Automation**: Running and monitoring your ${workflow.name}
💡 **Best Practices**: Industry-standard recommendations

**Next Steps:**
• Visit [Agent Station](/dashboard/agents) to see your new agent
• Start configuring the ${workflow.name} workflow
• Get specialized help from your dedicated agent

Would you like to begin configuring this workflow now, or explore more automation options?`,
        timestamp: new Date(),
      };

      setChatMessages(prev => [...prev, successMessage]);
      
    } catch (error) {
      console.error('Error creating agent:', error);
      const errorMessage: ChatMessage = {
        id: `agent-error-${Date.now()}`,
        type: 'agent',
        content: `I encountered an error while creating your specialized agent. Please try again or contact support if the issue persists.`,
        timestamp: new Date(),
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const searchWorkflows = async (query: string) => {
    setIsSearching(true);
    
    try {
      const response = await fetch('/api/automation/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          limit: 5
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to search workflows');
      }

      const searchResponse: SearchResponse = await response.json();
      setSearchResults(searchResponse.results);

      let responseMessage = searchResponse.aiExplanation;

      if (searchResponse.results.length > 0) {
        responseMessage += '\n\n🔍 **Found workflows:**\n';
        searchResponse.results.forEach((result, index) => {
          responseMessage += `\n${index + 1}. **${result.name}** (${result.relevanceScore}% match)\n`;
          responseMessage += `   ${result.explanation}\n`;
        });
        responseMessage += '\n\n💬 **Choose an option:**\n';
        responseMessage += '• Reply with a workflow number to **configure it**\n';
        responseMessage += '• Type "create agent [number]" to **create a specialized agent** for that workflow\n';
        responseMessage += '• Ask me to create a custom workflow instead';
      } else {
        responseMessage += '\n\n🛠️ Would you like me to help you create a custom workflow for this automation?';
      }

      const aiMessage: ChatMessage = {
        id: `search-${Date.now()}`,
        type: 'agent',
        content: responseMessage,
        timestamp: new Date()
      };
      
      setChatMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      console.error('Error searching workflows:', error);
      const errorMessage: ChatMessage = {
        id: `search-error-${Date.now()}`,
        type: 'agent',
        content: 'I had trouble searching for workflows. Would you like me to help you create a custom workflow instead?',
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsSearching(false);
    }
  };

  const configureWorkflowNode = async (input: string) => {
    const currentNode = workflowData!.nodes[currentNodeIndex];
    
    // Call the enhanced AI API
    const response = await fetch('/api/automation/agent', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        userInput: input,
        nodeType: currentNode.type,
        nodeName: currentNode.name,
        currentParameters: currentNode.parameters || {},
        context: `Workflow: ${workflowData!.name}, Node ${currentNodeIndex + 1} of ${workflowData!.nodes.length}`
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to process with AI');
    }

    const aiResponse: AIResponse = await response.json();
    
    let aiContent = aiResponse.explanation;
    
    // Add follow-up questions if needed
    if (aiResponse.needsMoreInfo && aiResponse.followUpQuestions && aiResponse.followUpQuestions.length > 0) {
      aiContent += '\n\n📝 I need some additional information:\n';
      aiResponse.followUpQuestions.forEach((question: string, index: number) => {
        aiContent += `${index + 1}. ${question}\n`;
      });
      aiContent += '\nPlease provide these details to complete the configuration.';
    } else {
      aiContent += '\n\n✅ Moving to the next node...';
    }

    const aiMessage: ChatMessage = {
      id: `ai-${Date.now()}`,
      type: 'agent',
      content: aiContent,
      timestamp: new Date(),
      nodeId: currentNode.id,
      suggestedValue: aiResponse.suggestedParameters
    };
    
    setChatMessages(prev => [...prev, aiMessage]);

    // Update completed parameters
    if (aiResponse.suggestedParameters) {
      setCompletedParameters(prev => ({
        ...prev,
        [currentNode.id]: {
          ...prev[currentNode.id],
          ...aiResponse.suggestedParameters
        }
      }));

      // Move to next node if we don't need more info
      if (!aiResponse.needsMoreInfo) {
        setTimeout(() => {
          const nextIndex = currentNodeIndex + 1;
          setCurrentNodeIndex(nextIndex);
          startNodeConfiguration(workflowData!.nodes, nextIndex);
        }, 2000);
      }
    }
  };

  const handleSelectWorkflow = async (workflowIndex: number) => {
    if (workflowIndex < 0 || workflowIndex >= searchResults.length) return;

    const selected = searchResults[workflowIndex];
    setSelectedWorkflow(selected);

    // Ask for confirmation
    const confirmMessage: ChatMessage = {
      id: `confirm-${Date.now()}`,
      type: 'agent',
      content: `Great choice! 🎯

**${selected.name}**
${selected.description}

This workflow has ${selected.nodes.length} nodes and is ${selected.relevanceScore}% relevant to your request.

${selected.explanation}

Would you like to:
1. **Use this workflow** - I'll help you configure the parameters
2. **See more details** - Show me what each step does
3. **Keep searching** - Look for other workflows

Just reply with 1, 2, or 3!`,
      timestamp: new Date()
    };
    
    setChatMessages(prev => [...prev, confirmMessage]);
  };

  const handleConfirmWorkflow = async () => {
    if (!selectedWorkflow) return;

    try {
      // Load the full workflow data
      const response = await fetch(`/api/automation/workflows/${selectedWorkflow.filename}`);
      if (!response.ok) {
        throw new Error('Failed to load workflow');
      }

      const fullWorkflowData: any = await response.json();
      
      setWorkflowData({
        id: fullWorkflowData.id || 'selected',
        name: fullWorkflowData.name || selectedWorkflow.name,
        description: selectedWorkflow.description,
        nodes: fullWorkflowData.nodes || selectedWorkflow.nodes,
        filename: selectedWorkflow.filename
      });

      setIsSearchMode(false);
      setCurrentNodeIndex(0);
      setCompletedParameters({});

      const startMessage: ChatMessage = {
        id: `start-${Date.now()}`,
        type: 'agent',
        content: `Perfect! Let's configure "${selectedWorkflow.name}" step by step.

This workflow has ${fullWorkflowData.nodes?.length || 0} nodes. I'll guide you through each one using natural language. 

Let's start with the first node! 🚀`,
        timestamp: new Date()
      };
      
      setChatMessages(prev => [...prev, startMessage]);
      
      // Start configuring the first node
      setTimeout(() => {
        startNodeConfiguration(fullWorkflowData.nodes || [], 0);
      }, 1000);

    } catch (error) {
      console.error('Error loading workflow:', error);
      const errorMessage: ChatMessage = {
        id: `load-error-${Date.now()}`,
        type: 'agent',
        content: 'Sorry, I had trouble loading that workflow. Would you like to try a different one?',
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleUserMessage = (input: string) => {
    const trimmedInput = input.trim().toLowerCase();

    // Handle workflow selection
    if (isSearchMode && searchResults.length > 0) {
      // Check for numeric selection
      const selectedIndex = parseInt(trimmedInput) - 1;
      if (!isNaN(selectedIndex) && selectedIndex >= 0 && selectedIndex < searchResults.length) {
        handleSelectWorkflow(selectedIndex);
        return;
      }

      // Check for confirmation
      if (selectedWorkflow) {
        if (trimmedInput === '1' || trimmedInput.includes('use')) {
          handleConfirmWorkflow();
          return;
        } else if (trimmedInput === '2' || trimmedInput.includes('details')) {
          const detailsMessage: ChatMessage = {
            id: `details-${Date.now()}`,
            type: 'agent',
            content: `📋 **Workflow Details: ${selectedWorkflow.name}**

**Description:** ${selectedWorkflow.description}

**Steps (${selectedWorkflow.nodes.length} nodes):**
${selectedWorkflow.nodes.map((node, index) => 
  `${index + 1}. ${node.name || 'Unnamed'} (${(node.type || '').replace('n8n-nodes-base.', '')})`
).join('\n')}

Would you like to use this workflow? Reply with "yes" to proceed!`,
            timestamp: new Date()
          };
          setChatMessages(prev => [...prev, detailsMessage]);
          return;
        } else if (trimmedInput === '3' || trimmedInput.includes('search')) {
          setSelectedWorkflow(null);
          setSearchResults([]);
          const searchAgainMessage: ChatMessage = {
            id: `search-again-${Date.now()}`,
            type: 'agent',
            content: 'No problem! What else would you like to automate? Describe it in your own words.',
            timestamp: new Date()
          };
          setChatMessages(prev => [...prev, searchAgainMessage]);
          return;
        } else if (trimmedInput.includes('yes') || trimmedInput.includes('proceed')) {
          handleConfirmWorkflow();
          return;
        }
      }
    }

    // Process the input normally
    processUserInput(input);
  };

  const generateAIResponse = (userInput: string, node: WorkflowNode) => {
    // Simple AI simulation - in real implementation, use OpenAI/Claude API
    const input = userInput.toLowerCase();
    
    // Basic parameter extraction based on node type and user input
    let suggestedParameters: Record<string, any> = {};
    let content = '';

    switch (node.type) {
      case 'n8n-nodes-base.httpRequest':
      case 'n8n-nodes-base.webhook':
        if (input.includes('get') || input.includes('fetch')) {
          suggestedParameters = { method: 'GET' };
        } else if (input.includes('post') || input.includes('send')) {
          suggestedParameters = { method: 'POST' };
        }
        
        // Extract URLs
        const urlMatch = input.match(/https?:\/\/[^\s]+/);
        if (urlMatch) {
          suggestedParameters.url = urlMatch[0];
        }
        
        content = `Perfect! I've configured this HTTP Request node with:\n- Method: ${suggestedParameters.method || 'GET'}\n- URL: ${suggestedParameters.url || 'Please provide the URL'}\n\nMoving to the next node...`;
        break;

      case 'n8n-nodes-base.gmail':
      case 'n8n-nodes-base.email':
        if (input.includes('@')) {
          const emailMatch = input.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/);
          if (emailMatch) {
            suggestedParameters.to = emailMatch[0];
          }
        }
        
        if (input.includes('subject:')) {
          const subjectMatch = input.match(/subject:\s*(.+?)(\n|$)/i);
          if (subjectMatch) {
            suggestedParameters.subject = subjectMatch[1].trim();
          }
        }
        
        content = `Great! I've configured this email node with:\n- To: ${suggestedParameters.to || 'Please specify recipient'}\n- Subject: ${suggestedParameters.subject || 'Automated email'}\n\nMoving to the next node...`;
        break;

      case 'n8n-nodes-base.set':
      case 'n8n-nodes-base.function':
        content = `I understand you want to process data with this node. I've set up basic data transformation parameters. Moving to the next node...`;
        suggestedParameters = { mode: 'set', values: {} };
        break;

      default:
        content = `I've configured the basic parameters for this ${node.type} node based on your description. Moving to the next node...`;
        suggestedParameters = { configured: true };
    }

    return { content, suggestedParameters };
  };

  const handleSendMessage = () => {
    if (userInput.trim()) {
      handleUserMessage(userInput);
      setUserInput('');
    }
  };

  const handleSaveWorkflow = () => {
    const updatedWorkflow = {
      ...workflowData,
      nodes: workflowData!.nodes.map(node => ({
        ...node,
        parameters: {
          ...node.parameters,
          ...completedParameters[node.id]
        }
      }))
    };
    
    console.log('Saving configured workflow:', updatedWorkflow);
    alert('Workflow configuration saved successfully!');
  };

  const handleRunWorkflow = () => {
    alert('Workflow execution started! (This is a simulation)');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!workflowData) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle>No Workflow Data</CardTitle>
            <CardDescription>No workflow data was provided.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => window.history.back()}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Go Back
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => window.history.back()}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-foreground">
                  AI Workflow Agent
                </h1>
                <p className="text-muted-foreground">
                  {isSearchMode 
                    ? 'Searching 2000+ workflows...' 
                    : `Configuring: ${workflowData?.name || 'Workflow'}`
                  }
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {!isSearchMode && workflowData && (
                <>
                  <Badge variant="secondary">
                    {currentNodeIndex}/{workflowData.nodes.length} nodes
                  </Badge>
                  <Button onClick={handleSaveWorkflow} variant="secondary" size="sm">
                    <Save className="h-4 w-4 mr-2" />
                    Save
                  </Button>
                  <Button onClick={handleRunWorkflow} size="sm">
                    <Play className="h-4 w-4 mr-2" />
                    Run
                  </Button>
                </>
              )}
              {isSearchMode && (
                <Badge variant="secondary">
                  Search Mode
                </Badge>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chat Interface */}
          <div className="lg:col-span-2">
            <Card className="h-[600px] flex flex-col">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bot className="h-5 w-5" />
                  AI Assistant
                </CardTitle>
                <CardDescription>
                  I&apos;ll help you configure your workflow parameters through natural conversation
                </CardDescription>
              </CardHeader>
              
              <CardContent className="flex-1 flex flex-col">
                {/* Messages */}
                <div className="flex-1 overflow-y-auto space-y-4 mb-4">
                  {chatMessages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${
                        message.type === 'user' ? 'justify-end' : 'justify-start'
                      }`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg p-3 ${
                          message.type === 'user'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted text-foreground'
                        }`}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          {message.type === 'user' ? (
                            <User className="h-4 w-4" />
                          ) : (
                            <Bot className="h-4 w-4" />
                          )}
                          <span className="text-xs opacity-75">
                            {message.timestamp.toLocaleTimeString()}
                          </span>
                        </div>
                        <div className="whitespace-pre-wrap">{message.content}</div>
                      </div>
                    </div>
                  ))}
                  
                  {isProcessing && (
                    <div className="flex gap-3 justify-start">
                      <div className="bg-muted rounded-lg p-3">
                        <div className="flex items-center gap-2">
                          <Bot className="h-4 w-4" />
                          <div className="flex gap-1">
                            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Input */}
                <div className="flex gap-2">
                  <Input
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    placeholder="Describe what you want this node to do..."
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    disabled={isProcessing || isSearching}
                  />
                  <Button 
                    onClick={handleSendMessage}
                    disabled={isProcessing || isSearching || !userInput.trim()}
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Workflow Overview or Search Results */}
          <div className="space-y-4">
            {isSearchMode ? (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="h-5 w-5" />
                    Search Mode
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-sm text-muted-foreground mb-4">
                    I&apos;m ready to help you find the perfect workflow from our 2000+ templates, or create a custom one.
                  </div>
                  
                  {searchResults.length > 0 && (
                    <div className="space-y-3">
                      <h4 className="font-medium">Found Workflows:</h4>
                      {searchResults.map((result, index) => (
                        <div
                          key={result.filename}
                          className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                            selectedWorkflow?.filename === result.filename
                              ? 'bg-primary/10 border-primary/20'
                              : 'bg-muted border-border hover:bg-muted/80'
                          }`}
                          onClick={() => handleSelectWorkflow(index)}
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <h5 className="font-medium text-sm text-foreground">{result.name}</h5>
                              <p className="text-xs text-muted-foreground">{result.nodes.length} nodes</p>
                            </div>
                            <Badge variant="secondary">
                              {result.relevanceScore}% match
                            </Badge>
                          </div>
                          <p className="text-xs text-muted-foreground mt-2">{result.explanation}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            ) : workflowData ? (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="h-5 w-5" />
                    Workflow Progress
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {workflowData.nodes.map((node, index) => (
                      <div
                        key={node.id}
                        className={`p-3 rounded-lg border ${
                          index < currentNodeIndex
                            ? 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800'
                            : index === currentNodeIndex
                            ? 'bg-primary/10 border-primary/20'
                            : 'bg-muted border-border'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-medium text-sm text-foreground">{node.name}</h4>
                            <p className="text-xs text-muted-foreground">{node.type}</p>
                          </div>
                          <Badge
                            variant={
                              index < currentNodeIndex
                                ? 'default'
                                : index === currentNodeIndex
                                ? 'secondary'
                                : 'secondary'
                            }
                          >
                            {index < currentNodeIndex
                              ? '✓'
                              : index === currentNodeIndex
                              ? '⚡'
                              : '⏳'}
                          </Badge>
                        </div>
                        
                        {completedParameters[node.id] && (
                          <div className="mt-2 text-xs">
                            <div className="text-green-600 dark:text-green-400">
                              Configured parameters:
                            </div>
                            <div className="text-muted-foreground">
                              {Object.keys(completedParameters[node.id]).join(', ')}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ) : null}

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {isSearchMode ? (
                  <>
                    <Button 
                      variant="secondary" 
                      className="w-full"
                      onClick={() => {
                        const examples = [
                          "Send automatic email notifications when someone fills a form",
                          "Sync data between Google Sheets and a database",
                          "Post to social media when a new blog post is published",
                          "Create calendar events from Slack messages",
                          "Send SMS alerts for critical system errors"
                        ];
                        setUserInput(examples[Math.floor(Math.random() * examples.length)]);
                      }}
                    >
                      Suggest Search Example
                    </Button>
                    <Button 
                      variant="secondary" 
                      className="w-full"
                      onClick={() => {
                        setUserInput("I want to create a custom workflow for my specific needs");
                      }}
                    >
                      Create Custom Workflow
                    </Button>
                  </>
                ) : workflowData ? (
                  <>
                    <Button 
                      variant="secondary" 
                      className="w-full"
                      onClick={() => {
                        const examples = [
                          "Send a GET request to https://api.github.com/user",
                          "Send an email to admin@example.com with subject 'Alert'",
                          "Set variable 'status' to 'completed'",
                          "Process the incoming data and extract email field"
                        ];
                        setUserInput(examples[Math.floor(Math.random() * examples.length)]);
                      }}
                    >
                      Suggest Example
                    </Button>
                    <Button 
                      variant="secondary" 
                      className="w-full"
                      onClick={() => {
                        if (currentNodeIndex < workflowData.nodes.length) {
                          const nextIndex = currentNodeIndex + 1;
                          setCurrentNodeIndex(nextIndex);
                          startNodeConfiguration(workflowData.nodes, nextIndex);
                        }
                      }}
                      disabled={currentNodeIndex >= workflowData.nodes.length}
                    >
                      Skip Node
                    </Button>
                  </>
                ) : null}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
