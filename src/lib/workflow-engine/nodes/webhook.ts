
import { NodeType } from '../types';

export const webhookNode: NodeType = {
  name: 'webhook',
  label: 'Webhook',
  description: 'Triggers the workflow when an HTTP request is received.',
  parameters: [
    { name: 'method', label: 'HTTP Method', type: 'options', options: ['GET', 'POST', 'PUT'], required: true },
    { name: 'path', label: 'Path', type: 'string', required: true, description: 'The unique path for this webhook.' },
  ],
  async execute(params) {
    console.log('Executing webhook node with params:', params);
    // In a real implementation, this would register the webhook endpoint.
    // For now, we'll just simulate success.
    return { success: true, data: { message: 'Webhook is waiting for data...' } };
  },
};
