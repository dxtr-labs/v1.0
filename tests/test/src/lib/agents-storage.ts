// Simple in-memory storage for agents
// In production, this should be replaced with a proper database

let agentsStorage: any[] = [];

// Initialize from localStorage if available (browser only)
if (typeof window !== 'undefined') {
  try {
    const stored = localStorage.getItem('agents-storage');
    if (stored) {
      agentsStorage = JSON.parse(stored);
      console.log('Loaded agents from localStorage:', agentsStorage.length);
    }
  } catch (error) {
    console.error('Error loading agents from localStorage:', error);
  }
}

function saveToLocalStorage() {
  if (typeof window !== 'undefined') {
    try {
      localStorage.setItem('agents-storage', JSON.stringify(agentsStorage));
    } catch (error) {
      console.error('Error saving agents to localStorage:', error);
    }
  }
}

export function getAgents() {
  // Try to load from localStorage on server-side too
  if (typeof window !== 'undefined') {
    try {
      const stored = localStorage.getItem('agents-storage');
      if (stored) {
        agentsStorage = JSON.parse(stored);
      }
    } catch (error) {
      // Ignore errors
    }
  }
  
  console.log('Getting agents from storage:', agentsStorage.length, 'agents');
  return agentsStorage;
}

export function addAgent(agent: any) {
  agentsStorage.push(agent);
  saveToLocalStorage();
  console.log('Added agent to storage. Total agents:', agentsStorage.length);
  console.log('Storage contents:', agentsStorage);
  return agent;
}

export function deleteAgent(agentId: string) {
  const index = agentsStorage.findIndex(agent => agent.AgentID === agentId);
  if (index !== -1) {
    const deleted = agentsStorage.splice(index, 1)[0];
    saveToLocalStorage();
    return deleted;
  }
  return null;
}

export function findAgent(agentId: string) {
  return agentsStorage.find(agent => agent.AgentID === agentId);
}

export function updateAgent(agentId: string, updates: any) {
  const index = agentsStorage.findIndex(agent => agent.AgentID === agentId);
  if (index !== -1) {
    agentsStorage[index] = { ...agentsStorage[index], ...updates };
    saveToLocalStorage();
    return agentsStorage[index];
  }
  return null;
}
