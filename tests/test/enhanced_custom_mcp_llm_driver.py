#!/usr/bin/env python3
"""
Enhanced DXTR AutoFlow - Custom MCP LLM Chat OpenAI Driver
Advanced AI system with workflow discovery and JSON script generation
"""

import asyncio
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import openai
from pathlib import Path

class WorkflowTemplateManager:
    """Manages pre-built workflow templates and pattern matching"""
    
    def __init__(self):
        self.templates_db = self._load_workflow_templates()
        self.usage_patterns = self._load_usage_patterns()
    
    def _load_workflow_templates(self) -> Dict[str, Any]:
        """Load pre-built workflow templates"""
        return {
            "task_creation_notification": {
                "template_id": "task_creation_v1",
                "name": "Task Creation with Notifications",
                "description": "Creates tasks in project management tools and sends notifications",
                "pattern_keywords": ["create task", "new task", "task creation", "assign task"],
                "drivers_used": ["asana_driver", "slack_driver", "email_driver"],
                "usage_count": 156,
                "success_rate": 0.98,
                "template": {
                    "steps": [
                        {
                            "driver": "asana_driver",
                            "operation": "create_task",
                            "parameters": ["name", "description", "project", "assignee", "priority"]
                        },
                        {
                            "driver": "slack_driver", 
                            "operation": "send_message",
                            "parameters": ["channel", "message"]
                        },
                        {
                            "driver": "email_driver",
                            "operation": "send_email", 
                            "parameters": ["to", "subject", "body"]
                        }
                    ]
                }
            },
            "customer_onboarding": {
                "template_id": "customer_onboarding_v2",
                "name": "Enterprise Customer Onboarding",
                "description": "Complete customer setup across all platforms",
                "pattern_keywords": ["new customer", "onboarding", "customer setup", "enterprise setup"],
                "drivers_used": ["asana_driver", "slack_driver", "stripe_driver", "email_driver", "analytics_driver"],
                "usage_count": 89,
                "success_rate": 0.95,
                "template": {
                    "steps": [
                        {
                            "driver": "asana_driver",
                            "operation": "create_workspace",
                            "parameters": ["name", "members", "projects"]
                        },
                        {
                            "driver": "slack_driver",
                            "operation": "create_channels", 
                            "parameters": ["workspace", "channels", "members"]
                        },
                        {
                            "driver": "stripe_driver",
                            "operation": "setup_subscription",
                            "parameters": ["customer", "plan", "billing"]
                        },
                        {
                            "driver": "email_driver",
                            "operation": "send_welcome_sequence",
                            "parameters": ["customer_email", "template", "variables"]
                        },
                        {
                            "driver": "analytics_driver",
                            "operation": "setup_tracking",
                            "parameters": ["customer_id", "metrics", "dashboard"]
                        }
                    ]
                }
            },
            "social_media_campaign": {
                "template_id": "social_campaign_v1", 
                "name": "Social Media Content Campaign",
                "description": "Multi-platform social media content distribution",
                "pattern_keywords": ["social media", "post", "tweet", "campaign", "content distribution"],
                "drivers_used": ["twitter_driver", "analytics_driver", "slack_driver"],
                "usage_count": 234,
                "success_rate": 0.92,
                "template": {
                    "steps": [
                        {
                            "driver": "twitter_driver",
                            "operation": "create_tweet",
                            "parameters": ["content", "hashtags", "media"]
                        },
                        {
                            "driver": "analytics_driver",
                            "operation": "track_engagement",
                            "parameters": ["platform", "post_id", "metrics"]
                        },
                        {
                            "driver": "slack_driver",
                            "operation": "notify_team",
                            "parameters": ["channel", "campaign_status"]
                        }
                    ]
                }
            },
            "payment_processing": {
                "template_id": "payment_processing_v1",
                "name": "Payment Processing and Confirmation",
                "description": "Process payments and send confirmations",
                "pattern_keywords": ["payment", "charge", "invoice", "billing", "subscription"],
                "drivers_used": ["stripe_driver", "email_driver", "slack_driver"],
                "usage_count": 445,
                "success_rate": 0.99,
                "template": {
                    "steps": [
                        {
                            "driver": "stripe_driver",
                            "operation": "process_payment",
                            "parameters": ["amount", "customer", "method"]
                        },
                        {
                            "driver": "email_driver",
                            "operation": "send_receipt",
                            "parameters": ["customer_email", "transaction_details"]
                        },
                        {
                            "driver": "slack_driver",
                            "operation": "notify_sales",
                            "parameters": ["channel", "payment_details"]
                        }
                    ]
                }
            },
            "incident_response": {
                "template_id": "incident_response_v1",
                "name": "Incident Response and Communication",
                "description": "Automated incident detection and team notification",
                "pattern_keywords": ["incident", "alert", "emergency", "critical", "outage"],
                "drivers_used": ["slack_driver", "email_driver", "asana_driver", "analytics_driver"],
                "usage_count": 67,
                "success_rate": 0.97,
                "template": {
                    "steps": [
                        {
                            "driver": "slack_driver",
                            "operation": "send_alert",
                            "parameters": ["urgent_channel", "incident_details", "severity"]
                        },
                        {
                            "driver": "asana_driver",
                            "operation": "create_incident_task",
                            "parameters": ["project", "incident_description", "assignee"]
                        },
                        {
                            "driver": "email_driver",
                            "operation": "notify_stakeholders",
                            "parameters": ["stakeholder_list", "incident_summary"]
                        },
                        {
                            "driver": "analytics_driver",
                            "operation": "track_incident_metrics",
                            "parameters": ["incident_id", "start_time", "severity"]
                        }
                    ]
                }
            }
        }
    
    def _load_usage_patterns(self) -> Dict[str, Any]:
        """Load usage patterns for intelligent matching"""
        return {
            "common_phrases": {
                "task_creation": ["create", "make", "add", "new", "task", "todo", "assignment"],
                "notifications": ["notify", "tell", "inform", "alert", "message", "email", "slack"],
                "project_management": ["project", "workspace", "team", "assign", "due date", "priority"],
                "payments": ["pay", "charge", "bill", "invoice", "subscription", "refund"],
                "social_media": ["post", "tweet", "share", "publish", "social", "hashtag"],
                "analytics": ["track", "measure", "analyze", "report", "metrics", "dashboard"]
            },
            "action_verbs": ["create", "send", "notify", "update", "delete", "process", "generate", "analyze"],
            "integration_indicators": {
                "asana": ["asana", "task", "project", "workspace", "assign"],
                "slack": ["slack", "channel", "team", "message", "notification"],
                "stripe": ["stripe", "payment", "charge", "invoice", "billing"],
                "twitter": ["twitter", "tweet", "post", "social media"],
                "email": ["email", "send", "recipient", "subject", "message"]
            }
        }
    
    def find_matching_template(self, user_input: str) -> Tuple[Optional[Dict], float]:
        """Find the best matching workflow template"""
        user_input_lower = user_input.lower()
        best_match = None
        best_score = 0.0
        
        for template_id, template in self.templates_db.items():
            score = 0.0
            
            # Check keyword matches
            keyword_matches = sum(1 for keyword in template["pattern_keywords"] 
                                if keyword.lower() in user_input_lower)
            keyword_score = keyword_matches / len(template["pattern_keywords"])
            
            # Check driver relevance
            driver_matches = 0
            for driver in template["drivers_used"]:
                driver_name = driver.replace("_driver", "")
                if driver_name in user_input_lower:
                    driver_matches += 1
            driver_score = driver_matches / len(template["drivers_used"]) if template["drivers_used"] else 0
            
            # Check common phrases
            phrase_matches = 0
            total_phrases = 0
            for category, phrases in self.usage_patterns["common_phrases"].items():
                total_phrases += len(phrases)
                phrase_matches += sum(1 for phrase in phrases if phrase in user_input_lower)
            phrase_score = phrase_matches / total_phrases if total_phrases > 0 else 0
            
            # Calculate weighted score
            total_score = (keyword_score * 0.5) + (driver_score * 0.3) + (phrase_score * 0.2)
            
            # Bonus for high usage and success rate
            usage_bonus = min(template["usage_count"] / 1000, 0.1)
            success_bonus = template["success_rate"] * 0.1
            
            final_score = total_score + usage_bonus + success_bonus
            
            if final_score > best_score:
                best_score = final_score
                best_match = template
        
        return (best_match, best_score) if best_score > 0.3 else (None, 0.0)

class WorkflowJSONGenerator:
    """Generates executable JSON workflow scripts"""
    
    def __init__(self):
        self.available_drivers = self._get_available_drivers()
    
    def _get_available_drivers(self) -> Dict[str, Dict]:
        """Get information about available drivers and their operations"""
        return {
            "asana_driver": {
                "operations": {
                    "create_task": ["name", "description", "project", "assignee", "due_date", "priority"],
                    "create_project": ["name", "description", "team", "privacy"],
                    "create_workspace": ["name", "members"],
                    "update_task": ["task_id", "updates"],
                    "get_tasks": ["project_id", "filters"]
                },
                "authentication": "bearer_token",
                "rate_limits": {"requests_per_minute": 1500}
            },
            "slack_driver": {
                "operations": {
                    "send_message": ["channel", "text", "blocks"],
                    "create_channel": ["name", "is_private", "members"],
                    "send_dm": ["user", "text"],
                    "update_message": ["channel", "timestamp", "text"],
                    "upload_file": ["channels", "file", "title"]
                },
                "authentication": "bot_token",
                "rate_limits": {"requests_per_minute": 50}
            },
            "stripe_driver": {
                "operations": {
                    "create_customer": ["email", "name", "description"],
                    "create_payment_intent": ["amount", "currency", "customer"],
                    "create_subscription": ["customer", "price_id", "trial_days"],
                    "create_invoice": ["customer", "auto_advance"],
                    "process_refund": ["payment_intent", "amount", "reason"]
                },
                "authentication": "secret_key",
                "rate_limits": {"requests_per_second": 25}
            },
            "twitter_driver": {
                "operations": {
                    "create_tweet": ["text", "media_ids"],
                    "reply_to_tweet": ["tweet_id", "text"],
                    "like_tweet": ["tweet_id"],
                    "retweet": ["tweet_id"],
                    "follow_user": ["user_id"]
                },
                "authentication": "bearer_token",
                "rate_limits": {"tweets_per_hour": 300}
            },
            "email_driver": {
                "operations": {
                    "send_email": ["to", "subject", "body", "html"],
                    "send_template_email": ["to", "template_id", "variables"],
                    "send_bulk_email": ["recipients", "subject", "template"],
                    "schedule_email": ["to", "subject", "body", "send_at"]
                },
                "authentication": "smtp_credentials",
                "rate_limits": {"emails_per_hour": 1000}
            },
            "analytics_driver": {
                "operations": {
                    "track_event": ["event_name", "properties", "user_id"],
                    "create_dashboard": ["name", "metrics", "filters"],
                    "get_report": ["report_id", "date_range"],
                    "set_goals": ["metric", "target", "timeframe"]
                },
                "authentication": "api_key",
                "rate_limits": {"requests_per_minute": 200}
            }
        }
    
    def generate_workflow_json(self, parsed_actions: List[Dict], template: Optional[Dict] = None) -> Dict:
        """Generate executable JSON workflow script"""
        workflow_id = f"wf_{int(time.time())}_{hashlib.md5(str(parsed_actions).encode()).hexdigest()[:8]}"
        
        workflow = {
            "workflow_id": workflow_id,
            "name": self._generate_workflow_name(parsed_actions),
            "description": self._generate_workflow_description(parsed_actions),
            "created_at": datetime.now().isoformat(),
            "template_id": template["template_id"] if template else None,
            "template_used": bool(template),
            "estimated_execution_time": self._estimate_execution_time(parsed_actions),
            "steps": [],
            "dependencies": {},
            "error_handling": {
                "retry_policy": "exponential_backoff",
                "max_retries": 3,
                "timeout_seconds": 300,
                "on_failure": "rollback_and_notify"
            },
            "monitoring": {
                "track_performance": True,
                "log_detailed_execution": True,
                "send_completion_notification": True,
                "analytics_tracking": True
            }
        }
        
        # Generate steps
        for i, action in enumerate(parsed_actions):
            step = self._create_workflow_step(action, i + 1, parsed_actions)
            workflow["steps"].append(step)
            
            # Add dependencies
            if i > 0:
                workflow["dependencies"][step["step_id"]] = [f"step_{i}"]
        
        # Add validation
        workflow["validation"] = self._validate_workflow(workflow)
        
        return workflow
    
    def _generate_workflow_name(self, actions: List[Dict]) -> str:
        """Generate descriptive workflow name"""
        if len(actions) == 1:
            action = actions[0]
            return f"{action['driver'].replace('_driver', '').title()} {action['operation'].replace('_', ' ').title()}"
        else:
            drivers = list(set(action['driver'].replace('_driver', '') for action in actions))
            return f"Multi-Step Workflow: {', '.join(drivers).title()}"
    
    def _generate_workflow_description(self, actions: List[Dict]) -> str:
        """Generate workflow description"""
        descriptions = []
        for action in actions:
            driver_name = action['driver'].replace('_driver', '').title()
            operation = action['operation'].replace('_', ' ')
            descriptions.append(f"{operation} using {driver_name}")
        
        return "; ".join(descriptions)
    
    def _estimate_execution_time(self, actions: List[Dict]) -> int:
        """Estimate workflow execution time in seconds"""
        base_times = {
            "asana_driver": 3,
            "slack_driver": 2, 
            "stripe_driver": 5,
            "twitter_driver": 3,
            "email_driver": 4,
            "analytics_driver": 6
        }
        
        total_time = sum(base_times.get(action['driver'], 3) for action in actions)
        return total_time + (len(actions) * 2)  # Add coordination overhead
    
    def _create_workflow_step(self, action: Dict, step_number: int, all_actions: List[Dict]) -> Dict:
        """Create individual workflow step"""
        step_id = f"step_{step_number}"
        
        step = {
            "step_id": step_id,
            "name": f"Step {step_number}: {action['operation'].replace('_', ' ').title()}",
            "driver": action['driver'],
            "operation": action['operation'],
            "parameters": action.get('parameters', {}),
            "timeout_seconds": 60,
            "retry_policy": {
                "enabled": True,
                "max_retries": 3,
                "retry_delay_seconds": 5,
                "exponential_backoff": True
            },
            "validation": {
                "required_parameters": self._get_required_parameters(action['driver'], action['operation']),
                "parameter_validation": True,
                "response_validation": True
            },
            "output_mapping": {
                "store_result": True,
                "result_key": f"{step_id}_result",
                "expose_variables": True
            }
        }
        
        # Add conditional logic for dependent steps
        if step_number > 1:
            step["conditional_execution"] = {
                "condition": f"step_{step_number - 1}.success == true",
                "on_condition_false": "skip_step"
            }
        
        # Add variable substitution for dynamic content
        step["variable_substitution"] = self._add_variable_substitution(action, step_number, all_actions)
        
        return step
    
    def _get_required_parameters(self, driver: str, operation: str) -> List[str]:
        """Get required parameters for driver operation"""
        driver_info = self.available_drivers.get(driver, {})
        operations = driver_info.get("operations", {})
        return operations.get(operation, [])
    
    def _add_variable_substitution(self, action: Dict, step_number: int, all_actions: List[Dict]) -> Dict:
        """Add variable substitution for dynamic workflow execution"""
        substitutions = {}
        
        # Add references to previous step results
        if step_number > 1:
            for i in range(1, step_number):
                substitutions[f"step_{i}_result"] = f"{{workflow.steps.step_{i}.result}}"
        
        # Add timestamp variables
        substitutions["current_timestamp"] = "{{system.current_timestamp}}"
        substitutions["workflow_id"] = "{{workflow.id}}"
        substitutions["user_id"] = "{{context.user_id}}"
        
        return substitutions
    
    def _validate_workflow(self, workflow: Dict) -> Dict:
        """Validate workflow structure and dependencies"""
        validation = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "suggestions": []
        }
        
        # Check for circular dependencies
        if self._has_circular_dependencies(workflow["dependencies"]):
            validation["errors"].append("Circular dependency detected")
            validation["is_valid"] = False
        
        # Check driver availability
        for step in workflow["steps"]:
            if step["driver"] not in self.available_drivers:
                validation["errors"].append(f"Driver {step['driver']} not available")
                validation["is_valid"] = False
        
        # Check parameter completeness
        for step in workflow["steps"]:
            required_params = self._get_required_parameters(step["driver"], step["operation"])
            missing_params = [p for p in required_params if p not in step["parameters"]]
            if missing_params:
                validation["warnings"].append(f"Step {step['step_id']} missing parameters: {missing_params}")
        
        # Performance suggestions
        if len(workflow["steps"]) > 10:
            validation["suggestions"].append("Consider breaking into smaller workflows for better performance")
        
        return validation
    
    def _has_circular_dependencies(self, dependencies: Dict) -> bool:
        """Check for circular dependencies in workflow"""
        def visit(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependencies.get(node, []):
                if neighbor not in visited:
                    if visit(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        rec_stack = set()
        
        for node in dependencies:
            if node not in visited:
                if visit(node, visited, rec_stack):
                    return True
        return False

class EnhancedMCPLLMDriver:
    """Enhanced MCP LLM Driver with workflow intelligence"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI()
        self.template_manager = WorkflowTemplateManager()
        self.workflow_generator = WorkflowJSONGenerator()
        self.execution_history = []
        
        # Enhanced system prompt for workflow intelligence
        self.system_prompt = """You are DXTR AutoFlow's advanced AI workflow orchestrator. Your mission is to:

1. WORKFLOW DISCOVERY: First check if user requests match existing workflow templates
2. INTELLIGENT PARSING: Extract actionable components from natural language
3. JSON GENERATION: Create executable workflow scripts with proper driver integration
4. OPTIMIZATION: Suggest improvements and handle error scenarios

Available Drivers and Operations:
- asana_driver: create_task, create_project, update_task, get_tasks
- slack_driver: send_message, create_channel, send_dm, upload_file  
- stripe_driver: create_customer, create_payment_intent, process_refund
- twitter_driver: create_tweet, reply_to_tweet, like_tweet, follow_user
- email_driver: send_email, send_template_email, schedule_email
- analytics_driver: track_event, create_dashboard, get_report

Always prioritize existing templates when possible, but create custom workflows when needed.
Focus on practical, executable solutions with proper error handling."""
    
    async def process_user_request(self, user_input: str, context: Dict = None) -> Dict:
        """Main entry point for processing user requests"""
        try:
            # Step 1: Check for existing workflow templates
            template_match, confidence = self.template_manager.find_matching_template(user_input)
            
            # Step 2: Use LLM to parse and understand the request
            parsed_request = await self._parse_user_request(user_input, template_match, context)
            
            # Step 3: Generate executable workflow JSON
            workflow_json = self.workflow_generator.generate_workflow_json(
                parsed_request["actions"], 
                template_match
            )
            
            # Step 4: Add intelligence and optimizations
            enhanced_workflow = await self._enhance_workflow(workflow_json, user_input, context)
            
            return {
                "success": True,
                "template_used": template_match is not None,
                "template_confidence": confidence,
                "template_id": template_match["template_id"] if template_match else None,
                "workflow": enhanced_workflow,
                "execution_ready": enhanced_workflow["validation"]["is_valid"],
                "estimated_time": enhanced_workflow["estimated_execution_time"],
                "user_explanation": await self._generate_user_explanation(enhanced_workflow, user_input)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_suggestion": "Please try rephrasing your request or break it into smaller steps"
            }
    
    async def _parse_user_request(self, user_input: str, template: Optional[Dict], context: Dict) -> Dict:
        """Use LLM to parse user request into actionable components"""
        
        template_context = ""
        if template:
            template_context = f"""
MATCHING TEMPLATE FOUND: {template['name']}
Template Steps: {json.dumps(template['template']['steps'], indent=2)}
Confidence: {self.template_manager.find_matching_template(user_input)[1]:.2f}

Consider adapting this template for the user's specific request.
"""
        
        parsing_prompt = f"""
{self.system_prompt}

{template_context}

USER REQUEST: "{user_input}"

CONTEXT: {json.dumps(context or {}, indent=2)}

Parse this request into actionable workflow steps. Return a JSON response with:
{{
  "intent": "brief description of what user wants",
  "complexity": "simple|moderate|complex",
  "actions": [
    {{
      "driver": "driver_name",
      "operation": "operation_name", 
      "parameters": {{
        "param1": "value1",
        "param2": "value2"
      }},
      "description": "what this step does"
    }}
  ],
  "dependencies": ["which steps depend on others"],
  "estimated_steps": "number",
  "user_intent_confidence": "0.0-1.0"
}}

Focus on practical, executable actions using available drivers.
"""
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": parsing_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _enhance_workflow(self, workflow: Dict, original_request: str, context: Dict) -> Dict:
        """Enhance workflow with AI intelligence and optimizations"""
        
        enhancement_prompt = f"""
Analyze and enhance this workflow for optimal execution:

ORIGINAL REQUEST: "{original_request}"
WORKFLOW: {json.dumps(workflow, indent=2)}

Suggest enhancements for:
1. Error handling and recovery
2. Performance optimizations  
3. User experience improvements
4. Security considerations
5. Monitoring and alerting

Return enhanced workflow JSON with improvements.
"""
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4", 
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": enhancement_prompt}
            ],
            temperature=0.2
        )
        
        try:
            enhancements = json.loads(response.choices[0].message.content)
            # Merge enhancements with original workflow
            return self._merge_workflow_enhancements(workflow, enhancements)
        except:
            # Return original if enhancement parsing fails
            return workflow
    
    def _merge_workflow_enhancements(self, original: Dict, enhancements: Dict) -> Dict:
        """Merge AI-suggested enhancements with original workflow"""
        enhanced = original.copy()
        
        # Add enhanced error handling
        if "error_handling" in enhancements:
            enhanced["error_handling"].update(enhancements["error_handling"])
        
        # Add performance optimizations
        if "performance_optimizations" in enhancements:
            enhanced["performance_optimizations"] = enhancements["performance_optimizations"]
        
        # Add security enhancements
        if "security" in enhancements:
            enhanced["security"] = enhancements["security"]
        
        return enhanced
    
    async def _generate_user_explanation(self, workflow: Dict, original_request: str) -> str:
        """Generate user-friendly explanation of what will happen"""
        
        explanation_prompt = f"""
Create a clear, user-friendly explanation of this workflow:

USER REQUEST: "{original_request}"
WORKFLOW: {workflow['name']}
STEPS: {len(workflow['steps'])} steps
ESTIMATED TIME: {workflow['estimated_execution_time']} seconds

Explain in simple terms:
1. What will happen
2. Which systems will be used
3. What the user can expect
4. Estimated completion time

Keep it concise and reassuring.
"""
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant explaining technical workflows in simple terms."},
                {"role": "user", "content": explanation_prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        return response.choices[0].message.content

# Usage Example
async def demo_enhanced_mcp_llm():
    """Demonstrate the enhanced MCP LLM capabilities"""
    
    driver = EnhancedMCPLLMDriver()
    
    test_requests = [
        "Create a high priority task in Asana for fixing the login bug and notify the dev team in Slack",
        "New enterprise customer TechCorp just signed up - set up their complete onboarding",
        "Post about our new AI features on Twitter and track engagement metrics",
        "Customer John Smith wants a refund for his $99 subscription", 
        "Critical database outage detected - initiate emergency response protocol"
    ]
    
    for request in test_requests:
        print(f"\n🎯 Processing: {request}")
        print("=" * 80)
        
        result = await driver.process_user_request(request)
        
        if result["success"]:
            print(f"✅ Template Used: {result['template_used']}")
            if result["template_used"]:
                print(f"📋 Template: {result['template_id']} (confidence: {result['template_confidence']:.2f})")
            
            print(f"⚙️ Workflow: {result['workflow']['name']}")
            print(f"📊 Steps: {len(result['workflow']['steps'])}")
            print(f"⏱️ Estimated Time: {result['estimated_time']}s")
            print(f"🎯 Ready to Execute: {result['execution_ready']}")
            print(f"\n💡 Explanation: {result['user_explanation']}")
        else:
            print(f"❌ Error: {result['error']}")

if __name__ == "__main__":
    asyncio.run(demo_enhanced_mcp_llm())
