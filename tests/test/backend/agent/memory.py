# 📂 backend/api/agents/memory.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Dict, Any

from backend.db.session import get_db
from backend.db import queries

router = APIRouter()


@router.get("/agents/{agent_id}/memory")
def get_agent_memory(agent_id: UUID, db: Session = Depends(get_db)):
    memory = queries.get_memory_for_agent(db, agent_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found for agent.")
    return {
        "agent_id": str(memory.AgentID),
        "iteration": memory.iteration,
        "message_history": memory.message_history,
        "last_updated": memory.last_updated
    }


@router.post("/agents/{agent_id}/memory/update")
def update_agent_memory(agent_id: UUID, payload: Dict[str, Any], db: Session = Depends(get_db)):
    user_id = UUID(payload.get("user_id"))
    messages = payload.get("message_history")

    if not isinstance(messages, list):
        raise HTTPException(status_code=400, detail="message_history must be a list.")

    queries.update_memory(db, agent_id=agent_id, user_id=user_id, message_history=messages)
    return {"status": "ok", "message": "Memory updated."}


@router.delete("/agents/{agent_id}/memory")
def clear_agent_memory(agent_id: UUID, db: Session = Depends(get_db)):
    memory = queries.get_memory_for_agent(db, agent_id)
    if not memory:
        raise HTTPException(status_code=404, detail="No memory to delete.")
    db.delete(memory)
    db.commit()
    return {"status": "ok", "message": "Memory cleared."}
