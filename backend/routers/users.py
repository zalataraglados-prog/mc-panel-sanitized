from fastapi import APIRouter, Depends, HTTPException

from backend.auth import create_or_update_user, delete_user, list_users, require_roles, get_current_user
from backend.models import UserCreateRequest, UserEntry, UserListResponse, UserUpdateRequest

router = APIRouter()


@router.get("/api/users", response_model=UserListResponse)
def list_users_endpoint(user=Depends(get_current_user)):
    require_roles(user, ["owner", "admin"])
    entries = [UserEntry(username=name, role=record["role"]) for name, record in list_users().items()]
    return UserListResponse(users=entries)


@router.post("/api/users", response_model=UserEntry)
def create_user(payload: UserCreateRequest, user=Depends(get_current_user)):
    require_roles(user, ["owner"])
    record = create_or_update_user(payload.username, payload.password, payload.role)
    return UserEntry(username=payload.username, role=record["role"])


@router.put("/api/users/{username}", response_model=UserEntry)
def update_user(username: str, payload: UserUpdateRequest, user=Depends(get_current_user)):
    require_roles(user, ["owner"])
    existing = list_users().get(username)
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    password = payload.password or existing["password"]
    role = payload.role or existing["role"]
    record = create_or_update_user(username, password, role)
    return UserEntry(username=username, role=record["role"])


@router.delete("/api/users/{username}")
def delete_user_endpoint(username: str, user=Depends(get_current_user)):
    require_roles(user, ["owner"])
    if username == "owner":
        raise HTTPException(status_code=400, detail="Cannot delete owner")
    delete_user(username)
    return {"status": "ok"}
