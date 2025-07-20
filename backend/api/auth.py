# backend/api/auth/auth.py

from fastapi import APIRouter, Request, Response, Depends, HTTPException, status, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import bcrypt, uuid

from backend.db.session import get_db
from backend.db.models import User, Session

auth_router = APIRouter()

SESSION_COOKIE_NAME = "session_token"
COOKIE_EXPIRES_DAYS = 7

# --- Helper ---
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

# --- Signup ---
@auth_router.post("/signup")
async def signup(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    name = f"{data.get('firstName', '')} {data.get('lastName', '')}".strip()

    existing = await db.execute(
        User.select().where(User.email == email)
    )
    if existing.scalar():
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(email=email, password=hash_password(password), name=name)
    db.add(user)
    await db.flush()

    token = str(uuid.uuid4())
    expires = datetime.utcnow() + timedelta(days=COOKIE_EXPIRES_DAYS)
    session = Session(user_id=user.user_id, token=token, expires_at=expires)
    db.add(session)
    await db.commit()

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=COOKIE_EXPIRES_DAYS * 86400,
        path="/"
    )

    return { "message": "Signup successful", "name": user.name, "email": user.email }

# --- Login ---
@auth_router.post("/login")
async def login(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    result = await db.execute(User.select().where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = str(uuid.uuid4())
    expires = datetime.utcnow() + timedelta(days=COOKIE_EXPIRES_DAYS)
    session = Session(user_id=user.user_id, token=token, expires_at=expires)
    db.add(session)
    await db.commit()

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=COOKIE_EXPIRES_DAYS * 86400,
        path="/"
    )

    return { "message": "Login successful", "name": user.name, "email": user.email }

# --- Logout ---
@auth_router.post("/logout")
async def logout(response: Response, token: str = Cookie(None), db: AsyncSession = Depends(get_db)):
    if token:
        await db.execute(Session.delete().where(Session.token == token))
        await db.commit()
        response.delete_cookie(key=SESSION_COOKIE_NAME)
    return { "message": "Logged out" }

# --- Who am I ---
@auth_router.get("/me")
async def me(token: str = Cookie(None), db: AsyncSession = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="No session")

    result = await db.execute(
        Session.select().where(Session.token == token)
    )
    session = result.scalar_one_or_none()

    if not session or session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Session expired")

    user = await db.get(User, session.user_id)
    return { "userId": user.user_id, "name": user.name, "email": user.email }
