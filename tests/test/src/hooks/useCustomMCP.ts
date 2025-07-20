import { useState, useCallback } from 'react';

interface CustomMCPAgent {
  agent_id: string;
  agent_name: string;
  personality: Record<string, any>;
  memory_entries: number;
  available_nodes: string[];
  llm_config: Record<string, any>;
}

interface ChatResponse {
  success: boolean;
  response_type: string;
  response: string;
  workflow_json?: Record<string, any>;
  validation?: Record<string, any>;
  action_required?: string;
  memory_updated?: boolean;
}

interface WorkflowResponse {
  status: string;
  workflow_id: string;
  trigger_id?: string;
  execution_result?: any;
}

interface TriggerInfo {
  trigger_id: string;
  workflow_id: string;
  trigger_type: string;
  trigger_config: Record<string, any>;
  last_triggered?: string;
  created_at: string;
}

const API_BASE = '/api/custom-mcp';

export const useCustomMCP = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRequest = useCallback(async <T>(
    url: string, 
    options: RequestInit = {}
  ): Promise<T> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}${url}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`Request failed: ${response.statusText}`);
      }

      const data = await response.json();
      return data as T;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Custom MCP Agent Management
  const createAgent = useCallback(async (
    agentId: string,
    agentName: string,
    llmConfig: Record<string, any>,
    personalityTraits?: Record<string, any>
  ) => {
    return handleRequest('/agents', {
      method: 'POST',
      body: JSON.stringify({
        agent_id: agentId,
        agent_name: agentName,
        llm_config: llmConfig,
        personality_traits: personalityTraits,
      }),
    });
  }, [handleRequest]);

  const getAgent = useCallback(async (agentId: string): Promise<CustomMCPAgent> => {
    const response = await handleRequest<{ agent: CustomMCPAgent }>(`/agents/${agentId}`);
    return response.agent;
  }, [handleRequest]);

  const listAgents = useCallback(async (): Promise<CustomMCPAgent[]> => {
    const response = await handleRequest<{ agents: CustomMCPAgent[] }>('/agents');
    return response.agents;
  }, [handleRequest]);

  const deleteAgent = useCallback(async (agentId: string) => {
    return handleRequest(`/agents/${agentId}`, {
      method: 'DELETE',
    });
  }, [handleRequest]);

  // Chat with Custom MCP - Code Builder AI Integration
  const chatWithAgent = useCallback(async (
    agentId: string,
    userInput: string,
    context?: Record<string, any>
  ): Promise<ChatResponse> => {
    return handleRequest(`/agents/${agentId}/chat`, {
      method: 'POST',
      body: JSON.stringify({
        agent_id: agentId,
        user_input: userInput,
        context,
      }),
    });
  }, [handleRequest]);

  // Memory Management
  const getAgentMemory = useCallback(async (agentId: string) => {
    return handleRequest(`/agents/${agentId}/memory`);
  }, [handleRequest]);

  const clearAgentMemory = useCallback(async (agentId: string) => {
    return handleRequest(`/agents/${agentId}/memory/clear`, {
      method: 'POST',
    });
  }, [handleRequest]);

  // Workflow Management - JSON Script Generation & Execution
  const createWorkflow = useCallback(async (
    agentId: string,
    workflowJson: Record<string, any>,
    triggerConfig?: Record<string, any>
  ): Promise<WorkflowResponse> => {
    return handleRequest(`/agents/${agentId}/workflows`, {
      method: 'POST',
      body: JSON.stringify({
        agent_id: agentId,
        workflow_json: workflowJson,
        trigger_config: triggerConfig,
      }),
    });
  }, [handleRequest]);

  const executeWorkflow = useCallback(async (workflowId: string): Promise<WorkflowResponse> => {
    return handleRequest(`/workflows/${workflowId}/execute`, {
      method: 'POST',
    });
  }, [handleRequest]);

  const getWorkflowHistory = useCallback(async (workflowId: string, limit = 50) => {
    return handleRequest(`/workflows/${workflowId}/history?limit=${limit}`);
  }, [handleRequest]);

  // Automation Engine - Driver-Based Execution
  const processWithAutomation = useCallback(async (
    nodeType: string,
    parameters: Record<string, any>
  ) => {
    return handleRequest('/workflows', {
      method: 'POST',
      body: JSON.stringify({
        node_type: nodeType,
        parameters,
      }),
    });
  }, [handleRequest]);

  // Trigger Management - Automated Workflow Execution
  const getAllTriggers = useCallback(async (): Promise<TriggerInfo[]> => {
    const response = await handleRequest<{ triggers: TriggerInfo[] }>('/triggers');
    return response.triggers;
  }, [handleRequest]);

  const pauseTrigger = useCallback(async (triggerId: string) => {
    return handleRequest(`/triggers/${triggerId}/pause`, {
      method: 'POST',
    });
  }, [handleRequest]);

  const resumeTrigger = useCallback(async (triggerId: string) => {
    return handleRequest(`/triggers/${triggerId}/resume`, {
      method: 'POST',
    });
  }, [handleRequest]);

  const deleteTrigger = useCallback(async (triggerId: string) => {
    return handleRequest(`/triggers/${triggerId}`, {
      method: 'DELETE',
    });
  }, [handleRequest]);

  // Webhook Triggers - External Integration
  const triggerWebhook = useCallback(async (
    webhookId: string,
    payload: Record<string, any>
  ) => {
    return handleRequest(`/webhooks/${webhookId}`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }, [handleRequest]);

  // Node Templates - JSON Script Templates
  const getNodeTemplates = useCallback(async () => {
    return handleRequest('/templates');
  }, [handleRequest]);

  // System Health & Status
  const checkHealth = useCallback(async () => {
    return handleRequest('/health');
  }, [handleRequest]);

  const getSystemInfo = useCallback(async () => {
    return handleRequest('/system-info');
  }, [handleRequest]);

  // High-level workflow operations
  const generateAndExecuteWorkflow = useCallback(async (
    agentId: string,
    naturalLanguageRequest: string,
    autoExecute = false
  ) => {
    try {
      // Step 1: Chat with agent to generate workflow
      const chatResponse = await chatWithAgent(agentId, naturalLanguageRequest);
      
      if (chatResponse.response_type === 'workflow' && chatResponse.workflow_json) {
        // Step 2: Create the workflow
        const workflowResponse = await createWorkflow(
          agentId, 
          chatResponse.workflow_json
        );
        
        // Step 3: Auto-execute if requested
        if (autoExecute && workflowResponse.workflow_id) {
          const executionResponse = await executeWorkflow(workflowResponse.workflow_id);
          
          return {
            chatResponse,
            workflowResponse,
            executionResponse,
            completed: true
          };
        }
        
        return {
          chatResponse,
          workflowResponse,
          completed: false,
          requiresConfirmation: true
        };
      }
      
      // Just a conversational response
      return {
        chatResponse,
        completed: true,
        conversational: true
      };
      
    } catch (error) {
      throw new Error(`Workflow generation failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }, [chatWithAgent, createWorkflow, executeWorkflow]);

  return {
    loading,
    error,
    
    // Agent Management
    createAgent,
    getAgent,
    listAgents,
    deleteAgent,
    
    // Chat & Code Builder AI
    chatWithAgent,
    generateAndExecuteWorkflow,
    
    // Memory
    getAgentMemory,
    clearAgentMemory,
    
    // Workflows & JSON Scripts
    createWorkflow,
    executeWorkflow,
    getWorkflowHistory,
    
    // Automation Engine
    processWithAutomation,
    
    // Triggers
    getAllTriggers,
    pauseTrigger,
    resumeTrigger,
    deleteTrigger,
    triggerWebhook,
    
    // Templates & System
    getNodeTemplates,
    checkHealth,
    getSystemInfo,
  };
};
