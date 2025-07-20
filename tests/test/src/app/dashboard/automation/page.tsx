'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, MessageCircle, Grid, List, ArrowUpDown, Settings } from 'lucide-react';

// Types
interface Workflow {
  id: string;
  name: string;
  description: string;
  category: string;
  mainCategory?: string;
  subcategory?: string;
  fileName: string;
  nodes: any[];
}

interface WorkflowsResponse {
  workflows: Workflow[];
  total: number;
  loaded: number;
  filtered: number;
  categories: string[];
  pagination: {
    offset: number;
    limit: number;
    hasMore: boolean;
  };
}

const AutomationDashboard = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [filteredWorkflows, setFilteredWorkflows] = useState<Workflow[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedMainCategory, setSelectedMainCategory] = useState('');
  const [selectedSubCategory, setSelectedSubCategory] = useState('');
  const [showSubdivisions, setShowSubdivisions] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState<'name' | 'category' | 'nodes' | 'recent'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [isLoading, setIsLoading] = useState(true);
  const [totalWorkflows, setTotalWorkflows] = useState(0);
  const [loadedCount, setLoadedCount] = useState(0);
  const [canLoadMore, setCanLoadMore] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);

  const loadWorkflows = useCallback(async () => {
    try {
      setIsLoading(true);
      
      // Load a larger batch of workflows (500 at a time for better performance)
      const response = await fetch('/api/automation/workflows?limit=500');
      if (response.ok) {
        const data = await response.json() as WorkflowsResponse;
        console.log(`Loaded ${data.loaded} workflows out of ${data.total} total files`);
        setWorkflows(data.workflows || []);
        setTotalWorkflows(data.total);
        setLoadedCount(data.loaded);
        setCanLoadMore(data.pagination.hasMore);
      } else {
        console.error('Failed to fetch workflows:', response.statusText);
        // Fallback to mock data if API fails
        loadMockWorkflows();
      }
    } catch (error) {
      console.error('Error loading workflows:', error);
      // Fallback to mock data if API fails
      loadMockWorkflows();
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadMoreWorkflows = useCallback(async () => {
    if (!canLoadMore || isLoadingMore) return;
    
    try {
      setIsLoadingMore(true);
      const response = await fetch(`/api/automation/workflows?limit=500&offset=${workflows.length}`);
      if (response.ok) {
        const data = await response.json() as WorkflowsResponse;
        setWorkflows(prev => [...prev, ...data.workflows]);
        setLoadedCount(prev => prev + data.loaded);
        setCanLoadMore(data.pagination.hasMore);
      }
    } catch (error) {
      console.error('Error loading more workflows:', error);
    } finally {
      setIsLoadingMore(false);
    }
  }, [workflows.length, canLoadMore, isLoadingMore]);

  useEffect(() => {
    loadWorkflows();
  }, [loadWorkflows]);

  const filterWorkflows = useCallback(() => {
    let filtered = workflows;
    
    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(workflow => 
        workflow.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        workflow.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        workflow.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (workflow.subcategory && workflow.subcategory.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (workflow.mainCategory && workflow.mainCategory.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }
    
    // Apply main category filter
    if (selectedMainCategory && selectedMainCategory !== 'All') {
      filtered = filtered.filter(workflow => 
        workflow.mainCategory === selectedMainCategory || 
        workflow.category === selectedMainCategory
      );
    }
    
    // Apply subcategory filter
    if (selectedSubCategory && selectedSubCategory !== 'All') {
      filtered = filtered.filter(workflow => 
        workflow.subcategory === selectedSubCategory || 
        workflow.category === selectedSubCategory
      );
    }
    
    // Legacy category filter for backwards compatibility
    if (selectedCategory && !selectedMainCategory && !selectedSubCategory) {
      filtered = filtered.filter(workflow => workflow.category === selectedCategory);
    }
    
    // Apply sorting
    filtered.sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name);
          break;
        case 'category':
          comparison = (a.mainCategory || a.category).localeCompare(b.mainCategory || b.category);
          break;
        case 'nodes':
          comparison = a.nodes.length - b.nodes.length;
          break;
        case 'recent':
          // Sort by filename (assuming newer files have higher numbers)
          const aNum = parseInt(a.fileName.match(/(\d+)/)?.[1] || '0');
          const bNum = parseInt(b.fileName.match(/(\d+)/)?.[1] || '0');
          comparison = bNum - aNum; // Reverse for recent first
          break;
        default:
          comparison = a.name.localeCompare(b.name);
      }
      
      return sortOrder === 'desc' ? -comparison : comparison;
    });
    
    setFilteredWorkflows(filtered);
  }, [workflows, searchTerm, selectedCategory, selectedMainCategory, selectedSubCategory, sortBy, sortOrder]);

  useEffect(() => {
    filterWorkflows();
  }, [filterWorkflows]);

  const loadMockWorkflows = () => {
    const mockWorkflows: Workflow[] = [
      {
        id: 'email-automation',
        name: 'Email Campaign Automation',
        description: 'Automate email marketing campaigns with personalization and scheduling',
        category: 'Marketing',
        fileName: '0001_Email_Automation_Template.json',
        nodes: Array.from({ length: 5 }, (_, i) => ({ id: i }))
      },
      {
        id: 'totp-generator',
        name: 'TOTP Code Generator',
        description: 'Complete guide to setting up and generating TOTP codes',
        category: 'Security',
        fileName: '0002_Manual_Totp_Automation_Triggered.json',
        nodes: Array.from({ length: 3 }, (_, i) => ({ id: i }))
      },
      {
        id: 'bitwarden-automate',
        name: 'Bitwarden Integration',
        description: 'Automated password management with Bitwarden',
        category: 'Security',
        fileName: '0003_Bitwarden_Automate.json',
        nodes: Array.from({ length: 4 }, (_, i) => ({ id: i }))
      }
    ];
    setWorkflows(mockWorkflows);
  };

  const handleOpenBuilder = (workflow: Workflow) => {
    // Open workflow builder with the selected workflow
    console.log('Opening builder for workflow:', workflow);
    // Redirect to builder page with the workflow ID and file
    window.location.href = `/dashboard/automation/builder?workflow=${workflow.id}&file=${workflow.fileName}`;
  };

  // Enhanced category system with main categories and subdivisions (5x5 structure)
  const CATEGORY_STRUCTURE = {
    'Productivity': {
      icon: '⚡',
      color: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
      subdivisions: [
        { value: 'Task Management', label: 'Task Management', icon: '✅' },
        { value: 'Note Taking', label: 'Note Taking', icon: '📝' },
        { value: 'Project Planning', label: 'Project Planning', icon: '📋' },
        { value: 'Time Tracking', label: 'Time Tracking', icon: '⏱️' },
        { value: 'Document Automation', label: 'Document Automation', icon: '📄' }
      ]
    },
    'Communication': {
      icon: '💬',
      color: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
      subdivisions: [
        { value: 'Email', label: 'Email', icon: '📧' },
        { value: 'Team Chat', label: 'Team Chat', icon: '💬' },
        { value: 'Video Calls', label: 'Video Calls', icon: '📹' },
        { value: 'Notifications', label: 'Notifications', icon: '�' },
        { value: 'Social Media', label: 'Social Media', icon: '📱' }
      ]
    },
    'Business': {
      icon: '💼',
      color: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
      subdivisions: [
        { value: 'CRM', label: 'CRM', icon: '👥' },
        { value: 'Sales', label: 'Sales', icon: '�' },
        { value: 'Marketing', label: 'Marketing', icon: '📊' },
        { value: 'Finance', label: 'Finance', icon: '💳' },
        { value: 'HR', label: 'HR', icon: '👤' }
      ]
    },
    'Data & Analytics': {
      icon: '📈',
      color: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300',
      subdivisions: [
        { value: 'Data Processing', label: 'Data Processing', icon: '⚙️' },
        { value: 'Spreadsheets', label: 'Spreadsheets', icon: '📊' },
        { value: 'Database', label: 'Database', icon: '�️' },
        { value: 'Reporting', label: 'Reporting', icon: '📋' },
        { value: 'API Integration', label: 'API Integration', icon: '�' }
      ]
    },
    'Security & Operations': {
      icon: '🔒',
      color: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
      subdivisions: [
        { value: 'Authentication', label: 'Authentication', icon: '�' },
        { value: 'Monitoring', label: 'Monitoring', icon: '👁️' },
        { value: 'Backup', label: 'Backup', icon: '💾' },
        { value: 'Deployment', label: 'Deployment', icon: '�' },
        { value: 'Calendar & Scheduling', label: 'Calendar & Scheduling', icon: '�' }
      ]
    }
  };

  const getAllSubdivisions = () => {
    const allSubs: Array<{value: string, label: string, icon: string, mainCategory: string}> = [];
    Object.entries(CATEGORY_STRUCTURE).forEach(([mainCat, data]) => {
      data.subdivisions.forEach(sub => {
        allSubs.push({
          ...sub,
          mainCategory: mainCat
        });
      });
    });
    return allSubs;
  };

  const getWorkflowCountForCategory = (categoryValue: string, isSubdivision = false) => {
    console.log('🔢 Counting workflows for:', categoryValue, 'isSubdivision:', isSubdivision);
    
    if (isSubdivision) {
      const count = workflows.filter(w => {
        const match = w.subcategory === categoryValue || w.category === categoryValue;
        if (match) {
          console.log('  ✅ Match found:', w.name, 'subcategory:', w.subcategory, 'category:', w.category);
        }
        return match;
      }).length;
      console.log('  📊 Subdivision count:', count);
      return count;
    }
    
    const count = workflows.filter(w => {
      const match = w.mainCategory === categoryValue || w.category === categoryValue;
      if (match) {
        console.log('  ✅ Match found:', w.name, 'mainCategory:', w.mainCategory, 'category:', w.category);
      }
      return match;
    }).length;
    console.log('  📊 Main category count:', count);
    return count;
  };

  const getUniqueCategories = () => {
    const workflowCategories = workflows.map(w => w.category);
    const uniqueWorkflowCategories = [...new Set(workflowCategories)];
    
    // Get all main categories from our structure
    const mainCategories = Object.keys(CATEGORY_STRUCTURE).map(key => ({
      value: key,
      label: key,
      icon: CATEGORY_STRUCTURE[key as keyof typeof CATEGORY_STRUCTURE].icon
    }));
    
    // Add any categories from workflows that aren't in our predefined list
    uniqueWorkflowCategories.forEach(category => {
      if (!mainCategories.find(cat => cat.value === category)) {
        mainCategories.push({ value: category, label: category, icon: '📁' });
      }
    });
    
    return mainCategories.sort((a, b) => a.label.localeCompare(b.label));
  };

  const getCategoryColor = (category: string) => {
    const colors = [
      'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
      'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
      'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
      'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300',
      'bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-300',
      'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300',
      'bg-teal-100 text-teal-800 dark:bg-teal-900/30 dark:text-teal-300',
      'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
    ];
    const index = category.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length;
    return colors[index];
  };

  return (
    <div className="h-full w-full overflow-auto">
      <div className="container mx-auto p-6 min-h-full">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2 text-[#0F172A] dark:text-[#F8FAFC]">Automation Workflows</h1>
          <p className="text-[#0F172A]/70 dark:text-[#F8FAFC]/70">
            Browse and interact with pre-built automation workflows 
            {totalWorkflows > 0 && (
              <span className="ml-2 text-sm">
                ({loadedCount} loaded of {totalWorkflows} total)
              </span>
            )}
          </p>
        </div>

        {/* Search and Filter Bar */}
        <div className="flex flex-col gap-4 mb-6">
          {/* Search Bar */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-3 h-4 w-4 text-[#0F172A]/40 dark:text-[#F8FAFC]/40" />
            <Input
              placeholder="Search workflows..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 bg-white/60 dark:bg-[#0F172A]/60 border-[#3B82F6]/20 dark:border-[#8B5CF6]/20 text-[#0F172A] dark:text-[#F8FAFC] placeholder:text-[#0F172A]/40 dark:placeholder:text-[#F8FAFC]/40"
            />
          </div>

          {/* Category Filters - Enhanced 5x5 Structure */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium text-[#0F172A] dark:text-[#F8FAFC]">Filter by Category</h3>
            
            {/* Main Categories (5 categories) */}
            <div className="space-y-3">
              <div className="flex flex-wrap gap-2">
                <Button
                  variant={selectedMainCategory === '' && selectedSubCategory === '' ? 'primary' : 'secondary'}
                  size="sm"
                  onClick={() => {
                    setSelectedMainCategory('');
                    setSelectedSubCategory('');
                    setShowSubdivisions(false);
                  }}
                  className="flex items-center gap-2 text-sm"
                >
                  🔍 All Categories
                </Button>
                {Object.entries(CATEGORY_STRUCTURE).map(([categoryKey, categoryData]) => (
                  <Button
                    key={categoryKey}
                    variant={selectedMainCategory === categoryKey ? 'primary' : 'secondary'}
                    size="sm"
                    onClick={() => {
                      if (selectedMainCategory === categoryKey) {
                        setShowSubdivisions(!showSubdivisions);
                      } else {
                        setSelectedMainCategory(categoryKey);
                        setSelectedSubCategory('');
                        setShowSubdivisions(true);
                      }
                    }}
                    className="flex items-center gap-2 text-sm hover:scale-105 transition-transform"
                  >
                    <span className="text-base">{categoryData.icon}</span>
                    {categoryKey}
                    <Badge variant="outline" className="ml-1 text-xs">
                      {getWorkflowCountForCategory(categoryKey, false)}
                    </Badge>
                  </Button>
                ))}
              </div>

              {/* Subdivisions (5 subdivisions per category) */}
              {showSubdivisions && selectedMainCategory && CATEGORY_STRUCTURE[selectedMainCategory as keyof typeof CATEGORY_STRUCTURE] && (
                <div className="ml-4 pl-4 border-l-2 border-[#3B82F6]/20 dark:border-[#8B5CF6]/20">
                  <h4 className="text-xs font-medium text-[#0F172A]/70 dark:text-[#F8FAFC]/70 mb-2">
                    {selectedMainCategory} Subdivisions:
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {CATEGORY_STRUCTURE[selectedMainCategory as keyof typeof CATEGORY_STRUCTURE].subdivisions.map(subdivision => (
                      <Button
                        key={subdivision.value}
                        variant={selectedSubCategory === subdivision.value ? 'primary' : 'secondary'}
                        size="sm"
                        onClick={() => {
                          setSelectedSubCategory(
                            selectedSubCategory === subdivision.value ? '' : subdivision.value
                          );
                        }}
                        className="flex items-center gap-2 text-xs hover:scale-105 transition-transform"
                      >
                        <span className="text-sm">{subdivision.icon}</span>
                        {subdivision.label}
                        <Badge variant="outline" className="ml-1 text-xs">
                          {getWorkflowCountForCategory(subdivision.value, true)}
                        </Badge>
                      </Button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* Sorting and View Controls */}
          <div className="flex flex-col sm:flex-row gap-2 items-start sm:items-center justify-between">
            <div className="flex gap-2">
              <div className="relative">
                <ArrowUpDown className="absolute left-3 top-3 h-4 w-4 text-[#0F172A]/40 dark:text-[#F8FAFC]/40 pointer-events-none" />
                <select
                  value={`${sortBy}-${sortOrder}`}
                  onChange={(e) => {
                    const [newSortBy, newSortOrder] = e.target.value.split('-') as [typeof sortBy, typeof sortOrder];
                    setSortBy(newSortBy);
                    setSortOrder(newSortOrder);
                  }}
                  className="pl-10 pr-3 py-2 border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20 rounded-md bg-white/60 dark:bg-[#0F172A]/60 text-[#0F172A] dark:text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6] dark:focus:ring-[#8B5CF6] min-w-[180px] appearance-none cursor-pointer"
                >
                  <option value="name-asc">Name A-Z</option>
                  <option value="name-desc">Name Z-A</option>
                  <option value="category-asc">Category A-Z</option>
                  <option value="category-desc">Category Z-A</option>
                  <option value="nodes-asc">Steps (Low-High)</option>
                  <option value="nodes-desc">Steps (High-Low)</option>
                  <option value="recent-desc">Most Recent</option>
                  <option value="recent-asc">Oldest First</option>
                </select>
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                variant={viewMode === 'grid' ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => setViewMode('grid')}
              >
                <Grid className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === 'list' ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => setViewMode('list')}
              >
                <List className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* Results Summary */}
        {(selectedMainCategory || selectedSubCategory || searchTerm) && (
          <div className="mb-4 p-3 bg-[#3B82F6]/10 dark:bg-[#8B5CF6]/10 rounded-lg border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20">
            <p className="text-sm text-[#0F172A] dark:text-[#F8FAFC]">
              {filteredWorkflows.length > 0 ? (
                <>
                  Showing <span className="font-semibold">{filteredWorkflows.length}</span> workflow{filteredWorkflows.length !== 1 ? 's' : ''} 
                  {selectedMainCategory && <span> in <span className="font-semibold">{selectedMainCategory}</span></span>}
                  {selectedSubCategory && <span> → <span className="font-semibold">{selectedSubCategory}</span></span>}
                  {searchTerm && <span> matching &ldquo;<span className="font-semibold">{searchTerm}</span>&rdquo;</span>}
                  <span className="text-[#0F172A]/70 dark:text-[#F8FAFC]/70"> out of {workflows.length} total</span>
                </>
              ) : (
                <>
                  No workflows found
                  {selectedMainCategory && <span> in <span className="font-semibold">{selectedMainCategory}</span></span>}
                  {selectedSubCategory && <span> → <span className="font-semibold">{selectedSubCategory}</span></span>}
                  {searchTerm && <span> matching &ldquo;<span className="font-semibold">{searchTerm}</span>&rdquo;</span>}
                  . Try adjusting your filters.
                </>
              )}
            </p>
          </div>
        )}

        {/* Workflows Display */}
        {isLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#3B82F6] dark:border-[#8B5CF6] mx-auto"></div>
            <p className="mt-4 text-[#0F172A]/70 dark:text-[#F8FAFC]/70">Loading workflows...</p>
          </div>
        ) : (
          <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}>
            {filteredWorkflows.map((workflow) => (
              <Card 
                key={workflow.id} 
                className={`cursor-pointer hover:shadow-lg transition-all duration-200 hover:scale-105 bg-white/60 dark:bg-[#0F172A]/60 backdrop-blur-sm border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20 ${viewMode === 'list' ? 'flex flex-row' : ''}`}
                onClick={() => handleOpenBuilder(workflow)}
              >
                <CardHeader className={viewMode === 'list' ? 'flex-1' : ''}>
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-lg line-clamp-2 pr-2 text-[#0F172A] dark:text-[#F8FAFC]">{workflow.name}</CardTitle>
                    <Badge className={`${getCategoryColor(workflow.category)} shrink-0`}>
                      {workflow.category}
                    </Badge>
                  </div>
                  <CardDescription className="line-clamp-3 text-[#0F172A]/70 dark:text-[#F8FAFC]/70">
                    {workflow.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className={viewMode === 'list' ? 'flex items-center' : ''}>
                  <div className="flex justify-between items-center w-full">
                    <div className="text-sm text-[#0F172A]/60 dark:text-[#F8FAFC]/60">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{workflow.nodes.length}</span>
                        <span>steps</span>
                      </div>
                      <div className="text-xs text-[#0F172A]/40 dark:text-[#F8FAFC]/40 mt-1 truncate max-w-[180px]">
                        {workflow.fileName}
                      </div>
                    </div>
                    <Button 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleOpenBuilder(workflow);
                      }}
                      className="flex items-center gap-2 ml-4"
                      size="sm"
                    >
                      <Settings className="h-4 w-4" />
                      Build
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Load More Button */}
        {!isLoading && canLoadMore && (
          <div className="text-center mt-8">
            <Button 
              onClick={loadMoreWorkflows}
              disabled={isLoadingMore}
              className="px-8 py-3"
            >
              {isLoadingMore ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Loading more...
                </>
              ) : (
                `Load More (${totalWorkflows - loadedCount} remaining)`
              )}
            </Button>
          </div>
        )}

        {!isLoading && filteredWorkflows.length === 0 && (
          <div className="text-center py-12">
            <div className="text-[#0F172A]/40 dark:text-[#F8FAFC]/40 mb-4">
              <Search className="h-12 w-12 mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-[#0F172A] dark:text-[#F8FAFC] mb-2">No workflows found</h3>
            <p className="text-[#0F172A]/70 dark:text-[#F8FAFC]/70 max-w-md mx-auto">
              {searchTerm || selectedCategory 
                ? "Try adjusting your search terms or filters to find what you're looking for."
                : "No automation workflows are currently available."
              }
            </p>
            {(searchTerm || selectedCategory) && (
              <Button 
                variant="secondary" 
                onClick={() => {
                  setSearchTerm('');
                  setSelectedCategory('');
                  setSortBy('name');
                  setSortOrder('asc');
                }}
                className="mt-4"
              >
                Clear filters & reset sort
              </Button>
            )}
          </div>
        )}

        {/* Stats Section */}
        <div className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div className="bg-white/60 dark:bg-[#0F172A]/60 backdrop-blur-sm border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-[#3B82F6] dark:text-[#8B5CF6]">{totalWorkflows}</div>
            <div className="text-sm text-[#0F172A]/60 dark:text-[#F8FAFC]/60">Total Available</div>
          </div>
          <div className="bg-white/60 dark:bg-[#0F172A]/60 backdrop-blur-sm border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">{loadedCount}</div>
            <div className="text-sm text-[#0F172A]/60 dark:text-[#F8FAFC]/60">Currently Loaded</div>
          </div>
          <div className="bg-white/60 dark:bg-[#0F172A]/60 backdrop-blur-sm border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">{filteredWorkflows.length}</div>
            <div className="text-sm text-[#0F172A]/60 dark:text-[#F8FAFC]/60">Showing</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutomationDashboard;


