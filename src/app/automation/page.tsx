'use client';

import { useState, useRef, useEffect } from 'react';

type WorkflowNode = {
  name: string;
  type: string;
  position: number[];
  parameters?: any;
};

type WorkflowData = {
  nodes: WorkflowNode[];
  connections: any;
  metadata?: any;
};

type AutomationResponse = {
  done: boolean;
  success?: boolean;
  json?: WorkflowData;
  message?: string;
  n8n_deployment?: {
    deployed: boolean;
    workflow_id?: string;
    workflow_url?: string;
    message: string;
    error?: string;
  };
  error?: string;
  // AI Service Selection Response
  status?: string;
  ai_service_options?: AIServiceOption[];
  original_request?: string;
};

type AIServiceOption = {
  id: string;
  name: string;
  description: string;
  credits: number;
  features: string[];
};

export default function MinimalAutomationPage() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AutomationResponse | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'checking' | 'connected' | 'error'>('checking');
  const [showAIServiceModal, setShowAIServiceModal] = useState(false);
  const [selectedAIService, setSelectedAIService] = useState<string | null>(null);
  const [originalRequest, setOriginalRequest] = useState('');
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    checkBackendConnection();
  }, []);

  useEffect(() => {
    if (result?.json) {
      drawWorkflow(result.json);
    }
  }, [result]); // drawWorkflow is defined inside the component, so this is safe

  const checkBackendConnection = async () => {
    try {
      const response = await fetch('http://localhost:8002/health');
      if (response.ok) {
        setConnectionStatus('connected');
      } else {
        setConnectionStatus('error');
      }
    } catch (error) {
      setConnectionStatus('error');
    }
  };

  const drawWorkflow = (workflow: WorkflowData) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Set canvas size
    canvas.width = 800;
    canvas.height = 500;

    // Draw background
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw grid
    ctx.strokeStyle = '#16213e';
    ctx.lineWidth = 1;
    for (let x = 0; x < canvas.width; x += 20) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += 20) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }

    // Draw connections first
    const { connections } = workflow;
    ctx.strokeStyle = '#4ade80';
    ctx.lineWidth = 2;

    Object.entries(connections).forEach(([nodeKey, nodeConnections]: [string, any]) => {
      const sourceNode = workflow.nodes.find(n => n.name === nodeKey);
      if (!sourceNode || !nodeConnections.main) return;

      nodeConnections.main[0]?.forEach((connection: any) => {
        const targetNode = workflow.nodes.find(n => n.name === connection.node);
        if (!targetNode) return;

        const sourceX = sourceNode.position[0];
        const sourceY = sourceNode.position[1];
        const targetX = targetNode.position[0];
        const targetY = targetNode.position[1];

        // Draw arrow
        ctx.beginPath();
        ctx.moveTo(sourceX + 60, sourceY + 20);
        ctx.lineTo(targetX - 10, targetY + 20);
        
        // Arrow head
        const angle = Math.atan2(targetY - sourceY, targetX - sourceX);
        ctx.lineTo(targetX - 15, targetY + 15);
        ctx.moveTo(targetX - 10, targetY + 20);
        ctx.lineTo(targetX - 15, targetY + 25);
        ctx.stroke();
      });
    });

    // Draw nodes
    workflow.nodes.forEach((node, index) => {
      const x = node.position[0];
      const y = node.position[1];

      // Node background
      ctx.fillStyle = getNodeColor(node.type);
      ctx.fillRect(x, y, 120, 40);

      // Node border
      ctx.strokeStyle = '#374151';
      ctx.lineWidth = 2;
      ctx.strokeRect(x, y, 120, 40);

      // Node text
      ctx.fillStyle = '#ffffff';
      ctx.font = '12px Arial';
      ctx.textAlign = 'center';
      ctx.fillText(node.name, x + 60, y + 25);

      // Node icon
      ctx.font = '16px Arial';
      ctx.fillText(getNodeIcon(node.type), x + 10, y + 25);
    });
  };

  const getNodeColor = (type: string): string => {
    if (type.includes('cron')) return '#6b7280';
    if (type.includes('email')) return '#3b82f6';
    if (type.includes('weather')) return '#10b981';
    if (type.includes('http')) return '#8b5cf6';
    return '#6b7280';
  };

  const getNodeIcon = (type: string): string => {
    if (type.includes('cron')) return '⏰';
    if (type.includes('email')) return '📧';
    if (type.includes('weather')) return '🌤️';
    if (type.includes('http')) return '🔗';
    return '⚙️';
  };

  const handleGenerate = async () => {
    if (!input.trim() || loading) return;

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8002/api/chat/mcpai', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input.trim(),
          user_id: 'automation_user'
        }),
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`);
      }

      const data: AutomationResponse = await response.json();
      
      // Check if this is an AI service selection response
      if (data.status === 'ai_service_selection' && data.ai_service_options) {
        setOriginalRequest(data.original_request || input.trim());
        setResult(data);
        setShowAIServiceModal(true);
      } else {
        setResult(data);
      }

    } catch (error) {
      setResult({
        done: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        message: 'Failed to generate automation'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAIServiceSelection = async (serviceId: string) => {
    setSelectedAIService(serviceId);
    setShowAIServiceModal(false);
    setLoading(true);

    try {
      // Resubmit the request with the selected AI service
      const messageWithService = `service:${serviceId} ${originalRequest}`;
      
      const response = await fetch('http://localhost:8002/api/chat/mcpai', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageWithService,
          user_id: 'automation_user'
        }),
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`);
      }

      const data: AutomationResponse = await response.json();
      setResult(data);

    } catch (error) {
      setResult({
        done: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        message: 'Failed to generate automation with selected AI service'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async () => {
    if (!result?.n8n_deployment?.workflow_id) return;

    try {
      const response = await fetch('http://localhost:8002/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow_id: result.n8n_deployment.workflow_id
        }),
      });

      const data = await response.json();
      console.log('Execution result:', data);
    } catch (error) {
      console.error('Execution failed:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">🤖 AI Automation Bridge</h1>
            <p className="text-gray-400 text-sm">
              Generate → Visualize → Deploy to n8n
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className={`px-3 py-1 rounded text-xs ${
              connectionStatus === 'connected' ? 'bg-green-600' : 
              connectionStatus === 'error' ? 'bg-red-600' : 'bg-gray-600'
            }`}>
              {connectionStatus === 'connected' ? '🟢 Backend' : 
               connectionStatus === 'error' ? '🔴 Backend' : '🟡 Backend'}
            </div>
            <div className="px-3 py-1 rounded text-xs bg-blue-600">
              🟢 n8n:5678
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto p-6">
        {/* Input Section */}
        <div className="bg-gray-800 rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Describe Your Automation</h2>
          <div className="flex gap-4">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="e.g., Send an email to user@domain.com every day at 9AM"
              className="flex-1 bg-gray-700 rounded-lg px-4 py-3 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              disabled={loading}
            />
            <button
              onClick={handleGenerate}
              disabled={loading || !input.trim()}
              className="px-6 py-3 bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Generating...
                </div>
              ) : (
                'Generate & Deploy'
              )}
            </button>
          </div>
        </div>

        {/* Results Section */}
        {result && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Workflow Visualizer */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Workflow Visualization</h3>
              <canvas
                ref={canvasRef}
                className="w-full h-64 border border-gray-700 rounded-lg"
                style={{ maxWidth: '100%', height: '300px' }}
              />
              {result.json && (
                <div className="mt-4 text-sm text-gray-400">
                  {result.json.nodes.length} nodes • {Object.keys(result.json.connections).length} connections
                </div>
              )}
            </div>

            {/* Deployment Status */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Deployment Status</h3>
              
              {result.n8n_deployment?.deployed ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <span className="text-green-400">✅</span>
                    <span>Successfully deployed to n8n</span>
                  </div>
                  
                  <div className="bg-gray-700 rounded-lg p-4">
                    <p className="text-sm text-gray-300 mb-2">Workflow ID:</p>
                    <p className="font-mono text-blue-400">{result.n8n_deployment.workflow_id}</p>
                  </div>

                  <div className="flex gap-3">
                    <a
                      href={result.n8n_deployment.workflow_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-green-600 rounded-lg hover:bg-green-700 text-sm"
                    >
                      Open in n8n
                    </a>
                    <button
                      onClick={handleExecute}
                      className="px-4 py-2 bg-blue-600 rounded-lg hover:bg-blue-700 text-sm"
                    >
                      Execute Now
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <span className="text-gray-400">⚠️</span>
                    <span>Not deployed to n8n</span>
                  </div>
                  
                  <div className="bg-gray-700 rounded-lg p-4">
                    <p className="text-sm text-gray-300">
                      {result.n8n_deployment?.message || result.message}
                    </p>
                  </div>

                  {result.json && (
                    <div className="bg-gray-700 rounded-lg p-4">
                      <p className="text-sm text-gray-300 mb-2">Generated JSON:</p>
                      <pre className="text-xs text-green-400 overflow-auto max-h-40">
                        {JSON.stringify(result.json, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Quick Examples */}
        {!result && (
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Quick Examples</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { icon: '📧', text: 'Send email to user@domain.com every day at 9AM' },
                { icon: '🌤️', text: 'Get weather data every morning at 8AM' },
                { icon: '🔗', text: 'Create a webhook for processing customer data' }
              ].map((example, index) => (
                <button
                  key={index}
                  onClick={() => setInput(example.text)}
                  className="text-left p-4 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
                >
                  <div className="text-lg mb-2">{example.icon}</div>
                  <div className="text-sm text-gray-300">{example.text}</div>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* AI Service Selection Modal */}
      {showAIServiceModal && result?.ai_service_options && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold">Choose AI Service</h2>
              <button
                onClick={() => setShowAIServiceModal(false)}
                className="text-gray-400 hover:text-white text-2xl"
              >
                ×
              </button>
            </div>
            
            <p className="text-gray-300 mb-6">
              {result.message}
            </p>

            <div className="space-y-4">
              {result.ai_service_options.map((service) => (
                <div
                  key={service.id}
                  onClick={() => handleAIServiceSelection(service.id)}
                  className="bg-gray-700 rounded-lg p-4 hover:bg-gray-600 cursor-pointer transition-colors border-2 border-transparent hover:border-blue-500"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-lg font-semibold">{service.name}</h3>
                    <div className="flex items-center gap-2">
                      <span className="bg-blue-600 text-white text-xs px-2 py-1 rounded">
                        {service.credits} credits
                      </span>
                    </div>
                  </div>
                  
                  <p className="text-gray-300 text-sm mb-3">{service.description}</p>
                  
                  <div className="flex flex-wrap gap-2">
                    {service.features.map((feature, index) => (
                      <span
                        key={index}
                        className="bg-gray-600 text-gray-200 text-xs px-2 py-1 rounded"
                      >
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 text-center">
              <button
                onClick={() => setShowAIServiceModal(false)}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-500"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
