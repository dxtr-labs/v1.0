from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from uuid import UUID
from typing import List
from backend.db import get_db
from sqlalchemy.orm import Session
from backend.models import VirtualAgent  # your SQLAlchemy model

router = APIRouter()

# Pydantic model for creating a new agent
class AgentCreateRequest(BaseModel):
    user_id: UUID
    name: str
    role: str
    mode: str = "single"
    personality: dict = {}
    llm_config: dict = {}

# GET /agents?user_id=...
@router.get("/", response_model=List[dict])
def get_agents(user_id: UUID, db: Session = Depends(get_db)):
    agents = db.query(VirtualAgent).filter_by(UserID=user_id).all()
    return [agent.to_dict() for agent in agents]

# POST /agents/create
@router.post("/create")
def create_agent(request: AgentCreateRequest, db: Session = Depends(get_db)):
    new_agent = VirtualAgent(
        UserID=request.user_id,
        name=request.name,
        role=request.role,
        mode=request.mode,
        personality=request.personality,
        llm_config=request.llm_config
    )
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    return {"success": True, "agent_id": str(new_agent.AgentID)}

# GET /agents/{agent_id}
@router.get("/{agent_id}")
def get_agent(agent_id: UUID, db: Session = Depends(get_db)):
    agent = db.query(VirtualAgent).filter_by(AgentID=agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent.to_dict()

# DELETE /agents/{agent_id}
@router.delete("/{agent_id}")
def delete_agent(agent_id: UUID, db: Session = Depends(get_db)):
    agent = db.query(VirtualAgent).filter_by(AgentID=agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    db.delete(agent)
    db.commit()
    return {"success": True}
