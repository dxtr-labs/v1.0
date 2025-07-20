// lib/user-db.js
// User database operations and workflow management

import crypto from 'crypto';

// Mock database storage (in production, this would be a real database)
const mockAIWorkflows = new Map();
const mockUserLogs = new Map();

// AI Workflow structure (TypeScript interface equivalent)
// {
//   id: string;
//   userId: number;
//   name: string;
//   description?: string;
//   workflow_json: any;
//   created_at: Date;
//   updated_at: Date;
//   status: 'active' | 'inactive' | 'draft';
// }

// Create AI workflow for user
export const createAIWorkflow = async (workflowData) => {
  const id = crypto.randomUUID();
  const workflow = {
    id,
    ...workflowData,
    created_at: new Date(),
    updated_at: new Date(),
    status: 'active'
  };
  
  mockAIWorkflows.set(id, workflow);
  return workflow;
};

// Get user AI workflows
export const getUserAIWorkflows = async (userId, limit = 50) => {
  const userWorkflows = Array.from(mockAIWorkflows.values())
    .filter(workflow => workflow.userId === userId)
    .sort((a, b) => b.created_at.getTime() - a.created_at.getTime())
    .slice(0, limit);
    
  return userWorkflows;
};

// Get specific AI workflow
export const getAIWorkflow = async (workflowId) => {
  return mockAIWorkflows.get(workflowId) || null;
};

// Update AI workflow
export const updateAIWorkflow = async (workflowId, updateData) => {
  const workflow = mockAIWorkflows.get(workflowId);
  if (!workflow) {
    throw new Error('Workflow not found');
  }
  
  const updatedWorkflow = {
    ...workflow,
    ...updateData,
    updated_at: new Date()
  };
  
  mockAIWorkflows.set(workflowId, updatedWorkflow);
  return updatedWorkflow;
};

// Delete AI workflow
export const deleteAIWorkflow = async (workflowId) => {
  const deleted = mockAIWorkflows.delete(workflowId);
  return { success: deleted };
};

// User logs functionality
export const createUserLog = async (logData) => {
  const id = crypto.randomUUID();
  const log = {
    id,
    ...logData,
    created_at: new Date()
  };
  
  mockUserLogs.set(id, log);
  return log;
};

export const getUserLogs = async (userId, limit = 100) => {
  const userLogs = Array.from(mockUserLogs.values())
    .filter(log => log.userId === userId)
    .sort((a, b) => b.created_at.getTime() - a.created_at.getTime())
    .slice(0, limit);
    
  return userLogs;
};

export const deleteUserLog = async (logId) => {
  const deleted = mockUserLogs.delete(logId);
  return { success: deleted };
};

// Aliases for compatibility
export const getUserWorkflowLogs = async (userId, requestId = null, limit = 100) => {
  let userLogs = Array.from(mockUserLogs.values())
    .filter(log => log.userId === userId);
  
  if (requestId) {
    userLogs = userLogs.filter(log => log.requestId === requestId);
  }
  
  return userLogs
    .sort((a, b) => b.created_at.getTime() - a.created_at.getTime())
    .slice(0, limit);
};

export const logUserWorkflowExecution = async (userId, logData) => {
  const id = crypto.randomUUID();
  const log = {
    id,
    userId,
    ...logData,
    created_at: new Date()
  };
  
  mockUserLogs.set(id, log);
  return log;
};
