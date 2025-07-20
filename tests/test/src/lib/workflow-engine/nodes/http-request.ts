
import { NodeType } from '../types';

export const httpRequestNode: NodeType = {
  name: 'http-request',
  label: 'HTTP Request',
  description: 'Makes an HTTP request to an external API.',
  parameters: [
    { name: 'method', label: 'Method', type: 'options', options: ['GET', 'POST', 'PUT', 'DELETE'], required: true },
    { name: 'url', label: 'URL', type: 'string', required: true },
    { name: 'headers', label: 'Headers', type: 'json', required: false },
    { name: 'body', label: 'Body', type: 'json', required: false },
  ],
  async execute(params) {
    console.log('Executing http-request node with params:', params);
    try {
      const response = await fetch(params.url, {
        method: params.method,
        headers: params.headers,
        body: params.body ? JSON.stringify(params.body) : undefined,
      });
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      return { success: false, error: message };
    }
  },
};
