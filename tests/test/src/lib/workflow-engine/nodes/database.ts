
import { NodeType } from '../types';
import { pool } from '../../db';

export const databaseNode: NodeType = {
  name: 'database',
  label: 'Database Management',
  description: 'Read from or write to a SQL database.',
  parameters: [
    { name: 'operation', label: 'Operation', type: 'options', options: ['select', 'insert', 'update', 'delete'], required: true },
    { name: 'query', label: 'SQL Query', type: 'string', required: true },
  ],
  async execute(params) {
    console.log('Executing database node with params:', params);
    const client = await pool.connect();
    try {
      const result = await client.query(params.query);
      return { success: true, data: result.rows };
    } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return { success: false, error: message };
    } finally {
      client.release();
    }
  },
};
