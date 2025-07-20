# 📂 backend/api/agents/model.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
from uuid import UUID

class AgentCreate(BaseModel):
    name: str
    personality: Optional[Dict] = Field(default_factory=dict)
    memory: Optional[Dict] = Field(default_factory=dict)
    preferences: Optional[Dict] = Field(default_factory=dict)

class AgentUpdate(BaseModel):
    personality: Optional[Dict] = None
    memory: Optional[Dict] = None
    preferences: Optional[Dict] = None

class AgentOut(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    personality: Dict
    memory: Dict
    preferences: Dict

    class Config:
        orm_mode = True
