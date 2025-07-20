// src/app/automation/advanced/page.tsx
// Advanced automation page with interactive workflow builder

'use client';

import React, { useState, useEffect } from 'react';
import InteractiveWorkflowBuilder from '@/components/workflow/InteractiveWorkflowBuilder';

interface Workflow {
  id: string;
  name: string;
  description?: string;
  nodes: any[];
  connections: any[];
  active: boolean;
  nodeCount: number;
  createdAt: string;
  updatedAt: string;
}

const AdvancedAutomationPage: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentWorkflow, setCurrentWorkflow] = useState<any>(null);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [message, setMessage] = useState('');
  const [availableNodes, setAvailableNodes] = useState<any[]>([]);

  // Load user workflows on component mount
  useEffect(() => {
    loadWorkflows();
    loadAvailableNodes();
  }, []);

  const loadWorkflows = async () => {
    try {
      const response = await fetch('/api/automation/advanced', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'list_workflows' })
      });

      const data: any = await response.json();
      if (data.success) {
        setWorkflows(data.workflows);
      }
    } catch (error) {
      console.error('Failed to load workflows:', error);
    }
  };

  const loadAvailableNodes = async () => {
    try {
      const response = await fetch('/api/automation/advanced?action=available_nodes');
      const data: any = await response.json();
      if (data.success) {
        setAvailableNodes(data.nodes);
      }
    } catch (error) {
      console.error('Failed to load available nodes:', error);
    }
  };

  const createWorkflow = async () => {
    if (!prompt.trim()) {
      setMessage('Please enter a prompt to create a workflow');
      return;
    }

    setIsLoading(true);
    setMessage('');

    try {
      const response = await fetch('/api/automation/advanced', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'create_workflow',
          prompt: prompt.trim()
        })
      });

      const data: any = await response.json();
      
      if (data.success) {
        setCurrentWorkflow(data.workflow);
        setMessage(`✅ Workflow "${data.workflow.name}" created successfully!`);
        setPrompt('');
        loadWorkflows(); // Refresh the list
      } else {
        setMessage(`❌ Error: ${data.error}`);
      }
    } catch (error) {
      setMessage(`❌ Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const executeWorkflow = async (workflowId: string) => {
    setIsLoading(true);
    setMessage('');

    try {
      const response = await fetch('/api/automation/advanced', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'execute_workflow',
          workflowId,
          triggerData: { timestamp: new Date().toISOString() }
        })
      });

      const data: any = await response.json();
      
      if (data.success) {
        setMessage(`✅ Workflow executed successfully! Status: ${data.execution.status}`);
      } else {
        setMessage(`❌ Execution error: ${data.error}`);
      }
    } catch (error) {
      setMessage(`❌ Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const loadWorkflow = async (workflowId: string) => {
    try {
      const response = await fetch('/api/automation/advanced', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'get_workflow',
          workflowId
        })
      });

      const data: any = await response.json();
      if (data.success) {
        setCurrentWorkflow(data.workflow);
        setMessage(`Loaded workflow: ${data.workflow.name}`);
      } else {
        setMessage(`❌ Error loading workflow: ${data.error}`);
      }
    } catch (error) {
      setMessage(`❌ Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const samplePrompts = [
    "Send a welcome email to new users",
    "Fetch data from an API and store it in database",
    "Process text with AI and send results via email",
    "Create a data transformation workflow",
    "Set up automated database backup notifications"
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🤖 Advanced Automation Studio
          </h1>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Create powerful workflows using real n8n nodes. Click on nodes to edit their parameters and build custom automation flows.
          </p>
        </div>

        {/* Workflow Creation Section */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-semibold mb-4">Create New Workflow</h2>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Describe your automation workflow:
            </label>
            <textarea
              className="w-full p-3 border border-gray-300 rounded-lg text-sm"
              rows={3}
              placeholder="Example: Send a welcome email to new users with their account details..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
          </div>

          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-2">Try these sample prompts:</p>
            <div className="flex flex-wrap gap-2">
              {samplePrompts.map((sample, index) => (
                <button
                  key={index}
                  onClick={() => setPrompt(sample)}
                  className="px-3 py-1 bg-blue-100 text-blue-700 rounded-md text-sm hover:bg-blue-200 transition-colors"
                >
                  {sample}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={createWorkflow}
            disabled={isLoading || !prompt.trim()}
            className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? '🔄 Creating...' : '🚀 Create Workflow'}
          </button>
        </div>

        {/* Message Display */}
        {message && (
          <div className={`p-4 rounded-lg mb-6 ${
            message.includes('❌') 
              ? 'bg-red-100 text-red-700 border border-red-200'
              : 'bg-green-100 text-green-700 border border-green-200'
          }`}>
            {message}
          </div>
        )}

        {/* Current Workflow Display */}
        {currentWorkflow && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-semibold">
                {currentWorkflow.name}
              </h2>
              <button
                onClick={() => executeWorkflow(currentWorkflow.id)}
                disabled={isLoading}
                className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 disabled:bg-gray-300 transition-colors"
              >
                {isLoading ? '⏳ Running...' : '▶️ Execute'}
              </button>
            </div>
            
            <p className="text-gray-600 mb-4">{currentWorkflow.description}</p>
            
            <div className="text-sm text-gray-500 mb-4">
              Nodes: {currentWorkflow.nodes?.length || 0} | 
              Connections: {currentWorkflow.connections?.length || 0}
            </div>

            <InteractiveWorkflowBuilder 
              workflowData={currentWorkflow}
              onWorkflowChange={setCurrentWorkflow}
            />
          </div>
        )}

        {/* Available Nodes Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-semibold mb-4">Available Nodes</h3>
            <div className="grid grid-cols-2 gap-2 max-h-60 overflow-y-auto">
              {availableNodes.map((node) => (
                <div
                  key={node.name}
                  className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span>{node.icon}</span>
                    <span className="font-medium text-sm">{node.displayName}</span>
                  </div>
                  <div className="text-xs text-gray-500">{node.category}</div>
                  <div className="text-xs text-gray-600 mt-1">
                    {node.description.substring(0, 50)}...
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* User Workflows */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-semibold mb-4">Your Workflows</h3>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {workflows.length === 0 ? (
                <p className="text-gray-500 text-sm">No workflows created yet</p>
              ) : (
                workflows.map((workflow) => (
                  <div
                    key={workflow.id}
                    className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
                    onClick={() => loadWorkflow(workflow.id)}
                  >
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-medium text-sm">{workflow.name}</span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        workflow.active 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-gray-100 text-gray-600'
                      }`}>
                        {workflow.active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    <div className="text-xs text-gray-500">
                      {workflow.nodeCount} nodes • {new Date(workflow.updatedAt).toLocaleDateString()}
                    </div>
                    {workflow.description && (
                      <div className="text-xs text-gray-600 mt-1">
                        {workflow.description.substring(0, 60)}...
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Help Section */}
        <div className="bg-blue-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-3 text-blue-900">
            💡 How to Use the Advanced Automation Studio
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800">
            <div>
              <h4 className="font-medium mb-2">Creating Workflows:</h4>
              <ul className="space-y-1 text-blue-700">
                <li>• Describe your automation in natural language</li>
                <li>• The system will generate appropriate n8n nodes</li>
                <li>• Click on any node to edit its parameters</li>
                <li>• Execute workflows to see them in action</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">Available Node Types:</h4>
              <ul className="space-y-1 text-blue-700">
                <li>• 📧 Email sending and processing</li>
                <li>• 🌐 HTTP requests and API integrations</li>
                <li>• 🗄️ Database operations</li>
                <li>• 🤖 AI text processing</li>
                <li>• 💻 Custom code execution</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedAutomationPage;
