
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

// This is a top-level await, which is allowed in modern ES modules.
export const dbPromise = open({
  filename: './workflow.db',
  driver: sqlite3.Database
});
