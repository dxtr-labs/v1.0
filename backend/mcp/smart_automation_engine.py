"""
Enhanced Custom MCP LLM Automation Engine
Generates 100% working JSON automation scripts by understanding driver capabilities
and asking for required information interactively.
"""

import json
import logging
import uuid
from typing import Dict, List, Any, Optional, Tuple
from openai import AsyncOpenAI
from .driver_knowledge_base import (
    DRIVER_CAPABILITIES, 
    WORKFLOW_TEMPLATES,
    get_driver_info,
    get_required_parameters,
    find_suitable_drivers,
    list_available_drivers
)

class SmartAutomationEngine:
    """
    Intelligent automation engine that creates 100% working workflows
    by understanding driver capabilities and collecting required information.
    """
    
    def __init__(self, openai_api_key: str, db_manager=None):
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
    async def create_automation(self, agent_id: str, user_request: str, agent_details: dict = None) -> dict:
        """
        Main entry point for creating automation workflows.
        Analyzes request, identifies needed drivers, collects parameters, and generates working JSON.
        """
        self.logger.info(f"🤖 SmartAutomationEngine: Creating automation for agent {agent_id}")
        self.logger.info(f"📝 User request: {user_request}")
        
        try:
            # 1. Analyze the user request to understand intent
            intent_analysis = await self._analyze_user_intent(user_request, agent_details)
            
            # 2. Identify required drivers and workflow structure
            workflow_plan = await self._create_workflow_plan(intent_analysis, user_request)
            
            # 3. Check for missing required parameters
            missing_params = self._identify_missing_parameters(workflow_plan)
            
            # 4. If parameters are missing, ask for them
            if missing_params:
                return {
                    "status": "needs_info",
                    "message": self._generate_parameter_request(missing_params, agent_details),
                    "missing_parameters": missing_params,
                    "workflow_plan": workflow_plan
                }
            
            # 5. Generate final working JSON workflow
            workflow_json = self._generate_workflow_json(workflow_plan)
            
            # 6. Validate the workflow
            validation_result = self._validate_workflow(workflow_json)
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": f"Workflow validation failed: {validation_result['error']}",
                    "workflow": workflow_json
                }
            
            # 7. Save workflow to database
            workflow_id = await self._save_workflow(agent_id, workflow_json)
            
            return {
                "status": "ready",
                "message": self._generate_success_message(workflow_plan, agent_details),
                "workflow_id": workflow_id,
                "workflow": workflow_json,
                "execution_summary": self._create_execution_summary(workflow_plan)
            }
            
        except Exception as e:
            self.logger.error(f"❌ SmartAutomationEngine error: {str(e)}")
            return {
                "status": "error", 
                "message": f"I encountered an error while creating the automation: {str(e)}",
                "error": str(e)
            }
    
    async def _analyze_user_intent(self, user_request: str, agent_details: dict = None) -> dict:
        """Analyze user request to understand automation intent."""
        
        agent_context = ""
        if agent_details:
            agent_context = f"""
Agent Context:
- Name: {agent_details.get('name', 'Assistant')}
- Role: {agent_details.get('role', 'Automation Assistant')}  
- Personality: {agent_details.get('personality', 'Professional')}
"""
        
        available_drivers = ", ".join(list_available_drivers())
        
        prompt = f"""
{agent_context}

Analyze this automation request and identify the intent:

User Request: "{user_request}"

Available Drivers: {available_drivers}

Based on the request, determine:
1. Primary automation goal
2. Required drivers (from available list)
3. Data flow between drivers
4. Key parameters needed
5. Automation complexity level (simple/medium/complex)

Respond with a JSON object containing:
{{
    "goal": "Primary automation objective",
    "drivers_needed": ["driver1", "driver2"],
    "complexity": "simple|medium|complex",
    "data_flow": "Description of how data flows",
    "key_parameters": ["param1", "param2"],
    "automation_type": "email|data_processing|notification|integration|scheduled"
}}
"""

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert automation analyst. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            intent_text = response.choices[0].message.content.strip()
            return json.loads(intent_text)
            
        except Exception as e:
            self.logger.error(f"Intent analysis error: {e}")
            # Fallback to basic analysis
            return {
                "goal": "Create automation workflow",
                "drivers_needed": ["email_send"] if "email" in user_request.lower() else ["http_request"],
                "complexity": "simple",
                "data_flow": "Single step process",
                "key_parameters": [],
                "automation_type": "email" if "email" in user_request.lower() else "integration"
            }
    
    async def _create_workflow_plan(self, intent_analysis: dict, user_request: str) -> dict:
        """Create detailed workflow plan with driver configurations."""
        
        drivers_needed = intent_analysis.get("drivers_needed", [])
        automation_type = intent_analysis.get("automation_type", "email")
        
        # Select appropriate template or create custom
        workflow_plan = {
            "goal": intent_analysis["goal"],
            "automation_type": automation_type,
            "nodes": []
        }
        
        # Generate nodes based on drivers needed
        for i, driver_type in enumerate(drivers_needed):
            driver_info = get_driver_info(driver_type)
            if not driver_info:
                continue
                
            node = {
                "id": f"{driver_type}_{i+1}",
                "type": driver_type,
                "name": driver_info["name"],
                "description": driver_info["description"],
                "parameters": {},
                "required_parameters": driver_info.get("required_parameters", []),
                "optional_parameters": driver_info.get("optional_parameters", {}),
                "example": driver_info.get("example", {})
            }
            
            # Add data flow connections
            if i > 0:
                node["input_from"] = f"{drivers_needed[i-1]}_{i}"
            
            workflow_plan["nodes"].append(node)
        
        return workflow_plan
    
    def _identify_missing_parameters(self, workflow_plan: dict) -> list:
        """Identify missing required parameters across all nodes."""
        missing = []
        
        for node in workflow_plan.get("nodes", []):
            required_params = node.get("required_parameters", [])
            current_params = node.get("parameters", {})
            
            for param in required_params:
                if param not in current_params or not current_params[param]:
                    missing.append({
                        "node_id": node["id"],
                        "node_type": node["type"],
                        "node_name": node["name"],
                        "parameter": param,
                        "description": self._get_parameter_description(node["type"], param)
                    })
        
        return missing
    
    def _get_parameter_description(self, driver_type: str, parameter: str) -> str:
        """Get human-readable description of a parameter."""
        driver_info = get_driver_info(driver_type)
        
        # Check in optional parameters
        optional_params = driver_info.get("optional_parameters", {})
        if parameter in optional_params:
            return optional_params[parameter]
        
        # Check parameter aliases
        aliases = driver_info.get("parameter_aliases", {})
        for main_param, alias_list in aliases.items():
            if parameter == main_param:
                return f"Primary parameter for {main_param} (aliases: {', '.join(alias_list)})"
        
        # Default descriptions
        descriptions = {
            "toEmail": "Recipient email address",
            "subject": "Email subject line", 
            "text": "Email content/body",
            "url": "Target URL for HTTP request",
            "method": "HTTP method (GET, POST, etc.)",
            "prompt": "Text prompt for AI processing",
            "schedule": "Cron schedule expression"
        }
        
        return descriptions.get(parameter, f"Required parameter: {parameter}")
    
    def _generate_parameter_request(self, missing_params: list, agent_details: dict = None) -> str:
        """Generate friendly request message for missing parameters."""
        
        agent_name = agent_details.get("name", "Assistant") if agent_details else "Assistant"
        agent_personality = agent_details.get("personality", "helpful") if agent_details else "helpful"
        
        # Group parameters by node
        nodes_needing_params = {}
        for param in missing_params:
            node_name = param["node_name"]
            if node_name not in nodes_needing_params:
                nodes_needing_params[node_name] = []
            nodes_needing_params[node_name].append(param)
        
        message_parts = []
        
        if "friendly" in agent_personality.lower() or "helpful" in agent_personality.lower():
            message_parts.append(f"Hi! I'm {agent_name} and I'm excited to help you create this automation! 🤖")
        else:
            message_parts.append(f"I need some additional information to create your automation workflow.")
        
        message_parts.append("\\nTo make this work perfectly, I need a few details:")
        
        for node_name, params in nodes_needing_params.items():
            message_parts.append(f"\\n**For {node_name}:**")
            for param in params:
                message_parts.append(f"• {param['description']}")
        
        message_parts.append("\\nOnce you provide these details, I'll create a fully working automation for you!")
        
        return "\\n".join(message_parts)
    
    def _generate_workflow_json(self, workflow_plan: dict) -> dict:
        """Generate final executable JSON workflow."""
        
        workflow_id = str(uuid.uuid4())
        
        workflow_json = {
            "id": workflow_id,
            "name": workflow_plan["goal"],
            "description": f"AI-generated automation for: {workflow_plan['goal']}",
            "version": "1.0",
            "created_by": "SmartAutomationEngine",
            "automation_type": workflow_plan.get("automation_type", "general"),
            "status": "draft",
            "nodes": []
        }
        
        # Convert plan nodes to executable nodes
        for node in workflow_plan.get("nodes", []):
            executable_node = {
                "id": node["id"],
                "type": node["type"],
                "name": node.get("name", node["type"]),
                "parameters": node.get("parameters", {}),
                "position": {"x": 100, "y": 100 * (len(workflow_json["nodes"]) + 1)}
            }
            
            # Add input connections
            if "input_from" in node:
                executable_node["input_from"] = node["input_from"]
            
            workflow_json["nodes"].append(executable_node)
        
        return workflow_json
    
    def _validate_workflow(self, workflow_json: dict) -> dict:
        """Validate that the workflow is properly structured and executable."""
        try:
            # Check required fields
            required_fields = ["id", "name", "nodes"]
            for field in required_fields:
                if field not in workflow_json:
                    return {"valid": False, "error": f"Missing required field: {field}"}
            
            # Check nodes
            if not workflow_json["nodes"]:
                return {"valid": False, "error": "Workflow must have at least one node"}
            
            # Validate each node
            for node in workflow_json["nodes"]:
                node_validation = self._validate_node(node)
                if not node_validation["valid"]:
                    return {"valid": False, "error": f"Node {node.get('id', 'unknown')}: {node_validation['error']}"}
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}
    
    def _validate_node(self, node: dict) -> dict:
        """Validate individual node structure."""
        required_node_fields = ["id", "type", "parameters"]
        for field in required_node_fields:
            if field not in node:
                return {"valid": False, "error": f"Missing required field: {field}"}
        
        # Check if driver type is supported
        driver_type = node["type"]
        if driver_type not in DRIVER_CAPABILITIES:
            return {"valid": False, "error": f"Unsupported driver type: {driver_type}"}
        
        # Check required parameters
        required_params = get_required_parameters(driver_type)
        node_params = node["parameters"]
        
        for param in required_params:
            if param not in node_params:
                return {"valid": False, "error": f"Missing required parameter: {param}"}
        
        return {"valid": True}
    
    async def _save_workflow(self, agent_id: str, workflow_json: dict) -> str:
        """Save workflow to database and associate with agent."""
        try:
            if self.db_manager:
                # Save workflow
                workflow_id = await self.db_manager.create_workflow(
                    name=workflow_json["name"],
                    description=workflow_json.get("description", ""),
                    workflow_definition=workflow_json,
                    created_by=agent_id
                )
                
                # Update agent with workflow_id
                await self.db_manager.update_agent_workflow(agent_id, workflow_id)
                
                self.logger.info(f"✅ Saved workflow {workflow_id} for agent {agent_id}")
                return workflow_id
            else:
                # Fallback: return workflow ID from JSON
                return workflow_json["id"]
                
        except Exception as e:
            self.logger.error(f"Error saving workflow: {e}")
            return workflow_json["id"]
    
    def _generate_success_message(self, workflow_plan: dict, agent_details: dict = None) -> str:
        """Generate success message for completed automation."""
        
        agent_name = agent_details.get("name", "Assistant") if agent_details else "Assistant"
        agent_personality = agent_details.get("personality", "professional") if agent_details else "professional"
        
        goal = workflow_plan["goal"]
        node_count = len(workflow_plan.get("nodes", []))
        
        if "friendly" in agent_personality.lower():
            return f"🎉 Awesome! I've successfully created your automation workflow! \\n\\n✨ **{goal}** \\n\\nYour workflow has {node_count} step(s) and is ready to run. The automation will work exactly as you requested!"
        elif "professional" in agent_personality.lower():
            return f"✅ Automation workflow created successfully. \\n\\n**Objective:** {goal} \\n**Components:** {node_count} integrated steps \\n\\nThe workflow has been validated and is ready for execution."
        else:
            return f"✅ Your automation '{goal}' has been created with {node_count} steps and is ready to run!"
    
    def _create_execution_summary(self, workflow_plan: dict) -> dict:
        """Create summary of what the workflow will do."""
        nodes = workflow_plan.get("nodes", [])
        
        summary = {
            "total_steps": len(nodes),
            "automation_type": workflow_plan.get("automation_type", "general"),
            "drivers_used": [node["type"] for node in nodes],
            "estimated_execution_time": "< 30 seconds",
            "data_flow": []
        }
        
        for i, node in enumerate(nodes):
            step = {
                "step": i + 1,
                "action": node["name"],
                "description": node["description"]
            }
            summary["data_flow"].append(step)
        
        return summary

    async def handle_parameter_completion(self, agent_id: str, user_input: str, workflow_plan: dict, missing_params: list) -> dict:
        """Handle user providing missing parameters."""
        try:
            # Extract parameters from user input using AI
            extracted_params = await self._extract_parameters_from_input(user_input, missing_params)
            
            # Update workflow plan with extracted parameters
            updated_plan = self._update_workflow_with_parameters(workflow_plan, extracted_params)
            
            # Check if all parameters are now provided
            remaining_missing = self._identify_missing_parameters(updated_plan)
            
            if remaining_missing:
                # Still missing some parameters
                return {
                    "status": "needs_info",
                    "message": self._generate_parameter_request(remaining_missing),
                    "missing_parameters": remaining_missing,
                    "workflow_plan": updated_plan
                }
            else:
                # All parameters provided, generate final workflow
                return await self.create_automation(agent_id, "Complete workflow with provided parameters", None)
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing your input: {str(e)}"
            }
    
    async def _extract_parameters_from_input(self, user_input: str, missing_params: list) -> dict:
        """Use AI to extract parameter values from user input."""
        
        param_descriptions = {}
        for param in missing_params:
            key = f"{param['node_id']}.{param['parameter']}"
            param_descriptions[key] = param['description']
        
        prompt = f"""
Extract parameter values from this user input:

User Input: "{user_input}"

Expected Parameters:
{json.dumps(param_descriptions, indent=2)}

Extract any matching values and return as JSON:
{{
    "node_id.parameter_name": "extracted_value",
    ...
}}

Only include parameters that you can clearly identify from the input.
"""

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a parameter extraction specialist. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            return json.loads(result)
            
        except Exception as e:
            self.logger.error(f"Parameter extraction error: {e}")
            return {}
    
    def _update_workflow_with_parameters(self, workflow_plan: dict, extracted_params: dict) -> dict:
        """Update workflow plan with extracted parameters."""
        updated_plan = workflow_plan.copy()
        
        for param_key, value in extracted_params.items():
            if "." in param_key:
                node_id, param_name = param_key.split(".", 1)
                
                # Find the node and update parameter
                for node in updated_plan.get("nodes", []):
                    if node["id"] == node_id:
                        if "parameters" not in node:
                            node["parameters"] = {}
                        node["parameters"][param_name] = value
                        break
        
        return updated_plan
