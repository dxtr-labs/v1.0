# backend/core/prompt_builder.py
# Custom FastMCP Prompts for Agent Interactions

from typing import Dict, Any

class FastMCPPromptBuilder:
    """
    Builder class for creating custom FastMCP prompts based on agent configuration
    and user requirements.
    """

    @staticmethod
    def build_agent_system_prompt(agent_config: Dict[str, Any]) -> str:
        name = agent_config.get("name", "Assistant")
        role = agent_config.get("role", "helper")
        personality = agent_config.get("personality", {})

        base_prompt = f"""You are {name}, a specialized {role} agent with FastMCP capabilities.

Your core responsibilities:
1. Understand user requests and analyze their automation needs
2. Detect when workflows or automations are needed
3. Generate appropriate n8n workflow JSON (dev mode) or send directly to Automation Engine (production)
4. Fix any broken workflows using feedback/errors from the engine
5. Provide clear, helpful responses tailored to your role as a {role}

Agent Personality: {personality if isinstance(personality, str) else 'Professional and helpful'}
"""

        role_prompts = FastMCPPromptBuilder.get_role_specific_prompts(role)
        if role_prompts:
            base_prompt += f"\n\nRole-Specific Guidelines:\n{role_prompts}"

        workflow_prompts = FastMCPPromptBuilder.get_workflow_detection_prompts()
        base_prompt += f"\n\n{workflow_prompts}"

        return base_prompt

    @staticmethod
    def get_role_specific_prompts(role: str) -> str:
        role_prompts = {
            "Customer Support": """
- Automate repetitive support tasks
- Suggest workflows for ticketing, email replies, or alerts
            """,
            "Marketing": """
- Automate email campaigns, lead capture, and CRM updates
- Recommend workflows for scheduling posts, tracking performance
            """,
            "Sales": """
- Build workflows for lead intake, follow-up reminders
- Suggest CRM integrations, WhatsApp/SMS follow-ups
            """,
            "Project Manager": """
- Connect task tools, automate daily standup reports
- Suggest deadline alerts or reporting triggers
            """,
            "Data Analysis": """
- Automate database queries and reporting pipelines
- Trigger chart generation or alerts on thresholds
            """,
            "Content Creator": """
- Automate content scheduling and backups
- Suggest workflows for YouTube/Instagram publishing
            """
        }
        return role_prompts.get(role, "")

    @staticmethod
    def get_workflow_detection_prompts() -> str:
        return """
WORKFLOW DETECTION GUIDELINES:

Always convert the user input into a JSON-based n8n automation that:
- Includes a Trigger node (manual, cron, webhook, etc.)
- Adds Action or Logic nodes (email, HTTP request, conditionals, etc.)
- Connects nodes using proper `connections` structure
- Uses required parameters from n8n node specs

### Valid Node Types:
- Trigger Nodes: Cron, Webhook, Email Trigger
- Logic Nodes: If, Set, Merge, Code
- Action Nodes: HTTP Request, Email Send, Database Write
- Integration Nodes: Google Sheets, Slack, GitHub, Drive, S3, Twilio

Always include full `parameters`, `type`, and `name` in each node. Return JSON if in dev mode.
        """

    @staticmethod
    def build_workflow_generation_prompt(user_input: str, agent_config: Dict[str, Any]) -> str:
        agent_name = agent_config.get("name", "Assistant")

        return f"""
As {agent_name}, analyze the following user request:
"{user_input}"

And convert it into a complete `n8n` JSON workflow that can be run directly.

REQUIREMENTS:
1. Include a `trigger` node (manual, cron, webhook, etc.)
2. Add all required action nodes
3. Link nodes in correct order using `connections`
4. Include full node `parameters`, `type`, and `name`
5. Output JSON that matches n8n schema
6. Assume production mode: send JSON to backend engine (or display in dev)

Ensure this JSON works with our Automation Engine.
        """

    @staticmethod
    def build_error_handling_prompt() -> str:
        return """
If the Automation Engine reports an error:
1. Inspect which node or connection failed
2. Respond with a fix: either config update or logic change
3. Regenerate the JSON workflow with corrections
4. Re-run or ask user for more info if needed
5. Ensure final workflow runs without error
        """

FASTMCP_TEMPLATES = {
    "workflow_request": """
Let's create a workflow.

Please answer:
1. What triggers the workflow? (time-based, webhook, manual)
2. What should happen after that?
3. Any external services to connect? (Google, Slack, etc.)
4. What should be the final result/output?
    """,

    "clarification_needed": """
I need a bit more detail to build this automation.
- [Ask about missing node, trigger, or logic]
Once I have that, I’ll generate the workflow JSON for you.
    """,

    "workflow_generated": """
✅ Here's your automation JSON (for dev/debug):

```json
{{workflow_json}}
```

Would you like to run this now in the Automation Engine?
    """
}
