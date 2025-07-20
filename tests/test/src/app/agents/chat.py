from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from backend.db import get_session
from backend.mcp.mcp_router import query_mcp  # hypothetical call
from backend.models import AgentMemory, VirtualAgent, UserRequest

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    agent_id: str
    message: str

@router.post("/stream")
async def chat_with_agent(data: ChatRequest):
    session = get_session()
    agent = session.query(VirtualAgent).filter_by(AgentID=data.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Load or create memory
    memory = session.query(AgentMemory).filter_by(UserID=data.user_id, AgentID=data.agent_id).first()
    if not memory:
        memory = AgentMemory(UserID=data.user_id, AgentID=data.agent_id, message_history=[])
        session.add(memory)

    # Build prompt from memory
    conversation = memory.message_history or []
    conversation.append({"role": "user", "content": data.message})

    # Call MCP-LLM (stream optionally)
    response = await query_mcp(agent.llm_config, conversation, personality=agent.personality)

    # Update memory
    conversation.append({"role": "assistant", "content": response["content"]})
    memory.message_history = conversation
    memory.iteration += 1
    session.commit()

    return {
        "reply": response["content"],
        "tokens_used": response.get("tokens", 0)
    }
