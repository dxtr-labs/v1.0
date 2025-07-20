# backend/api/chat/chat.py
# MCP-powered Agent Chat → streams reply + builds workflow when needed

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from backend.mcp.workflow_builder import WorkflowBuilder
from backend.mcp.prompt_builder import FastMCPPromptBuilder
from backend.db.queries import get_agent_by_id, update_agent_memory
from backend.core.llm_router import stream_llm_response
import json

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: Request):
    body = await request.json()
    user_id = body.get("user_id")
    agent_id = body.get("agent_id")
    user_input = body.get("message")

    agent = get_agent_by_id(agent_id)
    memory = agent.get("memory", [])
    system_prompt = FastMCPPromptBuilder.build_agent_system_prompt(agent)

    chat_history = memory + [
        {"role": "user", "content": user_input}
    ]

    async def stream():
        buffer = ""
        async for chunk in stream_llm_response(system_prompt, chat_history):
            yield chunk
            buffer += chunk

        # Try building automation if AI replied with task logic
        if "create a workflow" in buffer or "automation" in buffer.lower():
            workflow = WorkflowBuilder.try_parse_and_build(buffer)
            if workflow:
                yield "\n\n[Workflow JSON]:\n"
                yield json.dumps(workflow, indent=2)

    # Update memory
    update_agent_memory(agent_id, user_id, chat_history)
    return StreamingResponse(stream(), media_type="text/plain")
