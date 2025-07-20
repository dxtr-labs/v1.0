# backend/api/agent/create_agent.py

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid

from backend.db.session import get_db
from backend.db.models import VirtualAgent, User
from backend.core.dependencies import get_current_user

create_agent_router = APIRouter()

@create_agent_router.post("/create")
async def create_agent(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data = await request.json()

    name = data.get("name")
    role = data.get("role")
    mode = data.get("mode")  # "single" or "multi"
    personality = data.get("personality", {})
    llm_config = data.get("llm_config", {
        "model": "deepseek-v2",
        "temperature": 0.7,
        "tools": ["emailSend", "httpRequest", "if", "cron"]
    })

    if not name or not role or mode not in ("single", "multi"):
        raise HTTPException(status_code=400, detail="Missing required fields")

    agent = VirtualAgent(
        agent_id=uuid.uuid4(),
        user_id=current_user.user_id,
        name=name,
        role=role,
        mode=mode,
        status="active",
        personality=personality,
        llm_config=llm_config,
        created_at=datetime.utcnow()
    )
    db.add(agent)
    await db.commit()

    return { "message": "Agent created", "agent_id": str(agent.agent_id) }
