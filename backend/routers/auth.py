from fastapi import APIRouter, HTTPException

from backend.auth import list_users
from backend.models import LoginRequest, LoginResponse

router = APIRouter()


@router.post("/api/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    record = list_users().get(payload.username)
    if not record or payload.password != record.get("password"):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return LoginResponse(token=record["token"], role=record["role"])
