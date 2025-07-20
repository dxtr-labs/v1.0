import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '100'); // Default to 100, but allow more
    const offset = parseInt(searchParams.get('offset') || '0');
    const search = searchParams.get('search') || '';
    const category = searchParams.get('category') || '';
    
    const workflowsDir = path.join(process.cwd(), 'src/app/dashboard/automation/workflows');
    
    // Check if directory exists
    if (!fs.existsSync(workflowsDir)) {
      return NextResponse.json({ error: 'Workflows directory not found' }, { status: 404 });
    }

    // Get all JSON files
    let files = fs.readdirSync(workflowsDir).filter(file => file.endsWith('.json'));
    
    console.log(`Found ${files.length} workflow files`);
    
    const workflows = [];

    // Process all files (or with pagination)
    const filesToProcess = limit > 0 ? files.slice(offset, offset + limit) : files;
    
    for (const fileName of filesToProcess) {
      try {
        const filePath = path.join(workflowsDir, fileName);
        const fileContent = fs.readFileSync(filePath, 'utf-8');
        const workflowData = JSON.parse(fileContent);
        
        // Enhanced category detection with main categories and subdivisions
        const getCategoryFromWorkflow = (fileName: string, workflowData: any) => {
          const name = fileName.toLowerCase();
          const workflowName = (workflowData.name || '').toLowerCase();
          const content = (JSON.stringify(workflowData)).toLowerCase();
          
          // Productivity → subdivisions
          if (name.includes('task') || name.includes('todo') || name.includes('reminder') ||
              workflowName.includes('task') || workflowName.includes('todo')) {
            return { mainCategory: 'Productivity', subcategory: 'Task Management', category: 'Task Management' };
          }
          if (name.includes('note') || name.includes('document') || name.includes('text') ||
              workflowName.includes('note') || workflowName.includes('document')) {
            return { mainCategory: 'Productivity', subcategory: 'Note Taking', category: 'Note Taking' };
          }
          if (name.includes('project') || name.includes('plan') || workflowName.includes('project')) {
            return { mainCategory: 'Productivity', subcategory: 'Project Planning', category: 'Project Planning' };
          }
          if (name.includes('time') || name.includes('track') || workflowName.includes('time')) {
            return { mainCategory: 'Productivity', subcategory: 'Time Tracking', category: 'Time Tracking' };
          }
          if (name.includes('automation') && (name.includes('doc') || name.includes('file'))) {
            return { mainCategory: 'Productivity', subcategory: 'Document Automation', category: 'Document Automation' };
          }
          
          // Communication → subdivisions
          if (name.includes('email') || name.includes('gmail') || name.includes('outlook') ||
              workflowName.includes('email')) {
            return { mainCategory: 'Communication', subcategory: 'Email', category: 'Email' };
          }
          if (name.includes('slack') || name.includes('teams') || name.includes('chat') ||
              workflowName.includes('slack') || workflowName.includes('chat')) {
            return { mainCategory: 'Communication', subcategory: 'Team Chat', category: 'Team Chat' };
          }
          if (name.includes('zoom') || name.includes('meet') || name.includes('video') ||
              workflowName.includes('video') || workflowName.includes('call')) {
            return { mainCategory: 'Communication', subcategory: 'Video Calls', category: 'Video Calls' };
          }
          if (name.includes('notification') || name.includes('alert') || workflowName.includes('notification')) {
            return { mainCategory: 'Communication', subcategory: 'Notifications', category: 'Notifications' };
          }
          if (name.includes('twitter') || name.includes('facebook') || name.includes('linkedin') ||
              name.includes('instagram') || name.includes('social') || workflowName.includes('social')) {
            return { mainCategory: 'Communication', subcategory: 'Social Media', category: 'Social Media' };
          }
          
          // Business → subdivisions
          if (name.includes('crm') || name.includes('contact') || name.includes('customer') ||
              workflowName.includes('crm') || workflowName.includes('customer')) {
            return { mainCategory: 'Business', subcategory: 'CRM', category: 'CRM' };
          }
          if (name.includes('sales') || name.includes('lead') || workflowName.includes('sales')) {
            return { mainCategory: 'Business', subcategory: 'Sales', category: 'Sales' };
          }
          if (name.includes('marketing') || name.includes('campaign') || workflowName.includes('marketing')) {
            return { mainCategory: 'Business', subcategory: 'Marketing', category: 'Marketing' };
          }
          if (name.includes('finance') || name.includes('payment') || name.includes('invoice') ||
              name.includes('billing') || workflowName.includes('payment')) {
            return { mainCategory: 'Business', subcategory: 'Finance', category: 'Finance' };
          }
          if (name.includes('hr') || name.includes('employee') || name.includes('staff') ||
              workflowName.includes('employee')) {
            return { mainCategory: 'Business', subcategory: 'HR', category: 'HR' };
          }
          
          // Data & Analytics → subdivisions
          if (name.includes('process') || name.includes('transform') || workflowName.includes('process')) {
            return { mainCategory: 'Data & Analytics', subcategory: 'Data Processing', category: 'Data Processing' };
          }
          if (name.includes('spreadsheet') || name.includes('excel') || name.includes('googlesheets') ||
              workflowName.includes('spreadsheet')) {
            return { mainCategory: 'Data & Analytics', subcategory: 'Spreadsheets', category: 'Spreadsheets' };
          }
          if (name.includes('database') || name.includes('sql') || workflowName.includes('database')) {
            return { mainCategory: 'Data & Analytics', subcategory: 'Database', category: 'Database' };
          }
          if (name.includes('report') || name.includes('analytics') || workflowName.includes('report')) {
            return { mainCategory: 'Data & Analytics', subcategory: 'Reporting', category: 'Reporting' };
          }
          if (name.includes('api') || name.includes('webhook') || name.includes('integration') ||
              workflowName.includes('api')) {
            return { mainCategory: 'Data & Analytics', subcategory: 'API Integration', category: 'API Integration' };
          }
          
          // Security & Operations → subdivisions
          if (name.includes('auth') || name.includes('login') || name.includes('password') ||
              name.includes('2fa') || name.includes('totp') || workflowName.includes('auth')) {
            return { mainCategory: 'Security & Operations', subcategory: 'Authentication', category: 'Authentication' };
          }
          if (name.includes('monitor') || name.includes('health') || workflowName.includes('monitor')) {
            return { mainCategory: 'Security & Operations', subcategory: 'Monitoring', category: 'Monitoring' };
          }
          if (name.includes('backup') || name.includes('restore') || workflowName.includes('backup')) {
            return { mainCategory: 'Security & Operations', subcategory: 'Backup', category: 'Backup' };
          }
          if (name.includes('deploy') || name.includes('build') || workflowName.includes('deploy')) {
            return { mainCategory: 'Security & Operations', subcategory: 'Deployment', category: 'Deployment' };
          }
          if (name.includes('calendar') || name.includes('schedule') || name.includes('cron') ||
              workflowName.includes('schedule')) {
            return { mainCategory: 'Security & Operations', subcategory: 'Calendar & Scheduling', category: 'Calendar & Scheduling' };
          }
          
          // Default fallback
          return { mainCategory: 'Security & Operations', subcategory: 'Others', category: 'Others' };
        };
        
        const categoryInfo = getCategoryFromWorkflow(fileName, workflowData);
        
        const workflow = {
          id: workflowData.id || fileName.replace('.json', ''),
          name: workflowData.name || fileName.replace('.json', '').replace(/_/g, ' ').replace(/^\d+\s*/, ''),
          description: workflowData.name ? `Automated workflow: ${workflowData.name}` : `Workflow with ${workflowData.nodes?.length || 0} steps`,
          category: categoryInfo.category,
          mainCategory: categoryInfo.mainCategory,
          subcategory: categoryInfo.subcategory,
          fileName: fileName,
          nodes: workflowData.nodes || [],
          nodeCount: workflowData.nodes?.length || 0,
          tags: workflowData.tags || []
        };
        
        workflows.push(workflow);
      } catch (error) {
        console.error(`Error parsing workflow ${fileName}:`, error);
      }
    }

    // Apply search and category filters after loading
    let filteredWorkflows = workflows;
    
    if (search) {
      const searchLower = search.toLowerCase();
      filteredWorkflows = workflows.filter(w => 
        w.name.toLowerCase().includes(searchLower) ||
        w.description.toLowerCase().includes(searchLower) ||
        w.category.toLowerCase().includes(searchLower) ||
        (w.mainCategory && w.mainCategory.toLowerCase().includes(searchLower)) ||
        (w.subcategory && w.subcategory.toLowerCase().includes(searchLower))
      );
    }
    
    if (category) {
      filteredWorkflows = filteredWorkflows.filter(w => 
        w.category === category || 
        w.mainCategory === category || 
        w.subcategory === category
      );
    }

    return NextResponse.json({ 
      workflows: filteredWorkflows,
      total: files.length, // Total files in directory
      loaded: workflows.length, // Actually loaded and parsed
      filtered: filteredWorkflows.length, // After search/category filters
      categories: [...new Set(workflows.map(w => w.category))].sort(),
      pagination: {
        offset,
        limit,
        hasMore: offset + limit < files.length
      }
    });
    
  } catch (error) {
    console.error('Error fetching workflows:', error);
    return NextResponse.json({ error: 'Failed to fetch workflows' }, { status: 500 });
  }
}
