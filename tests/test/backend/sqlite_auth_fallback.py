#!/usr/bin/env python3
"""
SQLite Database Fallback for Authentication
Use this when PostgreSQL is not available
"""

import sqlite3
import bcrypt
import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os

class SQLiteAuthManager:
    """SQLite-based authentication manager as PostgreSQL fallback"""
    
    def __init__(self, db_path: str = "local-auth.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
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
            CREATE TABLE IF NOT EXISTS credit_logs (
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
        conn.close()
        print("✅ SQLite authentication database initialized")
    
    async def create_user(self, email: str, password: str, first_name: str = None, 
                         last_name: str = None, username: str = None, 
                         organization: bool = False) -> Dict[str, Any]:
        """Create a new user account"""
        user_id = str(uuid.uuid4())
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (user_id, email, password, first_name, last_name, username, organization)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, email, password_hash, first_name, last_name, username, organization))
            
            # Add welcome bonus
            cursor.execute('''
                INSERT INTO credit_logs (user_id, change, reason)
                VALUES (?, ?, ?)
            ''', (user_id, 100, "Welcome bonus"))
            
            conn.commit()
            
            # Return user data
            return {
                'user_id': user_id,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'credits': 100,
                'organization': organization
            }
            
        except sqlite3.IntegrityError as e:
            if 'email' in str(e):
                raise ValueError("Email already exists")
            elif 'username' in str(e):
                raise ValueError("Username already exists")
            else:
                raise ValueError("User already exists")
        finally:
            conn.close()
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user and return user data if successful"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, email, password, first_name, last_name, username, 
                   organization, credits, created_at, updated_at
            FROM users WHERE email = ?
        ''', (email,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            return {
                'user_id': user[0],
                'email': user[1],
                'password': user[2],
                'first_name': user[3],
                'last_name': user[4],
                'username': user[5],
                'organization': user[6],
                'credits': user[7],
                'created_at': user[8],
                'updated_at': user[9]
            }
        return None
    
    async def update_user_session(self, user_id: str, session_token: str, 
                                 expires_hours: int = 24) -> bool:
        """Update user session token and expiration"""
        expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET session_token = ?, session_expires = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (session_token, expires_at, user_id))
        
        result = cursor.rowcount == 1
        conn.commit()
        conn.close()
        
        return result
    
    async def get_user_by_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get user by session token if not expired"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, email, first_name, last_name, username, 
                   organization, credits, created_at, updated_at
            FROM users 
            WHERE session_token = ? AND session_expires > CURRENT_TIMESTAMP
        ''', (session_token,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'user_id': user[0],
                'email': user[1],
                'first_name': user[2],
                'last_name': user[3],
                'username': user[4],
                'organization': user[5],
                'credits': user[6],
                'created_at': user[7],
                'updated_at': user[8]
            }
        return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by UUID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, email, first_name, last_name, username, 
                   organization, credits, created_at, updated_at
            FROM users WHERE user_id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'user_id': user[0],
                'email': user[1],
                'first_name': user[2],
                'last_name': user[3],
                'username': user[4],
                'organization': user[5],
                'credits': user[6],
                'created_at': user[7],
                'updated_at': user[8]
            }
        return None

# Create global instance for backwards compatibility
sqlite_auth_manager = SQLiteAuthManager()

# Export functions that match the PostgreSQL interface
async def create_user(email: str, password: str, first_name: str = None, 
                     last_name: str = None, username: str = None, 
                     organization: bool = False) -> Dict[str, Any]:
    return await sqlite_auth_manager.create_user(email, password, first_name, last_name, username, organization)

async def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    return await sqlite_auth_manager.authenticate_user(email, password)

async def get_user_by_session(session_token: str) -> Optional[Dict[str, Any]]:
    return await sqlite_auth_manager.get_user_by_session(session_token)

async def update_user_session(user_id: str, session_token: str, expires_hours: int = 24) -> bool:
    return await sqlite_auth_manager.update_user_session(user_id, session_token, expires_hours)

async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    return await sqlite_auth_manager.get_user_by_id(user_id)

# Dummy functions for credits (can be implemented later)
async def add_credits(user_id: str, amount: int, reason: str, service_used: str = None) -> bool:
    return True

async def deduct_credits(user_id: str, amount: int, reason: str, service_used: str = None) -> bool:
    return True

async def get_credit_history(user_id: str, limit: int = 50) -> list:
    return []

if __name__ == "__main__":
    # Test the SQLite auth system
    import asyncio
    
    async def test():
        print("Testing SQLite Auth System...")
        
        # Test user creation
        user = await create_user("test@example.com", "test123", "Test", "User", "testuser")
        print(f"Created user: {user['email']}")
        
        # Test authentication
        auth_user = await authenticate_user("test@example.com", "test123")
        print(f"Authentication successful: {auth_user is not None}")
        
        if auth_user:
            # Test session
            import secrets
            token = secrets.token_urlsafe(32)
            await update_user_session(auth_user['user_id'], token)
            
            session_user = await get_user_by_session(token)
            print(f"Session lookup successful: {session_user is not None}")
    
    asyncio.run(test())
