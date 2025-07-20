#!/usr/bin/env python3
"""
Check and fix SQLite database schema
"""

import sqlite3
import os

def check_and_fix_database():
    """Check the current database schema and fix if needed"""
    db_path = "local-auth.db"
    
    print(f"🔍 Checking database: {db_path}")
    
    if os.path.exists(db_path):
        print(f"📁 Database file exists: {os.path.getsize(db_path)} bytes")
        
        # Check current schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("📋 Current users table schema:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Check if user_id column exists
        column_names = [col[1] for col in columns]
        if 'user_id' not in column_names:
            print("❌ user_id column missing - recreating table...")
            
            # Drop and recreate table
            cursor.execute("DROP TABLE IF EXISTS users")
            cursor.execute("DROP TABLE IF EXISTS credit_logs")
            
            # Create users table with correct schema
            cursor.execute('''
                CREATE TABLE users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    username TEXT UNIQUE,
                    organization BOOLEAN DEFAULT FALSE,
                    credits INTEGER DEFAULT 100,
                    session_token TEXT,
                    session_expires TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create credit_logs table
            cursor.execute('''
                CREATE TABLE credit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    change INTEGER NOT NULL,
                    reason TEXT,
                    service_used TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
            print("✅ Database schema fixed!")
        else:
            print("✅ Database schema looks correct")
        
        conn.close()
    else:
        print("📝 Database file doesn't exist - will be created on first use")

if __name__ == "__main__":
    check_and_fix_database()
