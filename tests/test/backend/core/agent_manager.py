import asyncpg
import uuid
import json # For handling JSON fields like memory_context
from typing import Optional, Dict, Any

# Import the LLM engine type for type hints
from mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine

class AgentManager:
    def __init__(self, db_pool):
        """
        Initializes the AgentManager with a database connection pool.
        """
        self.db_pool = db_pool
        self._llm_instances = {}  # Cache for LLM instances

    async def _execute_db_query(self, query: str, *args, user_id: str = None, is_admin: bool = False):
        """
        Helper to execute database queries with RLS context.
        """
        async with self.db_pool.acquire() as conn:
            # Set RLS context for the session
            if user_id:
                await conn.execute(f"SET app.current_user_id = '{user_id}';")
            
            if is_admin:
                await conn.execute("SET ROLE app_admin;")
            else:
                await conn.execute("SET ROLE app_user;") # Default for non-admin operations

            try:
                result = await conn.fetch(query, *args)
                return result
            except Exception as e:
                print(f"Database query error: {e}")
                raise
            finally:
                # Reset role and user_id after query
                await conn.execute("RESET ROLE;")
                await conn.execute("RESET app.current_user_id;")

    async def create_agent(self, user_id: str, agent_name: str, agent_role: str, agent_personality: str, agent_expectations: str, trigger_config: dict = None, custom_mcp_code: str = None) -> dict:
        """
        Creates a new agent profile in the database and initializes its CustomMCPLLM instance.
        """
        # Ensure user_id is a valid UUID string
        try:
            uuid.UUID(user_id)
        except ValueError:
            raise ValueError("Invalid user_id provided. Must be a valid UUID.")

        # Create initial workflow structure
        initial_workflow = {
            "nodes": [
                {
                    "id": "trigger_node_1",
                    "type": "manual_trigger",
                    "parameters": {
                        "trigger_type": "manual",
                        "description": f"Manual trigger for {agent_name}"
                    },
                    "position": {"x": 100, "y": 100},
                    "description": f"Trigger node for {agent_name} automation"
                }
            ],
            "edges": [],
            "status": "active",
            "created_from": "agent_creation"
        }

        # First create the workflow
        workflow_id = str(uuid.uuid4())
        workflow_query = """
        INSERT INTO workflows (workflow_id, user_id, workflow_definition, status)
        VALUES ($1, $2, $3, 'active')
        RETURNING workflow_id;
        """
        
        async with self.db_pool.acquire() as conn:
            # Set RLS context
            await conn.execute(f"SET app.current_user_id = '{user_id}';")
            await conn.execute("SET ROLE app_user;")
            
            try:
                # Create workflow first
                await conn.execute(workflow_query, workflow_id, user_id, json.dumps(initial_workflow))
                
                # Then create the agent with the workflow_id
                query = """
                INSERT INTO agents (
                    user_id, agent_name, agent_role, agent_personality, 
                    agent_expectations, trigger_config, custom_mcp_code, workflow_id
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING agent_id, agent_name, agent_role, agent_personality, 
                          agent_expectations, trigger_config, custom_mcp_code, workflow_id;
                """
                
                result = await conn.fetchrow(
                    query, 
                    user_id, agent_name, agent_role, agent_personality,
                    agent_expectations, json.dumps(trigger_config) if trigger_config else None,
                    custom_mcp_code, workflow_id
                )
                
                # Initialize CustomMCPLLM for this agent
                agent_llm = CustomMCPLLMIterationEngine(
                    agent_id=str(result['agent_id']),
                    session_id=f"session_{result['agent_id']}",
                    db_manager=self.db_pool
                )
                
                # Convert DB row to dict and add LLM instance
                agent_data = dict(result)
                agent_data['llm_instance'] = agent_llm
                
                return agent_data
                
            except Exception as e:
                print(f"Error creating agent: {e}")
                raise
            finally:
                await conn.execute("RESET ROLE;")
                await conn.execute("RESET app.current_user_id;")

    async def get_agent_details(self, agent_id: str, user_id: str, is_admin: bool = False) -> dict:
        """
        Retrieves details for a specific agent.
        Access is controlled by RLS: user can only see their own agents unless they are admin.
        """
        query = """
        SELECT agent_id, user_id, agent_name, agent_role, agent_personality, agent_expectations, agent_memory_context
        FROM agents
        WHERE agent_id = $1;
        """
        try:
            row = await self._execute_db_query(query, agent_id, user_id=user_id, is_admin=is_admin)
            if row:
                agent_data = dict(row[0])
                # Ensure memory_context is parsed if stored as JSON string
                if agent_data.get('agent_memory_context'):
                    try:
                        agent_data['agent_memory_context'] = json.loads(agent_data['agent_memory_context'])
                    except json.JSONDecodeError:
                        pass # Keep as string if not valid JSON
                return agent_data
            return None
        except Exception as e:
            print(f"Error retrieving agent details: {e}")
            raise

    async def update_agent_memory(self, agent_id: str, new_memory_context: dict, user_id: str, is_admin: bool = False) -> bool:
        """
        Updates the agent_memory_context for a specific agent.
        """
        # Ensure new_memory_context is a JSON string for storage
        memory_json_str = json.dumps(new_memory_context)

        query = """
        UPDATE agents
        SET agent_memory_context = $1, updated_at = CURRENT_TIMESTAMP
        WHERE agent_id = $2
        RETURNING agent_id;
        """
        try:
            rows = await self._execute_db_query(query, memory_json_str, agent_id, user_id=user_id, is_admin=is_admin)
            return len(rows) > 0 # Returns True if update was successful
        except Exception as e:
            print(f"Error updating agent memory: {e}")
            raise

    async def get_user_agents(self, user_id: str, is_admin: bool = False) -> list[dict]:
        """
        Retrieves all agents belonging to a specific user.
        RLS ensures only the user's agents are returned unless admin.
        """
        query = """
        SELECT agent_id, agent_name, agent_role, agent_personality, agent_expectations, agent_memory_context
        FROM agents
        WHERE user_id = $1;
        """
        try:
            rows = await self._execute_db_query(query, user_id, user_id=user_id, is_admin=is_admin)
            agents = []
            for row in rows:
                agent_data = dict(row)
                if agent_data.get('agent_memory_context'):
                    try:
                        agent_data['agent_memory_context'] = json.loads(agent_data['agent_memory_context'])
                    except json.JSONDecodeError:
                        pass
                agents.append(agent_data)
            return agents
        except Exception as e:
            print(f"Error fetching user agents: {e}")
            raise

    async def delete_agent(self, agent_id: str, user_id: str, is_admin: bool = False) -> bool:
        """
        Deletes an agent. Access controlled by RLS.
        """
        query = """
        DELETE FROM agents
        WHERE agent_id = $1
        RETURNING agent_id;
        """
        try:
            rows = await self._execute_db_query(query, agent_id, user_id=user_id, is_admin=is_admin)
            return len(rows) > 0
        except Exception as e:
            print(f"Error deleting agent: {e}")
            raise

    async def get_agent_llm(self, agent_id: str) -> 'CustomMCPLLMIterationEngine':
        """
        Gets or creates a CustomMCPLLM instance for the specified agent.
        Loads agent context from database if needed.
        """
        # Check cache first
        if agent_id in self._llm_instances:
            return self._llm_instances[agent_id]
        
        # Load agent details from database
        query = """
        SELECT agent_id, agent_name, agent_role, agent_personality, 
               agent_expectations, trigger_config, custom_mcp_code, workflow_id
        FROM agents 
        WHERE agent_id = $1;
        """
        
        async with self.db_pool.acquire() as conn:
            result = await conn.fetchrow(query, agent_id)
            
            if not result:
                raise ValueError(f"Agent {agent_id} not found")
            
            # Get OpenAI API key from environment
            import os
            openai_api_key = os.getenv("OPENAI_API_KEY")
            
            # Prepare agent context
            agent_data = dict(result)
            agent_context = {
                'agent_data': agent_data,
                'memory': {'conversation_history': [], 'context': {'user_preferences': {}}},
                'user_id': 'default_user'
            }
            
            # Initialize CustomMCPLLM with proper context and OpenAI integration
            from mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine
            agent_llm = CustomMCPLLMIterationEngine(
                agent_id=str(result['agent_id']),
                session_id=f"session_{result['agent_id']}",
                db_manager=self.db_pool,
                openai_api_key=openai_api_key,  # Pass OpenAI API key!
                automation_engine=None,  # TODO: Pass automation engine if needed
                agent_context=agent_context  # Pass agent context!
            )
            
            # Cache the instance
            self._llm_instances[agent_id] = agent_llm
            
            return agent_llm
