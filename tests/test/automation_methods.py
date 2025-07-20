import time
import json
import logging

logger = logging.getLogger(__name__)

async def create_email_automation_with_context(self, user_input: str, automation_result: dict, enriched_context: dict) -> dict:
    """Create email automation with enriched context"""
    try:
        # Build context string for AI
        context_str = self._build_context_string_for_ai(enriched_context)
        
        # Basic email automation structure
        workflow_json = {
            "workflow_type": "email_automation",
            "status": "automation_ready", 
            "workflow_id": f"email_auto_{int(time.time())}",
            "steps": [
                {
                    "action": "send_email",
                    "parameters": {
                        "to": automation_result.get("target_recipient", "recipient@email.com"),
                        "subject": f"Email from {enriched_context.get('company_info', {}).get('company_name', 'DXTR Labs')}",
                        "content": f"Hello,\n\nThis is regarding: {user_input}\n\nContext: {context_str}\n\nBest regards,\n{self.agent_data.get('agent_name', 'AI Assistant')}",
                        "from_name": self.agent_data.get('agent_name', 'AI Assistant'),
                        "sender_email": "noreply@dxtrlabs.com",
                        "email_type": "business"
                    }
                }
            ],
            "estimated_execution_time": "2 minutes",
            "requires_approval": True,
            "automation_summary": f"Email automation: {automation_result.get('specific_action', 'Send email')}"
        }
        
        workflow_id = workflow_json["workflow_id"]
        self._store_workflow_in_memory(workflow_id, workflow_json, user_input)
        
        return {
            "success": True,
            "status": "automation_ready",
            "message": f"✅ Email automation created: {workflow_json['automation_summary']}",
            "response": f"I've created a personalized email automation using your context. {workflow_json['automation_summary']}",
            "workflow_json": workflow_json,
            "hasWorkflowJson": True,
            "hasWorkflowPreview": True,
            "workflow_preview": self._create_workflow_preview(workflow_json),
            "done": True
        }
        
    except Exception as e:
        logger.error(f"❌ Email automation with context error: {e}")
        return await self._create_helpful_conversational_response(user_input)

def build_context_string_for_ai(enriched_context: dict) -> str:
    """Build a context string for AI to use in automation"""
    context_parts = []
    
    try:
        # Company information
        company_info = enriched_context.get('company_info', {})
        if company_info.get('company_name'):
            context_parts.append(f"Company: {company_info['company_name']}")
        if company_info.get('business_type'):
            context_parts.append(f"Business: {company_info['business_type']}")
        if company_info.get('products_services'):
            products = ', '.join(company_info['products_services'][:3])
            context_parts.append(f"Products/Services: {products}")
        
        # Personal information
        personal_info = enriched_context.get('personal_info', {})
        if personal_info.get('email_addresses'):
            context_parts.append(f"Contact emails: {', '.join(personal_info['email_addresses'])}")
        
        # Communication style
        comm_style = enriched_context.get('communication_style', {})
        if comm_style.get('tone'):
            context_parts.append(f"Preferred tone: {comm_style['tone']}")
        
        # Project context
        project_context = enriched_context.get('project_context', {})
        if project_context.get('current_project'):
            context_parts.append(f"Current project: {project_context['current_project']}")
        
        return " | ".join(context_parts) if context_parts else "No specific context available"
        
    except Exception as e:
        logger.error(f"❌ Failed to build context string: {e}")
        return "Context unavailable"
