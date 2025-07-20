import logging
import sys
import os

# Add the backend directory to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(backend_dir)

from mcp.drivers.base_driver import BaseDriver

class LoopItemsDriver(BaseDriver):
    def __init__(self, db_pool, engine_instance):
        super().__init__(db_pool)
        self.engine = engine_instance # Reference to the main AutomationEngine for recursive calls

    async def execute(self, parameters: dict, input_data: dict, user_id: str, engine_instance=None) -> dict:
        logging.info(f"LoopItemsDriver: Executing for user {user_id}")

        # 1. Parameter Validation
        required_params = ["items", "loopBody"]
        if not all(p in parameters for p in required_params):
            logging.error(f"LoopItemsDriver: Missing required parameter: {required_params}")
            return {"status": "failed", "error": f"Missing required parameter: {required_params}"}

        items_expression = parameters["items"]
        loop_body_nodes = parameters["loopBody"]
        
        # 2. Resolve Items List (CRITICAL: Implement securely!)
        # This is similar to condition evaluation. You need to safely extract the list
        # from the input_data based on the 'items_expression'.
        # Example: "{{$node['Get Data'].json['users']}}"
        items_to_loop = []
        try:
            # Placeholder: A real implementation would parse and safely resolve items_expression
            # For demonstration, assume input_data directly contains a list under 'users'
            if "users" in input_data and isinstance(input_data["users"], list):
                items_to_loop = input_data["users"]
            else:
                logging.warning(f"LoopItemsDriver: Placeholder item resolution for '{items_expression}'. Assuming empty list.")
                items_to_loop = [] # Default to empty if not explicitly resolved

            logging.info(f"LoopItemsDriver: Resolved {len(items_to_loop)} items to loop over.")

        except Exception as e:
            logging.error(f"LoopItemsDriver: Error resolving items expression '{items_expression}': {e}", exc_info=True)
            return {"status": "failed", "error": f"Error resolving items for loop: {e}"}

        # 3. Execute Loop Body for each item
        loop_results = []
        for i, item in enumerate(items_to_loop):
            logging.info(f"LoopItemsDriver: Processing item {i+1}/{len(items_to_loop)}")
            # The 'input_data' for each iteration of the loop body is the current item.
            # You might want to merge it with the original input_data if needed.
            iteration_input_data = {"current_item": item, **input_data} # Merge current item with original input

            item_output = iteration_input_data # Initialize output for this item
            for node_def in loop_body_nodes:
                # Recursively call the engine's _execute_node for nested nodes
                item_output = await self.engine._execute_node(node_def, item_output, user_id)
                if item_output.get("status") == "failed":
                    logging.error(f"LoopItemsDriver: Node in loopBody failed for item {i+1}: {node_def.get('node')}")
                    # Decide if you want to stop the whole loop or just log and continue
                    return {"status": "failed", "error": f"Loop iteration {i+1} failed: {item_output.get('error')}"}
            loop_results.append(item_output)

        logging.info(f"LoopItemsDriver: Loop completed. Processed {len(items_to_loop)} items.")
        return {"status": "success", "loop_results": loop_results}

