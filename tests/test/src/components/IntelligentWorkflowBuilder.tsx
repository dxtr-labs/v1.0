'use client';

import { useState, useEffect, useCallback } from 'react';
import { Search, Play, Settings, AlertCircle, CheckCircle, Zap, Bot } from 'lucide-react';

interface WorkflowParameter {
  name: string;
  type: 'text' | 'email' | 'number' | 'select' | 'password' | 'url';
  required: boolean;
  description: string;
  options?: string[];
  placeholder?: string;
  keywords: string[];
}

interface WorkflowMatch {
  id: string;
  name: string;
  description: string;
  confidence: number;
  parameters: WorkflowParameter[];
  category: string;
  tags: string[];
  extractedParameters?: { [key: string]: string };
  explanation?: string;
}

interface ParameterValues {
  [key: string]: string;
}

export default function IntelligentWorkflowBuilder() {
  const [userInput, setUserInput] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [workflowMatches, setWorkflowMatches] = useState<WorkflowMatch[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowMatch | null>(null);
  const [parameterValues, setParameterValues] = useState<ParameterValues>({});
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<string | null>(null);

  // Predefined workflows with parameters and keywords
  const predefinedWorkflows: WorkflowMatch[] = [
    {
      id: 'email-automation',
      name: 'Send Email with Attachment',
      description: 'Send professional emails with optional attachments using Gmail or Outlook',
      confidence: 0.95,
      category: 'Communication',
      tags: ['email', 'gmail', 'outlook', 'communication', 'send', 'message', 'mail'],
      parameters: [
        {
          name: 'recipient',
          type: 'email',
          required: true,
          description: 'Email address of the recipient',
          placeholder: 'user@example.com',
          keywords: ['to', 'recipient', 'send to', 'email address', 'target', '@']
        },
        {
          name: 'subject',
          type: 'text',
          required: true,
          description: 'Email subject line',
          placeholder: 'Meeting Request',
          keywords: ['subject', 'title', 'about', 'regarding', 'topic', 're:']
        },
        {
          name: 'message',
          type: 'text',
          required: true,
          description: 'Email body content',
          placeholder: 'Your message here...',
          keywords: ['message', 'body', 'content', 'text', 'email body', 'write']
        },
        {
          name: 'priority',
          type: 'select',
          required: false,
          description: 'Email priority level',
          options: ['Low', 'Normal', 'High', 'Urgent'],
          keywords: ['priority', 'importance', 'urgent', 'level', 'high', 'low']
        }
      ]
    },
    {
      id: 'social-media-post',
      name: 'Create Social Media Post',
      description: 'Post content to Twitter, LinkedIn, Instagram, or Facebook',
      confidence: 0.90,
      category: 'Social Media',
      tags: ['twitter', 'linkedin', 'instagram', 'facebook', 'post', 'social', 'content', 'share'],
      parameters: [
        {
          name: 'platform',
          type: 'select',
          required: true,
          description: 'Social media platform',
          options: ['Twitter', 'LinkedIn', 'Instagram', 'Facebook'],
          keywords: ['platform', 'social media', 'where', 'post to', 'channel', 'twitter', 'linkedin', 'instagram', 'facebook']
        },
        {
          name: 'content',
          type: 'text',
          required: true,
          description: 'Post content',
          placeholder: 'Your post content...',
          keywords: ['content', 'post', 'message', 'text', 'caption', 'write', 'share']
        },
        {
          name: 'hashtags',
          type: 'text',
          required: false,
          description: 'Hashtags (comma-separated)',
          placeholder: '#automation, #productivity',
          keywords: ['hashtags', 'tags', 'keywords', 'labels', '#']
        },
        {
          name: 'schedule',
          type: 'text',
          required: false,
          description: 'Schedule time (optional)',
          placeholder: '2024-01-01 10:00',
          keywords: ['schedule', 'time', 'when', 'post at', 'timing', 'later']
        }
      ]
    },
    {
      id: 'task-creation',
      name: 'Create Task in Project Manager',
      description: 'Create tasks in Asana, Trello, Jira, or other project management tools',
      confidence: 0.88,
      category: 'Productivity',
      tags: ['asana', 'trello', 'jira', 'task', 'project', 'management', 'todo', 'create'],
      parameters: [
        {
          name: 'platform',
          type: 'select',
          required: true,
          description: 'Project management platform',
          options: ['Asana', 'Trello', 'Jira', 'Monday.com', 'Notion'],
          keywords: ['platform', 'tool', 'project manager', 'where', 'system', 'asana', 'trello', 'jira']
        },
        {
          name: 'title',
          type: 'text',
          required: true,
          description: 'Task title',
          placeholder: 'Fix login bug',
          keywords: ['title', 'task', 'name', 'what', 'task name', 'create']
        },
        {
          name: 'description',
          type: 'text',
          required: false,
          description: 'Task description',
          placeholder: 'Detailed task description...',
          keywords: ['description', 'details', 'explain', 'about', 'notes']
        },
        {
          name: 'priority',
          type: 'select',
          required: false,
          description: 'Task priority',
          options: ['Low', 'Medium', 'High', 'Critical'],
          keywords: ['priority', 'importance', 'urgent', 'level', 'high', 'medium', 'low', 'critical']
        },
        {
          name: 'assignee',
          type: 'text',
          required: false,
          description: 'Task assignee',
          placeholder: 'team@company.com',
          keywords: ['assignee', 'assign to', 'responsible', 'owner', 'who', 'assigned']
        },
        {
          name: 'dueDate',
          type: 'text',
          required: false,
          description: 'Due date',
          placeholder: '2024-01-15',
          keywords: ['due date', 'deadline', 'when', 'completion date', 'due']
        }
      ]
    },
    {
      id: 'calendly-meeting',
      name: 'Schedule Meeting with Calendly',
      description: 'Create and send Calendly meeting invitation',
      confidence: 0.92,
      category: 'Scheduling',
      tags: ['calendly', 'meeting', 'schedule', 'appointment', 'calendar', 'book'],
      parameters: [
        {
          name: 'recipient',
          type: 'email',
          required: true,
          description: 'Meeting participant email',
          placeholder: 'client@company.com',
          keywords: ['to', 'recipient', 'participant', 'attendee', 'client', 'with', '@']
        },
        {
          name: 'meetingType',
          type: 'select',
          required: true,
          description: 'Meeting type',
          options: ['15-minute call', '30-minute meeting', '60-minute consultation', 'Custom'],
          keywords: ['type', 'duration', 'meeting type', 'length', 'kind', 'minutes', 'call', 'consultation']
        },
        {
          name: 'subject',
          type: 'text',
          required: true,
          description: 'Meeting subject',
          placeholder: 'Project Discussion',
          keywords: ['subject', 'topic', 'about', 'meeting topic', 'agenda', 'discussion']
        },
        {
          name: 'message',
          type: 'text',
          required: false,
          description: 'Personal message',
          placeholder: 'Looking forward to discussing...',
          keywords: ['message', 'note', 'personal message', 'additional info']
        }
      ]
    },
    {
      id: 'data-processing',
      name: 'Process Data File',
      description: 'Process CSV, JSON, Excel files with transformations and analysis',
      confidence: 0.85,
      category: 'Data Processing',
      tags: ['csv', 'json', 'excel', 'data', 'processing', 'transform', 'analyze', 'file'],
      parameters: [
        {
          name: 'fileType',
          type: 'select',
          required: true,
          description: 'File type to process',
          options: ['CSV', 'JSON', 'Excel', 'PDF'],
          keywords: ['file type', 'format', 'data type', 'extension', 'csv', 'json', 'excel', 'pdf']
        },
        {
          name: 'sourceUrl',
          type: 'url',
          required: true,
          description: 'Source file URL or path',
          placeholder: 'https://example.com/data.csv',
          keywords: ['source', 'file', 'url', 'path', 'location', 'input', 'from']
        },
        {
          name: 'operation',
          type: 'select',
          required: true,
          description: 'Processing operation',
          options: ['Filter', 'Transform', 'Merge', 'Split', 'Validate', 'Analyze'],
          keywords: ['operation', 'action', 'process', 'transform', 'what to do', 'filter', 'merge', 'split']
        },
        {
          name: 'outputFormat',
          type: 'select',
          required: false,
          description: 'Output format',
          options: ['CSV', 'JSON', 'Excel', 'PDF'],
          keywords: ['output', 'format', 'export', 'save as', 'result', 'to']
        }
      ]
    },
    {
      id: 'webhook-trigger',
      name: 'Setup Webhook Trigger',
      description: 'Create webhook endpoints for external integrations and notifications',
      confidence: 0.80,
      category: 'Integration',
      tags: ['webhook', 'trigger', 'api', 'integration', 'endpoint', 'notification'],
      parameters: [
        {
          name: 'webhookUrl',
          type: 'url',
          required: true,
          description: 'Webhook endpoint URL',
          placeholder: 'https://api.example.com/webhook',
          keywords: ['webhook', 'url', 'endpoint', 'callback', 'trigger url', 'api']
        },
        {
          name: 'method',
          type: 'select',
          required: true,
          description: 'HTTP method',
          options: ['GET', 'POST', 'PUT', 'DELETE'],
          keywords: ['method', 'http method', 'request type', 'verb', 'get', 'post', 'put', 'delete']
        },
        {
          name: 'headers',
          type: 'text',
          required: false,
          description: 'Custom headers (JSON format)',
          placeholder: '{"Authorization": "Bearer token"}',
          keywords: ['headers', 'authentication', 'auth', 'custom headers', 'token']
        },
        {
          name: 'payload',
          type: 'text',
          required: false,
          description: 'Request payload template',
          placeholder: '{"event": "user_signup", "data": "{{data}}"}',
          keywords: ['payload', 'body', 'data', 'request body', 'content', 'json']
        }
      ]
    }
  ];

  // Intelligent workflow matching using keywords and LLM
  const analyzeUserInput = useCallback(async (input: string) => {
    setIsAnalyzing(true);
    
    try {
      // Keyword-based matching
      const keywordMatches = predefinedWorkflows.map(workflow => {
        const inputLower = input.toLowerCase();
        const keywordScore = workflow.tags.reduce((score, tag) => {
          return inputLower.includes(tag.toLowerCase()) ? score + 1 : score;
        }, 0);
        
        const parameterScore = workflow.parameters.reduce((score, param) => {
          const paramKeywordScore = param.keywords.reduce((pScore, keyword) => {
            return inputLower.includes(keyword.toLowerCase()) ? pScore + 1 : pScore;
          }, 0);
          return score + paramKeywordScore;
        }, 0);
        
        const totalScore = keywordScore + parameterScore;
        const confidence = Math.min(totalScore / 10, 1); // Normalize to 0-1
        
        return {
          ...workflow,
          confidence: confidence
        };
      });

      // Sort by confidence and filter meaningful matches
      const sortedMatches = keywordMatches
        .filter(match => match.confidence > 0.1)
        .sort((a, b) => b.confidence - a.confidence)
        .slice(0, 5); // Top 5 matches

      // Enhanced matching with LLM (fallback to keyword matching if LLM fails)
      try {
        const enhancedMatches = await enhanceMatchesWithLLM(input, sortedMatches);
        setWorkflowMatches(enhancedMatches);
        
        // Auto-select the best match if confidence is high
        if (enhancedMatches.length > 0 && enhancedMatches[0].confidence > 0.7) {
          setSelectedWorkflow(enhancedMatches[0]);
          extractParametersFromInput(input, enhancedMatches[0]);
        }
      } catch (error) {
        console.error('LLM enhancement failed, using keyword matching:', error);
        setWorkflowMatches(sortedMatches);
        
        if (sortedMatches.length > 0 && sortedMatches[0].confidence > 0.5) {
          setSelectedWorkflow(sortedMatches[0]);
          extractParametersFromInput(input, sortedMatches[0]);
        }
      }
    } catch (error) {
      console.error('Error analyzing user input:', error);
    } finally {
      setIsAnalyzing(false);
    }
  }, [predefinedWorkflows]);

  // Enhanced LLM matching
  const enhanceMatchesWithLLM = async (input: string, matches: WorkflowMatch[]) => {
    const response = await fetch('/api/mcp/llm/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        userInput: input,
        candidateWorkflows: matches.map(m => ({
          id: m.id,
          name: m.name,
          description: m.description,
          tags: m.tags,
          parameters: m.parameters.map(p => ({
            name: p.name,
            description: p.description,
            keywords: p.keywords
          }))
        }))
      })
    });

    if (response.ok) {
      const result = await response.json();
      return result.enhancedMatches || matches;
    }
    
    throw new Error('LLM analysis failed');
  };

  // Extract parameters from user input using keywords
  const extractParametersFromInput = (input: string, workflow: WorkflowMatch) => {
    const inputLower = input.toLowerCase();
    const extractedParams: ParameterValues = {};

    workflow.parameters.forEach(param => {
      param.keywords.forEach(keyword => {
        const keywordIndex = inputLower.indexOf(keyword.toLowerCase());
        if (keywordIndex !== -1) {
          // Extract value after keyword
          const afterKeyword = input.substring(keywordIndex + keyword.length).trim();
          const words = afterKeyword.split(/\s+/);
          
          if (param.type === 'email') {
            const emailMatch = afterKeyword.match(/[\w.-]+@[\w.-]+\.\w+/);
            if (emailMatch) {
              extractedParams[param.name] = emailMatch[0];
            }
          } else if (param.type === 'url') {
            const urlMatch = afterKeyword.match(/https?:\/\/[^\s]+/);
            if (urlMatch) {
              extractedParams[param.name] = urlMatch[0];
            }
          } else if (param.type === 'select' && param.options) {
            const option = param.options.find(opt => 
              inputLower.includes(opt.toLowerCase())
            );
            if (option) {
              extractedParams[param.name] = option;
            }
          } else if (param.type === 'text') {
            // Extract quoted text or next few words
            const quotedMatch = afterKeyword.match(/"([^"]+)"/);
            if (quotedMatch) {
              extractedParams[param.name] = quotedMatch[1];
            } else if (words.length > 0 && words[0].length > 1) {
              extractedParams[param.name] = words.slice(0, 4).join(' ').replace(/[^\w\s@.-]/g, '');
            }
          }
        }
      });
    });

    // Merge with any LLM-extracted parameters
    if (workflow.extractedParameters) {
      Object.assign(extractedParams, workflow.extractedParameters);
    }

    setParameterValues(extractedParams);
  };

  // Execute the workflow
  const executeWorkflow = async () => {
    if (!selectedWorkflow) return;

    setIsExecuting(true);
    try {
      const response = await fetch('/api/workflows/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflowId: selectedWorkflow.id,
          parameters: parameterValues
        })
      });

      if (response.ok) {
        const result = await response.json();
        setExecutionResult(`✅ Workflow executed successfully! ${result.message}`);
      } else {
        setExecutionResult(`❌ Workflow execution failed: ${response.statusText}`);
      }
    } catch (error) {
      setExecutionResult(`❌ Error executing workflow: ${error}`);
    } finally {
      setIsExecuting(false);
    }
  };

  // Handle input change with debounced analysis
  useEffect(() => {
    if (userInput.trim().length > 3) {
      const timer = setTimeout(() => {
        analyzeUserInput(userInput);
      }, 500);
      return () => clearTimeout(timer);
    } else {
      setWorkflowMatches([]);
      setSelectedWorkflow(null);
      setParameterValues({});
    }
  }, [userInput, analyzeUserInput]);

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center space-x-2">
          <Bot className="h-8 w-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">Intelligent Workflow Builder</h1>
          <Zap className="h-8 w-8 text-gray-500" />
        </div>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Describe what you want to automate in natural language, and I&apos;ll find the perfect workflow for you. 
          I can extract parameters automatically and guide you through the setup.
        </p>
      </div>

      {/* Example Prompts */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg">
        <h3 className="font-medium text-gray-900 mb-2">Try these examples:</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
          <div className="cursor-pointer hover:text-blue-600" onClick={() => setUserInput('Send email to john@company.com about meeting tomorrow')}>
            💌 &quot;Send email to john@company.com about meeting tomorrow&quot;
          </div>
          <div className="cursor-pointer hover:text-blue-600" onClick={() => setUserInput('Create high priority task in Asana for bug fix')}>
            📋 &quot;Create high priority task in Asana for bug fix&quot;
          </div>
          <div className="cursor-pointer hover:text-blue-600" onClick={() => setUserInput('Post to Twitter about our new product launch')}>
            📱 &quot;Post to Twitter about our new product launch&quot;
          </div>
          <div className="cursor-pointer hover:text-blue-600" onClick={() => setUserInput('Schedule 30-minute meeting with client using Calendly')}>
            📅 &quot;Schedule 30-minute meeting with client using Calendly&quot;
          </div>
        </div>
      </div>

      {/* Input Section */}
      <div className="relative">
        <div className="relative">
          <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
          <textarea
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Describe your automation needs... (e.g., 'Send email to john@company.com about meeting tomorrow' or 'Create high priority task in Asana for bug fix')"
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows={3}
          />
        </div>
        
        {isAnalyzing && (
          <div className="absolute right-3 top-3">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
          </div>
        )}
      </div>

      {/* Workflow Matches */}
      {workflowMatches.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center space-x-2">
            <Bot className="h-5 w-5" />
            <span>Matching Workflows</span>
          </h2>
          <div className="grid gap-3">
            {workflowMatches.map((workflow) => (
              <div
                key={workflow.id}
                className={`p-4 border rounded-lg cursor-pointer transition-all ${
                  selectedWorkflow?.id === workflow.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => {
                  setSelectedWorkflow(workflow);
                  if (workflow.extractedParameters) {
                    setParameterValues(prev => ({ ...prev, ...workflow.extractedParameters }));
                  }
                }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{workflow.name}</h3>
                    <p className="text-sm text-gray-600">{workflow.description}</p>
                    {workflow.explanation && (
                      <p className="text-sm text-blue-600 mt-1">💡 {workflow.explanation}</p>
                    )}
                    <div className="flex items-center mt-2 space-x-2">
                      <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                        {workflow.category}
                      </span>
                      <span className="text-xs text-gray-500">
                        {Math.round(workflow.confidence * 100)}% match
                      </span>
                      {workflow.extractedParameters && Object.keys(workflow.extractedParameters).length > 0 && (
                        <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                          AI extracted {Object.keys(workflow.extractedParameters).length} parameters
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${
                      workflow.confidence > 0.7 ? 'bg-green-500' : 
                      workflow.confidence > 0.4 ? 'bg-gray-500' : 'bg-gray-400'
                    }`}></div>
                    <Settings className="h-4 w-4 text-gray-400" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Parameter Collection */}
      {selectedWorkflow && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center space-x-2">
            <Settings className="h-5 w-5" />
            <span>Configure Parameters</span>
          </h2>
          <div className="bg-gray-50 p-6 rounded-lg space-y-4">
            {selectedWorkflow.parameters.map((param) => (
              <div key={param.name} className="space-y-2">
                <label className="flex items-center space-x-2">
                  <span className="font-medium text-gray-700">{param.name}</span>
                  {param.required && <span className="text-red-500">*</span>}
                  {parameterValues[param.name] && (
                    <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                      ✨ Auto-extracted
                    </span>
                  )}
                </label>
                <p className="text-sm text-gray-600">{param.description}</p>
                <p className="text-xs text-gray-500">Keywords: {param.keywords.join(', ')}</p>
                
                {param.type === 'select' && param.options ? (
                  <select
                    value={parameterValues[param.name] || ''}
                    onChange={(e) => setParameterValues(prev => ({
                      ...prev,
                      [param.name]: e.target.value
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select {param.name}</option>
                    {param.options.map(option => (
                      <option key={option} value={option}>{option}</option>
                    ))}
                  </select>
                ) : (
                  <input
                    type={param.type === 'password' ? 'password' : 'text'}
                    value={parameterValues[param.name] || ''}
                    onChange={(e) => setParameterValues(prev => ({
                      ...prev,
                      [param.name]: e.target.value
                    }))}
                    placeholder={param.placeholder}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                )}
              </div>
            ))}
            
            {/* Execute Button */}
            <div className="pt-4 flex justify-end">
              <button
                onClick={executeWorkflow}
                disabled={isExecuting || !selectedWorkflow.parameters.filter(p => p.required).every(p => parameterValues[p.name])}
                className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                <Play className="h-4 w-4" />
                <span>{isExecuting ? 'Executing...' : 'Execute Workflow'}</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Execution Result */}
      {executionResult && (
        <div className={`p-4 rounded-lg ${
          executionResult.includes('✅') ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
        }`}>
          <div className="flex items-center space-x-2">
            {executionResult.includes('✅') ? (
              <CheckCircle className="h-5 w-5" />
            ) : (
              <AlertCircle className="h-5 w-5" />
            )}
            <span>{executionResult}</span>
          </div>
        </div>
      )}
    </div>
  );
}
