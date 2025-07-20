// /lib/firebase.ts (or wherever your database functions are)

import { Pool } from 'pg'; // Assuming you're using 'pg' for PostgreSQL connection

// Initialize PostgreSQL connection pool
const pool = new Pool({
  host: process.env.PGHOST,
  port: parseInt(process.env.PGPORT || '5432'),
  user: process.env.PGUSER,
  password: process.env.PGPASSWORD,
  database: process.env.PGDATABASE,
  ssl: {
    rejectUnauthorized: false // Use with caution in production. Better to provide CA cert.
  }
});

const ENABLE_LOGGING = process.env.ENABLE_LOGGING === 'true'; // For debugging logs

// Function to insert prompt and response into the database
export async function insertPromptAndResponseToDB(requestId: string, userPrompt: string, aiResponse: string) {
  if (ENABLE_LOGGING) console.log(`Attempting to log prompt and response for request_id: ${requestId}`);
  try {
    const client = await pool.connect();
    try {
      const query = `
        INSERT INTO ai_workflow_requests (request_id, user_prompt, ai_response)
        VALUES ($1, $2, $3);
      `;
      const values = [requestId, userPrompt, aiResponse];
      await client.query(query, values);
      if (ENABLE_LOGGING) console.log(`Successfully logged prompt and response for request_id: ${requestId}`);
    } finally {
      client.release();
    }
  } catch (error: unknown) {
    const errorMessage = `Database insertion failed: ${error instanceof Error ? error.message : String(error)}`;
    console.error(`DB Error: ${errorMessage}`);
    throw new Error(errorMessage); // Re-throw to be caught by the API route's catch block
  }
}

// Function to log workflow status to the database
export async function logWorkflowStatusToDB(requestId: string, logLevel: string, message: string) {
  if (ENABLE_LOGGING) console.log(`Attempting to log workflow status for request_id: ${requestId}, level: ${logLevel}`);
  try {
    const client = await pool.connect();
    try {
      const query = `
        INSERT INTO n8n_workflow_logs (request_id, log_level, message)
        VALUES ($1, $2, $3);
      `;
      const values = [requestId, logLevel, message];
      await client.query(query, values);
      if (ENABLE_LOGGING) console.log(`Successfully logged status for request_id: ${requestId}`);
    } finally {
      client.release();
    }
  } catch (error: unknown) {
    const errorMessage = `Failed to log status for request_id ${requestId}: ${error instanceof Error ? error.message : String(error)}`;
    console.error(`DB Log Error: ${errorMessage}`);
    // Do not re-throw here, as logging failure shouldn't necessarily stop the main process
  }
}