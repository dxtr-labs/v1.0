import asyncpg
import os
import json
import logging

class BaseDriver:
    def __init__(self, db_pool: asyncpg.pool.Pool):
        self.db_pool = db_pool
        logging.info(f"Initialized BaseDriver for {self.__class__.__name__}")

    async def _get_user_service_keys(self, user_id: str, service_name: str) -> dict:
        """
        Retrieves service-specific keys from the users.service_keys JSONB column.
        This method needs to be robust and handle encryption/decryption.
        """
        async with self.db_pool.acquire() as conn:
            # Check if we're running as postgres (superuser) - if so, skip role switching
            current_user_result = await conn.fetchrow("SELECT current_user")
            current_user = current_user_result['current_user']
            
            try:
                if current_user != 'postgres':
                    # Only set RLS context and switch roles if not running as postgres superuser
                    await conn.execute(f"SET app.current_user_id = '{user_id}';")
                    await conn.execute("SET ROLE app_user;")
                
                row = await conn.fetchrow(
                    "SELECT service_keys FROM users WHERE user_id = $1",
                    user_id
                )
                if row and row['service_keys']:
                    # Parse JSON if it's a string, or use directly if it's already a dict
                    service_keys = row['service_keys']
                    if isinstance(service_keys, str):
                        import json
                        service_keys = json.loads(service_keys)
                    
                    # Access the specific service's keys
                    keys = service_keys.get(service_name, {})
                    return keys
                return {}
            except Exception as e:
                logging.error(f"Error fetching service keys for user {user_id}, service {service_name}: {e}", exc_info=True)
                raise
            finally:
                if current_user != 'postgres':
                    # Only reset if we switched roles
                    await conn.execute("RESET ROLE;")
                    await conn.execute("RESET app.current_user_id;")

    async def execute(self, parameters: dict, input_data: dict, user_id: str, engine_instance=None) -> dict:
        """
        Abstract method to be implemented by concrete drivers.
        
        Args:
            parameters (dict): The parameters for this specific node from the workflow JSON.
            input_data (dict): The output data from the previous node in the workflow.
            user_id (str): The ID of the user running the workflow.
            engine_instance (AutomationEngine, optional): The main engine instance, needed for logic nodes.

        Returns:
            dict: The output data to be passed to the next node.
        """
        raise NotImplementedError("Execute method must be implemented by subclass.")

