#!/usr/bin/env python3
"""
DXTR AutoFlow - Enhanced Agent Workflow System
Includes agent personality, expectations, and connectivity management
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class AgentPersonality:
    """Agent personality configuration"""
    name: str
    role: str
    communication_style: str  # formal, casual, technical, friendly
    decision_making: str      # conservative, balanced, aggressive
    workflow_preferences: List[str]
    risk_tolerance: str       # low, medium, high
    automation_level: str     # minimal, moderate, extensive

@dataclass
class AgentExpectation:
    """Agent expectations for workflows"""
    priority_drivers: List[str]
    preferred_integrations: List[str]
    notification_preferences: Dict[str, Any]
    approval_required: List[str]
    execution_speed: str      # fast, normal, thorough
    error_handling: str       # strict, balanced, permissive

class ConnectivityManager:
    """Manages API credentials and connection status"""
    
    def __init__(self):
        self.connections = {
            "asana": {
                "name": "Asana Project Management",
                "icon": "📋",
                "required_fields": ["api_token", "workspace_id"],
                "optional_fields": ["default_project"],
                "status": "disconnected",
                "test_endpoint": "https://app.asana.com/api/1.0/users/me"
            },
            "slack": {
                "name": "Slack Team Communication", 
                "icon": "💬",
                "required_fields": ["bot_token", "webhook_url"],
                "optional_fields": ["default_channel", "user_token"],
                "status": "disconnected",
                "test_endpoint": "https://slack.com/api/auth.test"
            },
            "stripe": {
                "name": "Stripe Payment Processing",
                "icon": "💳", 
                "required_fields": ["secret_key", "publishable_key"],
                "optional_fields": ["webhook_secret"],
                "status": "disconnected",
                "test_endpoint": "https://api.stripe.com/v1/account"
            },
            "twitter": {
                "name": "Twitter/X Social Media",
                "icon": "🐦",
                "required_fields": ["api_key", "api_secret", "access_token", "access_token_secret"],
                "optional_fields": ["bearer_token"],
                "status": "disconnected", 
                "test_endpoint": "https://api.twitter.com/2/users/me"
            },
            "google_sheets": {
                "name": "Google Sheets",
                "icon": "📊",
                "required_fields": ["service_account_json"],
                "optional_fields": ["default_spreadsheet_id"],
                "status": "disconnected",
                "test_endpoint": "https://sheets.googleapis.com/v4/spreadsheets"
            },
            "email": {
                "name": "Email Service",
                "icon": "📧",
                "required_fields": ["smtp_host", "smtp_port", "username", "password"],
                "optional_fields": ["from_name", "default_template"],
                "status": "disconnected",
                "test_endpoint": "smtp_connection_test"
            },
            "telegram": {
                "name": "Telegram Bot",
                "icon": "🤖",
                "required_fields": ["bot_token"],
                "optional_fields": ["webhook_url"],
                "status": "disconnected",
                "test_endpoint": "https://api.telegram.org/bot{token}/getMe"
            },
            "analytics": {
                "name": "Google Analytics",
                "icon": "📈",
                "required_fields": ["property_id", "service_account_json"],
                "optional_fields": ["default_date_range"],
                "status": "disconnected",
                "test_endpoint": "https://analyticsdata.googleapis.com/v1beta"
            },
            "trello": {
                "name": "Trello Project Management",
                "icon": "📌",
                "required_fields": ["api_key", "token"],
                "optional_fields": ["default_board_id"],
                "status": "disconnected",
                "test_endpoint": "https://api.trello.com/1/members/me"
            },
            "openai": {
                "name": "OpenAI API",
                "icon": "🤖",
                "required_fields": ["api_key"],
                "optional_fields": ["organization_id", "default_model"],
                "status": "disconnected",
                "test_endpoint": "https://api.openai.com/v1/models"
            }
        }
    
    def get_connectivity_dashboard_data(self):
        """Generate data for connectivity dashboard"""
        return {
            "total_connections": len(self.connections),
            "connected": sum(1 for conn in self.connections.values() if conn["status"] == "connected"),
            "disconnected": sum(1 for conn in self.connections.values() if conn["status"] == "disconnected"),
            "connections": self.connections
        }
    
    def get_required_connections_for_workflow(self, workflow: Dict) -> List[str]:
        """Get required connections for a workflow"""
        required = []
        for step in workflow.get("steps", []):
            driver = step.get("driver", "").replace("_driver", "")
            if driver in self.connections:
                required.append(driver)
        return list(set(required))

class EnhancedAgentWorkflowSystem:
    """Enhanced workflow system with agent personality and expectations"""
    
    def __init__(self):
        self.connectivity_manager = ConnectivityManager()
        self.agent_profiles = {
            "technical_lead": AgentPersonality(
                name="Technical Lead Agent",
                role="technical_decision_maker",
                communication_style="technical",
                decision_making="conservative",
                workflow_preferences=["asana", "slack", "github", "monitoring"],
                risk_tolerance="low",
                automation_level="extensive"
            ),
            "marketing_manager": AgentPersonality(
                name="Marketing Manager Agent",
                role="marketing_automation",
                communication_style="friendly",
                decision_making="balanced",
                workflow_preferences=["twitter", "analytics", "email", "stripe"],
                risk_tolerance="medium",
                automation_level="moderate"
            ),
            "customer_success": AgentPersonality(
                name="Customer Success Agent",
                role="customer_support",
                communication_style="formal",
                decision_making="balanced",
                workflow_preferences=["slack", "email", "asana", "stripe"],
                risk_tolerance="low",
                automation_level="moderate"
            ),
            "sales_executive": AgentPersonality(
                name="Sales Executive Agent",
                role="sales_automation",
                communication_style="casual",
                decision_making="aggressive",
                workflow_preferences=["stripe", "email", "slack", "analytics"],
                risk_tolerance="high",
                automation_level="extensive"
            )
        }
        
        self.workflow_templates = {
            "task_creation_notification": {
                "template_id": "task_creation_v1",
                "name": "Task Creation with Notifications",
                "description": "Create tasks and notify relevant team members",
                "agent_suitability": {
                    "technical_lead": 0.9,
                    "marketing_manager": 0.3,
                    "customer_success": 0.7,
                    "sales_executive": 0.4
                },
                "required_connections": ["asana", "slack"],
                "optional_connections": ["email"],
                "pattern_keywords": ["create task", "new task", "task creation", "assign task", "asana", "notify"],
                "drivers_used": ["asana_driver", "slack_driver", "email_driver"],
                "usage_count": 156,
                "success_rate": 0.98,
                "execution_time": 12
            },
            "customer_onboarding": {
                "template_id": "customer_onboarding_v2",
                "name": "Enterprise Customer Onboarding",
                "description": "Complete customer setup with billing and communication",
                "agent_suitability": {
                    "technical_lead": 0.4,
                    "marketing_manager": 0.6,
                    "customer_success": 0.95,
                    "sales_executive": 0.8
                },
                "required_connections": ["stripe", "slack"],
                "optional_connections": ["asana", "email", "analytics"],
                "pattern_keywords": ["new customer", "onboarding", "customer setup", "enterprise", "signup"],
                "drivers_used": ["asana_driver", "slack_driver", "stripe_driver", "email_driver", "analytics_driver"],
                "usage_count": 89,
                "success_rate": 0.95,
                "execution_time": 45
            },
            "payment_processing": {
                "template_id": "payment_processing_v1",
                "name": "Payment Processing and Confirmation",
                "description": "Process payments and send confirmations",
                "agent_suitability": {
                    "technical_lead": 0.3,
                    "marketing_manager": 0.5,
                    "customer_success": 0.8,
                    "sales_executive": 0.95
                },
                "required_connections": ["stripe"],
                "optional_connections": ["email", "slack"],
                "pattern_keywords": ["payment", "charge", "invoice", "billing", "subscription", "refund"],
                "drivers_used": ["stripe_driver", "email_driver", "slack_driver"],
                "usage_count": 445,
                "success_rate": 0.99,
                "execution_time": 8
            },
            "social_campaign": {
                "template_id": "social_campaign_v1",
                "name": "Social Media Campaign Management",
                "description": "Publish and track social media campaigns",
                "agent_suitability": {
                    "technical_lead": 0.2,
                    "marketing_manager": 0.95,
                    "customer_success": 0.3,
                    "sales_executive": 0.7
                },
                "required_connections": ["twitter"],
                "optional_connections": ["analytics", "slack"],
                "pattern_keywords": ["tweet", "social", "campaign", "post", "twitter", "engagement"],
                "drivers_used": ["twitter_driver", "analytics_driver", "slack_driver"],
                "usage_count": 234,
                "success_rate": 0.94,
                "execution_time": 15
            },
            "incident_response": {
                "template_id": "incident_response_v1",
                "name": "Incident Response and Recovery",
                "description": "Handle system incidents with notifications and tracking",
                "agent_suitability": {
                    "technical_lead": 0.98,
                    "marketing_manager": 0.2,
                    "customer_success": 0.6,
                    "sales_executive": 0.1
                },
                "required_connections": ["slack", "email"],
                "optional_connections": ["asana", "analytics"],
                "pattern_keywords": ["incident", "emergency", "alert", "critical", "outage", "urgent"],
                "drivers_used": ["slack_driver", "email_driver", "asana_driver", "analytics_driver"],
                "usage_count": 67,
                "success_rate": 0.97,
                "execution_time": 20
            }
        }
    
    def find_best_workflow_for_agent(self, user_input: str, agent_type: str) -> Tuple[Optional[Dict], float, List[str]]:
        """Find best workflow considering agent personality and expectations"""
        
        agent = self.agent_profiles.get(agent_type)
        if not agent:
            return self._find_generic_workflow(user_input)
        
        user_input_lower = user_input.lower()
        best_match = None
        best_score = 0.0
        missing_connections = []
        
        for template_id, template in self.workflow_templates.items():
            # Base keyword matching score
            keyword_matches = sum(1 for keyword in template["pattern_keywords"] 
                                if keyword.lower() in user_input_lower)
            if keyword_matches == 0:
                continue
            
            keyword_score = keyword_matches / len(template["pattern_keywords"])
            
            # Agent suitability score
            agent_suitability = template["agent_suitability"].get(agent_type, 0.1)
            
            # Workflow preference bonus
            preference_bonus = 0.0
            for driver in template["drivers_used"]:
                driver_service = driver.replace("_driver", "")
                if driver_service in agent.workflow_preferences:
                    preference_bonus += 0.1
            
            # Success rate and usage bonus
            performance_bonus = template["success_rate"] * 0.1 + min(template["usage_count"] / 1000, 0.1)
            
            # Calculate total score
            total_score = (keyword_score * 0.4 + 
                          agent_suitability * 0.3 + 
                          preference_bonus + 
                          performance_bonus)
            
            # Check connection requirements
            required_connections = template["required_connections"]
            missing = self._check_missing_connections(required_connections)
            
            # Penalty for missing connections
            if missing:
                total_score *= 0.7  # Reduce score by 30% if connections missing
            
            if total_score > best_score:
                best_score = total_score
                best_match = template
                missing_connections = missing
        
        return (best_match, best_score, missing_connections) if best_score > 0.2 else (None, 0.0, [])
    
    def _find_generic_workflow(self, user_input: str) -> Tuple[Optional[Dict], float, List[str]]:
        """Fallback generic workflow matching"""
        user_input_lower = user_input.lower()
        best_match = None
        best_score = 0.0
        
        for template_id, template in self.workflow_templates.items():
            keyword_matches = sum(1 for keyword in template["pattern_keywords"] 
                                if keyword.lower() in user_input_lower)
            if keyword_matches > 0:
                score = keyword_matches / len(template["pattern_keywords"])
                score += template["success_rate"] * 0.1
                
                if score > best_score:
                    best_score = score
                    best_match = template
        
        missing_connections = []
        if best_match:
            missing_connections = self._check_missing_connections(best_match["required_connections"])
        
        return (best_match, best_score, missing_connections) if best_score > 0.3 else (None, 0.0, [])
    
    def _check_missing_connections(self, required_connections: List[str]) -> List[str]:
        """Check which required connections are missing"""
        missing = []
        for connection in required_connections:
            if connection in self.connectivity_manager.connections:
                if self.connectivity_manager.connections[connection]["status"] != "connected":
                    missing.append(connection)
        return missing
    
    async def process_agent_request(self, user_input: str, agent_type: str = "technical_lead") -> Dict:
        """Process user request with agent personality consideration"""
        
        agent = self.agent_profiles.get(agent_type)
        agent_name = agent.name if agent else "Unknown Agent"
        print(f"🤖 Agent: {agent_name}")
        print(f"🔍 Analyzing request: {user_input}")
        
        # Find best workflow for agent
        template_match, confidence, missing_connections = self.find_best_workflow_for_agent(user_input, agent_type)
        
        if template_match:
            print(f"✅ Found agent-optimized template: {template_match['name']} (confidence: {confidence:.2f})")
            
            if missing_connections:
                print(f"⚠️ Missing connections: {', '.join(missing_connections)}")
                return {
                    "success": False,
                    "error": "missing_connections",
                    "missing_connections": missing_connections,
                    "template": template_match,
                    "connectivity_setup_required": True
                }
        else:
            print("🆕 No suitable template found - will create custom workflow")
        
        # Generate workflow
        workflow_json = self._generate_agent_optimized_workflow(user_input, template_match, agent_type)
        
        # Check all required connections
        required_connections = self.connectivity_manager.get_required_connections_for_workflow(workflow_json)
        missing_for_execution = self._check_missing_connections(required_connections)
        
        if missing_for_execution:
            return {
                "success": False,
                "error": "missing_connections_for_execution",
                "missing_connections": missing_for_execution,
                "workflow": workflow_json,
                "connectivity_setup_required": True,
                "agent_type": agent_type
            }
        
        return {
            "success": True,
            "agent_type": agent_type,
            "agent_optimized": template_match is not None,
            "template_confidence": confidence,
            "template_id": template_match["template_id"] if template_match else None,
            "workflow": workflow_json,
            "execution_ready": True,
            "estimated_time": workflow_json["estimated_execution_time"],
            "required_connections": required_connections,
            "all_connections_ready": len(missing_for_execution) == 0
        }
    
    def _generate_agent_optimized_workflow(self, user_input: str, template: Optional[Dict], agent_type: str) -> Dict:
        """Generate workflow optimized for specific agent"""
        
        agent = self.agent_profiles.get(agent_type)
        workflow_id = f"wf_{agent_type}_{int(time.time())}"
        
        # Mock workflow generation based on agent preferences
        steps = []
        
        # Add steps based on agent preferences and user input
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ["task", "asana"]) and "asana" in agent.workflow_preferences:
            steps.append({
                "step_id": f"step_{len(steps) + 1}",
                "name": "Create Task (Agent Optimized)",
                "driver": "asana_driver",
                "operation": "create_task",
                "parameters": {
                    "priority": "high" if agent.decision_making == "aggressive" else "normal",
                    "automation_level": agent.automation_level
                }
            })
        
        if any(word in user_input_lower for word in ["notify", "slack"]) and "slack" in agent.workflow_preferences:
            communication_style = "formal" if agent.communication_style == "formal" else "casual"
            steps.append({
                "step_id": f"step_{len(steps) + 1}",
                "name": f"Send Notification ({communication_style.title()})",
                "driver": "slack_driver", 
                "operation": "send_message",
                "parameters": {
                    "tone": communication_style,
                    "urgency": agent.risk_tolerance
                }
            })
        
        # Add more steps based on other preferences...
        
        return {
            "workflow_id": workflow_id,
            "name": f"Agent-Optimized Workflow for {agent.name if agent else 'Unknown Agent'}",
            "description": f"Workflow optimized for {agent.role if agent else 'general'} with {agent.communication_style if agent else 'default'} communication style",
            "agent_type": agent_type,
            "agent_personality": agent.__dict__ if agent else None,
            "created_at": datetime.now().isoformat(),
            "template_used": template is not None,
            "template_id": template["template_id"] if template else None,
            "estimated_execution_time": len(steps) * 8 + 5,
            "steps": steps,
            "agent_optimizations": {
                "communication_style": agent.communication_style if agent else "default",
                "risk_tolerance": agent.risk_tolerance if agent else "medium",
                "automation_level": agent.automation_level if agent else "moderate"
            }
        }

async def demo_agent_workflow_system():
    """Demonstrate the enhanced agent workflow system"""
    
    system = EnhancedAgentWorkflowSystem()
    
    # Test scenarios for different agent types
    test_scenarios = [
        {
            "agent": "technical_lead",
            "request": "Create a critical bug fix task and alert the development team immediately"
        },
        {
            "agent": "marketing_manager", 
            "request": "Launch our new product announcement on Twitter and track engagement"
        },
        {
            "agent": "customer_success",
            "request": "Set up onboarding for our new enterprise client Microsoft"
        },
        {
            "agent": "sales_executive",
            "request": "Process refund for customer John Smith and notify the team"
        }
    ]
    
    print("🤖 DXTR AutoFlow - Enhanced Agent Workflow System Demo")
    print("=" * 80)
    print("Testing agent personality-based workflow selection and connectivity requirements\n")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🎯 Scenario {i}: {scenario['agent'].replace('_', ' ').title()} Agent")
        print(f"📝 Request: {scenario['request']}")
        print("─" * 80)
        
        result = await system.process_agent_request(scenario['request'], scenario['agent'])
        
        if result["success"]:
            print(f"✅ Agent-Optimized: {result['agent_optimized']}")
            print(f"🎯 Workflow: {result['workflow']['name']}")
            print(f"⚙️ Steps: {len(result['workflow']['steps'])}")
            print(f"🔗 Required Connections: {', '.join(result['required_connections'])}")
            print(f"🚀 Ready to Execute: {result['execution_ready']}")
        else:
            print(f"❌ Error: {result['error']}")
            if result.get("missing_connections"):
                print(f"🔌 Missing Connections: {', '.join(result['missing_connections'])}")
                print("🔧 Please configure these connections in the dashboard")
    
    print(f"\n🔌 Connectivity Dashboard Data:")
    dashboard_data = system.connectivity_manager.get_connectivity_dashboard_data()
    print(json.dumps(dashboard_data, indent=2))

if __name__ == "__main__":
    asyncio.run(demo_agent_workflow_system())
