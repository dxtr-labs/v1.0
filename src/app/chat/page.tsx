'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Send, Bot, User, FileCode, Settings } from 'lucide-react';
import { useSearchParams, useRouter } from 'next/navigation';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
}

interface WorkflowInfo {
  id: string;
  name: string;
  fileName: string;
  description: string;
  nodeCount: number;
}

const ChatPage = () => {
  const searchParams = useSearchParams();
  const router = useRouter();
  const workflowId = searchParams.get('workflow');
  const fileName = searchParams.get('file');
  const agentId = searchParams.get('agent_id') || searchParams.get('agentId');

  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [workflowInfo, setWorkflowInfo] = useState<WorkflowInfo | null>(null);

  useEffect(() => {
    // If this is an agent chat, redirect to the agent chat interface
    if (agentId && !workflowId) {
      router.push(`/dashboard/agents/${agentId}/chat?agentId=${agentId}`);
      return;
    }

    if (workflowId && fileName) {
      // Initialize with welcome message
      const welcomeMessage: Message = {
        id: '1',
        type: 'bot',
        content: `Hi! I'm here to help you with the "${fileName}" workflow. You can ask me questions about how it works, how to modify it, or how to use it in your automation. What would you like to know?`,
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);

      // Set workflow info
      setWorkflowInfo({
        id: workflowId,
        name: fileName.replace('.json', '').replace(/_/g, ' ').replace(/^\d+\s*/, ''),
        fileName: fileName,
        description: `Automation workflow loaded from ${fileName}`,
        nodeCount: Math.floor(Math.random() * 10) + 2 // Mock data for now
      });
    }
  }, [workflowId, fileName, agentId, router]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: `I understand you're asking about "${inputMessage}". This workflow contains ${workflowInfo?.nodeCount || 'several'} automation steps. Based on the filename "${fileName}", this appears to be a ${getCategoryFromFileName(fileName || '')} automation. Would you like me to explain specific parts of the workflow or help you modify it?`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botResponse]);
      setIsLoading(false);
    }, 1000);
  };

  const getCategoryFromFileName = (fileName: string) => {
    if (fileName.includes('Telegram')) return 'communication';
    if (fileName.includes('GoogleSheets') || fileName.includes('Spreadsheet')) return 'data management';
    if (fileName.includes('HTTP') || fileName.includes('Webhook')) return 'API integration';
    if (fileName.includes('Schedule') || fileName.includes('Cron')) return 'scheduling';
    if (fileName.includes('Email') || fileName.includes('Gmail')) return 'email';
    return 'general automation';
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // If no workflow is selected, show error
  if (!workflowId && !agentId) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle>No Workflow Selected</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">Please select a workflow to start chatting.</p>
            <Button onClick={() => router.push('/dashboard/automation')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Workflows
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.push('/dashboard/automation')}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Workflows
            </Button>
            <div>
              <h1 className="text-xl font-semibold">
                {workflowInfo?.name || 'Workflow Chat'}
              </h1>
              <p className="text-sm text-gray-500">
                {workflowInfo?.fileName || 'Loading...'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge className="bg-blue-100 text-blue-800">
              <FileCode className="h-3 w-3 mr-1" />
              {workflowInfo?.nodeCount || 0} steps
            </Badge>
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4 mr-2" />
              Configure
            </Button>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex flex-col h-[calc(100vh-80px)]">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`flex items-start gap-3 max-w-[70%] ${
                    message.type === 'user' ? 'flex-row-reverse' : 'flex-row'
                  }`}
                >
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      message.type === 'user'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 text-gray-600'
                    }`}
                  >
                    {message.type === 'user' ? (
                      <User className="h-4 w-4" />
                    ) : (
                      <Bot className="h-4 w-4" />
                    )}
                  </div>
                  <div
                    className={`rounded-lg px-4 py-2 ${
                      message.type === 'user'
                        ? 'bg-blue-500 text-white'
                        : 'bg-white border border-gray-200'
                    }`}
                  >
                    <p className="text-sm">{message.content}</p>
                    <p
                      className={`text-xs mt-1 ${
                        message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}
                    >
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center">
                    <Bot className="h-4 w-4" />
                  </div>
                  <div className="bg-white border border-gray-200 rounded-lg px-4 py-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 bg-white p-6">
          <div className="max-w-4xl mx-auto">
            <div className="flex gap-4">
              <div className="flex-1">
                <Textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me about this workflow..."
                  className="min-h-[44px] max-h-32 resize-none"
                  rows={1}
                />
              </div>
              <Button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading}
                className="self-end"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex justify-between items-center mt-2">
              <p className="text-xs text-gray-500">
                Press Enter to send, Shift+Enter for new line
              </p>
              <div className="flex gap-2">
                <Button variant="outline" size="sm">
                  View Code
                </Button>
                <Button variant="outline" size="sm">
                  Export
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
