import logging
import sys
import os

# Add the backend directory to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(backend_dir)

from mcp.drivers.base_driver import BaseDriver

class IfElseDriver(BaseDriver):
    def __init__(self, db_pool, engine_instance):
        super().__init__(db_pool)
        self.engine = engine_instance # Reference to the main AutomationEngine for recursive calls

    async def execute(self, parameters: dict, input_data: dict, user_id: str, engine_instance=None) -> dict:
        logging.info(f"IfElseDriver: Executing for user {user_id}")

        # 1. Parameter Validation
        required_params = ["condition", "truePath", "falsePath"]
        if not all(p in parameters for p in required_params):
            logging.error(f"IfElseDriver: Missing required parameter: {required_params}")
            return {"status": "failed", "error": f"Missing required parameter: {required_params}"}

        condition_str = parameters["condition"]
        true_path_nodes = parameters["truePath"]
        false_path_nodes = parameters["falsePath"]

        # 2. Evaluate Condition (CRITICAL: Implement securely!)
        # This is where you need a safe expression evaluator.
        # Example: "{{$json.status == 'completed'}}"
        # DO NOT use eval() or exec() with untrusted input.
        # Consider libraries like `jsonpath-rw` or a custom, sandboxed expression parser.
        condition_met = False
        try:
            # Placeholder: A real implementation would parse and safely evaluate condition_str
            # against the input_data.
            # For demonstration, let's assume a simple check if 'status' in input_data is 'completed'
            if "status" in input_data and input_data["status"] == "completed":
                condition_met = True
            elif "value" in input_data and input_data["value"] > 100: # Example for a numeric condition
                condition_met = True
            else: # Fallback for other conditions
                logging.warning(f"IfElseDriver: Placeholder condition evaluation for '{condition_str}'. Assuming False.")
                condition_met = False # Default to false if not explicitly handled
            
            logging.info(f"IfElseDriver: Condition '{condition_str}' evaluated to: {condition_met}")

        except Exception as e:
            logging.error(f"IfElseDriver: Error evaluating condition '{condition_str}': {e}", exc_info=True)
            return {"status": "failed", "error": f"Error evaluating condition: {e}"}

        # 3. Execute the appropriate path
        path_output = input_data # Start with current input_data for the path
        if condition_met:
            logging.info("IfElseDriver: Condition is TRUE. Executing truePath.")
            for node_def in true_path_nodes:
                # Recursively call the engine's _execute_node for nested nodes
                path_output = await self.engine._execute_node(node_def, path_output, user_id)
                if path_output.get("status") == "failed":
                    logging.error(f"IfElseDriver: Node in truePath failed: {node_def.get('node')}")
                    return path_output # Propagate failure
        else:
            logging.info("IfElseDriver: Condition is FALSE. Executing falsePath.")
            for node_def in false_path_nodes:
                # Recursively call the engine's _execute_node for nested nodes
                path_output = await self.engine._execute_node(node_def, path_output, user_id)
                if path_output.get("status") == "failed":
                    logging.error(f"IfElseDriver: Node in falsePath failed: {node_def.get('node')}")
                    return path_output # Propagate failure

        return {"status": "success", "output": path_output}
