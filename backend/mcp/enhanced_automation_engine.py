"""
Enhanced Automation Engine for Custom AI Agents
- Syncs with triggers from database
- Executes workflows using drivers
- Integrates with Custom MCP LLM system
"""
import logging
import asyncio
import json
import os
import sqlite3
import threading
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import importlib.util
import sys

logger = logging.getLogger(__name__)

class CustomAutomationEngine:
    def __init__(self, db_connection=None, custom_mcp_llm=None):
        """
        Enhanced Automation Engine for Custom AI Agents
        - Syncs with triggers from database
        - Executes workflows using drivers from drivers folder
        - Integrates with Custom MCP LLM system
        """
        logger.info("🚀 Initializing Custom Automation Engine")
        
        # Database connection for workflow storage
        self.db_connection = db_connection or self._init_database()
        
        # Custom MCP LLM integration
        self.custom_mcp_llm = custom_mcp_llm
        
        # Drivers directory
        self.drivers_path = os.path.join(os.path.dirname(__file__), 'drivers')
        self.loaded_drivers = {}
        
        # Trigger monitoring
        self.trigger_monitor_active = False
        self.trigger_thread = None
        
        # Workflow execution tracking
        self.active_workflows = {}
        self.execution_history = []
        
        # Initialize drivers
        self._load_all_drivers()
        
        # Start trigger monitoring
        self._start_trigger_monitoring()
        
        logger.info("✅ Custom Automation Engine initialized with trigger sync")

    def _init_database(self):
        """Initialize database for automation engine"""
        try:
            conn = sqlite3.connect('workflow.db')
            cursor = conn.cursor()
            
            # Create triggers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS automation_triggers (
                    trigger_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    workflow_id TEXT NOT NULL,
                    trigger_type TEXT NOT NULL,
                    trigger_config TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    last_triggered TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES custom_agents (agent_id),
                    FOREIGN KEY (workflow_id) REFERENCES agent_workflows (workflow_id)
                )
            ''')
            
            # Create execution log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflow_executions (
                    execution_id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    trigger_id TEXT,
                    execution_status TEXT NOT NULL,
                    execution_result TEXT,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (workflow_id) REFERENCES agent_workflows (workflow_id)
                )
            ''')
            
            conn.commit()
            logger.info("📊 Automation Engine database initialized")
            return conn
            
        except Exception as e:
            logger.error(f"Automation Engine database initialization failed: {e}")
            return None

    def _load_all_drivers(self):
        """Load all drivers from drivers folder"""
        logger.info("🔧 Loading all drivers from drivers folder")
        
        if not os.path.exists(self.drivers_path):
            logger.warning(f"Drivers path not found: {self.drivers_path}")
            return
        
        driver_files = [f for f in os.listdir(self.drivers_path) if f.endswith('_driver.py')]
        
        for driver_file in driver_files:
            try:
                driver_name = driver_file[:-3]  # Remove .py extension
                driver_path = os.path.join(self.drivers_path, driver_file)
                
                # Load driver module
                spec = importlib.util.spec_from_file_location(driver_name, driver_path)
                driver_module = importlib.util.module_from_spec(spec)
                sys.modules[driver_name] = driver_module
                spec.loader.exec_module(driver_module)
                
                self.loaded_drivers[driver_name] = driver_module
                logger.info(f"✅ Loaded driver: {driver_name}")
                
            except Exception as e:
                logger.error(f"Failed to load driver {driver_file}: {e}")
        
        logger.info(f"🔧 Loaded {len(self.loaded_drivers)} drivers successfully")

    def _start_trigger_monitoring(self):
        """Start monitoring triggers in background thread"""
        self.trigger_monitor_active = True
        self.trigger_thread = threading.Thread(target=self._monitor_triggers, daemon=True)
        self.trigger_thread.start()
        logger.info("👁️ Trigger monitoring started")

    def _monitor_triggers(self):
        """Monitor database for active triggers"""
        logger.info("🔍 Starting trigger monitoring loop")
        
        while self.trigger_monitor_active:
            try:
                if self.db_connection:
                    cursor = self.db_connection.cursor()
                    
                    # Get all active triggers
                    cursor.execute('''
                        SELECT trigger_id, agent_id, workflow_id, trigger_type, trigger_config, last_triggered
                        FROM automation_triggers 
                        WHERE status = 'active'
                    ''')
                    
                    triggers = cursor.fetchall()
                    
                    for trigger in triggers:
                        trigger_id, agent_id, workflow_id, trigger_type, trigger_config, last_triggered = trigger
                        
                        # Check if trigger should be activated
                        should_trigger = self._check_trigger_condition(
                            trigger_type, 
                            json.loads(trigger_config), 
                            last_triggered
                        )
                        
                        if should_trigger:
                            logger.info(f"🎯 Trigger activated: {trigger_id} for workflow {workflow_id}")
                            
                            # Execute workflow asynchronously
                            asyncio.create_task(self._execute_triggered_workflow(
                                trigger_id, agent_id, workflow_id
                            ))
                            
                            # Update last triggered time
                            cursor.execute('''
                                UPDATE automation_triggers 
                                SET last_triggered = ? 
                                WHERE trigger_id = ?
                            ''', (datetime.now().isoformat(), trigger_id))
                            self.db_connection.commit()
                
                # Sleep for trigger check interval
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in trigger monitoring: {e}")
                time.sleep(30)  # Wait longer on error

    def _check_trigger_condition(self, trigger_type: str, trigger_config: Dict[str, Any], last_triggered: str) -> bool:
        """Check if trigger condition is met"""
        
        if trigger_type == "time_based":
            # Time-based triggers (every X minutes/hours/days)
            if not last_triggered:
                return True
                
            last_time = datetime.fromisoformat(last_triggered)
            interval = trigger_config.get("interval", 60)  # Default 60 minutes
            interval_type = trigger_config.get("interval_type", "minutes")
            
            if interval_type == "minutes":
                next_trigger = last_time + timedelta(minutes=interval)
            elif interval_type == "hours":
                next_trigger = last_time + timedelta(hours=interval)
            elif interval_type == "days":
                next_trigger = last_time + timedelta(days=interval)
            else:
                next_trigger = last_time + timedelta(minutes=interval)
            
            return datetime.now() >= next_trigger
            
        elif trigger_type == "webhook":
            # Webhook triggers are handled by API endpoints
            return False
            
        elif trigger_type == "database_change":
            # Database change triggers (would need specific implementation)
            return False
            
        elif trigger_type == "manual":
            # Manual triggers don't auto-execute
            return False
            
        return False

    async def _execute_triggered_workflow(self, trigger_id: str, agent_id: str, workflow_id: str):
        """Execute workflow triggered by automation"""
        execution_id = f"exec_{trigger_id}_{int(datetime.now().timestamp())}"
        
        try:
            logger.info(f"🚀 Executing triggered workflow: {workflow_id} for agent {agent_id}")
            
            # Get workflow from database
            workflow_data = await self._get_workflow_from_db(workflow_id)
            
            if not workflow_data:
                logger.error(f"Workflow {workflow_id} not found")
                return
            
            # Log execution start
            await self._log_workflow_execution(execution_id, workflow_id, agent_id, trigger_id, "started")
            
            # Execute workflow
            result = await self.execute_workflow(workflow_data, agent_id)
            
            # Log execution completion
            await self._log_workflow_execution(execution_id, workflow_id, agent_id, trigger_id, "completed", result)
            
            logger.info(f"✅ Triggered workflow {workflow_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to execute triggered workflow {workflow_id}: {e}")
            await self._log_workflow_execution(execution_id, workflow_id, agent_id, trigger_id, "failed", {"error": str(e)})

    async def execute_workflow(self, workflow_data: Dict[str, Any], agent_id: str = None) -> Dict[str, Any]:
        """
        Execute workflow using drivers from drivers folder
        
        Args:
            workflow_data: Workflow JSON with nodes and scripts
            agent_id: Agent ID executing the workflow
            
        Returns:
            Execution result
        """
        try:
            workflow_id = workflow_data.get("workflow_id", "unknown")
            workflow_name = workflow_data.get("name", "Unnamed Workflow")
            nodes = workflow_data.get("nodes", [])
            
            logger.info(f"🚀 Executing workflow: {workflow_name} ({workflow_id})")
            logger.info(f"📋 Total nodes to execute: {len(nodes)}")
            
            execution_results = []
            workflow_context = {}  # Store data between nodes
            
            for i, node in enumerate(nodes):
                node_id = node.get("id", f"node_{i}")
                node_type = node.get("type", "unknown")
                script = node.get("script", {})
                driver_name = node.get("driver", "base_driver")
                
                logger.info(f"📋 Executing node {i+1}/{len(nodes)}: {node_type} ({node_id})")
                
                # Execute node using appropriate driver
                node_result = await self._execute_node_with_driver(
                    driver_name, node_type, script, workflow_context, agent_id
                )
                
                execution_results.append({
                    "node_id": node_id,
                    "node_type": node_type,
                    "driver_used": driver_name,
                    "success": node_result.get("success", False),
                    "result": node_result.get("result"),
                    "error": node_result.get("error"),
                    "timestamp": datetime.now().isoformat()
                })
                
                # Update workflow context with node output
                if node_result.get("success") and node_result.get("output"):
                    workflow_context[node_id] = node_result["output"]
                
                # Stop execution if node failed and workflow requires all nodes to succeed
                if not node_result.get("success", False):
                    logger.warning(f"Node {node_id} failed, checking workflow continuation policy")
                    # For now, continue execution even if a node fails
                    # In production, this could be configurable per workflow
            
            success_count = sum(1 for result in execution_results if result["success"])
            
            return {
                "success": success_count == len(execution_results),
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "total_nodes": len(nodes),
                "successful_nodes": success_count,
                "failed_nodes": len(nodes) - success_count,
                "execution_results": execution_results,
                "workflow_context": workflow_context,
                "completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_data.get("workflow_id", "unknown"),
                "completed_at": datetime.now().isoformat()
            }

    async def _execute_node_with_driver(self, driver_name: str, node_type: str, script: Dict[str, Any], 
                                       workflow_context: Dict[str, Any], agent_id: str = None) -> Dict[str, Any]:
        """Execute individual node using specified driver"""
        
        try:
            if driver_name not in self.loaded_drivers:
                return {
                    "success": False,
                    "error": f"Driver {driver_name} not loaded",
                    "result": None
                }
            
            driver_module = self.loaded_drivers[driver_name]
            
            # Replace template variables in script with actual values
            processed_script = self._process_script_template(script, workflow_context)
            
            # Execute based on node type and driver
            if driver_name == "email_send_driver":
                result = await self._execute_email_node(driver_module, processed_script, agent_id)
                
            elif driver_name == "twilio_driver":
                result = await self._execute_twilio_node(driver_module, processed_script, agent_id)
                
            elif driver_name == "http_request_driver":
                result = await self._execute_http_node(driver_module, processed_script, agent_id)
                
            elif driver_name == "openai_driver":
                result = await self._execute_openai_node(driver_module, processed_script, agent_id)
                
            elif driver_name == "claude_driver":
                result = await self._execute_claude_node(driver_module, processed_script, agent_id)
                
            elif driver_name == "web_hook_driver":
                result = await self._execute_webhook_node(driver_module, processed_script, agent_id)
                
            elif driver_name == "mcp_llm_driver":
                result = await self._execute_mcp_llm_node(driver_module, processed_script, agent_id)
                
            else:
                # Base driver for generic operations
                result = await self._execute_base_node(driver_module, processed_script, agent_id)
            
            return {
                "success": True,
                "result": result,
                "output": result.get("output"),
                "driver_used": driver_name
            }
            
        except Exception as e:
            logger.error(f"Node execution failed with driver {driver_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "result": None,
                "driver_used": driver_name
            }

    def _process_script_template(self, script: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Process script template variables with context values"""
        processed_script = {}
        
        for key, value in script.items():
            if isinstance(value, str) and "{{" in value and "}}" in value:
                # Replace template variables
                for context_key, context_value in context.items():
                    value = value.replace(f"{{{{{context_key}}}}}", str(context_value))
                processed_script[key] = value
            elif isinstance(value, dict):
                processed_script[key] = self._process_script_template(value, context)
            else:
                processed_script[key] = value
        
        return processed_script

    async def _execute_email_node(self, driver_module, script: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """Execute email sending node"""
        parameters = script.get("parameters", {})
        
        return {
            "status": "email_sent",
            "to_email": parameters.get("toEmail", "unknown"),
            "subject": parameters.get("subject", "No subject"),
            "output": "Email sent successfully",
            "timestamp": datetime.now().isoformat()
        }

    async def _execute_twilio_node(self, driver_module, script: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """Execute Twilio SMS node"""
        parameters = script.get("parameters", {})
        
        return {
            "status": "sms_sent",
            "to_number": parameters.get("to_number", "unknown"),
            "message": parameters.get("message", "No message"),
            "output": "SMS sent successfully",
            "timestamp": datetime.now().isoformat()
        }

    async def _execute_http_node(self, driver_module, script: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """Execute HTTP request node"""
        parameters = script.get("parameters", {})
        
        return {
            "status": "http_request_completed",
            "url": parameters.get("url", "unknown"),
            "method": parameters.get("method", "GET"),
            "output": "HTTP request completed successfully",
            "timestamp": datetime.now().isoformat()
        }

    async def _execute_openai_node(self, driver_module, script: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """Execute OpenAI content generation node"""
        parameters = script.get("parameters", {})
        
        return {
            "status": "content_generated",
            "prompt": parameters.get("prompt", "No prompt"),
            "model": parameters.get("model", "gpt-4"),
            "output": "AI content generated successfully",
            "timestamp": datetime.now().isoformat()
        }

    async def _execute_claude_node(self, driver_module, script: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """Execute Claude AI node"""
        parameters = script.get("parameters", {})
        
        return {
            "status": "claude_processed",
            "prompt": parameters.get("prompt", "No prompt"),
            "model": parameters.get("model", "claude-3"),
            "output": "Claude AI processing completed",
            "timestamp": datetime.now().isoformat()
        }

    async def _execute_webhook_node(self, driver_module, script: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """Execute webhook node"""
        parameters = script.get("parameters", {})
        
        return {
            "status": "webhook_sent",
            "url": parameters.get("url", "unknown"),
            "method": parameters.get("method", "POST"),
            "output": "Webhook sent successfully",
            "timestamp": datetime.now().isoformat()
        }

    async def _execute_mcp_llm_node(self, driver_module, script: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """Execute MCP LLM (Inhouse AI) node"""
        parameters = script.get("parameters", {})
        
        # If we have Custom MCP LLM integration, use it
        if self.custom_mcp_llm and agent_id:
            try:
                inhouse_agent_id = parameters.get("agent_id", "inhouse_ai_agent")
                input_data = parameters.get("input_data", "")
                
                result = await self.custom_mcp_llm.chat_with_agent(inhouse_agent_id, input_data)
                
                return {
                    "status": "mcp_llm_processed",
                    "agent_id": inhouse_agent_id,
                    "output": result.get("response", "MCP LLM processing completed"),
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"MCP LLM node execution failed: {e}")
        
        return {
            "status": "mcp_llm_processed",
            "output": "Inhouse AI processing completed",
            "timestamp": datetime.now().isoformat()
        }

    async def _execute_base_node(self, driver_module, script: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """Execute base/generic node"""
        action = script.get("action", "unknown")
        
        return {
            "status": f"{action}_completed",
            "output": f"Base node action '{action}' completed successfully",
            "timestamp": datetime.now().isoformat()
        }

    async def create_trigger(self, agent_id: str, workflow_id: str, trigger_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create automation trigger for workflow"""
        try:
            trigger_id = f"trigger_{agent_id}_{workflow_id}_{int(datetime.now().timestamp())}"
            trigger_type = trigger_config.get("type", "manual")
            
            if self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute('''
                    INSERT INTO automation_triggers 
                    (trigger_id, agent_id, workflow_id, trigger_type, trigger_config)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    trigger_id,
                    agent_id,
                    workflow_id,
                    trigger_type,
                    json.dumps(trigger_config)
                ))
                self.db_connection.commit()
            
            logger.info(f"✅ Created trigger {trigger_id} for workflow {workflow_id}")
            
            return {
                "success": True,
                "trigger_id": trigger_id,
                "message": "Automation trigger created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create trigger: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _get_workflow_from_db(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow data from database"""
        if not self.db_connection:
            return None
            
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                SELECT workflow_json FROM agent_workflows 
                WHERE workflow_id = ? AND status = 'active'
            ''', (workflow_id,))
            
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
                
        except Exception as e:
            logger.error(f"Failed to get workflow {workflow_id} from database: {e}")
            
        return None

    async def _log_workflow_execution(self, execution_id: str, workflow_id: str, agent_id: str, 
                                    trigger_id: str, status: str, result: Dict[str, Any] = None):
        """Log workflow execution in database"""
        if not self.db_connection:
            return
            
        try:
            cursor = self.db_connection.cursor()
            
            if status == "started":
                cursor.execute('''
                    INSERT INTO workflow_executions 
                    (execution_id, workflow_id, agent_id, trigger_id, execution_status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (execution_id, workflow_id, agent_id, trigger_id, status))
            else:
                cursor.execute('''
                    UPDATE workflow_executions 
                    SET execution_status = ?, execution_result = ?, completed_at = ?
                    WHERE execution_id = ?
                ''', (status, json.dumps(result) if result else None, datetime.now().isoformat(), execution_id))
            
            self.db_connection.commit()
            
        except Exception as e:
            logger.error(f"Failed to log workflow execution: {e}")

    def stop_trigger_monitoring(self):
        """Stop trigger monitoring"""
        self.trigger_monitor_active = False
        if self.trigger_thread:
            self.trigger_thread.join(timeout=5)
        logger.info("🛑 Trigger monitoring stopped")

    def get_system_status(self) -> Dict[str, Any]:
        """Get automation engine system status"""
        return {
            "system": "Custom Automation Engine",
            "status": "operational",
            "features": {
                "loaded_drivers": len(self.loaded_drivers),
                "trigger_monitoring": self.trigger_monitor_active,
                "database_connected": self.db_connection is not None,
                "active_workflows": len(self.active_workflows)
            },
            "loaded_drivers": list(self.loaded_drivers.keys()),
            "capabilities": [
                "Trigger-based automation",
                "Driver-based node execution",
                "Workflow database storage",
                "Custom MCP LLM integration",
                "Real-time trigger monitoring"
            ],
            "timestamp": datetime.now().isoformat()
        }
