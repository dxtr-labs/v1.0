
export interface WorkflowNode {
  id: string;
  type: string;
  data: {
    label: string;
    [key: string]: any;
  };
  position: { x: number; y: number };
}

export interface WorkflowConnection {
  source: string;
  target: string;
  sourceHandle?: string | null;
  targetHandle?: string | null;
}

export interface Workflow {
  id: string;
  name: string;
  nodes: WorkflowNode[];
  connections: WorkflowConnection[];
  creatorId: string;
  version: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface NodeParameter {
  name: string;
  label: string;
  type: 'string' | 'number' | 'boolean' | 'options' | 'json';
  options?: string[];
  required: boolean;
  description?: string;
}

export interface NodeType {
  name: string;
  label: string;
  description: string;
  parameters: NodeParameter[];
  execute: (params: Record<string, any>) => Promise<any>;
}
