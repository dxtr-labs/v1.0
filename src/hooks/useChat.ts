// src/hooks/useChat.ts
// Custom hook for managing chat state and functionality

'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { parseUserMessage } from '../../lib/parameter-extractor';

export type Message = {
  role: 'user' | 'assistant';
  content: string;
  type?: 'options';
  buttons?: Array<{ label: string; action: string; requestId: string }>;
  json?: any;
  requestId?: string;
  missingParameters?: string[];
  timestamp?: Date;
};

export interface UseChatReturn {
  messages: Message[];
  input: string;
  loading: boolean;
  finalJSON: any;
  currentRequestId: string | null;
  pendingWorkflow: {workflow: any, requestId: string} | null;
  automationStatus: {[key: string]: 'loading' | 'success' | 'failed'};
  setInput: (value: string) => void;
  sendMessage: () => Promise<void>;
  handleButtonAction: (action: string, requestId: string, json: any, button: any) => Promise<void>;
  clearChat: () => void;
  setFinalJSON: (json: any) => void;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [finalJSON, setFinalJSON] = useState<any>(null);
  const [currentRequestId, setCurrentRequestId] = useState<string | null>(null);
  const [pendingWorkflow, setPendingWorkflow] = useState<{workflow: any, requestId: string} | null>(null);
  const [automationStatus, setAutomationStatus] = useState<{[key: string]: 'loading' | 'success' | 'failed'}>({});

  const sendMessage = useCallback(async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('/api/ai-enhancement', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ message: input.trim() })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json() as any;

      if (data.error) {
        throw new Error(data.error);
      }

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.message?.content || data.response || 'I received your message but couldn\'t generate a proper response.',
        timestamp: new Date()
      };

      // Handle parameter extraction results
      if (data.extractedData) {
        const extractionResult = data.extractedData;
        
        if (extractionResult.missingParameters && extractionResult.missingParameters.length > 0) {
          assistantMessage.missingParameters = extractionResult.missingParameters;
          assistantMessage.content = extractionResult.enhancedPrompt || data.message?.content || data.response;
        }

        if (extractionResult.workflowJSON) {
          assistantMessage.json = extractionResult.workflowJSON;
          assistantMessage.type = 'options';
          assistantMessage.buttons = [
            { label: '✅ Looks Good - Generate Full Workflow', action: 'approve', requestId: extractionResult.requestId },
            { label: '✏️ Modify Parameters', action: 'modify', requestId: extractionResult.requestId },
            { label: '🚀 Run Automation Now', action: 'run', requestId: extractionResult.requestId }
          ];
          setCurrentRequestId(extractionResult.requestId);
        }

        if (extractionResult.finalWorkflow) {
          setFinalJSON(extractionResult.finalWorkflow);
          setPendingWorkflow({
            workflow: extractionResult.finalWorkflow,
            requestId: extractionResult.requestId
          });
        }
      }

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  }, [input, loading]);

  const handleButtonAction = useCallback(async (action: string, requestId: string, json: any, button: any) => {
    if (action === 'run') {
      setAutomationStatus(prev => ({ ...prev, [requestId]: 'loading' }));
      
      try {
        const workflow = json || pendingWorkflow?.workflow;
        if (!workflow) {
          throw new Error('No workflow available to run');
        }

        const response = await fetch('/api/automation/simple', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ 
            prompt: "Execute provided workflow",
            step: 'execute',
            workflow: workflow
          })
        });

        const result = await response.json() as any;

        if (result.success) {
          setAutomationStatus(prev => ({ ...prev, [requestId]: 'success' }));
          
          const successMessage: Message = {
            role: 'assistant',
            content: `🎉 **Automation Executed Successfully!**\n\n${result.message || 'Your workflow has been processed.'}`,
            timestamp: new Date()
          };
          setMessages(prev => [...prev, successMessage]);
        } else {
          throw new Error(result.error || 'Automation failed');
        }

      } catch (error) {
        console.error('Automation error:', error);
        setAutomationStatus(prev => ({ ...prev, [requestId]: 'failed' }));
        
        const errorMessage: Message = {
          role: 'assistant',
          content: `❌ **Automation Failed**\n\nError: ${error instanceof Error ? error.message : 'Unknown error'}. You can try running it again.`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } else if (action === 'approve') {
      // Handle approval action
      const approvalMessage: Message = {
        role: 'assistant',
        content: '✅ Great! I\'ll generate the complete workflow for you.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, approvalMessage]);
      
      // Here you could trigger final workflow generation
      if (json) {
        setFinalJSON(json);
      }
    } else if (action === 'modify') {
      // Handle modification request
      const modifyMessage: Message = {
        role: 'assistant',
        content: '✏️ Please tell me what you\'d like to modify about the automation parameters.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, modifyMessage]);
    }
  }, [pendingWorkflow]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setInput('');
    setLoading(false);
    setFinalJSON(null);
    setCurrentRequestId(null);
    setPendingWorkflow(null);
    setAutomationStatus({});
  }, []);

  return {
    messages,
    input,
    loading,
    finalJSON,
    currentRequestId,
    pendingWorkflow,
    automationStatus,
    setInput,
    sendMessage,
    handleButtonAction,
    clearChat,
    setFinalJSON
  };
}
