"""
Automation Script Builder for Custom MCP LLM
Creates 100% working JSON automation scripts by understanding driver requirements
and collecting necessary parameters interactively.
"""

import json
import logging
from typing import Dict, List, Any, Optional

class AutomationScriptBuilder:
    """
    Simple automation builder that creates working JSON scripts for the automation engine.
    Focuses on three main use cases:
    1. Simple email sending
    2. AI-generated apology emails for missed events  
    3. Fetch data from website + AI summary + email
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Define driver templates with required parameters
        self.driver_templates = {
            "email_send": {
                "required": ["toEmail", "subject", "text"],
                "optional": {"template_style": "professional", "sender_name": "DXTR Labs"},
                "description": "Sends professional emails"
            },
            "http_request": {
                "required": ["url", "method"],
                "optional": {"headers": []},
                "description": "Fetches data from websites/APIs"
            },
            "openai": {
                "required": ["prompt"],
                "optional": {"model": "gpt-3.5-turbo", "context": "You are a helpful assistant", "temperature": 0.7},
                "description": "Generates AI content using OpenAI"
            }
        }
        
        # Pre-built automation templates
        self.automation_templates = {
            "simple_email": {
                "name": "Simple Email",
                "description": "Send a single email",
                "missing_params": ["toEmail", "subject", "text"],
                "template": {
                    "id": "{{workflow_id}}",
                    "name": "Simple Email Automation",
                    "nodes": [
                        {
                            "id": "email_1",
                            "type": "email_send",
                            "name": "Send Email",
                            "parameters": {
                                "toEmail": "{{toEmail}}",
                                "subject": "{{subject}}",
                                "text": "{{text}}",
                                "template_style": "professional"
                            },
                            "position": {"x": 100, "y": 100}
                        }
                    ]
                }
            },
            
            "apology_email": {
                "name": "AI Apology Email",
                "description": "Generate AI apology for missed events and send email",
                "missing_params": ["customer_email", "customer_name", "event_name", "event_details"],
                "template": {
                    "id": "{{workflow_id}}",
                    "name": "AI Apology Email Automation",
                    "nodes": [
                        {
                            "id": "ai_generate_1",
                            "type": "openai",
                            "name": "Generate Apology",
                            "parameters": {
                                "prompt": "Write a sincere, professional apology email for missing an event. Customer: {{customer_name}}, Event: {{event_name}}, Details: {{event_details}}. Make it personalized and apologetic.",
                                "context": "You are writing professional apology emails for a company. Be sincere, take responsibility, and offer to make it right.",
                                "temperature": 0.7
                            },
                            "position": {"x": 100, "y": 100}
                        },
                        {
                            "id": "email_1",
                            "type": "email_send", 
                            "name": "Send Apology Email",
                            "parameters": {
                                "toEmail": "{{customer_email}}",
                                "subject": "Sincere Apologies - {{event_name}}",
                                "text": "{{ai_generate_1.output}}",
                                "template_style": "professional"
                            },
                            "position": {"x": 100, "y": 200}
                        }
                    ]
                }
            },
            
            "fetch_summarize_email": {
                "name": "Fetch, Summarize & Email",
                "description": "Fetch data from website, create AI summary, and email it",
                "missing_params": ["website_url", "recipient_email", "summary_topic"],
                "template": {
                    "id": "{{workflow_id}}",
                    "name": "Website Data Summary Email",
                    "nodes": [
                        {
                            "id": "fetch_1",
                            "type": "http_request",
                            "name": "Fetch Website Data",
                            "parameters": {
                                "url": "{{website_url}}",
                                "method": "GET"
                            },
                            "position": {"x": 100, "y": 100}
                        },
                        {
                            "id": "ai_summarize_1",
                            "type": "openai",
                            "name": "Create Summary",
                            "parameters": {
                                "prompt": "Analyze and summarize this data focusing on {{summary_topic}}. Data: {{fetch_1.output}}. Create a clear, concise summary.",
                                "context": "You are a data analyst creating professional summaries of web content",
                                "temperature": 0.3
                            },
                            "position": {"x": 100, "y": 200}
                        },
                        {
                            "id": "email_1",
                            "type": "email_send",
                            "name": "Email Summary",
                            "parameters": {
                                "toEmail": "{{recipient_email}}",
                                "subject": "Website Data Summary - {{summary_topic}}",
                                "text": "Here's your requested summary:\\n\\n{{ai_summarize_1.output}}",
                                "template_style": "professional"
                            },
                            "position": {"x": 100, "y": 300}
                        }
                    ]
                }
            }
        }
    
    def analyze_request(self, user_input: str) -> Dict[str, Any]:
        """Analyze user request and determine which automation template to use."""
        user_lower = user_input.lower()
        
        # Simple email keywords
        if any(word in user_lower for word in ["send email", "email to", "notify", "simple email"]):
            if "apolog" in user_lower or "sorry" in user_lower or "missed" in user_lower:
                return {
                    "template": "apology_email",
                    "confidence": 0.9,
                    "reasoning": "User wants to send an apology email"
                }
            else:
                return {
                    "template": "simple_email", 
                    "confidence": 0.8,
                    "reasoning": "User wants to send a simple email"
                }
        
        # Fetch and summarize keywords
        elif any(word in user_lower for word in ["fetch", "get data", "summarize", "website", "scrape"]):
            return {
                "template": "fetch_summarize_email",
                "confidence": 0.9,
                "reasoning": "User wants to fetch data and create summary"
            }
        
        # Default to simple email
        return {
            "template": "simple_email",
            "confidence": 0.5,
            "reasoning": "Default to simple email automation"
        }
    
    def get_missing_parameters(self, template_name: str) -> List[str]:
        """Get list of missing parameters for a template."""
        template = self.automation_templates.get(template_name, {})
        return template.get("missing_params", [])
    
    def generate_parameter_request(self, template_name: str, agent_details: Dict = None) -> str:
        """Generate friendly request for missing parameters."""
        template = self.automation_templates.get(template_name, {})
        missing_params = template.get("missing_params", [])
        
        agent_name = agent_details.get("name", "Assistant") if agent_details else "Assistant"
        
        # Create user-friendly parameter names and descriptions
        param_descriptions = {
            "toEmail": "📧 Recipient email address",
            "subject": "📝 Email subject line", 
            "text": "✍️ Email content/message",
            "customer_email": "📧 Customer's email address",
            "customer_name": "👤 Customer's name",
            "event_name": "📅 Name of the missed event",
            "event_details": "📋 Details about the event (date, time, what happened)",
            "website_url": "🌐 Website URL to fetch data from",
            "recipient_email": "📧 Email address to send summary to",
            "summary_topic": "🎯 What topic to focus on in the summary"
        }
        
        message_parts = [
            f"Hi! I'm {agent_name} and I'll help you create this automation! 🤖\\n",
            f"**{template.get('name', 'Automation')}**: {template.get('description', '')}\\n",
            "To make this work perfectly, I need the following information:\\n"
        ]
        
        for param in missing_params:
            description = param_descriptions.get(param, f"• {param}")
            message_parts.append(f"{description}")
        
        message_parts.append("\\nJust provide these details and I'll create a fully working automation for you! ✨")
        
        return "\\n".join(message_parts)
    
    def extract_parameters_from_input(self, user_input: str, missing_params: List[str]) -> Dict[str, str]:
        """Extract parameter values from user input using simple pattern matching."""
        extracted = {}
        user_lower = user_input.lower()
        
        # Email extraction patterns
        import re
        email_pattern = r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b'
        emails = re.findall(email_pattern, user_input)
        
        # Extract based on context and keywords
        for param in missing_params:
            if param in ["toEmail", "customer_email", "recipient_email"] and emails:
                extracted[param] = emails[0]  # Use first email found
            
            elif param == "subject":
                # Look for subject patterns
                subject_patterns = [r'subject[:\\s]+"([^"]+)"', r'subject[:\\s]+(.+?)(?:\\.|$)']
                for pattern in subject_patterns:
                    match = re.search(pattern, user_lower)
                    if match:
                        extracted[param] = match.group(1).strip()
                        break
            
            elif param in ["customer_name"]:
                # Look for name patterns
                name_patterns = [r'name[:\\s]+"([^"]+)"', r'customer[:\\s]+([A-Za-z\\s]+)']
                for pattern in name_patterns:
                    match = re.search(pattern, user_input)
                    if match:
                        extracted[param] = match.group(1).strip()
                        break
            
            elif param == "website_url":
                # Look for URL patterns
                url_pattern = r'https?://[^\\s]+'
                urls = re.findall(url_pattern, user_input)
                if urls:
                    extracted[param] = urls[0]
        
        return extracted
    
    def fill_template(self, template_name: str, parameters: Dict[str, str]) -> Dict[str, Any]:
        """Fill automation template with provided parameters."""
        template = self.automation_templates.get(template_name, {})
        if not template:
            raise ValueError(f"Unknown template: {template_name}")
        
        # Create workflow with unique ID
        import uuid
        workflow_id = str(uuid.uuid4())
        
        # Convert template to string, replace placeholders, then back to dict
        template_json = json.dumps(template["template"])
        
        # Replace workflow ID
        template_json = template_json.replace("{{workflow_id}}", workflow_id)
        
        # Replace parameter placeholders
        for param, value in parameters.items():
            placeholder = f"{{{{{param}}}}}"
            template_json = template_json.replace(placeholder, str(value))
        
        # Convert back to dict
        workflow = json.loads(template_json)
        
        return {
            "workflow": workflow,
            "workflow_id": workflow_id,
            "template_name": template_name,
            "status": "ready"
        }
    
    def validate_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that workflow has all required parameters filled."""
        validation_errors = []
        
        for node in workflow.get("nodes", []):
            node_type = node.get("type")
            parameters = node.get("parameters", {})
            
            if node_type in self.driver_templates:
                required_params = self.driver_templates[node_type]["required"]
                
                for param in required_params:
                    if param not in parameters or not parameters[param] or "{{" in str(parameters[param]):
                        validation_errors.append(f"Node {node.get('id', 'unknown')}: Missing {param}")
        
        return {
            "valid": len(validation_errors) == 0,
            "errors": validation_errors
        }
    
    def create_automation(self, user_input: str, agent_details: Dict = None) -> Dict[str, Any]:
        """Main method to create automation from user input."""
        try:
            # Step 1: Analyze request to determine template
            analysis = self.analyze_request(user_input)
            template_name = analysis["template"]
            
            # Step 2: Check what parameters are missing
            missing_params = self.get_missing_parameters(template_name)
            
            # Step 3: Try to extract parameters from user input
            extracted_params = self.extract_parameters_from_input(user_input, missing_params)
            
            # Step 4: Check if we still need more parameters
            still_missing = [p for p in missing_params if p not in extracted_params]
            
            if still_missing:
                return {
                    "status": "needs_info",
                    "message": self.generate_parameter_request(template_name, agent_details),
                    "template_name": template_name,
                    "missing_parameters": still_missing,
                    "extracted_parameters": extracted_params
                }
            
            # Step 5: Create the workflow
            result = self.fill_template(template_name, extracted_params)
            
            # Step 6: Validate the workflow
            validation = self.validate_workflow(result["workflow"])
            if not validation["valid"]:
                return {
                    "status": "error",
                    "message": f"Workflow validation failed: {', '.join(validation['errors'])}",
                    "errors": validation["errors"]
                }
            
            return {
                "status": "ready",
                "message": f"✅ {self.automation_templates[template_name]['name']} created successfully! Your automation is ready to run.",
                "workflow": result["workflow"],
                "workflow_id": result["workflow_id"],
                "template_name": template_name
            }
            
        except Exception as e:
            self.logger.error(f"Error creating automation: {e}")
            return {
                "status": "error",
                "message": f"Error creating automation: {str(e)}",
                "error": str(e)
            }
    
    def complete_parameters(self, template_name: str, previous_params: Dict, user_input: str) -> Dict[str, Any]:
        """Complete missing parameters from additional user input."""
        try:
            missing_params = self.get_missing_parameters(template_name)
            
            # Extract new parameters from input
            new_params = self.extract_parameters_from_input(user_input, missing_params)
            
            # Merge with previous parameters
            all_params = {**previous_params, **new_params}
            
            # Check if we still need more
            still_missing = [p for p in missing_params if p not in all_params]
            
            if still_missing:
                return {
                    "status": "needs_info",
                    "message": f"I still need: {', '.join(still_missing)}. Please provide these details.",
                    "missing_parameters": still_missing,
                    "extracted_parameters": all_params
                }
            
            # Create the workflow
            result = self.fill_template(template_name, all_params)
            
            return {
                "status": "ready",
                "message": f"✅ Perfect! Your automation is now ready to run.",
                "workflow": result["workflow"],
                "workflow_id": result["workflow_id"]
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Error completing parameters: {str(e)}"
            }
