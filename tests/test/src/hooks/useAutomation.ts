// src/hooks/useAutomation.ts
// Custom hook for managing automation workflows and parameter collection

'use client';

import { useState, useCallback } from 'react';

export interface AutomationParameter {
  name: string;
  description: string;
  required: boolean;
  type: string;
  value?: string;
}

export interface AutomationRequest {
  userMessage?: string;
  providedParameters?: Record<string, any>;
  workflow?: any;
  requestId?: string;
}

export interface ParameterCollectionResponse {
  success: boolean;
  needsParameters?: boolean;
  missingParameters?: AutomationParameter[];
  workflowType?: string;
  helpText?: string;
  requestId?: string;
}

export interface AutomationExecutionResponse {
  success: boolean;
  message?: string;
  requestId?: string;
  workflowId?: string;
  executionResult?: any;
  matchedTemplate?: any;
}

export function useAutomation() {
  const [isCollectingParameters, setIsCollectingParameters] = useState(false);
  const [currentParameterRequest, setCurrentParameterRequest] = useState<ParameterCollectionResponse | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);

  const startAutomation = useCallback(async (userMessage: string): Promise<ParameterCollectionResponse | AutomationExecutionResponse> => {
    try {
      const request = {
        prompt: userMessage,
        step: 'analyze'
      };

      const response = await fetch('/api/automation/simple', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json() as any;

      if (result.needsParameters) {
        // Need to collect parameters
        setIsCollectingParameters(true);
        setCurrentParameterRequest(result as ParameterCollectionResponse);
        return result as ParameterCollectionResponse;
      } else {
        // Automation executed successfully
        return result as AutomationExecutionResponse;
      }
    } catch (error) {
      console.error('Automation start error:', error);
      throw error;
    }
  }, []);

  const submitParameters = useCallback(async (parameters: Record<string, string>): Promise<AutomationExecutionResponse> => {
    if (!currentParameterRequest) {
      throw new Error('No parameter request in progress');
    }

    setIsExecuting(true);
    
    try {
      const request = {
        prompt: "Complete automation with provided parameters",
        step: 'execute',
        parameters: parameters
      };

      const response = await fetch('/api/automation/simple', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json() as any;
      
      // Clear parameter collection state
      setIsCollectingParameters(false);
      setCurrentParameterRequest(null);
      
      return result as AutomationExecutionResponse;
    } catch (error) {
      console.error('Parameter submission error:', error);
      throw error;
    } finally {
      setIsExecuting(false);
    }
  }, [currentParameterRequest]);

  const cancelParameterCollection = useCallback(() => {
    setIsCollectingParameters(false);
    setCurrentParameterRequest(null);
  }, []);

  const executeWorkflow = useCallback(async (workflow: any, requestId?: string): Promise<AutomationExecutionResponse> => {
    setIsExecuting(true);
    
    try {
      const request = {
        prompt: "Execute provided workflow",
        step: 'execute',
        workflow: workflow
      };

      const response = await fetch('/api/automation/simple', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json() as any;
      return result as AutomationExecutionResponse;
    } catch (error) {
      console.error('Workflow execution error:', error);
      throw error;
    } finally {
      setIsExecuting(false);
    }
  }, []);

  return {
    isCollectingParameters,
    currentParameterRequest,
    isExecuting,
    startAutomation,
    submitParameters,
    cancelParameterCollection,
    executeWorkflow
  };
}
