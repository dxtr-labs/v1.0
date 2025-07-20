
import { NodeType } from '../types';

export const schedulerNode: NodeType = {
  name: 'scheduler',
  label: 'Scheduler',
  description: 'Triggers workflows on time-based events.',
  parameters: [
    { name: 'schedule', label: 'Cron Schedule', type: 'string', required: true, description: 'e.g., "0 9 * * 1" for every Monday at 9 AM' },
  ],
  async execute(params) {
    console.log('Executing scheduler node with params:', params);
    // In a real implementation, this would schedule a job.
    return { success: true, message: `Job scheduled with cron: ${params.schedule}` };
  },
};
