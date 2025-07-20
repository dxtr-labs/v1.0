'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Play, Save, Download, Upload, Plus, Trash2, Settings, UserPlus } from 'lucide-react';

// Types
interface WorkflowNode {
  id: string;
  type: string;
  name: string;
  position: { x: number; y: number };
  parameters: Record<string, any>;
  credentials?: Record<string, any>;
}

interface WorkflowData {
  id: string;
  name: string;
  description?: string;
  nodes: WorkflowNode[];
  connections: Array<{
    source: string;
    target: string;
    sourceOutput?: string;
    targetInput?: string;
  }>;
}

const WorkflowBuilder = () => {
  const searchParams = useSearchParams();
  const workflowId = searchParams.get('workflow');
  const fileName = searchParams.get('file');
  
  const [workflowData, setWorkflowData] = useState<WorkflowData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [isBuilding, setIsBuilding] = useState(false);

  const loadWorkflowData = async () => {
    if (!fileName) return;
    
    try {
      setIsLoading(true);
      
      // For now, we'll simulate loading the workflow JSON
      // In a real implementation, you'd fetch from an API
      const response = await fetch(`/api/automation/workflows/${fileName}`);
      if (response.ok) {
        const data = await response.json() as WorkflowData;
        setWorkflowData(data);
      } else {
        // Fallback: create a mock workflow based on the filename
        createMockWorkflow();
      }
    } catch (error) {
      console.error('Error loading workflow:', error);
      createMockWorkflow();
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!fileName) return;
    
    const createMockWorkflow = () => {
      // Create a mock workflow with some nodes for demonstration
      const mockNodes: WorkflowNode[] = [
        {
          id: 'start',
          type: 'trigger',
          name: 'Start Trigger',
          position: { x: 100, y: 100 },
          parameters: { triggerType: 'manual' }
        },
        {
          id: 'node1',
          type: 'action',
          name: 'HTTP Request',
          position: { x: 300, y: 100 },
          parameters: { url: '', method: 'GET' }
        },
        {
          id: 'node2',
          type: 'condition',
          name: 'Check Response',
          position: { x: 500, y: 100 },
          parameters: { condition: 'response.status === 200' }
        },
        {
          id: 'node3',
          type: 'action',
          name: 'Send Email',
          position: { x: 700, y: 100 },
          parameters: { to: '', subject: '', body: '' }
        }
      ];

      setWorkflowData({
        id: workflowId || 'demo',
        name: fileName?.replace('.json', '').replace(/_/g, ' ') || 'Demo Workflow',
        description: 'Automated workflow with multiple steps',
        nodes: mockNodes,
        connections: [
          { source: 'start', target: 'node1' },
          { source: 'node1', target: 'node2' },
          { source: 'node2', target: 'node3' }
        ]
      });
    };
    
    const loadData = async () => {
      try {
        setIsLoading(true);
        
        // For now, we'll simulate loading the workflow JSON
        // In a real implementation, you'd fetch from an API
        const response = await fetch(`/api/automation/workflows/${fileName}`);
        if (response.ok) {
          const data = await response.json() as WorkflowData;
          setWorkflowData(data);
        } else {
          // Fallback: create a mock workflow based on the filename
          createMockWorkflow();
        }
      } catch (error) {
        console.error('Error loading workflow:', error);
        createMockWorkflow();
      } finally {
        setIsLoading(false);
      }
    };
    
    loadData();
  }, [workflowId, fileName]);

  const handleNodeClick = (nodeId: string) => {
    setSelectedNode(nodeId);
  };

  const handleNodeUpdate = (nodeId: string, updates: Partial<WorkflowNode>) => {
    if (!workflowData) return;
    
    setWorkflowData(prev => ({
      ...prev!,
      nodes: prev!.nodes.map(node => 
        node.id === nodeId ? { ...node, ...updates } : node
      )
    }));
  };

  const handleLoadToAgent = async () => {
    setIsBuilding(true);
    
    try {
      if (!workflowData) {
        alert('No workflow data available');
        return;
      }

      // Prepare workflow data for agent
      const agentData = {
        name: workflowData.name,
        nodes: workflowData.nodes,
        filename: searchParams?.get('file') || 'unknown',
        originalWorkflow: workflowData
      };
      
      // Encode the data for URL parameter
      const encodedData = encodeURIComponent(JSON.stringify(agentData));
      
      // Redirect to agent creation page
      window.location.href = `/dashboard/automation/agent?workflow=${encodedData}`;
    } catch (error) {
      console.error('Error loading to agent:', error);
      alert('Error loading workflow to agent');
    } finally {
      setIsBuilding(false);
    }
  };

  const getNodeTypeColor = (type: string) => {
    const colors = {
      trigger: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
      action: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
      condition: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300',
      transform: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300'
    };
    return colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300';
  };

  if (isLoading) {
    return (
      <div className="h-full w-full overflow-auto">
        <div className="container mx-auto p-6">
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#3B82F6] dark:border-[#8B5CF6] mx-auto"></div>
            <p className="mt-4 text-[#0F172A]/70 dark:text-[#F8FAFC]/70">Loading workflow...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!workflowData) {
    return (
      <div className="h-full w-full overflow-auto">
        <div className="container mx-auto p-6">
          <div className="text-center py-8">
            <p className="text-[#0F172A]/70 dark:text-[#F8FAFC]/70">Workflow not found</p>
            <Button 
              onClick={() => window.history.back()} 
              className="mt-4"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Go Back
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full overflow-auto">
      <div className="container mx-auto p-6 min-h-full">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <Button 
              variant="secondary" 
              size="sm"
              onClick={() => window.history.back()}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-[#0F172A] dark:text-[#F8FAFC]">
                Workflow Builder
              </h1>
              <p className="text-[#0F172A]/70 dark:text-[#F8FAFC]/70">
                {workflowData.name} • {workflowData.nodes.length} nodes
              </p>
            </div>
          </div>
          
          {/* Action Buttons */}
          <div className="flex gap-2 flex-wrap">
            <Button 
              onClick={handleLoadToAgent}
              disabled={isBuilding}
              className="flex items-center gap-2"
            >
              {isBuilding ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Loading...
                </>
              ) : (
                <>
                  <UserPlus className="h-4 w-4" />
                  Load to Agent
                </>
              )}
            </Button>
            <Button variant="secondary" className="flex items-center gap-2">
              <Save className="h-4 w-4" />
              Save
            </Button>
            <Button variant="secondary" className="flex items-center gap-2">
              <Download className="h-4 w-4" />
              Export
            </Button>
          </div>
        </div>

        {/* Workflow Nodes Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-8">
          {workflowData.nodes.map((node, index) => (
            <Card 
              key={node.id}
              className={`cursor-pointer transition-all duration-200 hover:scale-105 bg-white/60 dark:bg-[#0F172A]/60 backdrop-blur-sm border-2 ${
                selectedNode === node.id 
                  ? 'border-[#3B82F6] dark:border-[#8B5CF6] ring-2 ring-[#3B82F6]/20 dark:ring-[#8B5CF6]/20' 
                  : 'border-[#3B82F6]/20 dark:border-[#8B5CF6]/20 hover:border-[#3B82F6]/40 dark:hover:border-[#8B5CF6]/40'
              }`}
              onClick={() => handleNodeClick(node.id)}
            >
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-2">
                    <span className="text-lg font-bold text-[#3B82F6] dark:text-[#8B5CF6]">
                      {index + 1}
                    </span>
                    <CardTitle className="text-base text-[#0F172A] dark:text-[#F8FAFC]">
                      {node.name}
                    </CardTitle>
                  </div>
                  <Badge className={getNodeTypeColor(node.type)}>
                    {node.type}
                  </Badge>
                </div>
                <CardDescription className="text-[#0F172A]/70 dark:text-[#F8FAFC]/70">
                  Configure the parameters for this {node.type} node
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(node.parameters).map(([key, value]) => (
                    <div key={key}>
                      <label className="text-sm font-medium text-[#0F172A]/80 dark:text-[#F8FAFC]/80 capitalize">
                        {key.replace(/([A-Z])/g, ' $1').trim()}
                      </label>
                      <Input
                        value={String(value || '')}
                        onChange={(e) => handleNodeUpdate(node.id, {
                          parameters: { ...node.parameters, [key]: e.target.value }
                        })}
                        placeholder={`Enter ${key}`}
                        className="mt-1 bg-white/60 dark:bg-[#0F172A]/60 border-[#3B82F6]/20 dark:border-[#8B5CF6]/20 text-[#0F172A] dark:text-[#F8FAFC]"
                      />
                    </div>
                  ))}
                </div>
                
                <div className="flex justify-between items-center mt-4 pt-3 border-t border-[#3B82F6]/20 dark:border-[#8B5CF6]/20">
                  <span className="text-xs text-[#0F172A]/60 dark:text-[#F8FAFC]/60">
                    Node ID: {node.id}
                  </span>
                  <Button 
                    size="sm" 
                    variant="secondary"
                    className="text-xs"
                  >
                    <Settings className="h-3 w-3 mr-1" />
                    Advanced
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Workflow Summary */}
        <div className="mt-8 p-6 bg-white/60 dark:bg-[#0F172A]/60 backdrop-blur-sm border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20 rounded-lg">
          <h3 className="text-lg font-semibold text-[#0F172A] dark:text-[#F8FAFC] mb-4">
            Workflow Summary
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-[#3B82F6] dark:text-[#8B5CF6]">
                {workflowData.nodes.length}
              </div>
              <div className="text-sm text-[#0F172A]/60 dark:text-[#F8FAFC]/60">Total Nodes</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                {workflowData.connections.length}
              </div>
              <div className="text-sm text-[#0F172A]/60 dark:text-[#F8FAFC]/60">Connections</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                {new Set(workflowData.nodes.map(n => n.type)).size}
              </div>
              <div className="text-sm text-[#0F172A]/60 dark:text-[#F8FAFC]/60">Node Types</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowBuilder;



