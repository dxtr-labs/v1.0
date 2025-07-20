"""
PostgreSQL Database Utilities for AutoFlow Platform
This module provides database connection and common operations for the new UUID-based schema.
"""

import os
import asyncpg
import bcrypt
import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import json
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Handles all database operations for the AutoFlow platform."""
    
    def __init__(self):
        self.pool = None
        self.connection_config = {
            'user': os.getenv('PGUSER', 'postgres'),
            'password': os.getenv('PGPASSWORD', 'devhouse'),
            'database': os.getenv('PGDATABASE', 'postgres'),
            'host': os.getenv('PGHOST', 'localhost'),
            'port': int(os.getenv('PGPORT', '5432'))
        }
    
    async def initialize(self):
        """Initialize the database connection pool."""
        try:
            self.pool = await asyncpg.create_pool(**self.connection_config)
            logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def close(self):
        """Close the database connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    async def get_connection(self):
        """Get a database connection from the pool."""
        if not self.pool:
            await self.initialize()
        return self.pool.acquire()
    
    # User Management Methods
    async def create_user(self, email: str, password: str, first_name: str = None, 
                         last_name: str = None, username: str = None, 
                         organization: bool = False) -> Dict[str, Any]:
        """Create a new user account."""
        # Hash the password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        async with self.pool.acquire() as conn:
            try:
                user_id = await conn.fetchval("""
                    INSERT INTO users (email, password, first_name, last_name, username, organization)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING user_id
                """, email, password_hash, first_name, last_name, username, organization)
                
                # Create initial credit log entry (welcome bonus)
                await self.add_credits(user_id, 100, "Welcome bonus")
                
                return await self.get_user_by_id(user_id)
            except asyncpg.UniqueViolationError as e:
                if 'email' in str(e):
                    raise ValueError("Email already exists")
                elif 'username' in str(e):
                    raise ValueError("Username already exists")
                else:
                    raise ValueError("User already exists")
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user and return user data if successful."""
        async with self.pool.acquire() as conn:
            user = await conn.fetchrow("""
                SELECT user_id, email, password, first_name, last_name, username, 
                       organization, credits, created_at, updated_at
                FROM users WHERE email = $1
            """, email)
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                return dict(user)
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by UUID."""
        async with self.pool.acquire() as conn:
            user = await conn.fetchrow("""
                SELECT user_id, email, first_name, last_name, username, 
                       organization, credits, memory_context, service_keys,
                       created_at, updated_at
                FROM users WHERE user_id = $1
            """, user_id)
            
            return dict(user) if user else None
    
    async def update_user_session(self, user_id: str, session_token: str, 
                                 expires_hours: int = 24) -> bool:
        """Update user session token and expiration."""
        expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
        
        async with self.pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE users 
                SET session_token = $1, session_expires = $2, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = $3
            """, session_token, expires_at, user_id)
            
            return result == "UPDATE 1"
    
    async def get_user_by_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get user by session token if not expired."""
        async with self.pool.acquire() as conn:
            user = await conn.fetchrow("""
                SELECT user_id, email, first_name, last_name, username, 
                       organization, credits, memory_context, service_keys,
                       created_at, updated_at
                FROM users 
                WHERE session_token = $1 AND session_expires > CURRENT_TIMESTAMP
            """, session_token)
            
            return dict(user) if user else None
    
    # Credit Management Methods
    async def add_credits(self, user_id: str, amount: int, reason: str, 
                         service_used: str = None) -> bool:
        """Add credits to user account."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Add to user's credit balance
                await conn.execute("""
                    UPDATE users SET credits = credits + $1, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = $2
                """, amount, user_id)
                
                # Log the credit change
                await conn.execute("""
                    INSERT INTO credit_logs (user_id, change, reason, service_used)
                    VALUES ($1, $2, $3, $4)
                """, user_id, amount, reason, service_used)
        
        return True
    
    async def deduct_credits(self, user_id: str, amount: int, reason: str, 
                            service_used: str = None) -> bool:
        """Deduct credits from user account if sufficient balance."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Check current balance
                current_credits = await conn.fetchval("""
                    SELECT credits FROM users WHERE user_id = $1
                """, user_id)
                
                if current_credits < amount:
                    return False  # Insufficient credits
                
                # Deduct from user's credit balance
                await conn.execute("""
                    UPDATE users SET credits = credits - $1, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = $2
                """, amount, user_id)
                
                # Log the credit change
                await conn.execute("""
                    INSERT INTO credit_logs (user_id, change, reason, service_used)
                    VALUES ($1, $2, $3, $4)
                """, user_id, -amount, reason, service_used)
        
        return True
    
    async def get_credit_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's credit transaction history."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, change, reason, service_used, created_at
                FROM credit_logs 
                WHERE user_id = $1 
                ORDER BY created_at DESC 
                LIMIT $2
            """, user_id, limit)
            
            return [dict(row) for row in rows]
    
    # Agent Management Methods
    async def create_agent(self, user_id: str, agent_name: str, agent_role: str = None,
                          agent_personality: str = None, agent_expectations: str = None,
                          agent_memory_context: str = None, trigger_config: dict = None,
                          custom_mcp_code: str = None) -> Dict[str, Any]:
        """Create a new AI agent for the user with automatic workflow creation."""
        async with self.pool.acquire() as conn:
            # Start a transaction to create both agent and workflow
            async with conn.transaction():
                # Step 1: Create the workflow first
                workflow_id = str(uuid.uuid4())
                
                # Default workflow definition for the agent
                default_workflow = {
                    "workflow_id": workflow_id,
                    "workflow_name": f"{agent_name} Workflow",
                    "description": f"Custom workflow for {agent_name}",
                    "trigger": {"type": "manual", "config": {}},
                    "nodes": [],
                    "iterations": 0,
                    "status": "draft",
                    "created_by": "agent_creation",
                    "agent_context": {
                        "agent_name": agent_name,
                        "agent_role": agent_role,
                        "personality": agent_personality
                    }
                }
                
                # Insert workflow
                await conn.execute("""
                    INSERT INTO workflows (workflow_id, user_id, workflow_definition, status)
                    VALUES ($1, $2, $3, $4)
                """, workflow_id, user_id, json.dumps(default_workflow), "draft")
                
                # Step 2: Create the agent with the workflow_id
                agent_id = await conn.fetchval("""
                    INSERT INTO agents (user_id, agent_name, agent_role, agent_personality, 
                                      agent_expectations, agent_memory_context, trigger_config, 
                                      custom_mcp_code, workflow_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    RETURNING agent_id
                """, user_id, agent_name, agent_role, agent_personality, 
                    agent_expectations, agent_memory_context, 
                    json.dumps(trigger_config) if trigger_config else None,
                    custom_mcp_code, workflow_id)
                
                logger.info(f"✅ Created agent {agent_id} with workflow {workflow_id}")
                
                # Return the agent data directly instead of calling get_agent_by_id
                agent_data = await conn.fetchrow("""
                    SELECT agent_id, user_id, agent_name, agent_role, agent_personality,
                           agent_expectations, agent_memory_context, workflow_id, created_at, updated_at
                    FROM agents WHERE agent_id = $1
                """, agent_id)
                
                return dict(agent_data) if agent_data else None
    
    async def get_agent_by_id(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent by UUID."""
        async with self.pool.acquire() as conn:
            agent = await conn.fetchrow("""
                SELECT agent_id, user_id, agent_name, agent_role, agent_personality,
                       agent_expectations, agent_memory_context, workflow_id, created_at, updated_at
                FROM agents WHERE agent_id = $1
            """, agent_id)
            
            logger.info(f"🔍 get_agent_by_id({agent_id}): {agent}")
            return dict(agent) if agent else None
    
    async def get_user_agents(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all agents for a specific user."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT agent_id, user_id, agent_name, agent_role, agent_personality,
                       agent_expectations, agent_memory_context, workflow_id, created_at, updated_at
                FROM agents 
                WHERE user_id = $1 
                ORDER BY created_at DESC
            """, user_id)
            
            return [dict(row) for row in rows]
    
    async def update_agent(self, agent_id: str, **kwargs) -> bool:
        """Update agent properties."""
        if not kwargs:
            return False
        
        # Build dynamic update query
        set_clauses = []
        params = []
        param_count = 1
        
        for key, value in kwargs.items():
            if key in ['agent_name', 'agent_role', 'agent_personality', 
                      'agent_expectations', 'agent_memory_context']:
                set_clauses.append(f"{key} = ${param_count}")
                params.append(value)
                param_count += 1
        
        if not set_clauses:
            return False
        
        set_clauses.append(f"updated_at = CURRENT_TIMESTAMP")
        params.append(agent_id)
        
        query = f"""
            UPDATE agents 
            SET {', '.join(set_clauses)}
            WHERE agent_id = ${param_count}
        """
        
        async with self.pool.acquire() as conn:
            result = await conn.execute(query, *params)
            return result == "UPDATE 1"
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent."""
        async with self.pool.acquire() as conn:
            result = await conn.execute("""
                DELETE FROM agents WHERE agent_id = $1
            """, agent_id)
            return result == "DELETE 1"
    
    # Workflow and Chat Methods
    async def create_workflow_request(self, user_id: str, input_prompt: str,
                                    llm_response: Dict = None) -> str:
        """Create a new AI workflow request."""
        async with self.pool.acquire() as conn:
            request_id = await conn.fetchval("""
                INSERT INTO ai_workflow_requests (user_id, input_prompt, llm_response)
                VALUES ($1, $2, $3)
                RETURNING request_id
            """, user_id, input_prompt, json.dumps(llm_response) if llm_response else None)
            
            return str(request_id)
    
    async def add_chat_message(self, request_id: str, user_id: str, 
                              message_role: str, message: str) -> bool:
        """Add a chat message to a workflow request."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO chat_sessions (request_id, user_id, message_role, message)
                VALUES ($1, $2, $3, $4)
            """, uuid.UUID(request_id), user_id, message_role, message)
            return True
    
    async def get_chat_history(self, request_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat history for a workflow request."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, message_role, message, created_at
                FROM chat_sessions 
                WHERE request_id = $1 
                ORDER BY created_at ASC 
                LIMIT $2
            """, uuid.UUID(request_id), limit)
            
            return [dict(row) for row in rows]
    
    # Workflow Management Methods
    async def create_workflow_for_agent(self, agent_id: str, workflow_script: Dict[str, Any] = None) -> str:
        """Create a new workflow for an agent"""
        
        workflow_id = str(uuid.uuid4())
        
        # Default empty workflow script
        default_script = {
            "workflow_id": workflow_id,
            "workflow_name": "Agent Workflow",
            "trigger": {"type": "manual", "config": {}},
            "nodes": [],
            "created_at": datetime.now().isoformat(),
            "iterations": 0
        }
        
        script = workflow_script or default_script
        
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO workflows (workflow_id, agent_id, script, created_at, updated_at)
                VALUES ($1, $2, $3, NOW(), NOW())
            ''', workflow_id, agent_id, json.dumps(script))
        
        logger.info(f"✅ Created workflow {workflow_id} for agent {agent_id}")
        return workflow_id

    async def get_workflow_by_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow for an agent using the existing table structure"""
        
        async with self.pool.acquire() as conn:
            # First get the workflow_id from the agent
            agent_row = await conn.fetchrow('''
                SELECT workflow_id FROM agents WHERE agent_id = $1
            ''', agent_id)
            
            if not agent_row or not agent_row['workflow_id']:
                return None
            
            # Then get the workflow details
            workflow_row = await conn.fetchrow('''
                SELECT workflow_id, user_id, workflow_definition, status, created_at, updated_at
                FROM workflows
                WHERE workflow_id = $1
            ''', agent_row['workflow_id'])
            
            if workflow_row:
                # Parse workflow_definition if it's a string
                workflow_definition = workflow_row['workflow_definition']
                if isinstance(workflow_definition, str):
                    try:
                        import json
                        workflow_definition = json.loads(workflow_definition)
                    except json.JSONDecodeError:
                        workflow_definition = {}
                
                return {
                    "workflow_id": workflow_row['workflow_id'],
                    "agent_id": agent_id,
                    "user_id": workflow_row['user_id'],
                    "script": workflow_definition,
                    "status": workflow_row['status'],
                    "created_at": workflow_row['created_at'],
                    "updated_at": workflow_row['updated_at']
                }
        
        return None

    async def update_workflow_script(self, workflow_id: str, new_script: Dict[str, Any]) -> bool:
        """Update workflow script with new iterations using existing table structure"""
        
        # Increment iteration count
        if "iterations" in new_script:
            new_script["iterations"] += 1
        else:
            new_script["iterations"] = 1
        
        new_script["last_updated"] = datetime.now().isoformat()
        
        async with self.pool.acquire() as conn:
            result = await conn.execute('''
                UPDATE workflows 
                SET workflow_definition = $1, updated_at = NOW(), status = $2
                WHERE workflow_id = $3
            ''', json.dumps(new_script), "updated", workflow_id)
            
            logger.info(f"✅ Updated workflow {workflow_id} - iteration {new_script.get('iterations', 0)}")
            return result == "UPDATE 1"

    async def get_workflow_by_id(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow by workflow_id using existing table structure"""
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT workflow_id, user_id, workflow_definition, status, created_at, updated_at
                FROM workflows
                WHERE workflow_id = $1
            ''', workflow_id)
            
            if row:
                return {
                    "workflow_id": row['workflow_id'],
                    "user_id": row['user_id'],
                    "script": row['workflow_definition'],
                    "status": row['status'],
                    "created_at": row['created_at'],
                    "updated_at": row['updated_at']
                }
        
        return None

# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions
async def init_db():
    """Initialize database connection."""
    await db_manager.initialize()

async def close_db():
    """Close database connection."""
    await db_manager.close()

# Export commonly used functions
create_user = db_manager.create_user
authenticate_user = db_manager.authenticate_user
get_user_by_id = db_manager.get_user_by_id
get_user_by_session = db_manager.get_user_by_session
update_user_session = db_manager.update_user_session
create_agent = db_manager.create_agent
get_user_agents = db_manager.get_user_agents
get_agent_by_id = db_manager.get_agent_by_id
update_agent = db_manager.update_agent
delete_agent = db_manager.delete_agent
add_credits = db_manager.add_credits
deduct_credits = db_manager.deduct_credits
get_credit_history = db_manager.get_credit_history
create_workflow_request = db_manager.create_workflow_request
add_chat_message = db_manager.add_chat_message
get_chat_history = db_manager.get_chat_history
get_workflow_by_agent = db_manager.get_workflow_by_agent
update_workflow_script = db_manager.update_workflow_script
get_workflow_by_id = db_manager.get_workflow_by_id
