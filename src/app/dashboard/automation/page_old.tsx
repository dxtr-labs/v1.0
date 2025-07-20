'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AlertCircle, Bot, Code, Play, Save, Settings, Search, Filter, Grid, List } from 'lucide-react';

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

type AgentTemplate = {
  template_id: string;
  template_name: string;
  template_description: string;
  category: string;
  agent_name_template: string;
  agent_role_template: string;
  agent_personality_template: string;
  agent_expectations_template: string;
  usage_count: number;
  created_at: string;
  updated_at: string;
};

type TemplatesResponse = {
  success: boolean;
  data?: {
    templates: AgentTemplate[];
    total: number;
    categories: { category: string; count: number }[];
    pagination: {
      limit: number;
      offset: number;
      hasMore: boolean;
    };
  };
  error?: string;
};

export default function DashboardAutomationPage() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AutomationResponse | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'checking' | 'connected' | 'error'>('checking');
  const [showAIServiceModal, setShowAIServiceModal] = useState(false);
  const [selectedService, setSelectedService] = useState<string>('');
  const [agentConfig, setAgentConfig] = useState({
    name: '',
    role: '',
    personality: '',
    expectations: ''
  });
  
  // Templates state
  const [templates, setTemplates] = useState<AgentTemplate[]>([]);
  const [categories, setCategories] = useState<{ category: string; count: number }[]>([]);
  const [templatesLoading, setTemplatesLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('template_name');
  const [sortOrder, setSortOrder] = useState('ASC');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [templatesPage, setTemplatesPage] = useState(0);
  const [totalTemplates, setTotalTemplates] = useState(0);

  const checkBackendConnection = async () => {
    try {
      const response = await fetch('/api/health');
      if (response.ok) {
        setConnectionStatus('connected');
      } else {
        setConnectionStatus('error');
      }
    } catch (error) {
      setConnectionStatus('error');
    }
  };

  const fetchTemplates = useCallback(async () => {
    setTemplatesLoading(true);
    try {
      const params = new URLSearchParams({
        category: selectedCategory,
        search: searchQuery,
        sortBy,
        sortOrder,
        limit: '20',
        offset: (templatesPage * 20).toString()
      });

      const response = await fetch(`/api/automation/templates?${params}`);
      const data: TemplatesResponse = await response.json();

      if (data.success && data.data) {
        setTemplates(data.data.templates);
        setCategories(data.data.categories);
        setTotalTemplates(data.data.total);
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
    } finally {
      setTemplatesLoading(false);
    }
  }, [selectedCategory, searchQuery, sortBy, sortOrder, templatesPage]);

  // Check backend connection on mount
  useEffect(() => {
    checkBackendConnection();
  }, []);

  // Fetch templates when filters change
  useEffect(() => {
    fetchTemplates();
  }, [fetchTemplates]);

  const handleSubmit = async () => {
    if (!input.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch('/api/automation/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: input,
          agentConfig: agentConfig
        }),
      });

      const data: AutomationResponse = await response.json();
      setResult(data);

      // Handle AI service selection
      if (data.status === 'ai_service_selection' && data.ai_service_options) {
        setShowAIServiceModal(true);
      }
    } catch (error) {
      setResult({
        done: true,
        success: false,
        error: 'Failed to create automation'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleServiceSelection = async (serviceId: string) => {
    setSelectedService(serviceId);
    setLoading(true);

    try {
      const response = await fetch('/api/automation/select-service', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service_id: serviceId,
          original_request: result?.original_request || input
        }),
      });

      const data: AutomationResponse = await response.json();
      setResult(data);
      setShowAIServiceModal(false);
    } catch (error) {
      setResult({
        done: true,
        success: false,
        error: 'Failed to process service selection'
      });
    } finally {
      setLoading(false);
    }
  };

  const ConnectionIndicator = () => (
    <div className="flex items-center gap-2 text-sm">
      <div className={`w-2 h-2 rounded-full ${
        connectionStatus === 'connected' ? 'bg-green-500' : 
        connectionStatus === 'error' ? 'bg-red-500' : 'bg-gray-500'
      }`} />
      <span className="text-muted-foreground">
        {connectionStatus === 'connected' ? 'Connected' : 
         connectionStatus === 'error' ? 'Connection Error' : 'Checking...'}
      </span>
    </div>
  );

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Automation Dashboard</h1>
          <p className="text-muted-foreground">Create and manage your AI-powered automations</p>
        </div>
        <ConnectionIndicator />
      </div>

      <Tabs defaultValue="templates" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="templates">Browse Templates</TabsTrigger>
          <TabsTrigger value="create">Create Automation</TabsTrigger>
          <TabsTrigger value="agent">Agent Config</TabsTrigger>
          <TabsTrigger value="results">Results</TabsTrigger>
        </TabsList>

        <TabsContent value="templates" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Grid className="w-5 h-5" />
                Browse Workflow Templates
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Search and Filter Controls */}
              <div className="flex flex-wrap gap-4 items-center justify-between">
                <div className="flex gap-2 items-center">
                  <div className="relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground" />
                    <Input
                      placeholder="Search templates..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-9 w-64"
                    />
                  </div>
                  
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="px-3 py-2 border rounded-md text-sm"
                  >
                    <option value="all">All Categories</option>
                    {categories.map((cat) => (
                      <option key={cat.category} value={cat.category}>
                        {cat.category} ({cat.count})
                      </option>
                    ))}
                  </select>

                  <select
                    value={`${sortBy}-${sortOrder}`}
                    onChange={(e) => {
                      const [field, order] = e.target.value.split('-');
                      setSortBy(field);
                      setSortOrder(order);
                    }}
                    className="px-3 py-2 border rounded-md text-sm"
                  >
                    <option value="template_name-ASC">Name (A-Z)</option>
                    <option value="template_name-DESC">Name (Z-A)</option>
                    <option value="category-ASC">Category (A-Z)</option>
                    <option value="usage_count-DESC">Most Popular</option>
                    <option value="created_at-DESC">Newest First</option>
                    <option value="created_at-ASC">Oldest First</option>
                  </select>
                </div>

                <div className="flex gap-2">
                  <Button
                    variant={viewMode === 'grid' ? 'primary' : 'secondary'}
                    size="sm"
                    onClick={() => setViewMode('grid')}
                  >
                    <Grid className="w-4 h-4" />
                  </Button>
                  <Button
                    variant={viewMode === 'list' ? 'primary' : 'secondary'}
                    size="sm"
                    onClick={() => setViewMode('list')}
                  >
                    <List className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              {/* Templates Display */}
              {templatesLoading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full w-8 h-8 border-b-2 border-primary" />
                  <span className="ml-2">Loading templates...</span>
                </div>
              ) : templates.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <Filter className="w-12 h-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground text-center">
                    No templates found matching your criteria.<br />
                    Try adjusting your search or filter options.
                  </p>
                </div>
              ) : (
                <>
                  <div className={viewMode === 'grid' 
                    ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' 
                    : 'space-y-3'
                  }>
                    {templates.map((template) => (
                      <Card key={template.template_id} className="hover:shadow-md transition-shadow cursor-pointer">
                        <CardHeader>
                          <div className="flex justify-between items-start">
                            <CardTitle className="text-base line-clamp-2">
                              {template.template_name}
                            </CardTitle>
                            <Badge variant="outline" className="ml-2 text-xs">
                              {template.category}
                            </Badge>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <p className="text-sm text-muted-foreground line-clamp-3 mb-3">
                            {template.template_description}
                          </p>
                          <div className="flex justify-between items-center text-xs text-muted-foreground">
                            <span>Used {template.usage_count} times</span>
                            <span>{new Date(template.created_at).toLocaleDateString()}</span>
                          </div>
                          <Button className="w-full mt-3" size="sm">
                            Use This Template
                          </Button>
                        </CardContent>
                      </Card>
                    ))}
                  </div>

                  {/* Pagination */}
                  {totalTemplates > 20 && (
                    <div className="flex justify-center items-center gap-2 pt-4">
                      <Button
                        variant="secondary"
                        size="sm"
                        disabled={templatesPage === 0}
                        onClick={() => setTemplatesPage(p => Math.max(0, p - 1))}
                      >
                        Previous
                      </Button>
                      <span className="text-sm text-muted-foreground">
                        Page {templatesPage + 1} of {Math.ceil(totalTemplates / 20)}
                      </span>
                      <Button
                        variant="secondary"
                        size="sm"
                        disabled={(templatesPage + 1) * 20 >= totalTemplates}
                        onClick={() => setTemplatesPage(p => p + 1)}
                      >
                        Next
                      </Button>
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="create" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bot className="w-5 h-5" />
                Create New Automation
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Automation Request</label>
                <Textarea
                  placeholder="Describe what you want to automate (e.g., 'Send a welcome email when someone signs up')"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  rows={4}
                />
              </div>
              <Button
                onClick={handleSubmit}
                disabled={loading || !input.trim() || connectionStatus !== 'connected'}
                className="w-full"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full w-4 h-4 border-b-2 border-white mr-2" />
                    Creating Automation...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Create Automation
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="agent" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5" />
                Agent Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Agent Name</label>
                  <Input
                    placeholder="My Assistant"
                    value={agentConfig.name}
                    onChange={(e) => setAgentConfig(prev => ({ ...prev, name: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Agent Role</label>
                  <Input
                    placeholder="Personal Assistant"
                    value={agentConfig.role}
                    onChange={(e) => setAgentConfig(prev => ({ ...prev, role: e.target.value }))}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Personality</label>
                <Input
                  placeholder="Helpful and friendly"
                  value={agentConfig.personality}
                  onChange={(e) => setAgentConfig(prev => ({ ...prev, personality: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Expectations</label>
                <Textarea
                  placeholder="What should this agent be good at?"
                  value={agentConfig.expectations}
                  onChange={(e) => setAgentConfig(prev => ({ ...prev, expectations: e.target.value }))}
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="results" className="space-y-4">
          {result && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Code className="w-5 h-5" />
                  Automation Result
                  {result.success !== undefined && (
                    <Badge variant={result.success ? "default" : "destructive"}>
                      {result.success ? "Success" : "Failed"}
                    </Badge>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {result.error && (
                  <div className="flex items-center gap-2 p-3 bg-red-50 text-red-700 rounded-md mb-4">
                    <AlertCircle className="w-4 h-4" />
                    <span>{result.error}</span>
                  </div>
                )}
                
                {result.message && (
                  <div className="space-y-2">
                    <h4 className="font-medium">Message:</h4>
                    <p className="text-sm text-muted-foreground">{result.message}</p>
                  </div>
                )}

                {result.json && (
                  <div className="space-y-2 mt-4">
                    <h4 className="font-medium">Workflow Definition:</h4>
                    <pre className="bg-gray-100 p-3 rounded-md text-xs overflow-auto max-h-64">
                      {JSON.stringify(result.json, null, 2)}
                    </pre>
                  </div>
                )}

                {result.n8n_deployment && (
                  <div className="space-y-2 mt-4">
                    <h4 className="font-medium">Deployment:</h4>
                    <div className="bg-blue-50 p-3 rounded-md">
                      <p className="text-sm">{result.n8n_deployment.message}</p>
                      {result.n8n_deployment.workflow_url && (
                        <a 
                          href={result.n8n_deployment.workflow_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline text-sm"
                        >
                          View Workflow
                        </a>
                      )}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {!result && (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Bot className="w-12 h-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground text-center">
                  No automation results yet.<br />
                  Create an automation to see results here.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* AI Service Selection Modal */}
      {showAIServiceModal && result?.ai_service_options && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl mx-4">
            <CardHeader>
              <CardTitle>Select AI Service</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {result.ai_service_options.map((service) => (
                <div
                  key={service.id}
                  className="border rounded-lg p-4 cursor-pointer hover:bg-gray-50"
                  onClick={() => handleServiceSelection(service.id)}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-medium">{service.name}</h3>
                    <Badge>{service.credits} credits</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">{service.description}</p>
                  <div className="flex flex-wrap gap-1">
                    {service.features.map((feature, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {feature}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
              <Button
                variant="secondary"
                onClick={() => setShowAIServiceModal(false)}
                className="w-full"
              >
                Cancel
              </Button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

