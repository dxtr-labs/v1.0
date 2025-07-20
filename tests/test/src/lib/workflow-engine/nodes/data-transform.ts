
import { NodeType } from '../types';

export const dataTransformNode: NodeType = {
  name: 'data-transform',
  label: 'Data Transformation',
  description: 'Modifies, cleans, or converts data between steps.',
  parameters: [
    { name: 'expression', label: 'Transformation Logic', type: 'string', required: true, description: 'e.g., { "newName": data.oldName.toUpperCase() }' },
  ],
  async execute(params) {
    console.log('Executing data-transform node with params:', params);
    // In a real implementation, this would use a safe execution environment like vm2
    return { success: true, result: 'transformed_data' };
  },
};
