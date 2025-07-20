import json
import asyncio
import asyncpg # For database interaction
import os
import uuid # For UUIDs
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Import your action, logic, and trigger node drivers here ---
# These files should be placed in a 'drivers' subdirectory.
from mcp.drivers.email_send_driver import EmailSendDriver
from mcp.drivers.http_request_driver import HttpRequestDriver
from mcp.drivers.twilio_driver import TwilioDriver
from mcp.drivers.email_read_imap_driver import EmailReadImapDriver
from mcp.drivers.cron_driver import CronDriver # For handling cron trigger logic (e.g., registering schedules)
from mcp.drivers.web_hook_driver import WebhookDriver # For handling webhook trigger logic (e.g., setting up listeners)
from mcp.drivers.if_else_driver import IfElseDriver
from mcp.drivers.loop_items_driver import LoopItemsDriver
from mcp.drivers.mcp_llm_driver import MCP_LLM_Driver
from mcp.drivers.openai_driver import OpenAI_Driver
from mcp.drivers.claude_driver import Claude_Driver

class AutomationEngine:
    def __init__(self, db_config: dict, mcp_orchestrator=None):
        self.db_config = db_config
        self.db_pool = None
        self.drivers = {} # Dictionary to hold instances of your node drivers
        self.drivers_registered = False
        self.mcp_orchestrator = mcp_orchestrator  # Store MCP orchestrator reference

    async def _init_db_pool(self):
        """Initializes the PostgreSQL connection pool."""
        if self.db_pool is None:
            self.db_pool = await asyncpg.create_pool(**self.db_config)
            logging.info("Automation Engine: Database connection pool initialized.")
        
        # Register drivers after DB pool is ready
        if not self.drivers_registered:
            self._register_drivers()
            self.drivers_registered = True

    def _register_drivers(self):
        """
        Registers all available action, logic, and trigger drivers.
        Each driver instance is responsible for executing its specific node type.
        """
        # Instantiate your drivers here. Each driver needs access to the DB pool
        # for credential retrieval and potentially for logging/state management.
        
        # Action drivers
        self.drivers['emailSend'] = EmailSendDriver(self.db_pool)
        self.drivers['httpRequest'] = HttpRequestDriver(self.db_pool)
        self.drivers['twilio'] = TwilioDriver(self.db_pool)
        self.drivers['emailReadImap'] = EmailReadImapDriver(self.db_pool)
        
        # AI drivers
        self.drivers['mcpLLM'] = MCP_LLM_Driver(self.db_pool, self.mcp_orchestrator)
        self.drivers['openai'] = OpenAI_Driver(self.db_pool)
        self.drivers['claude'] = Claude_Driver(self.db_pool)
        
        # Trigger drivers (Cron, Webhook) often need to register themselves with an external scheduler/server
        # and might need a reference to the engine to call execute_workflow later.
        self.drivers['cron'] = CronDriver(self.db_pool) 
        self.drivers['webhook'] = WebhookDriver(self.db_pool) 

        # Logic drivers (IfElse, LoopItems) need a reference to the engine to recursively execute sub-nodes.
        self.drivers['ifElse'] = IfElseDriver(self.db_pool, self) 
        self.drivers['loopItems'] = LoopItemsDriver(self.db_pool, self) 

        logging.info("Automation Engine: All node drivers registered.")

    async def _execute_node(self, node_definition: dict, current_data: dict, user_id: str) -> dict:
        """
        Executes a single node (action or logic) and returns its output.
        This is a recursive function for nested logic nodes.
        """
        node_type = node_definition.get("node")
        parameters = node_definition.get("parameters", {})

        if not node_type:
            raise ValueError("Node definition missing 'node' type.")

        driver = self.drivers.get(node_type)
        if not driver:
            raise ValueError(f"No driver registered for node type: {node_type}")

        logging.info(f"Executing node: {node_type} for user {user_id}")
        
        # All drivers will have an 'execute' method
        # Logic nodes (ifElse, loopItems) will receive the engine instance to recurse
        if node_type in ["ifElse", "loopItems"]:
            # Pass the engine instance to logic drivers for recursive execution of sub-workflows
            output_data = await driver.execute(parameters, current_data, user_id, self)
        else:
            output_data = await driver.execute(parameters, current_data, user_id)
        
        logging.info(f"Node {node_type} completed. Output status: {output_data.get('status')}")
        return output_data

    async def execute_workflow(self, workflow_json: dict, user_id: str) -> dict:
        """
        Main method to execute a complete workflow.

        Args:
            workflow_json (dict): The full JSON definition of the workflow.
            user_id (str): The ID of the user executing the workflow (for RLS and credentials).
        """
        await self._init_db_pool() # Ensure DB pool is ready

        logging.info(f"Starting workflow execution for user {user_id}...")
        logging.debug(f"Workflow JSON: {json.dumps(workflow_json, indent=2)}")

        try:
            workflow_data = workflow_json.get("workflow")
            if not workflow_data:
                raise ValueError("Invalid workflow JSON: 'workflow' key missing.")

            trigger_node_def = workflow_data.get("trigger")
            logic_nodes_def = workflow_data.get("logic", [])
            action_nodes_def = workflow_data.get("actions", [])

            if not trigger_node_def or not action_nodes_def:
                raise ValueError("Workflow must have a trigger and at least one action.")

            # --- 1. Handle Trigger ---
            # For immediate execution (e.g., after user confirmation via API),
            # we consider the trigger to have "fired" and provide initial data.
            # For actual scheduled/webhook triggers, this `execute_workflow` method
            # would be called by the respective driver's listener.
            
            initial_data = {"trigger_event": trigger_node_def.get("node"), "user_id": user_id, "trigger_params": trigger_node_def.get("parameters", {})}
            logging.info(f"Workflow initiated by trigger: {trigger_node_def.get('node')}")

            current_data = initial_data

            # --- 2. Orchestrate Execution: Logic and Actions ---
            # This is a simplified sequential execution for top-level nodes.
            # Nested logic (truePath, falsePath, loopBody) is handled recursively by logic drivers.
            
            # Combine top-level logic and action nodes for sequential processing
            # A more complex engine might build a proper DAG (Directed Acyclic Graph)
            # to handle parallel paths and merges.
            all_top_level_nodes = logic_nodes_def + action_nodes_def

            for node_def in all_top_level_nodes:
                # Pass the output of the previous node as input to the current node
                current_data = await self._execute_node(node_def, current_data, user_id)
                # Check for critical errors or early exits from nodes
                if current_data.get("status") == "failed":
                    logging.error(f"Workflow stopped due to failed node: {node_def.get('node')}")
                    return {"status": "failed", "error": f"Node {node_def.get('node')} failed: {current_data.get('error')}"}

            logging.info("Workflow execution completed successfully.")
            return {"status": "success", "final_output": current_data}

        except Exception as e:
            logging.error(f"Workflow execution failed: {e}", exc_info=True)
            return {"status": "failed", "error": str(e)}

# --- Example Usage (for direct testing of AutomationEngine) ---
async def main():
    # Load DB config from environment variables
    db_config = {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", 5432)),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD", "your_db_password"), # REPLACE THIS WITH YOUR ACTUAL DB PASSWORD
        "database": os.getenv("PGDATABASE", "automation")
    }

    engine = AutomationEngine(db_config)
    
    # Simulate a user ID (this would come from your auth system)
    # Ensure this UUID exists in your 'users' table and has an associated agent for testing
    test_user_id = "a1b2c3d4-e5f6-7890-1234-567890abcdef" # REPLACE with a real UUID from your 'users' table

    # Example workflow JSON (this would come from your MCP_LLM after user confirmation)
    # This example includes an emailSend and an httpRequest
    example_workflow = {
      "workflow": {
        "trigger": {
          "node": "manual",
          "parameters": {}
        },
        "logic": [], # Can add ifElse, loopItems here
        "actions": [
          {
            "node": "emailSend",
            "parameters": {
              "toEmail": "test@example.com", # REPLACE with a real email for testing
              "subject": "Test Email from Automation Engine",
              "text": "This is a test email sent by your custom automation engine!"
            }
          },
          {
            "node": "httpRequest",
            "parameters": {
              "url": "https://jsonplaceholder.typicode.com/posts",
              "method": "POST",
              "body": {
                "type": "json",
                "data": {
                  "title": "foo",
                  "body": "bar",
                  "userId": 1
                }
              }
            }
          }
        ]
      }
    }

    print("Automation Engine starting...")
    execution_result = await engine.execute_workflow(example_workflow, test_user_id)
    print("\nExecution Result:", execution_result)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv() # Load .env.local variables
    asyncio.run(main())
