'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, MessageCircle, Grid, List } from 'lucide-react';

// Types
interface Workflow {
  id: string;
  name: string;
  description: string;
  category: string;
  fileName: string;
  nodes: any[];
}

const AutomationDashboard = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [filteredWorkflows, setFilteredWorkflows] = useState<Workflow[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadWorkflows();
  }, []);

  useEffect(() => {
    filterWorkflows();
  }, [workflows, searchTerm, selectedCategory]);

  const loadWorkflows = async () => {
    try {
      setIsLoading(true);
      
      // Sample workflow files - in production this would come from the workflows directory
      const workflowFiles = [
        '0001_Telegram_Schedule_Automation_Scheduled.json',
        '0002_Manual_Totp_Automation_Triggered.json',
        '0003_Bitwarden_Automate.json',
        '0004_GoogleSheets_Typeform_Automate_Triggered.json',
        '0005_Manual_Twitter_Create_Triggered.json',
        '0006_Openweathermap_Cron_Automate_Scheduled.json',
        '0007_Manual_Todoist_Create_Triggered.json',
        '0008_Slack_Stripe_Create_Triggered.json',
        '0009_Process.json',
        '0010_Writebinaryfile_Create.json',
        '0011_Manual_Copper_Automate_Triggered.json',
        '0012_Manual_Copper_Automate_Triggered.json',
        '0013_Manual_Noop_Import_Triggered.json',
        '0014_Manual_Coda_Create_Triggered.json',
        '0015_HTTP_Cron_Update_Webhook.json'
      ];

      const loadedWorkflows: Workflow[] = [];

      for (const fileName of workflowFiles) {
        try {
          // For demo purposes, create mock workflow data
          // In production, you would fetch from /dashboard/automation/workflows/${fileName}
          const mockWorkflow = {
            id: fileName.replace('.json', ''),
            name: fileName.replace('.json', '').replace(/_/g, ' ').replace(/^\d+\s*/, ''),
            nodes: Array.from({ length: Math.floor(Math.random() * 10) + 2 }, (_, i) => ({ id: i }))
          };
          
          // Extract category from filename
          const parts = fileName.replace('.json', '').split('_');
          let category = 'General';
          
          if (parts.length > 2) {
            const categoryPart = parts.slice(1, -1).join(' ');
            category = categoryPart.charAt(0).toUpperCase() + categoryPart.slice(1);
          }
          
          // Determine category based on content
          if (fileName.includes('Telegram')) category = 'Communication';
          else if (fileName.includes('GoogleSheets') || fileName.includes('Spreadsheet')) category = 'Data Management';
          else if (fileName.includes('HTTP') || fileName.includes('Webhook')) category = 'API Integration';
          else if (fileName.includes('Twitter') || fileName.includes('Social')) category = 'Social Media';
          else if (fileName.includes('Schedule') || fileName.includes('Cron')) category = 'Scheduling';
          else if (fileName.includes('Email') || fileName.includes('Gmail')) category = 'Email';
          else if (fileName.includes('Slack') || fileName.includes('Chat')) category = 'Team Collaboration';
          
          const description = `Automated workflow for ${mockWorkflow.name.toLowerCase()} with ${mockWorkflow.nodes.length} steps`;
          
          loadedWorkflows.push({
            id: mockWorkflow.id,
            name: mockWorkflow.name,
            description: description,
            category: category,
            fileName: fileName,
            nodes: mockWorkflow.nodes
          });
        } catch (error) {
          console.error(`Error loading workflow ${fileName}:`, error);
        }
      }

      setWorkflows(loadedWorkflows);
    } catch (error) {
      console.error('Error loading workflows:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filterWorkflows = () => {
    let filtered = workflows;

    if (searchTerm) {
      filtered = filtered.filter(workflow =>
        workflow.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        workflow.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        workflow.category.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (selectedCategory) {
      filtered = filtered.filter(workflow => workflow.category === selectedCategory);
    }

    setFilteredWorkflows(filtered);
  };

  const handleOpenChat = (workflow: Workflow) => {
    // Open chat interface with the selected workflow
    console.log('Opening chat for workflow:', workflow);
    // For now, we'll redirect to a chat page with the workflow ID
    window.location.href = `/chat?workflow=${workflow.id}&file=${workflow.fileName}`;
  };

  const getUniqueCategories = () => {
    const categories = workflows.map(w => w.category);
    return [...new Set(categories)].sort();
  };

  const getCategoryColor = (category: string) => {
    const colors = [
      'bg-blue-100 text-blue-800',
      'bg-green-100 text-green-800',
      'bg-purple-100 text-purple-800',
      'bg-gray-100 text-gray-800',
      'bg-pink-100 text-pink-800',
      'bg-indigo-100 text-indigo-800',
      'bg-teal-100 text-teal-800',
      'bg-red-100 text-red-800'
    ];
    const index = category.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length;
    return colors[index];
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Automation Workflows</h1>
        <p className="text-gray-600">Browse and interact with pre-built automation workflows</p>
      </div>

      {/* Search and Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search workflows..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 min-w-[150px]"
        >
          <option value="">All Categories</option>
          {getUniqueCategories().map(category => (
            <option key={category} value={category}>{category}</option>
          ))}
        </select>

        <div className="flex gap-2">
          <Button
            variant={viewMode === 'grid' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('grid')}
          >
            <Grid className="h-4 w-4" />
          </Button>
          <Button
            variant={viewMode === 'list' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('list')}
          >
            <List className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Workflows Display */}
      {isLoading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading workflows...</p>
        </div>
      ) : (
        <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}>
          {filteredWorkflows.map((workflow) => (
            <Card 
              key={workflow.id} 
              className={`cursor-pointer hover:shadow-lg transition-all duration-200 hover:scale-105 ${viewMode === 'list' ? 'flex flex-row' : ''}`}
              onClick={() => handleOpenChat(workflow)}
            >
              <CardHeader className={viewMode === 'list' ? 'flex-1' : ''}>
                <div className="flex justify-between items-start">
                  <CardTitle className="text-lg line-clamp-2 pr-2">{workflow.name}</CardTitle>
                  <Badge className={`${getCategoryColor(workflow.category)} shrink-0`}>
                    {workflow.category}
                  </Badge>
                </div>
                <CardDescription className="line-clamp-3">
                  {workflow.description}
                </CardDescription>
              </CardHeader>
              <CardContent className={viewMode === 'list' ? 'flex items-center' : ''}>
                <div className="flex justify-between items-center w-full">
                  <div className="text-sm text-gray-500">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{workflow.nodes.length}</span>
                      <span>steps</span>
                    </div>
                    <div className="text-xs text-gray-400 mt-1 truncate max-w-[180px]">
                      {workflow.fileName}
                    </div>
                  </div>
                  <Button 
                    onClick={(e) => {
                      e.stopPropagation();
                      handleOpenChat(workflow);
                    }}
                    className="flex items-center gap-2 ml-4"
                    size="sm"
                  >
                    <MessageCircle className="h-4 w-4" />
                    Chat
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {!isLoading && filteredWorkflows.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <Search className="h-12 w-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No workflows found</h3>
          <p className="text-gray-600 max-w-md mx-auto">
            {searchTerm || selectedCategory 
              ? "Try adjusting your search terms or filters to find what you're looking for."
              : "No automation workflows are currently available."
            }
          </p>
          {(searchTerm || selectedCategory) && (
            <Button 
              variant="outline" 
              onClick={() => {
                setSearchTerm('');
                setSelectedCategory('');
              }}
              className="mt-4"
            >
              Clear filters
            </Button>
          )}
        </div>
      )}

      {/* Stats Footer */}
      <div className="mt-8 p-4 bg-gray-50 rounded-lg">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-blue-600">{workflows.length}</div>
            <div className="text-sm text-gray-600">Total Workflows</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-600">{getUniqueCategories().length}</div>
            <div className="text-sm text-gray-600">Categories</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-purple-600">{filteredWorkflows.length}</div>
            <div className="text-sm text-gray-600">Showing</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutomationDashboard;
