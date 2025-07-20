import { NodeType } from './types';

class NodeRegistry {
  private nodes: Map<string, NodeType> = new Map();

  register(node: NodeType) {
    if (this.nodes.has(node.name)) {
      throw new Error(`Node type "${node.name}" is already registered.`);
    }
    this.nodes.set(node.name, node);
  }

  get(nodeName: string): NodeType | undefined {
    return this.nodes.get(nodeName);
  }

  list(): NodeType[] {
    return Array.from(this.nodes.values());
  }
}

export const nodeRegistry = new NodeRegistry();

// Register some basic nodes for demonstration
import { sendEmailNode } from './nodes/send-email';
import { webhookNode } from './nodes/webhook';
import { filterNode } from './nodes/filter';
import { httpRequestNode } from './nodes/http-request';
import { dataTransformNode } from './nodes/data-transform';
import { databaseNode } from './nodes/database';
import { aiTextNode } from './nodes/ai-text';
import { spreadsheetNode } from './nodes/spreadsheet';
import { conditionalNode } from './nodes/conditional';
import { smsNode } from './nodes/sms';
import { summarizeNode } from './nodes/summarize';
import { schedulerNode } from './nodes/scheduler';

nodeRegistry.register(sendEmailNode);
nodeRegistry.register(webhookNode);
nodeRegistry.register(filterNode);
nodeRegistry.register(httpRequestNode);
nodeRegistry.register(dataTransformNode);
nodeRegistry.register(databaseNode);
nodeRegistry.register(aiTextNode);
nodeRegistry.register(spreadsheetNode);
nodeRegistry.register(conditionalNode);
nodeRegistry.register(smsNode);
nodeRegistry.register(summarizeNode);
nodeRegistry.register(schedulerNode);
