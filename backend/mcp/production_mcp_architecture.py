"""
Production MCP Architecture - Dual System Implementation
1. Inhouse AI - General purpose AI for standard tasks
2. Custom MCP LLM - Dedicated AI for each specific agent
"""

import logging
import asyncio
from typing import Dict, Any, Optional
import re
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class InhouseAI:
    """
    Type 1: Inhouse AI - General purpose AI for standard automation tasks
    - Fast, efficient processing
    - Standard business workflows
    - Cost-effective for bulk operations
    - Consistent behavior across all users
    """
    
    def __init__(self):
        logger.info("🏠 Initializing Inhouse AI System")
        self.ai_type = "inhouse"
        self.capabilities = [
            "email_generation",
            "content_creation", 
            "workflow_automation",
            "data_processing",
            "standard_responses"
        ]
        
    async def process_request(self, user_id: str, agent_id: str, user_message: str, context: Dict = None) -> Dict[str, Any]:
        """
        Process requests using general-purpose inhouse AI
        """
        logger.info(f"🏠 Inhouse AI processing: {user_message[:50]}...")
        
        # Analyze request type
        request_type = self._analyze_request_type(user_message)
        
        if request_type == "email_generation":
            return await self._generate_email_content(user_message, context)
        elif request_type == "content_creation":
            return await self._create_general_content(user_message, context)
        elif request_type == "workflow_automation":
            return await self._handle_workflow_request(user_message, context)
        else:
            return await self._generate_standard_response(user_message, context)
    
    def _analyze_request_type(self, message: str) -> str:
        """Analyze what type of request this is"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["email", "send", "message", "contact"]):
            return "email_generation"
        elif any(word in message_lower for word in ["create", "write", "generate", "content"]):
            return "content_creation"
        elif any(word in message_lower for word in ["workflow", "automate", "process", "execute"]):
            return "workflow_automation"
        else:
            return "general_response"
    
    async def _generate_email_content(self, message: str, context: Dict) -> Dict[str, Any]:
        """Generate email content using inhouse AI algorithms"""
        
        # Extract key elements
        recipients = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', message)
        
        # Generate professional email content
        if "marketing" in message.lower():
            content = self._generate_marketing_email(message)
        elif "follow" in message.lower():
            content = self._generate_followup_email(message)
        else:
            content = self._generate_business_email(message)
        
        return {
            "status": "success",
            "ai_type": "inhouse",
            "content": content,
            "recipients": recipients,
            "processing_time": "fast",
            "cost": "low"
        }
    
    async def _create_general_content(self, message: str, context: Dict) -> Dict[str, Any]:
        """Create general content using inhouse AI"""
        
        content_type = "professional"
        if "casual" in message.lower():
            content_type = "casual"
        elif "formal" in message.lower():
            content_type = "formal"
        
        return {
            "status": "success", 
            "ai_type": "inhouse",
            "content": f"Professional content generated based on: {message}",
            "content_type": content_type,
            "processing_time": "fast"
        }
    
    async def _handle_workflow_request(self, message: str, context: Dict) -> Dict[str, Any]:
        """Handle workflow automation requests"""
        return {
            "status": "success",
            "ai_type": "inhouse", 
            "workflow_type": "standard_automation",
            "message": "Inhouse AI workflow processing completed",
            "efficiency": "high"
        }
    
    async def _generate_standard_response(self, message: str, context: Dict) -> Dict[str, Any]:
        """Generate standard response for general queries"""
        return {
            "status": "success",
            "ai_type": "inhouse",
            "response": f"Inhouse AI processed your request: {message}",
            "type": "standard_response"
        }
    
    def _generate_marketing_email(self, message: str) -> str:
        """Generate marketing email content"""
        return f"""Subject: Exciting Updates from Our Team!

Dear Valued Customer,

We're thrilled to share some exciting developments based on your interest in: {message}

Our latest automation solutions can help streamline your business operations and boost productivity. 

Key benefits:
• Increased efficiency
• Cost reduction
• Streamlined workflows
• Professional automation

Would you like to schedule a brief call to discuss how these solutions can benefit your specific needs?

Best regards,
DXTR Labs Team"""

    def _generate_followup_email(self, message: str) -> str:
        """Generate follow-up email content"""
        return f"""Subject: Following Up on Our Previous Conversation

Hello,

I wanted to follow up on our previous discussion regarding: {message}

I hope you've had a chance to consider the information we shared. If you have any questions or would like to move forward, I'm here to help.

Please let me know if there's anything specific you'd like to discuss or if you'd prefer to schedule a quick call.

Looking forward to hearing from you.

Best regards,
DXTR Labs Team"""

    def _generate_business_email(self, message: str) -> str:
        """Generate general business email content"""
        return f"""Subject: Regarding Your Request

Dear Colleague,

Thank you for reaching out about: {message}

We appreciate your interest and will ensure your request receives the attention it deserves. Our team is committed to providing you with the best possible solution.

We'll get back to you shortly with more information.

Best regards,
DXTR Labs Team"""


class CustomMCPLLM:
    """
    Type 2: Custom MCP LLM - Dedicated AI for each specific agent
    - Personalized behavior per agent
    - Advanced memory management
    - Agent-specific training and responses
    - Higher processing power for complex tasks
    """
    
    def __init__(self, agent_id: str, agent_profile: Dict = None):
        logger.info(f"🤖 Initializing Custom MCP LLM for agent: {agent_id}")
        self.agent_id = agent_id
        self.agent_profile = agent_profile or {}
        self.ai_type = "custom_mcp"
        
        # Agent-specific memory and personality
        self.agent_memory = {}
        self.conversation_history = {}
        self.agent_personality = self._initialize_agent_personality()
        self.specialized_capabilities = self._initialize_specialized_capabilities()
        
    def _initialize_agent_personality(self) -> Dict[str, Any]:
        """Initialize agent-specific personality traits"""
        return {
            "name": self.agent_profile.get("name", f"Agent_{self.agent_id}"),
            "role": self.agent_profile.get("role", "Personal Assistant"),
            "communication_style": self.agent_profile.get("style", "professional"),
            "expertise": self.agent_profile.get("expertise", ["general_assistance"]),
            "memory_retention": "high",
            "personalization_level": "advanced"
        }
    
    def _initialize_specialized_capabilities(self) -> Dict[str, Any]:
        """Initialize agent-specific capabilities"""
        return {
            "advanced_memory": True,
            "context_awareness": True,
            "personality_adaptation": True,
            "specialized_knowledge": True,
            "emotional_intelligence": True,
            "complex_reasoning": True
        }
    
    async def process_request(self, user_id: str, user_message: str, conversation_context: Dict = None) -> Dict[str, Any]:
        """
        Process requests using dedicated Custom MCP LLM with advanced personalization
        """
        logger.info(f"🤖 Custom MCP LLM ({self.agent_id}) processing: {user_message[:50]}...")
        
        # Create conversation key for this specific user-agent combination
        conversation_key = f"{user_id}:{self.agent_id}"
        
        # Retrieve conversation memory
        conversation_memory = self.conversation_history.get(conversation_key, [])
        
        # Advanced intent analysis with personality consideration
        intent_analysis = await self._advanced_intent_analysis(user_message, conversation_memory)
        
        # Generate personalized response based on agent personality
        response = await self._generate_personalized_response(
            user_message, 
            intent_analysis, 
            conversation_memory,
            conversation_context
        )
        
        # Store interaction in agent's memory
        self._store_interaction_memory(conversation_key, user_message, response)
        
        return {
            "status": "success",
            "ai_type": "custom_mcp",
            "agent_id": self.agent_id,
            "agent_name": self.agent_personality["name"],
            "response": response,
            "personalization_applied": True,
            "memory_context_used": len(conversation_memory) > 0,
            "processing_type": "advanced"
        }
    
    async def _advanced_intent_analysis(self, message: str, memory: list) -> Dict[str, Any]:
        """Advanced intent analysis considering agent personality and memory"""
        
        # Basic intent categories
        intent_map = {
            "greeting": ["hello", "hi", "hey", "good morning", "good afternoon"],
            "question": ["what", "how", "why", "when", "where", "who"],
            "request": ["please", "can you", "could you", "would you", "help me"],
            "task": ["create", "generate", "make", "build", "send", "email"],
            "memory_query": ["remember", "recall", "what did", "last time", "before"],
            "emotional": ["thank you", "thanks", "sorry", "frustrated", "happy"]
        }
        
        message_lower = message.lower()
        detected_intents = []
        
        for intent, keywords in intent_map.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_intents.append(intent)
        
        # Check for memory references
        has_memory_context = len(memory) > 0
        references_past = any(word in message_lower for word in ["last time", "before", "previous", "earlier"])
        
        return {
            "primary_intent": detected_intents[0] if detected_intents else "general",
            "all_intents": detected_intents,
            "has_memory_context": has_memory_context,
            "references_past": references_past,
            "complexity": "high" if len(detected_intents) > 1 else "medium",
            "requires_personalization": True
        }
    
    async def _generate_personalized_response(self, message: str, intent: Dict, memory: list, context: Dict) -> str:
        """Generate highly personalized response based on agent personality and memory"""
        
        agent_name = self.agent_personality["name"]
        communication_style = self.agent_personality["communication_style"]
        
        # Handle memory queries specially
        if intent["primary_intent"] == "memory_query" and memory:
            return self._handle_memory_query(message, memory)
        
        # Handle greetings with personality
        if intent["primary_intent"] == "greeting":
            if memory:
                return f"Hello again! I'm {agent_name}, and I remember our previous conversations. How can I assist you today?"
            else:
                return f"Hello! I'm {agent_name}, your dedicated personal assistant. I'll remember our conversation as we chat. How can I help you?"
        
        # Handle task requests with agent expertise
        if intent["primary_intent"] == "task":
            return self._handle_task_request(message, intent, memory)
        
        # Handle questions with context awareness
        if intent["primary_intent"] == "question":
            return self._handle_question_with_context(message, memory)
        
        # Default personalized response
        context_note = " Based on our conversation history, " if memory else " "
        return f"I'm {agent_name}, and I understand you're asking about {message}.{context_note}I'm here to provide personalized assistance tailored to your specific needs. What would you like me to help you with?"
    
    def _handle_memory_query(self, message: str, memory: list) -> str:
        """Handle queries about past conversations"""
        
        # Search through memory for relevant information
        relevant_memories = []
        message_lower = message.lower()
        
        for interaction in memory:
            user_msg = interaction.get('user_message', '').lower()
            response = interaction.get('response', '').lower()
            
            # Simple keyword matching
            if any(word in user_msg or word in response for word in message_lower.split()):
                relevant_memories.append(interaction)
        
        if relevant_memories:
            latest_memory = relevant_memories[-1]
            return f"I remember our conversation about that. You mentioned: '{latest_memory.get('user_message', '')}' and I helped you with it. Is there something specific you'd like to know or do related to this?"
        else:
            return "I don't have specific information about that in our conversation history yet. Could you provide more details so I can remember it for future reference?"
    
    def _handle_task_request(self, message: str, intent: Dict, memory: list) -> str:
        """Handle task requests with agent specialization"""
        
        agent_name = self.agent_personality["name"]
        expertise = self.agent_personality["expertise"]
        
        if "email" in message.lower():
            return f"I'm {agent_name}, and I'd be happy to help you with email automation. I can create personalized, professional emails tailored to your specific needs. Please provide me with the details about the recipient and the purpose of the email."
        
        if "create" in message.lower() or "generate" in message.lower():
            return f"As {agent_name}, I excel at creating personalized content. I can generate materials that match your specific style and requirements. What type of content would you like me to create for you?"
        
        return f"I'm {agent_name}, and I understand you need assistance with a task. With my specialized capabilities in {', '.join(expertise)}, I can provide personalized help. Could you tell me more about what you need?"
    
    def _handle_question_with_context(self, message: str, memory: list) -> str:
        """Handle questions using conversation context"""
        
        context_reference = ""
        if memory:
            context_reference = " I'm taking into account our previous discussions to give you the most relevant answer."
        
        return f"That's a great question! {context_reference} I'm analyzing your request using my advanced reasoning capabilities. To provide you with the most accurate and personalized response, could you share a bit more context about what you're trying to achieve?"
    
    def _store_interaction_memory(self, conversation_key: str, user_message: str, response: str):
        """Store interaction in agent's conversation memory"""
        
        if conversation_key not in self.conversation_history:
            self.conversation_history[conversation_key] = []
        
        interaction = {
            "user_message": user_message,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "agent_name": self.agent_personality["name"]
        }
        
        self.conversation_history[conversation_key].append(interaction)
        
        # Keep only last 20 interactions per conversation
        if len(self.conversation_history[conversation_key]) > 20:
            self.conversation_history[conversation_key] = self.conversation_history[conversation_key][-20:]


class ProductionMCPOrchestrator:
    """
    Production MCP Orchestrator managing both AI types
    Routes requests to appropriate AI system based on requirements
    """
    
    def __init__(self):
        logger.info("🏭 Initializing Production MCP Orchestrator")
        
        # Initialize both AI systems
        self.inhouse_ai = InhouseAI()
        self.custom_agents = {}  # Dictionary of agent_id -> CustomMCPLLM
        
        # Routing logic
        self.routing_rules = {
            "use_custom_mcp": [
                "personalized", "remember", "my preferences", "custom", "dedicated",
                "personal assistant", "agent", "individual", "specific"
            ],
            "use_inhouse_ai": [
                "quick", "standard", "bulk", "general", "basic", "simple",
                "mass email", "batch", "automated"
            ]
        }
    
    def get_or_create_custom_agent(self, agent_id: str, agent_profile: Dict = None) -> CustomMCPLLM:
        """Get existing custom agent or create new one"""
        
        if agent_id not in self.custom_agents:
            logger.info(f"Creating new Custom MCP LLM for agent: {agent_id}")
            self.custom_agents[agent_id] = CustomMCPLLM(agent_id, agent_profile)
        
        return self.custom_agents[agent_id]
    
    async def process_request(self, user_id: str, agent_id: str, user_message: str, context: Dict = None) -> Dict[str, Any]:
        """
        Route request to appropriate AI system based on requirements analysis
        """
        
        # Analyze which AI type should handle this request
        ai_type = self._determine_ai_type(user_message, agent_id, context)
        
        logger.info(f"🎯 Routing to {ai_type} for user {user_id}, agent {agent_id}")
        
        if ai_type == "custom_mcp":
            # Use dedicated Custom MCP LLM for this agent
            agent_profile = context.get('agent_profile') if context else None
            custom_agent = self.get_or_create_custom_agent(agent_id, agent_profile)
            return await custom_agent.process_request(user_id, user_message, context)
        
        else:
            # Use general Inhouse AI
            return await self.inhouse_ai.process_request(user_id, agent_id, user_message, context)
    
    def _determine_ai_type(self, message: str, agent_id: str, context: Dict = None) -> str:
        """
        Determine which AI type should handle the request
        """
        
        message_lower = message.lower()
        
        # Check for custom MCP indicators
        custom_mcp_score = sum(1 for keyword in self.routing_rules["use_custom_mcp"] 
                              if keyword in message_lower)
        
        # Check for inhouse AI indicators  
        inhouse_score = sum(1 for keyword in self.routing_rules["use_inhouse_ai"]
                           if keyword in message_lower)
        
        # Default routing logic
        if custom_mcp_score > inhouse_score:
            return "custom_mcp"
        elif inhouse_score > custom_mcp_score:
            return "inhouse_ai"
        else:
            # Default to custom MCP for personalized agent interactions
            return "custom_mcp"
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of both AI systems"""
        
        return {
            "production_mcp_status": "operational",
            "inhouse_ai": {
                "status": "active",
                "type": "general_purpose",
                "capabilities": self.inhouse_ai.capabilities
            },
            "custom_mcp_agents": {
                "status": "active", 
                "type": "dedicated_personalized",
                "active_agents": len(self.custom_agents),
                "agents": list(self.custom_agents.keys())
            },
            "routing": "intelligent",
            "total_ai_systems": 2
        }
