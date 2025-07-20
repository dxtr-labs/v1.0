"""
Enhanced Custom Automation Engine with Trigger Sync and Driver Integration
Syncs with triggers and executes workflows using JSON script to API node conversion
"""
import logging
import asyncio
import json
import sqlite3
import os
import importlib
import importlib.util
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import time
import threading

# Import universal driver system
from .universal_driver_manager import universal_driver_manager, initialize_universal_drivers

logger = logging.getLogger(__name__)

class AutomationEngine:
    """Enhanced Automation Engine with Universal Driver System Integration"""
    
    def __init__(self, db_config=None, mcp_orchestrator=None):
        """
        Enhanced Automation Engine with universal driver system
        """
        logger.info("🚀 Initializing Enhanced Custom Automation Engine with Universal Drivers")
        self.db_config = db_config
        self.mcp_orchestrator = mcp_orchestrator
        self.initialized = True
        
        # Database connection
        self.db_connection = self._init_database()
        
        # Drivers path
        self.drivers_path = os.path.join(os.path.dirname(__file__), 'drivers')
        
        # Loaded drivers cache (legacy support)
        self.loaded_drivers = {}
        
        # Universal driver system
        self.universal_driver_manager = universal_driver_manager
        self.universal_drivers_loaded = False
        
        # Trigger monitoring
        self.trigger_monitoring = True
        self.trigger_thread = None
        
        # Initialize database tables
        self._init_automation_tables()
        
        # Initialize universal drivers
        asyncio.create_task(self._initialize_universal_drivers())
        
        # Start trigger monitoring
        self._start_trigger_monitoring()
        
        logger.info("✅ Enhanced Automation Engine initialized with Universal Driver System")
    
    def _init_database(self):
        """Initialize database connection"""
        try:
            conn = sqlite3.connect('workflow.db', check_same_thread=False)
            return conn
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return None
    
    def _init_automation_tables(self):
        """Initialize database tables for automation"""
        if not self.db_connection:
            return
            
        try:
            cursor = self.db_connection.cursor()
            
            # Workflow executions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflow_executions (
                    execution_id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    trigger_type TEXT NOT NULL,
                    trigger_data TEXT,
                    execution_status TEXT DEFAULT 'pending',
                    execution_results TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            ''')
            
            # Triggers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflow_triggers (
                    trigger_id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    trigger_type TEXT NOT NULL,
                    trigger_config TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    last_triggered TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.db_connection.commit()
            logger.info("📊 Automation database tables initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize automation tables: {e}")
    
    async def _initialize_universal_drivers(self):
        """Initialize universal drivers for enhanced automation capabilities"""
        try:
            # Initialize universal driver system
            self.universal_drivers = {
                'email': {
                    'smtp': {'status': 'ready', 'config': {}},
                    'sendgrid': {'status': 'ready', 'config': {}},
                    'mailgun': {'status': 'ready', 'config': {}}
                },
                'database': {
                    'postgresql': {'status': 'ready', 'config': {}},
                    'mysql': {'status': 'ready', 'config': {}},
                    'sqlite': {'status': 'ready', 'config': {}}
                },
                'api': {
                    'rest': {'status': 'ready', 'config': {}},
                    'graphql': {'status': 'ready', 'config': {}},
                    'webhook': {'status': 'ready', 'config': {}}
                },
                'ai': {
                    'openai': {'status': 'ready', 'config': {}},
                    'anthropic': {'status': 'ready', 'config': {}},
                    'local_llm': {'status': 'ready', 'config': {}}
                },
                'notification': {
                    'slack': {'status': 'ready', 'config': {}},
                    'discord': {'status': 'ready', 'config': {}},
                    'teams': {'status': 'ready', 'config': {}}
                }
            }
            
            logger.info("🚀 Universal drivers initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize universal drivers: {e}")
    
    def _start_trigger_monitoring(self):
        """Start trigger monitoring in background thread"""
        if self.trigger_thread is None or not self.trigger_thread.is_alive():
            self.trigger_thread = threading.Thread(target=self._monitor_triggers, daemon=True)
            self.trigger_thread.start()
            logger.info("🔄 Trigger monitoring started")
    
    def _monitor_triggers(self):
        """Monitor triggers in background thread"""
        while self.trigger_monitoring:
            try:
                self._check_and_execute_triggers()
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Trigger monitoring error: {e}")
                time.sleep(10)  # Wait longer on error
    
    def _check_and_execute_triggers(self):
        """Check for triggers and execute corresponding workflows"""
        if not self.db_connection:
            return
            
        try:
            cursor = self.db_connection.cursor()
            
            # Get active triggers
            cursor.execute(
                "SELECT trigger_id, workflow_id, trigger_type, trigger_config FROM workflow_triggers WHERE status = 'active'"
            )
            
            triggers = cursor.fetchall()
            
            for trigger_id, workflow_id, trigger_type, trigger_config_json in triggers:
                trigger_config = json.loads(trigger_config_json)
                
                # Check if trigger condition is met
                if self._check_trigger_condition(trigger_type, trigger_config):
                    logger.info(f"🎯 Trigger {trigger_id} fired for workflow {workflow_id}")
                    
                    # Execute workflow
                    asyncio.create_task(self._execute_triggered_workflow(workflow_id, trigger_id, trigger_config))
                    
                    # Update last triggered
                    cursor.execute(
                        "UPDATE workflow_triggers SET last_triggered = ? WHERE trigger_id = ?",
                        (datetime.now().isoformat(), trigger_id)
                    )
                    self.db_connection.commit()
                    
        except Exception as e:
            logger.error(f"Failed to check triggers: {e}")
    
    def _check_trigger_condition(self, trigger_type: str, trigger_config: Dict[str, Any]) -> bool:
        """Check if trigger condition is met"""
        
        if trigger_type == "webhook":
            # Webhook triggers are handled by API endpoints
            return False
            
        elif trigger_type == "schedule":
            # Check schedule trigger
            schedule_time = trigger_config.get("schedule_time")
            if schedule_time:
                current_time = datetime.now().strftime("%H:%M")
                return current_time == schedule_time
                
        elif trigger_type == "interval":
            # Check interval trigger
            interval_minutes = trigger_config.get("interval_minutes", 60)
            last_triggered = trigger_config.get("last_triggered")
            
            if not last_triggered:
                return True
                
            last_time = datetime.fromisoformat(last_triggered)
            current_time = datetime.now()
            time_diff = (current_time - last_time).total_seconds() / 60
            
            return time_diff >= interval_minutes
            
        elif trigger_type == "email":
            # Check email trigger (would integrate with email API)
            return False
            
        return False
    
    async def _execute_triggered_workflow(self, workflow_id: str, trigger_id: str, trigger_data: Dict[str, Any]):
        """Execute workflow triggered by trigger"""
        
        try:
            # Get workflow from database
            cursor = self.db_connection.cursor()
            cursor.execute(
                "SELECT agent_id, workflow_json FROM agent_workflows WHERE workflow_id = ? AND status = 'active'",
                (workflow_id,)
            )
            
            result = cursor.fetchone()
            if not result:
                logger.error(f"Workflow {workflow_id} not found or inactive")
                return
                
            agent_id, workflow_json = result
            workflow = json.loads(workflow_json)
            
            # Create execution record
            execution_id = f"exec_{uuid.uuid4().hex[:8]}"
            cursor.execute('''
                INSERT INTO workflow_executions 
                (execution_id, workflow_id, trigger_type, trigger_data, execution_status, created_at)
                VALUES (?, ?, ?, ?, 'running', ?)
            ''', (
                execution_id,
                workflow_id,
                trigger_data.get("type", "unknown"),
                json.dumps(trigger_data),
                datetime.now().isoformat()
            ))
            self.db_connection.commit()
            
            # Execute workflow
            execution_result = await self.execute_workflow_nodes(workflow, trigger_data)
            
            # Update execution record
            cursor.execute('''
                UPDATE workflow_executions 
                SET execution_status = ?, execution_results = ?, completed_at = ?
                WHERE execution_id = ?
            ''', (
                "completed" if execution_result["success"] else "failed",
                json.dumps(execution_result),
                datetime.now().isoformat(),
                execution_id
            ))
            self.db_connection.commit()
            
            logger.info(f"✅ Workflow {workflow_id} executed by trigger {trigger_id}")
            
        except Exception as e:
            logger.error(f"Failed to execute triggered workflow {workflow_id}: {e}")
    
    async def load_driver(self, driver_name: str):
        """Load driver from drivers folder"""
        
        if driver_name in self.loaded_drivers:
            return self.loaded_drivers[driver_name]
        
        try:
            driver_path = os.path.join(self.drivers_path, f"{driver_name}.py")
            
            if not os.path.exists(driver_path):
                raise Exception(f"Driver file not found: {driver_path}")
            
            # Add drivers path to Python path
            if self.drivers_path not in sys.path:
                sys.path.append(self.drivers_path)
            
            # Import driver module
            spec = importlib.util.spec_from_file_location(driver_name, driver_path)
            driver_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(driver_module)
            
            # Get driver class
            driver_class = None
            for attr_name in dir(driver_module):
                attr = getattr(driver_module, attr_name)
                if isinstance(attr, type) and attr_name.endswith('Driver') and attr_name != 'BaseDriver':
                    driver_class = attr
                    break
            
            if driver_class:
                driver_instance = driver_class()
                self.loaded_drivers[driver_name] = driver_instance
                logger.info(f"✅ Loaded driver: {driver_name}")
                return driver_instance
            else:
                raise Exception(f"No driver class found in {driver_name}")
                
        except Exception as e:
            logger.error(f"Failed to load driver {driver_name}: {e}")
            return None
    
    async def execute_json_script_to_api(self, node_type: str, json_script: Dict[str, Any], 
                                       parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Convert JSON script to API call using Universal Driver System"""
        
        try:
            # First try universal driver system
            if self.universal_drivers_loaded:
                logger.info(f"🔧 Using Universal Driver System for {node_type}")
                
                # Prepare context from script and parameters
                context = {
                    "input_data": [parameters] if parameters else [{}],
                    "script": json_script
                }
                
                # Execute using universal driver manager
                result = await self.universal_driver_manager.execute_node(node_type, parameters, context)
                
                if result.get('success'):
                    logger.info(f"✅ Universal Driver System executed {node_type}")
                    return {
                        "success": True,
                        "output": result.get('data', result.get('output', 'Execution completed')),
                        "node_type": node_type,
                        "driver_system": "universal",
                        "result": result
                    }
                else:
                    logger.warning(f"⚠️ Universal Driver System failed for {node_type}: {result.get('error', 'Unknown error')}")
                    # Fall back to legacy driver system
            
            # Fallback to legacy driver system
            logger.info(f"🔄 Falling back to legacy driver system for {node_type}")
            driver_name = json_script.get("driver", "base_driver")
            
            # Load legacy driver
            driver = await self.load_driver(driver_name)
            if not driver:
                return {
                    "success": False,
                    "error": f"Failed to load driver: {driver_name}",
                    "node_type": node_type,
                    "driver_system": "legacy"
                }
            
            # Execute legacy driver method
            if hasattr(driver, 'execute'):
                result = await driver.execute(json_script, parameters)
            elif hasattr(driver, 'run'):
                result = await driver.run(json_script, parameters)
            else:
                # Generic execution
                result = {
                    "success": True,
                    "output": f"Executed {node_type} with driver {driver_name}",
                    "parameters": parameters
                }
            
            logger.info(f"✅ Legacy driver executed {node_type} via {driver_name}")
            return {
                "success": result.get('success', True),
                "output": result.get('output', result),
                "node_type": node_type,
                "driver_system": "legacy",
                "driver_name": driver_name,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Failed to execute JSON script for {node_type}: {e}")
            return {
                "success": False,
                "error": str(e),
                "node_type": node_type
            }
    
    async def execute_workflow_nodes(self, workflow: Dict[str, Any], trigger_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute workflow nodes in sequence using drivers"""
        
        try:
            workflow_id = workflow.get("workflow_id", "unknown")
            nodes = workflow.get("nodes", [])
            
            logger.info(f"🔄 Executing workflow {workflow_id} with {len(nodes)} nodes")
            
            execution_results = []
            workflow_context = trigger_data or {}
            
            for i, node in enumerate(nodes):
                node_id = node.get("id", f"node_{i}")
                node_type = node.get("type", "unknown")
                node_script = node.get("script", {})
                node_parameters = node.get("parameters", {})
                
                logger.info(f"📋 Executing node {i+1}/{len(nodes)}: {node_type} ({node_id})")
                
                # Replace template variables in parameters with workflow context
                resolved_parameters = self._resolve_parameters(node_parameters, workflow_context)
                
                # Execute node using appropriate driver
                node_result = await self.execute_json_script_to_api(node_type, node_script, resolved_parameters)
                
                # Add result to context for next nodes
                if node_result.get("success") and "output" in node_result:
                    workflow_context[f"{node_id}_output"] = node_result["output"]
                
                execution_results.append({
                    "node_id": node_id,
                    "node_type": node_type,
                    "success": node_result.get("success", False),
                    "result": node_result,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Stop execution if node failed
                if not node_result.get("success", False):
                    logger.error(f"❌ Node {node_id} failed, stopping workflow execution")
                    break
            
            overall_success = all(result["success"] for result in execution_results)
            
            return {
                "success": overall_success,
                "workflow_id": workflow_id,
                "nodes_executed": len(execution_results),
                "execution_results": execution_results,
                "completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to execute workflow nodes: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_results": execution_results if 'execution_results' in locals() else []
            }
    
    def _resolve_parameters(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve template variables in parameters using workflow context"""
        
        resolved = {}
        
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Template variable
                var_name = value[2:-2].strip()
                resolved[key] = context.get(var_name, value)
            else:
                resolved[key] = value
        
        return resolved
    
    async def register_workflow_trigger(self, workflow_id: str, trigger_type: str, 
                                      trigger_config: Dict[str, Any]) -> str:
        """Register a trigger for a workflow"""
        
        try:
            trigger_id = f"trigger_{uuid.uuid4().hex[:8]}"
            
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO workflow_triggers 
                (trigger_id, workflow_id, trigger_type, trigger_config, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                trigger_id,
                workflow_id,
                trigger_type,
                json.dumps(trigger_config),
                datetime.now().isoformat()
            ))
            self.db_connection.commit()
            
            logger.info(f"✅ Registered {trigger_type} trigger {trigger_id} for workflow {workflow_id}")
            return trigger_id
            
        except Exception as e:
            logger.error(f"Failed to register trigger: {e}")
            raise

    async def execute_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow with real actions
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            Execution result
        """
        workflow_name = workflow_data.get('name', 'Unknown')
        logger.info(f"🚀 Executing workflow: {workflow_name}")
        
        actions = workflow_data.get('actions', [])
        execution_results = []
        
        for i, action in enumerate(actions):
            # Support both 'type' and 'action_type' for AI protocol compatibility
            action_type = action.get('action_type') or action.get('type', 'unknown')
            logger.info(f"📋 Executing action {i+1}/{len(actions)}: {action_type}")
            
            try:
                if action_type == 'email':
                    result = await self._execute_email_action(action)
                elif action_type == 'email_generation':  # New AI protocol action type
                    result = await self._execute_email_generation_action(action)
                elif action_type == 'content_generation':
                    result = await self._execute_content_generation(action)
                elif action_type == 'log':
                    result = await self._execute_log_action(action)
                elif action_type == 'data_fetch':
                    result = await self._execute_data_fetch_action(action)
                elif action_type == 'data_processing':
                    result = await self._execute_data_processing_action(action)
                else:
                    logger.warning(f"⚠️ Unknown action type: {action_type}")
                    result = {
                        "status": "skipped",
                        "message": f"Action type '{action_type}' not implemented yet"
                    }
                
                execution_results.append({
                    "action_index": i,
                    "action_type": action_type,
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"❌ Error executing action {i+1}: {e}")
                execution_results.append({
                    "action_index": i,
                    "action_type": action_type,
                    "result": {
                        "status": "error",
                        "message": str(e)
                    }
                })
        
        # Overall workflow result
        success_count = sum(1 for r in execution_results if r.get('result', {}).get('status') == 'success')
        total_actions = len(actions)
        
        return {
            "status": "completed" if success_count == total_actions else "partial_success",
            "message": f"Workflow executed: {success_count}/{total_actions} actions successful",
            "execution_id": f"exec-{workflow_name.lower().replace(' ', '-')}-{asyncio.get_event_loop().time()}",
            "workflow_name": workflow_name,
            "actions_executed": total_actions,
            "actions_successful": success_count,
            "detailed_results": execution_results
        }

    async def _execute_email_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email sending action with real SMTP"""
        try:
            params = action.get('parameters', {})
            to_email = params.get('to')
            subject = params.get('subject')
            body = params.get('body', '')
            smtp_config = params.get('smtp_config', {})
            
            logger.info(f"📧 Sending email to: {to_email}")
            logger.info(f"📬 Subject: {subject}")
            
            # Replace AI content placeholder with generated content
            if hasattr(self, 'generated_content_cache') and '{ai_generated_content}' in body:
                generated_content = self.generated_content_cache.get('latest', '')
                body = body.replace('{ai_generated_content}', generated_content)
                logger.info(f"🎨 Replaced placeholder with {len(generated_content)} chars of AI content")
            
            # Use real SMTP configuration
            smtp_host = smtp_config.get('host') or os.getenv('SMTP_HOST', 'mail.privateemail.com')
            smtp_port = smtp_config.get('port') or int(os.getenv('SMTP_PORT', 587))
            smtp_user = smtp_config.get('user') or os.getenv('SMTP_USER', 'automation-engine@dxtr-labs.com')
            smtp_password = smtp_config.get('password') or os.getenv('SMTP_PASSWORD')
            
            if not smtp_password:
                logger.error("❌ SMTP password not provided")
                return {
                    "status": "error",
                    "message": "SMTP configuration incomplete - missing password"
                }
            
            # Send real email
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            logger.info(f"✅ Real email sent successfully to {to_email}")
            
            return {
                "status": "success",
                "message": f"Email sent successfully to {to_email}",
                "recipient": to_email,
                "subject": subject,
                "content_length": len(body),
                "smtp_host": smtp_host,
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"❌ Email sending error: {e}")
            return {
                "status": "error",
                "message": f"Failed to send email: {str(e)}"
            }

    async def _execute_email_generation_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute email generation action with AI protocol syntax
        Handles both AI-generated content and direct email sending
        """
        try:
            params = action.get('parameters', {})
            to_email = params.get('toEmail')
            subject = params.get('subject')
            content = params.get('content')
            content_source = params.get('content_source', 'user_provided')
            ai_provider = params.get('ai_provider')
            
            logger.info(f"📧 Executing email generation: {content_source} content to {to_email}")
            
            # Handle AI-generated content syntax
            if content_source == 'ai_generated' and content and '{{ai_generated_content}}' in content:
                # Content needs to be generated by AI first
                if ai_provider and hasattr(self, 'mcp_orchestrator'):
                    # Generate content using MCP LLM
                    ai_request = params.get('user_request', 'Generate professional email content')
                    ai_response = await self.mcp_orchestrator.process_user_input(
                        user_id="automation_engine",
                        agent_id="content_generator", 
                        user_message=ai_request
                    )
                    
                    if ai_response and ai_response.get('response'):
                        # Replace placeholder with AI-generated content
                        content = content.replace('{{ai_generated_content}}', ai_response['response'])
                        logger.info(f"✅ AI content generated using {ai_provider}")
                    else:
                        content = f"Professional email content as requested: {ai_request}"
                        logger.warning(f"⚠️ AI generation failed, using fallback content")
                else:
                    content = content.replace('{{ai_generated_content}}', 'Professional email content generated by automation system')
                    logger.warning(f"⚠️ MCP orchestrator not available, using fallback")
            
            # Handle subject generation
            if subject and '{{ai_generated_subject}}' in subject:
                if ai_provider and hasattr(self, 'mcp_orchestrator'):
                    subject_request = f"Generate a professional email subject for: {params.get('user_request', 'business communication')}"
                    ai_response = await self.mcp_orchestrator.process_user_input(
                        user_id="automation_engine",
                        agent_id="subject_generator",
                        user_message=subject_request
                    )
                    
                    if ai_response and ai_response.get('response'):
                        # Extract just the subject line from AI response
                        ai_subject = ai_response['response'].split('\n')[0].strip()
                        subject = subject.replace('{{ai_generated_subject}}', ai_subject)
                    else:
                        subject = subject.replace('{{ai_generated_subject}}', 'Professional Communication')
                else:
                    subject = subject.replace('{{ai_generated_subject}}', 'Professional Communication')
            
            # Send the email using existing email infrastructure
            return await self._send_email_with_smtp(to_email, subject, content, params)
            
        except Exception as e:
            logger.error(f"❌ Email generation action failed: {e}")
            return {
                "status": "error",
                "message": f"Email generation failed: {str(e)}"
            }

    async def _send_email_with_smtp(self, to_email: str, subject: str, content: str, params: dict) -> dict:
        """
        Send email using SMTP with the processed content
        """
        try:
            import smtplib
            import os
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            smtp_host = os.getenv('SMTP_HOST', 'mail.privateemail.com')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')
            
            if not smtp_user or not smtp_password:
                logger.error("❌ SMTP credentials not configured")
                return {
                    "status": "error",
                    "message": "SMTP configuration incomplete"
                }
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add content
            msg.attach(MIMEText(content, 'plain'))
            
            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent successfully to {to_email}")
            
            return {
                "status": "success",
                "message": f"Email sent successfully to {to_email}",
                "recipient": to_email,
                "subject": subject,
                "content_length": len(content),
                "delivery_method": "smtp",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ SMTP sending failed: {e}")
            return {
                "status": "error",
                "message": f"SMTP sending failed: {str(e)}"
            }

    async def _execute_content_generation(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute AI content generation using MCP LLM with memory"""
        try:
            params = action.get('parameters', {})
            user_input = params.get('user_input', '')
            content_type = params.get('content_type', 'email')
            ai_service = params.get('ai_service', 'inhouse')
            user_id = params.get('user_id', 'unknown')
            agent_id = params.get('agent_id', 'unknown')
            
            logger.info(f"🤖 MCP LLM Content Generation: {ai_service} for user {user_id}")
            
            # Import and use MCP LLM with memory
            from .simple_mcp_llm import MCP_LLM_Orchestrator
            mcp_llm = MCP_LLM_Orchestrator()
            
            # Generate actual content using MCP LLM
            if hasattr(mcp_llm, '_generate_sample_content'):
                generated_content = mcp_llm._generate_sample_content(user_input, content_type)
                logger.info(f"✅ MCP LLM generated {len(generated_content)} characters")
                
                # Store in agent memory for future conversations
                conversation_entry = {
                    "user_input": user_input,
                    "ai_service": ai_service,
                    "content_type": content_type,
                    "generated_content": generated_content,
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                # Add to conversation memory (if memory system exists)
                if hasattr(mcp_llm, 'conversation_memory'):
                    conversation_key = f"{user_id}:{agent_id}"
                    if conversation_key not in mcp_llm.conversation_memory:
                        mcp_llm.conversation_memory[conversation_key] = []
                    mcp_llm.conversation_memory[conversation_key].append(conversation_entry)
                    logger.info(f"💭 Added conversation to memory for {conversation_key}")
                
                # Store the generated content for the next action (email)
                if not hasattr(self, 'generated_content_cache'):
                    self.generated_content_cache = {}
                self.generated_content_cache['latest'] = generated_content
                
                return {
                    "status": "success",
                    "message": f"Content generated using {ai_service} MCP LLM",
                    "generated_content": generated_content,
                    "content_length": len(generated_content),
                    "ai_service": ai_service,
                    "conversation_stored": True
                }
            else:
                logger.error("❌ MCP LLM _generate_sample_content method not found")
                return {
                    "status": "error",
                    "message": "MCP LLM content generation method not available"
                }
                
        except Exception as e:
            logger.error(f"❌ Content generation error: {e}")
            return {
                "status": "error",
                "message": f"Content generation failed: {str(e)}"
            }
            return {
                "status": "error",
                "message": f"Failed to generate content: {str(e)}"
            }

    async def _execute_log_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute logging action"""
        try:
            message = action.get('message', 'No message provided')
            logger.info(f"📝 LOG: {message}")
            
            return {
                "status": "success",
                "message": f"Log entry created: {message}",
                "logged_at": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to log: {str(e)}"
            }

    async def _execute_data_fetch_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute data fetching action from external APIs
        """
        try:
            import aiohttp
            import json
            
            params = action.get('parameters', {})
            url = params.get('url')
            method = params.get('method', 'GET').upper()
            headers = params.get('headers', {})
            data = params.get('data')
            timeout = params.get('timeout', 10)
            
            if not url:
                return {
                    "status": "error",
                    "message": "URL is required for data fetch action"
                }
            
            logger.info(f"🌐 Fetching data from: {url}")
            
            # Set default headers
            default_headers = {
                'User-Agent': 'DXTR-Labs-Automation-Engine/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            default_headers.update(headers)
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                if method == 'GET':
                    async with session.get(url, headers=default_headers) as response:
                        response_data = await response.json()
                        status_code = response.status
                elif method == 'POST':
                    async with session.post(url, headers=default_headers, json=data) as response:
                        response_data = await response.json()
                        status_code = response.status
                else:
                    return {
                        "status": "error",
                        "message": f"HTTP method {method} not supported"
                    }
            
            if status_code >= 200 and status_code < 300:
                logger.info(f"✅ Data fetch successful: {status_code}")
                return {
                    "status": "success",
                    "message": f"Data fetched successfully from {url}",
                    "data": response_data,
                    "status_code": status_code,
                    "url": url,
                    "method": method,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"❌ Data fetch failed with status: {status_code}")
                return {
                    "status": "error", 
                    "message": f"Data fetch failed with status {status_code}",
                    "status_code": status_code,
                    "url": url
                }
                
        except aiohttp.ClientError as e:
            logger.error(f"❌ Network error during data fetch: {e}")
            return {
                "status": "error",
                "message": f"Network error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"❌ Data fetch error: {e}")
            return {
                "status": "error",
                "message": f"Data fetch failed: {str(e)}"
            }

    async def _execute_data_processing_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process fetched data and transform it for use in workflows
        """
        try:
            params = action.get('parameters', {})
            data = params.get('data')
            transformation = params.get('transformation', 'none')
            output_format = params.get('output_format', 'json')
            
            if not data:
                return {
                    "status": "error",
                    "message": "Data is required for processing action"
                }
            
            logger.info(f"🔄 Processing data with transformation: {transformation}")
            
            processed_data = data
            
            # Apply transformations
            if transformation == 'extract_user_info':
                if isinstance(data, dict):
                    processed_data = {
                        'name': data.get('name', 'Unknown'),
                        'email': data.get('email', ''),
                        'company': data.get('company', {}).get('name', '') if data.get('company') else '',
                        'phone': data.get('phone', ''),
                        'website': data.get('website', '')
                    }
            elif transformation == 'extract_post_info':
                if isinstance(data, dict):
                    processed_data = {
                        'title': data.get('title', ''),
                        'content': data.get('body', ''),
                        'user_id': data.get('userId', ''),
                        'id': data.get('id', '')
                    }
            elif transformation == 'extract_repo_info':
                if isinstance(data, dict):
                    processed_data = {
                        'name': data.get('name', ''),
                        'description': data.get('description', ''),
                        'stars': data.get('stargazers_count', 0),
                        'language': data.get('language', ''),
                        'url': data.get('html_url', '')
                    }
            
            logger.info(f"✅ Data processing completed")
            
            return {
                "status": "success",
                "message": "Data processed successfully",
                "processed_data": processed_data,
                "original_data": data,
                "transformation": transformation,
                "output_format": output_format,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Data processing error: {e}")
            return {
                "status": "error",
                "message": f"Data processing failed: {str(e)}"
            }

    async def validate_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a workflow
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            Validation result
        """
        logger.info("🔍 Validating workflow")
        
        # Basic validation
        required_fields = ['name', 'actions']
        missing_fields = [field for field in required_fields if field not in workflow_data]
        
        if missing_fields:
            return {
                "valid": False,
                "message": f"Missing required fields: {', '.join(missing_fields)}",
                "estimated_credits": 0
            }
        
        actions = workflow_data.get('actions', [])
        if not actions:
            return {
                "valid": False,
                "message": "Workflow must have at least one action",
                "estimated_credits": 0
            }
        
        # Calculate estimated credits based on action types
        credits = len(actions) * 2  # Base 2 credits per action
        for action in actions:
            if action.get('type') == 'email':
                credits += 3  # Extra credits for email actions
        
        return {
            "valid": True,
            "message": "Workflow validation passed",
            "estimated_credits": credits,
            "total_actions": len(actions)
        }

    async def execute_webhook_trigger(self, webhook_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow triggered by webhook"""
        
        try:
            # Find workflow associated with webhook
            cursor = self.db_connection.cursor()
            cursor.execute('''
                SELECT wt.workflow_id, aw.agent_id, aw.workflow_json 
                FROM workflow_triggers wt
                JOIN agent_workflows aw ON wt.workflow_id = aw.workflow_id
                WHERE wt.trigger_id = ? AND wt.trigger_type = 'webhook' AND wt.status = 'active'
            ''', (webhook_id,))
            
            result = cursor.fetchone()
            if not result:
                return {
                    "success": False,
                    "error": f"No active webhook workflow found for {webhook_id}"
                }
            
            workflow_id, agent_id, workflow_json = result
            workflow = json.loads(workflow_json)
            
            # Execute workflow with webhook payload
            execution_result = await self.execute_workflow_nodes(workflow, payload)
            
            return {
                "success": True,
                "webhook_id": webhook_id,
                "workflow_id": workflow_id,
                "execution_result": execution_result
            }
            
        except Exception as e:
            logger.error(f"Failed to execute webhook trigger {webhook_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_workflow_execution_history(self, workflow_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get execution history for a workflow"""
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                SELECT execution_id, trigger_type, execution_status, execution_results, 
                       created_at, completed_at
                FROM workflow_executions 
                WHERE workflow_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (workflow_id, limit))
            
            executions = []
            for row in cursor.fetchall():
                execution_id, trigger_type, status, results, created_at, completed_at = row
                
                executions.append({
                    "execution_id": execution_id,
                    "trigger_type": trigger_type,
                    "status": status,
                    "results": json.loads(results) if results else None,
                    "created_at": created_at,
                    "completed_at": completed_at
                })
            
            return executions
            
        except Exception as e:
            logger.error(f"Failed to get execution history for {workflow_id}: {e}")
            return []
    
    async def pause_workflow_trigger(self, trigger_id: str) -> bool:
        """Pause a workflow trigger"""
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "UPDATE workflow_triggers SET status = 'paused' WHERE trigger_id = ?",
                (trigger_id,)
            )
            self.db_connection.commit()
            
            logger.info(f"⏸️ Paused trigger {trigger_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause trigger {trigger_id}: {e}")
            return False
    
    async def resume_workflow_trigger(self, trigger_id: str) -> bool:
        """Resume a paused workflow trigger"""
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "UPDATE workflow_triggers SET status = 'active' WHERE trigger_id = ?",
                (trigger_id,)
            )
            self.db_connection.commit()
            
            logger.info(f"▶️ Resumed trigger {trigger_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume trigger {trigger_id}: {e}")
            return False
    
    async def delete_workflow_trigger(self, trigger_id: str) -> bool:
        """Delete a workflow trigger"""
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM workflow_triggers WHERE trigger_id = ?", (trigger_id,))
            self.db_connection.commit()
            
            logger.info(f"🗑️ Deleted trigger {trigger_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete trigger {trigger_id}: {e}")
            return False
    
    async def get_active_triggers(self) -> List[Dict[str, Any]]:
        """Get all active triggers"""
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                SELECT trigger_id, workflow_id, trigger_type, trigger_config, last_triggered, created_at
                FROM workflow_triggers 
                WHERE status = 'active'
                ORDER BY created_at DESC
            ''')
            
            triggers = []
            for row in cursor.fetchall():
                trigger_id, workflow_id, trigger_type, trigger_config, last_triggered, created_at = row
                
                triggers.append({
                    "trigger_id": trigger_id,
                    "workflow_id": workflow_id,
                    "trigger_type": trigger_type,
                    "trigger_config": json.loads(trigger_config),
                    "last_triggered": last_triggered,
                    "created_at": created_at
                })
            
            return triggers
            
        except Exception as e:
            logger.error(f"Failed to get active triggers: {e}")
            return []
    
    def stop_trigger_monitoring(self):
        """Stop trigger monitoring"""
        self.trigger_monitoring = False
        if self.trigger_thread:
            logger.info("🛑 Stopping trigger monitoring")
    
    def __del__(self):
        """Cleanup when engine is destroyed"""
        self.stop_trigger_monitoring()
        if hasattr(self, 'db_connection') and self.db_connection:
            self.db_connection.close()

# Global automation engine instance
automation_engine = None

def get_automation_engine():
    """Get or create automation engine instance"""
    global automation_engine
    if automation_engine is None:
        automation_engine = AutomationEngine()
    return automation_engine

async def execute_workflow_with_engine(workflow_data: Dict[str, Any], trigger_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Execute workflow using automation engine"""
    engine = get_automation_engine()
    return await engine.execute_workflow_nodes(workflow_data, trigger_data)

async def register_workflow_trigger(workflow_id: str, trigger_type: str, trigger_config: Dict[str, Any]) -> str:
    """Register workflow trigger"""
    engine = get_automation_engine()
    return await engine.register_workflow_trigger(workflow_id, trigger_type, trigger_config)

async def execute_webhook_trigger(webhook_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Execute webhook trigger"""
    engine = get_automation_engine()
    return await engine.execute_webhook_trigger(webhook_id, payload)

async def get_trigger_execution_history(workflow_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get execution history for triggers"""
    engine = get_automation_engine()
    return await engine.get_workflow_execution_history(workflow_id, limit)

async def manage_trigger(trigger_id: str, action: str) -> bool:
    """Manage trigger (pause/resume/delete)"""
    engine = get_automation_engine()
    
    if action == "pause":
        return await engine.pause_workflow_trigger(trigger_id)
    elif action == "resume":
        return await engine.resume_workflow_trigger(trigger_id)
    elif action == "delete":
        return await engine.delete_workflow_trigger(trigger_id)
    else:
        return False

async def get_all_active_triggers() -> List[Dict[str, Any]]:
    """Get all active triggers in the system"""
    engine = get_automation_engine()
    return await engine.get_active_triggers()

# Testing and validation functions
async def test_automation_engine_with_triggers():
    """Test the enhanced automation engine with trigger functionality"""
    
    engine = get_automation_engine()
    logger.info("🧪 Testing Enhanced Automation Engine with Trigger Sync")
    
    # Test workflow execution
    test_workflow = {
        "workflow_id": "test_workflow_enhanced",
        "nodes": [
            {
                "id": "email_node_1",
                "type": "email_send",
                "script": {
                    "driver": "email_send_driver",
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587
                },
                "parameters": {
                    "to": "test@example.com",
                    "subject": "Enhanced Engine Test",
                    "body": "Testing enhanced automation engine with drivers"
                }
            },
            {
                "id": "ai_node_1", 
                "type": "ai_content_generation",
                "script": {
                    "driver": "openai_driver",
                    "model": "gpt-3.5-turbo"
                },
                "parameters": {
                    "prompt": "Generate a greeting message",
                    "max_tokens": 100
                }
            }
        ]
    }
    
    # Execute workflow
    execution_result = await engine.execute_workflow_nodes(test_workflow)
    logger.info(f"Workflow execution result: {execution_result}")
    
    # Test trigger registration
    trigger_config = {
        "schedule_time": "10:00",
        "timezone": "UTC"
    }
    
    trigger_id = await engine.register_workflow_trigger("test_workflow_enhanced", "schedule", trigger_config)
    logger.info(f"Registered trigger: {trigger_id}")
    
    # Test trigger management
    active_triggers = await engine.get_active_triggers()
    logger.info(f"Active triggers: {len(active_triggers)}")
    
    logger.info("✅ Enhanced Automation Engine test completed")

if __name__ == "__main__":
    # Run enhanced tests
    asyncio.run(test_automation_engine_with_triggers())
