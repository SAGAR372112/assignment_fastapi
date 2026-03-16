# app/routes/auth_routes.py
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from app.core.auth import AuthManager
from app.core.config import Settings
from typing import Dict, Any

router = APIRouter(prefix="/auth", tags=["Authentication"])

settings = Settings()
auth_manager = AuthManager(settings)
active_sessions: Dict[str, Dict[str, Any]] = {}

@router.post("/login")
async def login(username: str, password: str):
    if username == "demo" and password == "demo123":
        access_token = auth_manager.create_access_token(data={"sub": username})
        active_sessions[username] = {
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "request_count": 0
        }
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60
        }
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")