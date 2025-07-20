'use client';

import { useSearchParams, useRouter } from 'next/navigation';
import { useEffect, useState, useRef } from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, 
  Bot, 
  User, 
  Moon, 
  Sun, 
  ArrowLeft, 
  Settings, 
  Trash2,
  Copy,
  Download
} from 'lucide-react';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  needs_confirmation?: boolean;
  confirmation_prompt?: string;
  action_required?: string;
  original_message?: string;
  ai_service_options?: any[];
  status?: string;
  workflow_preview?: any;
  workflow_json?: any;
  ai_service_used?: string;
  estimated_credits?: number;
}

interface AgentData {
  id: string;  // Changed from AgentID to id to match backend
  name: string;
  role: string;
  mode: string;
  personality: any;
  llm_config: any;
}

export default function AgentChatPage() {
  const { isDarkMode, toggleTheme } = useTheme();
  const router = useRouter();
  const searchParams = useSearchParams();
  const agentId = searchParams?.get('agentId');
  
  const [agent, setAgent] = useState<AgentData | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [agentLoading, setAgentLoading] = useState(true);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [showAIServiceSelection, setShowAIServiceSelection] = useState(false);
  const [showWorkflowDialog, setShowWorkflowDialog] = useState(false);
  const [workflowPreview, setWorkflowPreview] = useState<any>(null);
  const [editableEmailContent, setEditableEmailContent] = useState('');
  const [editableEmailSubject, setEditableEmailSubject] = useState('');
  const [pendingConfirmation, setPendingConfirmation] = useState<{
    messageId: string;
    prompt: string;
    originalMessage: string;
    workflowJson?: any;
  } | null>(null);
  const [pendingAISelection, setPendingAISelection] = useState<{
    messageId: string;
    originalMessage: string;
    aiServiceOptions: any[];
  } | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Track dialog state changes
  useEffect(() => {
    console.log('Dialog State Changed:', {
      showWorkflowDialog,
      workflowPreview,
      shouldShow: showWorkflowDialog && workflowPreview,
      workflowPreviewType: typeof workflowPreview,
      workflowPreviewContent: workflowPreview
    });
  }, [showWorkflowDialog, workflowPreview]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${inputRef.current.scrollHeight}px`;
    }
  }, [input]);

  // Load agent data
  useEffect(() => {
    if (!agentId) return;
    
    fetch(`/api/agents/${agentId}`)
      .then(res => res.json())
      .then((data: any) => {
        setAgent(data as AgentData);
        setAgentLoading(false);
        // Add welcome message
        const welcomeMessage: ChatMessage = {
          id: 'welcome',
          type: 'assistant',
          content: `Hello! I'm ${data.name}, your ${data.role}. How can I help you today?`,
          timestamp: new Date()
        };
        setMessages([welcomeMessage]);
      })
      .catch(error => {
        console.error('Failed to load agent:', error);
        setAgentLoading(false);
      });
  }, [agentId]);

  const handleSend = async () => {
    if (!input.trim() || !agent || loading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/chat/mcpai', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          agentId: agent.id,
          agentConfig: {
            name: agent.name,
            role: agent.role,
            personality: agent.personality,
            llm_config: agent.llm_config
          }
        }),
      });

      if (res.ok) {
        console.log('🟢 BASIC DEBUG: Response received, parsing JSON...');
        const result: any = await res.json();
        console.log('🟢 BASIC DEBUG: JSON parsed successfully');
        console.log('🟢 BASIC DEBUG: Result type:', typeof result);
        console.log('🟢 BASIC DEBUG: Result keys:', Object.keys(result || {}));
        
        // COMPREHENSIVE DEBUG: Log everything about the response
        console.log('🚨🚨🚨 COMPREHENSIVE FRONTEND DEBUG 🚨🚨🚨');
        console.log('🔍 FRONTEND DEBUG: Raw response received:', result);
        console.log('🔍 Response Status:', result.status);
        console.log('🔍 Response Action Required:', result.action_required);
        console.log('🔍 Has workflow_preview:', !!result.workflow_preview);
        console.log('🔍 workflow_preview type:', typeof result.workflow_preview);
        console.log('🔍 workflow_preview content:', result.workflow_preview);
        console.log('🔍 Has workflow_json:', !!result.workflow_json);
        console.log('🔍 Has email_preview:', result.workflow_preview?.email_preview ? true : false);
        console.log('🔍 All response keys:', Object.keys(result));
        console.log('🚨🚨🚨 END COMPREHENSIVE DEBUG 🚨🚨🚨');
        
        console.log('🔍 FRONTEND DEBUG: Received response:', {
          status: result.status,
          action_required: result.action_required,
          hasWorkflowPreview: !!result.workflow_preview,
          hasEmailContent: !!result.email_content,
          hasRecipient: !!result.recipient,
          hasEmailSubject: !!result.email_subject,
          keys: Object.keys(result),
          debug_workflow_preview_exists: (result as any).debug_workflow_preview_exists,
          debug_workflow_preview_type: (result as any).debug_workflow_preview_type,
          debug_mcpResult_keys: (result as any).debug_mcpResult_keys,
          debug_mcpResult_status: (result as any).debug_mcpResult_status,
          debug_has_workflow_json: (result as any).debug_has_workflow_json
        });
        
        // Handle AI service selection
        if (result.status === 'ai_service_selection' && result.ai_service_options) {
          const serviceSelectionMessage: ChatMessage = {
            id: (Date.now() + 1).toString(),
            type: 'assistant',
            content: result.message,
            timestamp: new Date(),
            action_required: 'select_ai_service',
            ai_service_options: result.ai_service_options,
            status: 'ai_service_selection',
            original_message: input
          };
          setMessages(prev => [...prev, serviceSelectionMessage]);
          
          // Set up AI service selection dialog
          setPendingAISelection({
            messageId: serviceSelectionMessage.id,
            originalMessage: input,
            aiServiceOptions: result.ai_service_options
          });
          setShowAIServiceSelection(true);
        }
        // Handle workflow preview - Enhanced detection for editable email previews
        else if (result.status === 'workflow_preview' || 
                (result.workflow_preview && typeof result.workflow_preview === 'object')) {
          console.log('🎯 FRONTEND DEBUG: Workflow preview detected (enhanced detection)!', {
            status: result.status,
            hasWorkflowPreview: !!result.workflow_preview,
            workflowPreviewType: typeof result.workflow_preview,
            hasWorkflowJson: !!result.workflow_json,
            hasAiService: !!result.ai_service_used,
            workflowPreview: result.workflow_preview
          });
          
          // Check if this is an email automation workflow
          if (result.workflow_preview && result.workflow_preview.email_preview) {
            console.log('📧 FRONTEND DEBUG: Email workflow preview detected - showing editable dialog!', {
              emailPreview: result.workflow_preview.email_preview,
              recipient: result.workflow_preview.email_preview.to,
              subject: result.workflow_preview.email_preview.subject
            });
            
            const workflowMessage: ChatMessage = {
              id: (Date.now() + 1).toString(),
              type: 'assistant',
              content: result.message,
              timestamp: new Date(),
              action_required: 'confirm_workflow',
              workflow_preview: result.workflow_preview,
              workflow_json: result.workflow_json,
              ai_service_used: result.ai_service_used,
              estimated_credits: result.estimated_credits
            };
            setMessages(prev => [...prev, workflowMessage]);
            
            // Set up editable email preview dialog
            console.log('📧 FRONTEND DEBUG: Setting up editable email dialog...');
            setWorkflowPreview(result);
            setEditableEmailContent(result.workflow_preview.email_preview.preview_content || '');
            setEditableEmailSubject(result.workflow_preview.email_preview.subject || '');
            
            // Show workflow dialog immediately for editable email preview
            setShowWorkflowDialog(true);
            console.log('📧 FRONTEND DEBUG: Editable email dialog state set to TRUE!');
          } else if (result.workflow_json) {
            // Handle non-email workflow previews
            const workflowMessage: ChatMessage = {
              id: (Date.now() + 1).toString(),
              type: 'assistant',
              content: result.message,
              timestamp: new Date(),
              action_required: 'confirm_workflow',
              workflow_preview: result.workflow_preview,
              workflow_json: result.workflow_json,
              ai_service_used: result.ai_service_used,
              estimated_credits: result.estimated_credits
            };
            setMessages(prev => [...prev, workflowMessage]);
            
            // Set up workflow preview dialog with actual backend data
            console.log('🎯 FRONTEND DEBUG: Setting workflow preview state with backend data...');
            setWorkflowPreview({ ...result, workflow_preview: result.workflow_preview });
            
            // Show workflow dialog with proper state tracking
            console.log('🎯 FRONTEND DEBUG: About to show workflow dialog...', {
              currentDialogState: showWorkflowDialog,
              workflowPreviewState: workflowPreview,
              dialogVisibilityBeforeChange: showWorkflowDialog
            });

            // Small delay to prevent race conditions with dialog rendering
            setTimeout(() => {
              setShowWorkflowDialog(true);
              console.log('🎯 FRONTEND DEBUG: Workflow dialog visibility updated!', {
                newDialogState: true,
                timestamp: new Date().toISOString(),
                hasValidPreview: !!workflowPreview?.workflow_preview
              });
            }, 100);
          }
        }
        // Handle email preview - with multiple condition checks
        else if ((result.status === 'preview_ready' && result.action_required === 'approve_email') || 
                 (result.email_content && result.recipient && result.message && result.message.includes('Email Preview'))) {
          console.log('📧 FRONTEND DEBUG: Email preview condition MATCHED!', {
            status: result.status,
            action_required: result.action_required,
            hasWorkflowPreviewContent: !!result.workflowPreviewContent,
            hasEmailPreview: !!result.email_preview,
            hasEmailContent: !!result.email_content,
            recipient: result.recipient,
            subject: result.email_subject,
            conditionType: result.status === 'preview_ready' ? 'exact_match' : 'fallback_match',
            fullResult: result
          });
          
          const emailPreviewMessage: ChatMessage = {
            id: (Date.now() + 1).toString(),
            type: 'assistant',
            content: result.message || result.response,
            timestamp: new Date(),
            action_required: 'approve_email',
            workflow_preview: {
              title: 'Email Preview',
              description: `Review your email before sending to ${result.recipient}`,
              email_preview: {
                to: result.recipient,
                subject: result.email_subject,
                preview_content: result.email_content,
                ai_service: 'openai'
              }
            },
            workflow_json: {
              type: 'email_automation',
              workflow_id: result.workflow_id,
              recipient: result.recipient,
              email_content: result.email_content,
              email_subject: result.email_subject,
              action_type: 'approve_email'
            }
          };
          setMessages(prev => [...prev, emailPreviewMessage]);
          
          // Set up email preview dialog
          setWorkflowPreview({
            ...result,
            workflow_preview: {
              title: 'Email Preview',
              description: `Review your email before sending to ${result.recipient}`,
              email_preview: {
                to: result.recipient,
                subject: result.email_subject,
                preview_content: result.email_content,
                ai_service: 'openai'
              },
              workflow_id: result.workflow_id,
              html_preview: result.workflowPreviewContent
            },
            // Add workflow_json for email preview to make confirmation work
            workflow_json: {
              type: 'email_send',
              action: 'send_email',
              recipient: result.recipient,
              subject: result.email_subject,
              content: result.email_content,
              workflow_id: result.workflow_id
            },
            estimated_credits: 1,
            ai_service_used: 'openai'
          });
          
          // Set editable email content
          setEditableEmailContent(result.email_content || '');
          setEditableEmailSubject(result.email_subject || '');
          
          // Show email preview dialog immediately
          console.log('📧 FRONTEND DEBUG: About to show email preview dialog...', {
            workflowPreviewSet: !!workflowPreview,
            currentDialogState: showWorkflowDialog
          });
          
          setShowWorkflowDialog(true);
          console.log('📧 FRONTEND DEBUG: Email preview dialog state set to TRUE!');
          
          // Additional debugging - check state immediately
          setTimeout(() => {
            console.log('📧 FRONTEND DEBUG: Checking dialog state after set:', {
              showWorkflowDialog: showWorkflowDialog,
              workflowPreviewExists: !!workflowPreview,
              workflowPreviewKeys: workflowPreview ? Object.keys(workflowPreview) : [],
              hasEmailPreview: workflowPreview?.workflow_preview?.email_preview ? true : false
            });
          }, 50);
        }
        // Check if this might be an email preview that didn't match the condition
        else if (result.message && result.message.includes('Email Preview Ready')) {
          console.log('🔍 FRONTEND DEBUG: Email preview message detected but condition not matched!', {
            status: result.status,
            action_required: result.action_required,
            message: result.message,
            hasEmailContent: !!result.email_content,
            hasRecipient: !!result.recipient,
            allKeys: Object.keys(result)
          });
          
          // FALLBACK: If we detect an email preview message, force the dialog to open
          if (result.email_content && result.recipient) {
            console.log('🔧 FRONTEND DEBUG: Forcing email preview dialog to open via fallback!');
            
            const emailPreviewMessage: ChatMessage = {
              id: (Date.now() + 1).toString(),
              type: 'assistant',
              content: result.message || result.response || '📧 Email Preview Ready!',
              timestamp: new Date(),
              action_required: 'approve_email',
              workflow_preview: {
                title: 'Email Preview',
                description: `Review your email before sending to ${result.recipient}`,
                email_preview: {
                  to: result.recipient,
                  subject: result.email_subject || 'Generated Email',
                  preview_content: result.email_content,
                  ai_service: 'openai'
                }
              },
              workflow_json: {
                type: 'email_automation',
                workflow_id: result.workflow_id || `email_${Date.now()}`,
                recipient: result.recipient,
                email_content: result.email_content,
                email_subject: result.email_subject || 'Generated Email',
                action_type: 'approve_email'
              }
            };
            setMessages(prev => [...prev, emailPreviewMessage]);
            
            // Set up email preview dialog
            setWorkflowPreview({
              ...result,
              status: 'preview_ready',
              action_required: 'approve_email',
              workflow_preview: {
                title: 'Email Preview',
                description: `Review your email before sending to ${result.recipient}`,
                email_preview: {
                  to: result.recipient,
                  subject: result.email_subject || 'Generated Email',
                  preview_content: result.email_content,
                  ai_service: 'openai'
                },
                workflow_id: result.workflow_id || `email_${Date.now()}`,
                html_preview: result.workflowPreviewContent
              },
              estimated_credits: 1,
              ai_service_used: 'openai'
            });
            
            // Force dialog to show with immediate effect
            setShowWorkflowDialog(true);
            console.log('🔧 FRONTEND DEBUG: Email preview dialog state set to TRUE via fallback!');
          }
        }
        // Handle case where workflow_preview status but missing workflow_preview data
        else if (result.status === 'workflow_preview' && result.workflow_json && !result.workflow_preview) {
          console.error('🎯 FRONTEND DEBUG: Backend sent workflow_preview status but no workflow_preview data!', {
            status: result.status,
            hasWorkflowJson: !!result.workflow_json,
            hasWorkflowPreview: !!result.workflow_preview
          });
          
          // Show fallback message instead of broken dialog
          const errorMessage: ChatMessage = {
            id: (Date.now() + 1).toString(),
            type: 'assistant',
            content: 'I generated a workflow but there was an issue with the preview. Please try your request again.',
            timestamp: new Date()
          };
          setMessages(prev => [...prev, errorMessage]);
        }
        // Handle legacy workflow confirmation (keeping for backward compatibility)
        else if ((result.status === 'review_needed' || result.action_required === 'confirm_workflow') && result.workflow_json && !result.ai_service_used) {
          const workflowMessage: ChatMessage = {
            id: (Date.now() + 1).toString(),
            type: 'assistant',
            content: result.message || 'Workflow ready for confirmation',
            timestamp: new Date(),
            needs_confirmation: true,
            confirmation_prompt: `Would you like me to execute this automation workflow?`,
            action_required: 'confirm_workflow',
            original_message: input
          };
          setMessages(prev => [...prev, workflowMessage]);
          
          // Set up workflow confirmation dialog
          setPendingConfirmation({
            messageId: workflowMessage.id,
            prompt: `${result.message}\n\nWould you like me to execute this workflow?`,
            originalMessage: input,
            workflowJson: result.workflow_json
          });
          setShowConfirmation(true);
        }
        // Handle regular confirmation requests
        else if (result.needs_confirmation && result.confirmation_prompt) {
          const confirmationMessage: ChatMessage = {
            id: (Date.now() + 1).toString(),
            type: 'assistant',
            content: result.confirmation_prompt,
            timestamp: new Date(),
            needs_confirmation: true,
            confirmation_prompt: result.confirmation_prompt,
            action_required: result.action_required,
            original_message: input
          };
          setMessages(prev => [...prev, confirmationMessage]);
          
          // Set up confirmation dialog
          setPendingConfirmation({
            messageId: confirmationMessage.id,
            prompt: result.confirmation_prompt,
            originalMessage: input
          });
          setShowConfirmation(true);
        } else {
          // Normal response
          const assistantMessage: ChatMessage = {
            id: (Date.now() + 1).toString(),
            type: 'assistant',
            content: result.response || result.message || 'No response received',
            timestamp: new Date()
          };
          setMessages(prev => [...prev, assistantMessage]);
        }
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error('Chat error:', error);
      console.error('Error details:', {
        error: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined
      });
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleAIServiceSelection = async (selectedService: string) => {
    if (!pendingAISelection || !agent) return;

    setShowAIServiceSelection(false);
    setLoading(true);

    try {
      // Send the message with the selected AI service
      const res = await fetch('/api/chat/mcpai', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: `service:${selectedService} ${pendingAISelection.originalMessage}`,
          agentId: agent.id,
          agentConfig: {
            name: agent.name,
            role: agent.role,
            personality: agent.personality,
            llm_config: agent.llm_config
          }
        }),
      });

      if (res.ok) {
        const result: any = await res.json();
        
        // Remove the AI service selection message
        setMessages(prev => prev.filter(msg => msg.id !== pendingAISelection.messageId));
        
        // Handle different response types
        if (result.status === 'workflow_preview' && result.workflow_preview) {
          // Show workflow preview dialog
          const workflowMessage: ChatMessage = {
            id: (Date.now() + 1).toString(),
            type: 'assistant',
            content: result.message,
            timestamp: new Date(),
            action_required: 'confirm_workflow',
            workflow_preview: result.workflow_preview,
            workflow_json: result.workflow_json,
            ai_service_used: result.ai_service_used,
            estimated_credits: result.estimated_credits
          };
          setMessages(prev => [...prev, workflowMessage]);
          
          // Set up workflow preview dialog
          setWorkflowPreview(result);
          setShowWorkflowDialog(true);
        }
        // FALLBACK: Handle any response with workflow_preview that wasn't caught above
        else if (result.workflow_preview && result.workflow_preview.email_preview) {
          console.log('🔧 FRONTEND DEBUG: FALLBACK - Found workflow_preview with email_preview!', {
            status: result.status,
            hasWorkflowJson: !!result.workflow_json,
            emailPreview: result.workflow_preview.email_preview
          });
          
          // Force the editable email dialog to open
          setWorkflowPreview(result);
          setEditableEmailContent(result.workflow_preview.email_preview.preview_content || '');
          setEditableEmailSubject(result.workflow_preview.email_preview.subject || '');
          setShowWorkflowDialog(true);
          
          // Also add to messages
          const fallbackMessage: ChatMessage = {
            id: (Date.now() + 1).toString(),
            type: 'assistant',
            content: result.message || result.response || 'Email preview ready for editing!',
            timestamp: new Date(),
            action_required: 'confirm_workflow',
            workflow_preview: result.workflow_preview,
            workflow_json: result.workflow_json
          };
          setMessages(prev => [...prev, fallbackMessage]);
        } else {
          // Debug: Log unhandled response types
          console.log('🚨 FRONTEND DEBUG: Unhandled response type - falling back to regular message', {
            status: result.status,
            action_required: result.action_required,
            hasWorkflowPreview: !!result.workflow_preview,
            hasWorkflowJson: !!result.workflow_json,
            hasEmailPreview: result.workflow_preview?.email_preview ? true : false,
            message: result.message,
            response: result.response,
            allKeys: Object.keys(result),
            detailedResponse: result
          });
          
          // Regular response
          const resultMessage: ChatMessage = {
            id: (Date.now() + 1).toString(),
            type: 'assistant',
            content: result.response || result.message || 'Processing your request...',
            timestamp: new Date()
          };
          setMessages(prev => [...prev, resultMessage]);
        }
      } else {
        throw new Error('Failed to process AI service selection');
      }
    } catch (error) {
      console.error('AI service selection error:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: "Sorry, I encountered an error processing your AI service selection. Please try again.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      setPendingAISelection(null);
      setShowAIServiceSelection(false);
    }
  };

  const handleConfirmation = async (confirmed: boolean) => {
    if (!pendingConfirmation || !agent) return;

    setShowConfirmation(false);
    setLoading(true);

    try {
      const res = await fetch('/api/chat/mcpai/confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agentId: agent.id,
          confirmed: confirmed,
          original_message: pendingConfirmation.originalMessage,
          workflow_json: pendingConfirmation.workflowJson
        }),
      });

      if (res.ok) {
        const result: any = await res.json();
        
        // Remove the confirmation message and replace with result
        setMessages(prev => prev.filter(msg => msg.id !== pendingConfirmation.messageId));
        
        const resultMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: confirmed 
            ? (result.response || 'Workflow executed successfully!')
            : 'Workflow execution was cancelled.',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, resultMessage]);
      } else {
        throw new Error('Failed to process confirmation');
      }
    } catch (error) {
      console.error('Confirmation error:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: "Sorry, I encountered an error processing your confirmation. Please try again.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      setPendingConfirmation(null);
    }
  };

  // Handle email preview confirmation
  const handleEmailPreviewConfirmation = async (confirmed: boolean) => {
    console.log('📧 FRONTEND DEBUG: handleEmailPreviewConfirmation called:', { confirmed, workflowPreview });
    
    setShowWorkflowDialog(false);
    setLoading(true);

    try {
      if (confirmed) {
        console.log('📧 FRONTEND DEBUG: User approved email, sending...', {
          originalContent: workflowPreview?.workflow_json?.content,
          editedContent: editableEmailContent,
          originalSubject: workflowPreview?.workflow_json?.subject,
          editedSubject: editableEmailSubject
        });
        
        // Call email send endpoint with edited content using the backend's expected format
        const recipient = workflowPreview?.workflow_json?.recipient || workflowPreview?.recipient;
        const workflowId = workflowPreview?.workflow_id || 'email_workflow_' + Date.now();
        
        const res = await fetch('/api/chat/mcpai', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: `SEND_APPROVED_EMAIL:${workflowId}:${recipient}:${editableEmailSubject}`,
            agentId: agent?.id,
            agentConfig: agent || { name: 'Assistant', role: 'helper' },
            email_content: editableEmailContent
          }),
        });

        if (res.ok) {
          const result = await res.json() as any;
          console.log('📧 FRONTEND DEBUG: Email send response:', result);
          
          const successMessage: ChatMessage = {
            id: (Date.now()).toString(),
            type: 'assistant',
            content: result.message || `✅ Email sent successfully to ${workflowPreview?.workflow_json?.recipient}!`,
            timestamp: new Date()
          };
          setMessages(prev => [...prev, successMessage]);
        } else {
          throw new Error('Email send failed');
        }
      } else {
        console.log('📧 FRONTEND DEBUG: User cancelled email');
        const cancelMessage: ChatMessage = {
          id: (Date.now()).toString(),
          type: 'assistant',
          content: 'Email cancelled. How else can I assist you?',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, cancelMessage]);
      }
    } catch (error) {
      console.error('Email confirmation error:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now()).toString(),
        type: 'assistant',
        content: 'Sorry, there was an error sending the email. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      setWorkflowPreview(null);
    }
  };

  // Handle workflow confirmation
  const handleWorkflowConfirmation = async (confirmed: boolean) => {
    console.log('🎯 FRONTEND DEBUG: handleWorkflowConfirmation called with:', { 
      confirmed,
      hasWorkflowPreview: !!workflowPreview,
      workflowPreviewData: workflowPreview,
      hasWorkflowJson: workflowPreview?.workflow_json ? true : false,
      isLoading: loading,
      workflowType: workflowPreview?.workflow_json?.type
    });

    // Prevent double execution
    if (loading) {
      console.log('🎯 FRONTEND DEBUG: Already processing, ignoring duplicate call');
      return;
    }

    if (!workflowPreview || !workflowPreview.workflow_json) {
      console.error('🎯 FRONTEND DEBUG: Cannot process confirmation - missing workflow data');
      return;
    }

    // Handle email preview confirmation differently
    if (workflowPreview.workflow_json.type === 'email_send') {
      console.log('📧 FRONTEND DEBUG: Processing email preview confirmation:', confirmed);
      await handleEmailPreviewConfirmation(confirmed);
      return;
    }

    console.log('🎯 FRONTEND DEBUG: Processing workflow confirmation:', { 
      confirmed,
      hasData: !!workflowPreview,
      workflowId: workflowPreview.workflow_id,
      aiService: workflowPreview.ai_service_used,
      estimatedCredits: workflowPreview.estimated_credits
    });
    
    setShowWorkflowDialog(false);
    setLoading(true);

    try {
      if (confirmed) {
        console.log('🎯 FRONTEND DEBUG: Sending confirmation request to backend...');
        // Send workflow confirmation to backend
        const res = await fetch('/api/chat/mcpai/confirm', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            workflow_json: workflowPreview.workflow_json,
            agentId: agent?.id,
            confirmed: true
          }),
        });

        if (res.ok) {
          const result: any = await res.json();
          console.log('🎯 FRONTEND DEBUG: Confirmation successful:', result);
          const confirmationMessage: ChatMessage = {
            id: (Date.now() + 1).toString(),
            type: 'assistant',
            content: result.response || result.message || 'Workflow executed successfully!',
            timestamp: new Date()
          };
          setMessages(prev => [...prev, confirmationMessage]);
        } else {
          console.error('🎯 FRONTEND DEBUG: Confirmation failed:', res.status, res.statusText);
          throw new Error('Failed to execute workflow');
        }
      } else {
        // User cancelled workflow
        const cancelMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: 'Workflow cancelled. How else can I assist you?',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, cancelMessage]);
      }
    } catch (error) {
      console.error('Workflow confirmation error:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, there was an error processing your request. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      setWorkflowPreview(null);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    if (!agent) return;
    const welcomeMessage: ChatMessage = {
      id: 'welcome',
      type: 'assistant',
      content: `Hello! I'm ${agent.name}, your ${agent.role}. How can I help you today?`,
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
  };

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  const exportChat = () => {
    const chatData = messages.map(msg => ({
      sender: msg.type === 'user' ? 'You' : agent?.name || 'Assistant',
      message: msg.content,
      timestamp: msg.timestamp.toLocaleString()
    }));
    
    const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-${agent?.name || 'agent'}-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (agentLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-100 dark:bg-[#1a1a1a] transition-colors duration-300">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-600 dark:border-gray-400 mx-auto mb-4"></div>
          <p className="text-[#1a1a1a] dark:text-gray-100">Loading agent...</p>
        </div>
      </div>
    );
  }

  if (!agent) {
    return (
      <div className="h-screen flex items-center justify-center bg-[#F2EBE2] dark:bg-[#1a1a1a] transition-colors duration-300">
        <div className="text-center">
          <p className="text-[#1a1a1a] dark:text-[#F2EBE2] text-xl mb-4">Agent not found</p>
          <button
            onClick={() => router.push('/dashboard/agents')}
            className="px-6 py-2 bg-[#DAA520] hover:bg-[#B8941C] dark:bg-[#D2BD96] dark:hover:bg-[#C4AF89] text-white rounded-lg transition-colors"
          >
            Back to Agents
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-[#F2EBE2] dark:bg-[#1a1a1a] transition-colors duration-300">
      {/* Header */}
      <motion.div 
        className="flex items-center justify-between p-4 bg-white/80 dark:bg-[#1a1a1a]/80 backdrop-blur-xl border-b border-[#DAA520]/20 dark:border-[#D2BD96]/20"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.back()}
            className="p-2 rounded-lg bg-[#DAA520]/10 dark:bg-[#D2BD96]/10 hover:bg-[#DAA520]/20 dark:hover:bg-[#D2BD96]/20 transition-colors"
          >
            <ArrowLeft className="h-5 w-5 text-[#DAA520] dark:text-[#D2BD96]" />
          </button>
          
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-gradient-to-r from-[#DAA520] to-[#D2BD96] flex items-center justify-center">
              <Bot className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-[#1a1a1a] dark:text-[#F2EBE2]">{agent.name}</h1>
              <p className="text-sm text-[#1a1a1a]/70 dark:text-[#F2EBE2]/70">{agent.role}</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg bg-[#DAA520]/10 dark:bg-[#D2BD96]/10 hover:bg-[#DAA520]/20 dark:hover:bg-[#D2BD96]/20 transition-colors"
          >
            {isDarkMode ? (
              <Sun className="h-5 w-5 text-[#D2BD96]" />
            ) : (
              <Moon className="h-5 w-5 text-[#DAA520]" />
            )}
          </button>

          {/* Export Chat */}
          <button
            onClick={exportChat}
            className="p-2 rounded-lg bg-[#DAA520]/10 dark:bg-[#D2BD96]/10 hover:bg-[#DAA520]/20 dark:hover:bg-[#D2BD96]/20 transition-colors"
          >
            <Download className="h-5 w-5 text-[#DAA520] dark:text-[#D2BD96]" />
          </button>

          {/* Clear Chat */}
          <button
            onClick={clearChat}
            className="p-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 transition-colors"
          >
            <Trash2 className="h-5 w-5 text-red-500" />
          </button>
        </div>
      </motion.div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        <AnimatePresence initial={false}>
          {messages.map((message, index) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.type === 'assistant' && (
                <div className="h-8 w-8 rounded-full bg-gradient-to-r from-[#DAA520] to-[#D2BD96] flex items-center justify-center flex-shrink-0">
                  <Bot className="h-4 w-4 text-white" />
                </div>
              )}
              
              <div className={`max-w-[80%] ${message.type === 'user' ? 'order-first' : ''}`}>
                <div
                  className={`relative p-4 rounded-2xl ${
                    message.type === 'user'
                      ? 'bg-[#DAA520] dark:bg-[#D2BD96] text-white'
                      : message.needs_confirmation
                      ? 'bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-2 border-blue-200 dark:border-blue-700 text-[#1a1a1a] dark:text-[#F2EBE2]'
                      : 'bg-white/80 dark:bg-[#1a1a1a]/80 backdrop-blur-sm border border-[#DAA520]/20 dark:border-[#D2BD96]/20 text-[#1a1a1a] dark:text-[#F2EBE2]'
                  }`}
                >
                  <div className="whitespace-pre-wrap break-words">{message.content}</div>
                  
                  {/* Special indicator for confirmation messages */}
                  {message.needs_confirmation && (
                    <div className="mt-3 flex items-center gap-2 text-xs text-blue-600 dark:text-blue-400">
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                      Waiting for confirmation...
                    </div>
                  )}
                  
                  {/* Copy button for assistant messages */}
                  {message.type === 'assistant' && (
                    <button
                      onClick={() => copyMessage(message.content)}
                      className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 p-1 rounded bg-[#DAA520]/10 dark:bg-[#D2BD96]/10 hover:bg-[#DAA520]/20 dark:hover:bg-[#D2BD96]/20 transition-all"
                    >
                      <Copy className="h-3 w-3 text-[#DAA520] dark:text-[#D2BD96]" />
                    </button>
                  )}
                </div>
                
                <div className={`text-xs text-[#1a1a1a]/50 dark:text-[#F2EBE2]/50 mt-1 ${
                  message.type === 'user' ? 'text-right' : 'text-left'
                }`}>
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>

              {message.type === 'user' && (
                <div className="h-8 w-8 rounded-full bg-[#DAA520] dark:bg-[#D2BD96] flex items-center justify-center flex-shrink-0">
                  <User className="h-4 w-4 text-white" />
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-3 justify-start"
          >
            <div className="h-8 w-8 rounded-full bg-gradient-to-r from-[#DAA520] to-[#D2BD96] flex items-center justify-center flex-shrink-0">
              <Bot className="h-4 w-4 text-white" />
            </div>
            <div className="bg-white/80 dark:bg-[#1a1a1a]/80 backdrop-blur-sm border border-[#DAA520]/20 dark:border-[#D2BD96]/20 rounded-2xl p-4">
              <div className="flex gap-2">
                <div className="w-2 h-2 bg-[#DAA520] dark:bg-[#D2BD96] rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-[#DAA520] dark:bg-[#D2BD96] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-[#DAA520] dark:bg-[#D2BD96] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Input Area */}
      <motion.div 
        className="p-4 bg-white/80 dark:bg-[#1a1a1a]/80 backdrop-blur-xl border-t border-[#DAA520]/20 dark:border-[#D2BD96]/20"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.2 }}
      >
        <div className="flex gap-3 items-end max-w-4xl mx-auto">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`Message ${agent.name}...`}
              disabled={loading}
              className="w-full p-4 pr-12 rounded-2xl bg-white/80 dark:bg-[#1a1a1a]/80 border border-[#DAA520]/20 dark:border-[#D2BD96]/20 text-[#1a1a1a] dark:text-[#F2EBE2] placeholder-[#1a1a1a]/50 dark:placeholder-[#F2EBE2]/50 focus:outline-none focus:ring-2 focus:ring-[#DAA520] dark:focus:ring-[#D2BD96] focus:border-transparent resize-none min-h-[56px] max-h-32 transition-all"
              rows={1}
            />
            
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              className="absolute right-2 bottom-2 p-2 rounded-xl bg-[#DAA520] hover:bg-[#B8941C] dark:bg-[#D2BD96] dark:hover:bg-[#C4AF89] text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105 active:scale-95"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
        </div>
        
        <div className="text-xs text-[#1a1a1a]/50 dark:text-[#F2EBE2]/50 text-center mt-2">
          Press Enter to send, Shift+Enter for new line
        </div>
      </motion.div>

      {/* Confirmation Dialog */}
      <AnimatePresence>
        {showConfirmation && pendingConfirmation && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-white dark:bg-[#1a1a1a] rounded-2xl border border-[#DAA520]/20 dark:border-[#D2BD96]/20 p-6 max-w-2xl w-full mx-4 shadow-2xl max-h-[80vh] overflow-y-auto"
            >
              <div className="text-center mb-6">
                <div className="h-12 w-12 rounded-full bg-gradient-to-r from-[#DAA520] to-[#D2BD96] flex items-center justify-center mx-auto mb-4">
                  <Bot className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-[#1a1a1a] dark:text-[#F2EBE2] mb-2">
                  🔍 Workflow Preview
                </h3>
                <p className="text-[#1a1a1a]/70 dark:text-[#F2EBE2]/70 text-sm">
                  Review the automation workflow before execution
                </p>
              </div>

              {/* Workflow Preview */}
              {pendingConfirmation.workflowJson && (
                <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
                  <h4 className="font-semibold text-[#1a1a1a] dark:text-[#F2EBE2] mb-3 flex items-center gap-2">
                    ⚙️ Automation Steps
                  </h4>
                  
                  <div className="space-y-3">
                    {pendingConfirmation.workflowJson?.workflow?.actions?.map((action: any, index: number) => (
                      <div key={index} className="flex items-start gap-3 p-3 bg-white dark:bg-gray-700/50 rounded-lg">
                        <div className="flex-shrink-0 w-6 h-6 bg-[#DAA520] dark:bg-[#D2BD96] text-white rounded-full flex items-center justify-center text-xs font-semibold">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <div className="font-medium text-[#1a1a1a] dark:text-[#F2EBE2] mb-1">
                            {action.node === 'mcpLLM' ? '🤖 AI Content Generation (In-House)' : 
                             action.node === 'openai' ? '🧠 AI Content Generation (OpenAI)' :
                             action.node === 'claude' ? '🎯 AI Content Generation (Claude)' :
                             action.node === 'emailSend' ? '📧 Send Email' : 
                             `⚡ ${action.node}`}
                          </div>
                          <div className="text-sm text-[#1a1a1a]/70 dark:text-[#F2EBE2]/70">
                            {action.node === 'mcpLLM' || action.node === 'openai' || action.node === 'claude' ? 
                              `Generate: "${action.parameters?.user_input || 'Content generation'}"` :
                             action.node === 'emailSend' ? 
                              `To: ${action.parameters?.toEmail || 'recipient'} | Subject: ${action.parameters?.subject || 'Generated Content'}` :
                              'Configure automation parameters'}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Estimated Credits */}
                  <div className="mt-4 p-3 bg-[#DAA520]/10 dark:bg-[#D2BD96]/10 rounded-lg">
                    <div className="flex items-center gap-2 text-sm">
                      <span className="text-[#DAA520] dark:text-[#D2BD96] font-medium">💰 Estimated Cost:</span>
                      <span className="text-[#1a1a1a] dark:text-[#F2EBE2]">2-6 credits (depending on AI service)</span>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Main Message */}
              <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-200 dark:border-blue-700">
                <p className="text-[#1a1a1a] dark:text-[#F2EBE2] text-sm leading-relaxed">
                  {pendingConfirmation.prompt}
                </p>
              </div>
              
              <div className="flex gap-3">
                <button
                  onClick={() => handleConfirmation(false)}
                  disabled={loading}
                  className="flex-1 px-4 py-3 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-[#1a1a1a] dark:text-[#F2EBE2] rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                  ❌ Cancel
                </button>
                <button
                  onClick={() => handleConfirmation(true)}
                  disabled={loading}
                  className="flex-1 px-4 py-3 bg-gradient-to-r from-[#DAA520] to-[#D2BD96] hover:from-[#B8941C] hover:to-[#C4AF89] text-white rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-lg"
                >
                  {loading ? '⚙️ Executing...' : '✅ Confirm & Execute'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* AI Service Selection Dialog */}
      <AnimatePresence>
        {showAIServiceSelection && pendingAISelection && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-white dark:bg-[#1a1a1a] rounded-2xl border border-[#DAA520]/20 dark:border-[#D2BD96]/20 p-6 max-w-lg w-full mx-4 shadow-2xl"
            >
              <div className="text-center mb-6">
                <div className="h-12 w-12 rounded-full bg-gradient-to-r from-[#DAA520] to-[#D2BD96] flex items-center justify-center mx-auto mb-4">
                  <Bot className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-[#1a1a1a] dark:text-[#F2EBE2] mb-2">
                  Choose AI Service
                </h3>
                <p className="text-[#1a1a1a]/70 dark:text-[#F2EBE2]/70 text-sm">
                  Select your preferred AI service for content generation
                </p>
              </div>
              
              <div className="space-y-3 mb-6">
                {pendingAISelection.aiServiceOptions.map((service: any) => (
                  <button
                    key={service.id}
                    onClick={() => handleAIServiceSelection(service.id)}
                    disabled={loading}
                    className="w-full p-4 text-left bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-700/50 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed border border-gray-200 dark:border-gray-700 hover:border-[#DAA520]/30 dark:hover:border-[#D2BD96]/30"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-semibold text-[#1a1a1a] dark:text-[#F2EBE2]">
                        {service.name}
                      </h4>
                      <span className="text-xs bg-[#DAA520] dark:bg-[#D2BD96] text-white px-2 py-1 rounded-full">
                        {service.credits} credits
                      </span>
                    </div>
                    <p className="text-sm text-[#1a1a1a]/70 dark:text-[#F2EBE2]/70 mb-2">
                      {service.description}
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {service.features?.map((feature: string, index: number) => (
                        <span
                          key={index}
                          className="text-xs bg-[#DAA520]/10 dark:bg-[#D2BD96]/10 text-[#DAA520] dark:text-[#D2BD96] px-2 py-1 rounded-full"
                        >
                          {feature}
                        </span>
                      ))}
                    </div>
                  </button>
                ))}
              </div>
              
              <button
                onClick={() => {
                  setShowAIServiceSelection(false);
                  setPendingAISelection(null);
                }}
                disabled={loading}
                className="w-full px-4 py-3 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-[#1a1a1a] dark:text-[#F2EBE2] rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                Cancel
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Workflow Preview Dialog */}
      <AnimatePresence>
        {(() => {
          console.log('📧 DIALOG RENDER CHECK:', {
            showWorkflowDialog,
            hasWorkflowPreview: !!workflowPreview,
            hasEmailPreview: workflowPreview?.workflow_preview?.email_preview ? true : false,
            dialogShouldShow: showWorkflowDialog && workflowPreview
          });
          return showWorkflowDialog && workflowPreview;
        })() && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-white dark:bg-[#1a1a1a] rounded-2xl border border-[#DAA520]/20 dark:border-[#D2BD96]/20 p-6 max-w-2xl w-full mx-4 shadow-2xl max-h-[80vh] overflow-y-auto"
            >
              <div className="text-center mb-6">
                <div className="h-12 w-12 rounded-full bg-gradient-to-r from-[#DAA520] to-[#D2BD96] flex items-center justify-center mx-auto mb-4">
                  <Bot className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-[#1a1a1a] dark:text-[#F2EBE2] mb-2">
                  {workflowPreview.workflow_preview?.title || 'Workflow Preview'}
                </h3>
                <p className="text-[#1a1a1a]/70 dark:text-[#F2EBE2]/70">
                  {workflowPreview.workflow_preview?.description || 'Review the automation workflow before execution'}
                </p>
              </div>
              
              {workflowPreview.workflow_preview?.steps && (
                <div className="space-y-4 mb-6">
                  <h4 className="font-semibold text-[#1a1a1a] dark:text-[#F2EBE2] text-lg">
                    Workflow Steps:
                  </h4>
                  {workflowPreview.workflow_preview.steps.map((step: any, index: number) => (
                    <div
                      key={index}
                      className="flex items-start gap-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700"
                    >
                      <div className="flex-shrink-0 w-8 h-8 bg-[#DAA520] dark:bg-[#D2BD96] rounded-full flex items-center justify-center text-white font-semibold text-sm">
                        {step.step}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-lg">{step.icon}</span>
                          <h5 className="font-semibold text-[#1a1a1a] dark:text-[#F2EBE2]">
                            {step.action}
                          </h5>
                        </div>
                        <p className="text-sm text-[#1a1a1a]/70 dark:text-[#F2EBE2]/70">
                          {step.details}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              {/* Email Preview Section */}
              {workflowPreview.workflow_preview?.email_preview && (
                <div className="mb-6">
                  <h4 className="font-semibold text-[#1a1a1a] dark:text-[#F2EBE2] text-lg mb-4 flex items-center gap-2">
                    📧 Email Preview
                  </h4>
                  <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700 p-4">
                    <div className="space-y-3">
                      <div className="flex gap-4">
                        <span className="font-medium text-[#DAA520] dark:text-[#D2BD96] min-w-[60px]">TO:</span>
                        <span className="text-[#1a1a1a] dark:text-[#F2EBE2]">{workflowPreview.workflow_preview.email_preview.to}</span>
                      </div>
                      <div className="flex gap-4">
                        <span className="font-medium text-[#DAA520] dark:text-[#D2BD96] min-w-[60px]">SUBJECT:</span>
                        <input
                          type="text"
                          value={editableEmailSubject}
                          onChange={(e) => setEditableEmailSubject(e.target.value)}
                          className="flex-1 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-[#1a1a1a] dark:text-[#F2EBE2] focus:outline-none focus:ring-2 focus:ring-[#DAA520]/50"
                        />
                      </div>
                      <div className="border-t border-gray-200 dark:border-gray-700 pt-3">
                        <span className="font-medium text-[#DAA520] dark:text-[#D2BD96] block mb-2">CONTENT:</span>
                        <textarea
                          value={editableEmailContent}
                          onChange={(e) => setEditableEmailContent(e.target.value)}
                          rows={8}
                          className="w-full bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4 text-[#1a1a1a] dark:text-[#F2EBE2] focus:outline-none focus:ring-2 focus:ring-[#DAA520]/50 font-mono text-sm resize-vertical"
                          placeholder="Enter email content..."
                        />
                      </div>
                      <div className="flex items-center gap-2 text-sm text-[#1a1a1a]/70 dark:text-[#F2EBE2]/70">
                        <span className="w-2 h-2 bg-[#DAA520] rounded-full"></span>
                        Content will be generated by {workflowPreview.workflow_preview.email_preview.ai_service?.toUpperCase()} AI
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              <div className="grid grid-cols-2 gap-4 mb-6 p-4 bg-[#DAA520]/10 dark:bg-[#D2BD96]/10 rounded-xl">
                <div>
                  <p className="text-sm font-medium text-[#DAA520] dark:text-[#D2BD96]">
                    Estimated Cost
                  </p>
                  <p className="text-lg font-bold text-[#1a1a1a] dark:text-[#F2EBE2]">
                    {workflowPreview.estimated_credits || 0} Credits
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-[#DAA520] dark:text-[#D2BD96]">
                    AI Service
                  </p>
                  <p className="text-lg font-bold text-[#1a1a1a] dark:text-[#F2EBE2]">
                    {workflowPreview.ai_service_used?.toUpperCase() || 'N/A'}
                  </p>
                </div>
              </div>
              
              <div className="flex gap-3">
                <button
                  onClick={() => handleEmailPreviewConfirmation(false)}
                  disabled={loading}
                  className="flex-1 px-4 py-3 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-[#1a1a1a] dark:text-[#F2EBE2] rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleEmailPreviewConfirmation(true)}
                  disabled={loading}
                  className="flex-1 px-4 py-3 bg-gradient-to-r from-[#DAA520] to-[#D2BD96] hover:from-[#B8941C] hover:to-[#C0A875] text-white rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-lg"
                >
                  {loading ? 'Sending Email...' : 'Send Email 📧'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
