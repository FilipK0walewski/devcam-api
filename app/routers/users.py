import bcrypt

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.db.db import db
from app.models.users import UserLogin, UserRegister
from app.utils.auth import create_token, get_current_user

router = APIRouter(tags=["users"])


@router.post("/register")
async def register(user: UserRegister):
    if user.password != user.password_confirm:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # if len(user.password) < 8:
    #     raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

    record = await db.fetchrow("SELECT 1 FROM users WHERE username = $1", user.username)
    if record:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )
    query = "INSERT INTO users (username, password) VALUES ($1, $2)"
    await db.execute(query, user.username, hashed)

    token = create_token(user.username)
    return {"message": "User registered", "access_token": token, "token_type": "bearer"}


@router.post("/login")
async def login(user: UserLogin):
    query = "SELECT username, password FROM users WHERE username=$1"
    record = await db.fetchrow(query, user.username)
    if not record or not bcrypt.checkpw(
        user.password.encode("utf-8"), record["password"].encode("utf-8")
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(user.username)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
async def get_user_data(username: str = Depends(get_current_user)):
    return {"username": username}
