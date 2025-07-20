"""
Advanced Workflow Detection and Selection System for CustomMCPLLM
Analyzes user input and intelligently selects appropriate workflows from the 2000+ available workflows
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import re
from datetime import datetime

# OpenAI for intelligent workflow matching
try:
    from openai import AsyncOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

logger = logging.getLogger(__name__)

class WorkflowSelector:
    """
    Intelligent workflow selection system that:
    1. Analyzes user intent from natural language
    2. Matches intent to appropriate workflow templates
    3. Ranks workflows by relevance and complexity
    4. Suggests best workflow options to user
    5. Handles workflow customization and parameter injection
    """
    
    def __init__(self, openai_api_key: str = None, workflow_directory: str = None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.workflow_directory = workflow_directory or "workflows"
        
        # Load workflow catalog
        self.workflow_catalog = {}
        self.workflow_categories = {}
        self.workflow_patterns = {}
        
        # Initialize workflow indexing
        self._load_workflow_catalog()
        
        logger.info(f"🔍 WorkflowSelector initialized with {len(self.workflow_catalog)} workflows")
    
    def _load_workflow_catalog(self):
        """Load and index all available workflows for quick selection"""
        try:
            # Look for workflow files in multiple locations
            workflow_paths = [
                Path(__file__).parent.parent.parent / "workflows",
                Path(__file__).parent.parent / "workflows", 
                Path(__file__).parent / "workflows",
                Path("workflows"),
                Path(".")
            ]
            
            workflow_files = []
            for path in workflow_paths:
                if path.exists():
                    # Find JSON workflow files
                    json_files = list(path.glob("**/*.json"))
                    workflow_files.extend(json_files)
                    logger.info(f"Found {len(json_files)} workflow files in {path}")
            
            if not workflow_files:
                logger.warning("No workflow files found - creating sample catalog")
                self._create_sample_catalog()
                return
            
            # Index workflows by type, keywords, and patterns
            for workflow_file in workflow_files:
                try:
                    with open(workflow_file, 'r', encoding='utf-8') as f:
                        workflow_data = json.load(f)
                    
                    workflow_id = workflow_data.get('id', workflow_file.stem)
                    
                    # Extract workflow metadata
                    metadata = self._extract_workflow_metadata(workflow_data, workflow_file)
                    
                    self.workflow_catalog[workflow_id] = {
                        "file_path": str(workflow_file),
                        "workflow_data": workflow_data,
                        "metadata": metadata
                    }
                    
                    # Index by category
                    category = metadata.get('category', 'general')
                    if category not in self.workflow_categories:
                        self.workflow_categories[category] = []
                    self.workflow_categories[category].append(workflow_id)
                    
                    # Index by patterns/keywords
                    for keyword in metadata.get('keywords', []):
                        if keyword not in self.workflow_patterns:
                            self.workflow_patterns[keyword] = []
                        self.workflow_patterns[keyword].append(workflow_id)
                        
                except Exception as e:
                    logger.error(f"Error loading workflow {workflow_file}: {e}")
            
            logger.info(f"✅ Indexed {len(self.workflow_catalog)} workflows across {len(self.workflow_categories)} categories")
            
        except Exception as e:
            logger.error(f"Error loading workflow catalog: {e}")
            self._create_sample_catalog()
    
    def _extract_workflow_metadata(self, workflow_data: Dict, workflow_file: Path) -> Dict[str, Any]:
        """Extract searchable metadata from workflow data"""
        metadata = {
            "name": workflow_data.get('name', workflow_file.stem),
            "description": workflow_data.get('description', ''),
            "keywords": [],
            "category": "general",
            "complexity": "medium",
            "node_types": [],
            "services": [],
            "estimated_time": "unknown",
            "requires_user_input": False
        }
        
        # Extract node types and services
        nodes = workflow_data.get('nodes', [])
        for node in nodes:
            node_type = node.get('type', '')
            if node_type:
                metadata["node_types"].append(node_type)
                
                # Determine category based on node types
                if 'email' in node_type.lower():
                    metadata["category"] = "email"
                elif 'http' in node_type.lower() or 'api' in node_type.lower():
                    metadata["category"] = "api"
                elif 'ai' in node_type.lower() or 'openai' in node_type.lower():
                    metadata["category"] = "ai"
                elif 'database' in node_type.lower() or 'sql' in node_type.lower():
                    metadata["category"] = "database"
                elif 'webhook' in node_type.lower():
                    metadata["category"] = "webhook"
        
        # Extract keywords from name and description
        text_content = f"{metadata['name']} {metadata['description']}".lower()
        
        # Common automation keywords
        automation_keywords = [
            'email', 'send', 'notification', 'alert', 'message',
            'api', 'http', 'request', 'webhook', 'integration',
            'data', 'process', 'filter', 'transform', 'export',
            'ai', 'generate', 'analyze', 'summarize', 'translate',
            'schedule', 'trigger', 'automated', 'workflow',
            'customer', 'sales', 'marketing', 'support',
            'report', 'dashboard', 'analytics', 'metrics'
        ]
        
        for keyword in automation_keywords:
            if keyword in text_content:
                metadata["keywords"].append(keyword)
        
        # Determine complexity based on node count
        node_count = len(nodes)
        if node_count <= 3:
            metadata["complexity"] = "simple"
        elif node_count <= 7:
            metadata["complexity"] = "medium"
        else:
            metadata["complexity"] = "complex"
        
        # Check if workflow requires user input
        for node in nodes:
            node_type = node.get('type', '').lower()
            if 'manual' in node_type or 'input' in node_type or 'trigger' in node_type:
                metadata["requires_user_input"] = True
                break
        
        return metadata
    
    def _create_sample_catalog(self):
        """Create sample workflow catalog for demonstration"""
        sample_workflows = {
            "email_welcome": {
                "metadata": {
                    "name": "Welcome Email Automation",
                    "description": "Send personalized welcome emails to new users",
                    "category": "email",
                    "keywords": ["email", "welcome", "automation", "customer"],
                    "complexity": "simple",
                    "node_types": ["manualTrigger", "set", "emailSend"],
                    "requires_user_input": True
                }
            },
            "sales_outreach": {
                "metadata": {
                    "name": "Sales Outreach Campaign",
                    "description": "Automated sales email sequences with follow-ups",
                    "category": "email",
                    "keywords": ["sales", "outreach", "email", "campaign", "follow-up"],
                    "complexity": "medium",
                    "node_types": ["manualTrigger", "set", "emailSend", "wait", "condition"],
                    "requires_user_input": True
                }
            },
            "data_processing": {
                "metadata": {
                    "name": "Data Processing Pipeline",
                    "description": "Process and transform data from multiple sources",
                    "category": "data",
                    "keywords": ["data", "process", "transform", "pipeline"],
                    "complexity": "complex",
                    "node_types": ["httpRequest", "set", "filter", "merge"],
                    "requires_user_input": False
                }
            },
            "ai_content_generation": {
                "metadata": {
                    "name": "AI Content Generation",
                    "description": "Generate content using AI and distribute via multiple channels",
                    "category": "ai",
                    "keywords": ["ai", "content", "generate", "marketing"],
                    "complexity": "medium",
                    "node_types": ["manualTrigger", "openaiChat", "set", "emailSend"],
                    "requires_user_input": True
                }
            }
        }
        
        self.workflow_catalog = sample_workflows
        
        # Build category and pattern indexes
        for workflow_id, workflow in sample_workflows.items():
            metadata = workflow["metadata"]
            
            # Index by category
            category = metadata["category"]
            if category not in self.workflow_categories:
                self.workflow_categories[category] = []
            self.workflow_categories[category].append(workflow_id)
            
            # Index by keywords
            for keyword in metadata["keywords"]:
                if keyword not in self.workflow_patterns:
                    self.workflow_patterns[keyword] = []
                self.workflow_patterns[keyword].append(workflow_id)
    
    async def detect_workflow_intent(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze user input to determine workflow intent and requirements
        """
        logger.info(f"🔍 Analyzing workflow intent for: {user_input[:100]}...")
        
        if not HAS_OPENAI or not self.openai_api_key:
            # Fallback to pattern matching
            return await self._pattern_based_intent_detection(user_input, context)
        
        try:
            client = AsyncOpenAI(api_key=self.openai_api_key)
            
            system_prompt = """You are an expert workflow automation analyst. Analyze user requests to determine:
1. What type of automation they want
2. What specific workflows would be most suitable
3. What parameters they've provided
4. What additional information is needed

WORKFLOW CATEGORIES:
- email: Email automation, notifications, campaigns
- api: API integrations, data fetching, webhooks  
- data: Data processing, transformation, analysis
- ai: AI content generation, analysis, decision making
- scheduling: Time-based triggers, recurring tasks
- customer: Customer management, support, onboarding
- sales: Sales processes, lead management, outreach
- marketing: Marketing campaigns, content distribution

RESPOND IN JSON FORMAT:
{
  "intent_detected": true/false,
  "workflow_category": "email|api|data|ai|scheduling|customer|sales|marketing",
  "workflow_type": "specific workflow description",
  "confidence": 0.0-1.0,
  "extracted_parameters": {
    "recipient_email": "email if found",
    "content_topic": "what content to create",
    "action_type": "send|create|process|analyze|schedule",
    "urgency": "low|medium|high",
    "complexity": "simple|medium|complex"
  },
  "missing_parameters": ["list of what info is needed"],
  "suggested_workflows": ["workflow1", "workflow2", "workflow3"],
  "reasoning": "explanation of analysis"
}"""
            
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze this automation request: {user_input}"}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            try:
                result = json.loads(content)
                logger.info(f"✅ Intent detected: {result.get('workflow_category')} - {result.get('workflow_type')}")
                return result
            except json.JSONDecodeError:
                logger.error(f"Failed to parse AI response: {content}")
                return await self._pattern_based_intent_detection(user_input, context)
                
        except Exception as e:
            logger.error(f"OpenAI intent detection error: {e}")
            return await self._pattern_based_intent_detection(user_input, context)
    
    async def _pattern_based_intent_detection(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fallback pattern-based intent detection"""
        user_lower = user_input.lower()
        
        # Email patterns
        email_patterns = ['send email', 'email', 'message', 'notify', 'alert']
        if any(pattern in user_lower for pattern in email_patterns):
            # Extract email if present
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', user_input)
            extracted_email = email_match.group() if email_match else None
            
            return {
                "intent_detected": True,
                "workflow_category": "email",
                "workflow_type": "email_automation",
                "confidence": 0.8,
                "extracted_parameters": {
                    "recipient_email": extracted_email,
                    "action_type": "send",
                    "urgency": "medium",
                    "complexity": "simple"
                },
                "missing_parameters": ["content_topic"] if not extracted_email else ["recipient_email", "content_topic"],
                "suggested_workflows": ["email_welcome", "sales_outreach"],
                "reasoning": "Email keywords detected in user input"
            }
        
        # AI/Content patterns
        ai_patterns = ['generate', 'create content', 'write', 'ai', 'draft']
        if any(pattern in user_lower for pattern in ai_patterns):
            return {
                "intent_detected": True,
                "workflow_category": "ai",
                "workflow_type": "content_generation",
                "confidence": 0.7,
                "extracted_parameters": {
                    "action_type": "create",
                    "urgency": "medium",
                    "complexity": "medium"
                },
                "missing_parameters": ["content_topic", "output_format"],
                "suggested_workflows": ["ai_content_generation"],
                "reasoning": "AI/content generation keywords detected"
            }
        
        # Default fallback
        return {
            "intent_detected": False,
            "workflow_category": "general",
            "workflow_type": "custom_workflow",
            "confidence": 0.3,
            "extracted_parameters": {},
            "missing_parameters": ["automation_type", "specific_requirements"],
            "suggested_workflows": [],
            "reasoning": "No clear automation intent detected"
        }
    
    async def select_best_workflows(self, intent: Dict[str, Any], limit: int = 3) -> List[Dict[str, Any]]:
        """
        Select the best matching workflows based on detected intent
        """
        category = intent.get('workflow_category', 'general')
        workflow_type = intent.get('workflow_type', '')
        keywords = intent.get('extracted_parameters', {})
        
        logger.info(f"🎯 Selecting workflows for category: {category}, type: {workflow_type}")
        
        # Get workflows from matching category
        candidate_workflows = []
        
        # Primary matches from category
        if category in self.workflow_categories:
            for workflow_id in self.workflow_categories[category]:
                if workflow_id in self.workflow_catalog:
                    workflow = self.workflow_catalog[workflow_id]
                    score = self._calculate_workflow_score(workflow, intent)
                    candidate_workflows.append({
                        "workflow_id": workflow_id,
                        "workflow": workflow,
                        "relevance_score": score,
                        "match_reason": f"Category match: {category}"
                    })
        
        # Secondary matches from keyword patterns
        for keyword in intent.get('extracted_parameters', {}).values():
            if isinstance(keyword, str) and keyword in self.workflow_patterns:
                for workflow_id in self.workflow_patterns[keyword]:
                    if workflow_id in self.workflow_catalog:
                        # Avoid duplicates
                        if not any(cw['workflow_id'] == workflow_id for cw in candidate_workflows):
                            workflow = self.workflow_catalog[workflow_id]
                            score = self._calculate_workflow_score(workflow, intent)
                            candidate_workflows.append({
                                "workflow_id": workflow_id,
                                "workflow": workflow,
                                "relevance_score": score,
                                "match_reason": f"Keyword match: {keyword}"
                            })
        
        # If no matches found, include top general workflows
        if not candidate_workflows:
            logger.warning("No specific workflow matches found, using general workflows")
            for workflow_id, workflow in list(self.workflow_catalog.items())[:5]:
                score = self._calculate_workflow_score(workflow, intent)
                candidate_workflows.append({
                    "workflow_id": workflow_id,
                    "workflow": workflow,
                    "relevance_score": score,
                    "match_reason": "General workflow (no specific match)"
                })
        
        # Sort by relevance score and return top matches
        candidate_workflows.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        selected_workflows = candidate_workflows[:limit]
        
        logger.info(f"✅ Selected {len(selected_workflows)} workflows with scores: {[w['relevance_score'] for w in selected_workflows]}")
        
        return selected_workflows
    
    def _calculate_workflow_score(self, workflow: Dict[str, Any], intent: Dict[str, Any]) -> float:
        """Calculate relevance score for a workflow given the user intent"""
        score = 0.0
        metadata = workflow.get('metadata', {})
        
        # Category match (high weight)
        if metadata.get('category') == intent.get('workflow_category'):
            score += 0.4
        
        # Keyword matches
        intent_text = f"{intent.get('workflow_type', '')} {' '.join(str(v) for v in intent.get('extracted_parameters', {}).values())}"
        workflow_keywords = metadata.get('keywords', [])
        
        for keyword in workflow_keywords:
            if keyword.lower() in intent_text.lower():
                score += 0.1
        
        # Complexity preference (simple workflows preferred for simple requests)
        user_complexity = intent.get('extracted_parameters', {}).get('complexity', 'medium')
        workflow_complexity = metadata.get('complexity', 'medium')
        
        if user_complexity == workflow_complexity:
            score += 0.2
        elif user_complexity == 'simple' and workflow_complexity == 'medium':
            score += 0.1
        
        # User input requirements
        requires_input = metadata.get('requires_user_input', False)
        has_parameters = bool(intent.get('extracted_parameters', {}))
        
        if requires_input and has_parameters:
            score += 0.1
        elif not requires_input and not has_parameters:
            score += 0.1
        
        # Confidence boost
        confidence = intent.get('confidence', 0.5)
        score *= confidence
        
        return min(score, 1.0)  # Cap at 1.0
    
    async def customize_workflow(self, workflow_id: str, user_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Customize a selected workflow with user-provided parameters
        """
        if workflow_id not in self.workflow_catalog:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflow_catalog[workflow_id]
        workflow_data = workflow.get('workflow_data', {})
        
        logger.info(f"🔧 Customizing workflow {workflow_id} with parameters: {user_parameters}")
        
        # Create a copy for customization
        customized_workflow = json.loads(json.dumps(workflow_data))
        
        # Apply parameter substitutions
        customized_workflow = self._apply_parameter_substitutions(customized_workflow, user_parameters)
        
        # Add execution metadata
        customized_workflow['customization'] = {
            "base_workflow": workflow_id,
            "parameters_applied": user_parameters,
            "customized_at": datetime.now().isoformat(),
            "ready_for_execution": True
        }
        
        return customized_workflow
    
    def _apply_parameter_substitutions(self, workflow_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Apply parameter substitutions to workflow data"""
        # Convert to string for easy substitution
        workflow_str = json.dumps(workflow_data)
        
        # Common parameter mappings
        param_mappings = {
            'recipient_email': ['{{recipient}}', '{{email}}', '{{to_email}}'],
            'content_topic': ['{{topic}}', '{{subject}}', '{{content}}'],
            'sender_name': ['{{sender}}', '{{from_name}}'],
            'company_name': ['{{company}}', '{{organization}}']
        }
        
        # Apply substitutions
        for param_key, param_value in parameters.items():
            if param_value and isinstance(param_value, str):
                # Direct substitution
                workflow_str = workflow_str.replace(f'{{{{{param_key}}}}}', param_value)
                
                # Common mappings
                if param_key in param_mappings:
                    for mapping in param_mappings[param_key]:
                        workflow_str = workflow_str.replace(mapping, param_value)
        
        try:
            return json.loads(workflow_str)
        except json.JSONDecodeError:
            logger.error("Failed to parse customized workflow JSON")
            return workflow_data
    
    def get_workflow_summary(self, workflow_id: str) -> Dict[str, Any]:
        """Get a human-readable summary of a workflow"""
        if workflow_id not in self.workflow_catalog:
            return {"error": "Workflow not found"}
        
        workflow = self.workflow_catalog[workflow_id]
        metadata = workflow.get('metadata', {})
        
        return {
            "name": metadata.get('name', workflow_id),
            "description": metadata.get('description', 'No description available'),
            "category": metadata.get('category', 'general'),
            "complexity": metadata.get('complexity', 'unknown'),
            "estimated_steps": len(metadata.get('node_types', [])),
            "requires_user_input": metadata.get('requires_user_input', False),
            "keywords": metadata.get('keywords', [])
        }

# Integration function for CustomMCPLLM
async def enhance_mcp_with_workflow_selection(mcp_engine, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Enhance CustomMCPLLM with intelligent workflow selection capabilities
    """
    try:
        # Initialize workflow selector
        selector = WorkflowSelector(openai_api_key=mcp_engine.openai_api_key)
        
        # Detect workflow intent
        intent = await selector.detect_workflow_intent(user_input, context)
        
        if not intent.get('intent_detected'):
            # No workflow intent detected, proceed with normal MCP processing
            return {"workflow_selection": False, "reason": "No automation intent detected"}
        
        # Select best matching workflows
        suggested_workflows = await selector.select_best_workflows(intent, limit=3)
        
        if not suggested_workflows:
            # No suitable workflows found, let MCP create custom workflow
            return {"workflow_selection": False, "reason": "No suitable workflows found"}
        
        # Prepare workflow options for user
        workflow_options = []
        for suggestion in suggested_workflows:
            workflow_id = suggestion['workflow_id']
            summary = selector.get_workflow_summary(workflow_id)
            
            workflow_options.append({
                "workflow_id": workflow_id,
                "name": summary['name'],
                "description": summary['description'],
                "complexity": summary['complexity'],
                "relevance_score": suggestion['relevance_score'],
                "match_reason": suggestion['match_reason'],
                "estimated_steps": summary['estimated_steps'],
                "requires_input": summary['requires_user_input']
            })
        
        # If high confidence and good match, auto-select top workflow
        top_workflow = suggested_workflows[0]
        if (intent.get('confidence', 0) > 0.8 and 
            top_workflow['relevance_score'] > 0.7 and
            len(intent.get('missing_parameters', [])) == 0):
            
            # Auto-customize and execute workflow
            customized_workflow = await selector.customize_workflow(
                top_workflow['workflow_id'],
                intent.get('extracted_parameters', {})
            )
            
            return {
                "workflow_selection": True,
                "auto_selected": True,
                "selected_workflow": top_workflow['workflow_id'],
                "customized_workflow": customized_workflow,
                "intent": intent,
                "confidence": intent.get('confidence'),
                "reasoning": f"High confidence match: {top_workflow['match_reason']}"
            }
        
        # Present options to user for selection
        return {
            "workflow_selection": True,
            "auto_selected": False,
            "workflow_options": workflow_options,
            "intent": intent,
            "user_action_required": "select_workflow",
            "message": f"I found {len(workflow_options)} workflows that match your request. Which one would you like to use?",
            "missing_parameters": intent.get('missing_parameters', [])
        }
        
    except Exception as e:
        logger.error(f"Workflow selection enhancement error: {e}")
        return {"workflow_selection": False, "error": str(e)}

if __name__ == "__main__":
    # Test workflow selection
    async def test_workflow_selection():
        selector = WorkflowSelector()
        
        test_inputs = [
            "Send a welcome email to john@example.com",
            "Create a sales outreach campaign for our new product",
            "Generate AI content about blockchain technology",
            "Process customer data from our CRM"
        ]
        
        for user_input in test_inputs:
            print(f"\n🧪 Testing: {user_input}")
            intent = await selector.detect_workflow_intent(user_input)
            print(f"   Intent: {intent.get('workflow_category')} - {intent.get('workflow_type')}")
            
            workflows = await selector.select_best_workflows(intent)
            print(f"   Suggested workflows: {[w['workflow_id'] for w in workflows]}")
    
    asyncio.run(test_workflow_selection())
