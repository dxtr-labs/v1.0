# backend/api/credits/credits.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.dependencies import get_current_user
from backend.db.models import CreditTransaction, User
from backend.db.session import get_db
from datetime import datetime
import uuid

credits_router = APIRouter()

@credits_router.get("/history")
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        CreditTransaction.select().where(CreditTransaction.user_id == current_user.user_id)
    )
    transactions = result.scalars().all()
    return {
        "credits": current_user.credits,
        "transactions": [
            {
                "type": tx.type,
                "amount": tx.amount,
                "description": tx.description,
                "timestamp": tx.timestamp
            } for tx in transactions
        ]
    }

@credits_router.post("/refill")
async def refill_credits(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tx = CreditTransaction(
        transaction_id=uuid.uuid4(),
        user_id=current_user.user_id,
        type="refill",
        amount=100,
        description="Dev refill",
        timestamp=datetime.utcnow()
    )
    db.add(tx)
    current_user.credits += 100
    await db.commit()
    return { "message": "Refilled 100 credits" }
