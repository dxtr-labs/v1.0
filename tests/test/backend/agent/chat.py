# 📂 backend/agent/chat.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.db.queries import get_agent_by_id, update_agent_memory
from backend.core.llm_router import ask_mcp
from pydantic import BaseModel
import uuid

router = APIRouter()

# 🧠 Input schema for chat
class ChatRequest(BaseModel):
    agent_id: uuid.UUID
    user_id: uuid.UUID
    message: str

# 🧠 Output schema for response
class ChatResponse(BaseModel):
    agent_id: uuid.UUID
    user_message: str
    agent_reply: str
    updated_memory: list


@router.post("/agents/chat", response_model=ChatResponse)
def chat_with_agent(payload: ChatRequest, db: Session = Depends(get_db)):
    # 1. Load the agent
    agent = get_agent_by_id(db, payload.agent_id)
    if not agent or str(agent.user_id) != str(payload.user_id):
        raise HTTPException(status_code=404, detail="Agent not found or not authorized.")

    # 2. Append user message to memory
    memory = agent.memory or []
    memory.append({"role": "user", "content": payload.message})

    # 3. Ask MCP LLM with memory context
    reply = ask_mcp(memory=memory)

    # 4. Append LLM reply to memory
    memory.append({"role": "agent", "content": reply})

    # 5. Save updated memory
    update_agent_memory(db, agent.id, memory)

    return ChatResponse(
        agent_id=agent.id,
        user_message=payload.message,
        agent_reply=reply,
        updated_memory=memory
    )
