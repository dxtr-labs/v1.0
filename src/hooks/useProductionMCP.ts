/**
 * useProductionMCP Hook
 * React hook for connecting frontend to Production Dual MCP System
 */
import { useState, useCallback } from 'react';

export interface AgentMCPConfig {
  agent_id: string;
  agent_name: string;
  llm_config: {
    model: string;
    temperature: number;
    max_tokens?: number;
  };
  personality_traits?: {
    tone: string;
    expertise: string;
    style?: string;
  };
}

export interface WorkflowNode {
  node_type: string;
  parameters: Record<string, any>;
}

export interface WorkflowDefinition {
  agent_id: string;
  workflow_json: {
    name: string;
    description: string;
    nodes: Array<{
      id: string;
      type: string;
      parameters: Record<string, any>;
    }>;
  };
  trigger_config?: Record<string, any>;
}

export function useProductionMCP() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

  // Health check
  const checkHealth = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${baseUrl}/api/production-mcp/health`);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Health check failed');
      }
      
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Health check failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [baseUrl]);

  // Create Custom MCP LLM Agent
  const createAgent = useCallback(async (config: AgentMCPConfig) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${baseUrl}/api/production-mcp/agents/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to create agent');
      }
      
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create agent';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [baseUrl]);

  // Get Agent MCP
  const getAgent = useCallback(async (agentId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${baseUrl}/api/production-mcp/agents/${agentId}`);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to get agent');
      }
      
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get agent';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [baseUrl]);

  // Chat with Custom MCP LLM
  const chatWithCustomMCP = useCallback(async (
    agentId: string, 
    userInput: string, 
    context?: Record<string, any>
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${baseUrl}/api/production-mcp/chat/custom-mcp`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agent_id: agentId,
          user_input: userInput,
          context: context || {},
        }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Chat failed');
      }
      
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Chat failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [baseUrl]);

  // Process with Inhouse AI
  const processWithInhouseAI = useCallback(async (workflow: WorkflowNode) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${baseUrl}/api/production-mcp/workflow/inhouse-ai`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(workflow),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Workflow processing failed');
      }
      
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Workflow processing failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [baseUrl]);

  // Get available node types
  const getNodeTypes = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${baseUrl}/api/production-mcp/workflow/node-types`);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to get node types');
      }
      
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get node types';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [baseUrl]);

  // Create workflow
  const createWorkflow = useCallback(async (workflowDef: WorkflowDefinition) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${baseUrl}/api/production-mcp/workflow/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(workflowDef),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to create workflow');
      }
      
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create workflow';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [baseUrl]);

  // Execute workflow
  const executeWorkflow = useCallback(async (
    workflowId: string, 
    inputData?: Record<string, any>
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${baseUrl}/api/production-mcp/workflow/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow_id: workflowId,
          input_data: inputData || {},
        }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to execute workflow');
      }
      
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to execute workflow';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [baseUrl]);

  // Get system status
  const getSystemStatus = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${baseUrl}/api/production-mcp/system/status`);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error('Failed to get system status');
      }
      
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get system status';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [baseUrl]);

  // Run integration test
  const runIntegrationTest = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${baseUrl}/api/production-mcp/test/integration`, {
        method: 'POST',
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Integration test failed');
      }
      
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Integration test failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [baseUrl]);

  return {
    loading,
    error,
    
    // System operations
    checkHealth,
    getSystemStatus,
    runIntegrationTest,
    
    // Agent operations (Custom MCP LLM)
    createAgent,
    getAgent,
    chatWithCustomMCP,
    
    // Workflow operations (Inhouse AI)
    processWithInhouseAI,
    getNodeTypes,
    createWorkflow,
    executeWorkflow,
  };
}
