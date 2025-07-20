# backend/automation_engine/engine.py
# Custom Automation Engine to interpret and execute workflow JSON

import time
import requests
import json
from typing import Dict, List, Any

class NodeExecutor:
    def __init__(self, workflow: Dict[str, Any]):
        self.nodes = workflow.get("nodes", [])
        self.connections = workflow.get("connections", {})
        self.context = {}  # shared memory between nodes
        self.node_outputs = {}

    def execute_workflow(self):
        # Find the trigger node (manual, cron, webhook)
        trigger_node = next((n for n in self.nodes if n['type'].endswith('Trigger')), None)
        if not trigger_node:
            raise ValueError("No trigger node found")

        print(f"Triggering node: {trigger_node['name']}")
        self.run_node(trigger_node['name'])

    def run_node(self, node_name: str):
        node = next((n for n in self.nodes if n['name'] == node_name), None)
        if not node:
            raise ValueError(f"Node '{node_name}' not found")

        node_type = node['type']
        params = node.get("parameters", {})
        print(f"Running node '{node_name}' of type '{node_type}'")

        output = None
        if node_type == "manualTrigger":
            output = {"manual": True}

        elif node_type == "httpRequest":
            method = params.get("method", "GET")
            url = params["url"]
            headers = params.get("headers", {})
            body = params.get("body")
            res = requests.request(method, url, headers=headers, data=body)
            output = res.json()

        elif node_type == "set":
            output = params.get("fields", {})

        elif node_type == "if":
            a = self.resolve(params["valueA"])
            b = self.resolve(params["valueB"])
            condition = params.get("operation", "equals")
            output = {"pass": False}
            if condition == "equals":
                output["pass"] = a == b
            elif condition == "greater":
                output["pass"] = a > b

        # Add additional node types here...

        self.node_outputs[node_name] = output

        next_nodes = self.connections.get(node_name, [])
        if isinstance(next_nodes, dict):  # conditional outputs
            if output.get("pass"):
                next_list = next_nodes.get("true", [])
            else:
                next_list = next_nodes.get("false", [])
        else:
            next_list = next_nodes

        for next_node in next_list:
            self.run_node(next_node)

    def resolve(self, val):
        # Handle variable references (e.g., {{node_name.field}})
        if isinstance(val, str) and val.startswith("{{"):
            path = val.strip("{} ").split(".")
            node_data = self.node_outputs.get(path[0], {})
            return node_data.get(path[1], None)
        return val

# Entry function for FastAPI endpoint

def run_workflow(workflow_json: Dict[str, Any]):
    executor = NodeExecutor(workflow_json)
    executor.execute_workflow()
    return executor.node_outputs
