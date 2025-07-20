# 📂 backend/api/agents/create_agent.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from db.session import get_db
from db import models
from .model import AgentCreate, AgentOut, AgentUpdate

router = APIRouter(prefix="/agents", tags=["agents"])

# ➕ Create new agent
@router.post("/create", response_model=AgentOut)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    db_agent = models.Agent(
        name=agent.name,
        personality=agent.personality,
        memory=agent.memory,
        preferences=agent.preferences,
        user_id=None  # Replace with actual user from session later
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

# 📄 Get agent by ID
@router.get("/get/{agent_id}", response_model=AgentOut)
def get_agent(agent_id: UUID, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

# 🔁 Update agent fields
@router.put("/update/{agent_id}", response_model=AgentOut)
def update_agent(agent_id: UUID, agent_update: AgentUpdate, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if agent_update.personality is not None:
        agent.personality = agent_update.personality
    if agent_update.memory is not None:
        agent.memory = agent_update.memory
    if agent_update.preferences is not None:
        agent.preferences = agent_update.preferences

    db.commit()
    db.refresh(agent)
    return agent
