// Simple SQLite database test
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.join(process.cwd(), 'local-auth.db');

const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.log('❌ SQLite connection failed:', err.message);
    process.exit(1);
  }
  console.log('✅ SQLite connection successful!');
  
  // Create users table if it doesn't exist
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      userid INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      first_name TEXT NOT NULL,
      last_name TEXT NOT NULL,
      username TEXT UNIQUE,
      is_organization BOOLEAN DEFAULT 0,
      credits INTEGER DEFAULT 10,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `, (err) => {
    if (err) {
      console.log('❌ Table creation failed:', err.message);
    } else {
      console.log('✅ Users table ready');
    }
    
    // Test query
    db.get('SELECT COUNT(*) as count FROM users', (err, row) => {
      if (err) {
        console.log('❌ Query failed:', err.message);
      } else {
        console.log('📊 Number of users in database:', row.count);
      }
      
      db.close((err) => {
        if (err) {
          console.log('❌ Error closing database:', err.message);
        } else {
          console.log('✅ Database connection closed');
        }
      });
    });
  });
});
