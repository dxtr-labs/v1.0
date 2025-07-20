import { Pool } from 'pg';

export const pool = new Pool({
  user: process.env.POSTGRES_USER || 'postgres',
  host: process.env.POSTGRES_HOST || 'localhost',
  database: process.env.POSTGRES_DATABASE || 'postgres',
  password: process.env.POSTGRES_PASSWORD || 'devhouse',
  port: parseInt(process.env.POSTGRES_PORT || '5432'),
  ssl: process.env.NODE_ENV === 'production' ? {
    rejectUnauthorized: false
  } : false
});

// Test database connection with timeout
export async function testConnection(timeout = 5000): Promise<boolean> {
  return new Promise((resolve) => {
    const timeoutId = setTimeout(() => {
      console.error('Database connection test timed out');
      resolve(false);
    }, timeout);

    pool.query('SELECT NOW()')
      .then(() => {
        clearTimeout(timeoutId);
        resolve(true);
      })
      .catch((error) => {
        clearTimeout(timeoutId);
        console.error('Database connection test failed:', error);
        resolve(false);
      });
  });
}

pool.on('error', (err: Error & { code?: string }) => {
  console.error('Unexpected database error:', err);
  // Attempt to reconnect
  if (err.code === 'PROTOCOL_CONNECTION_LOST') {
    console.log('Lost connection to database. Attempting to reconnect...');
  }
});

export default pool;
