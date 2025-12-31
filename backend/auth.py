from typing import Dict, List, Optional

from fastapi import Depends, HTTPException, Header, status

USERS: Dict[str, Dict[str, str]] = {
    "owner": {"password": "ownerpass", "role": "owner", "token": "owner-token"},
    "admin": {"password": "adminpass", "role": "admin", "token": "admin-token"},
    "mod": {"password": "modpass", "role": "mod", "token": "mod-token"},
    "viewer": {"password": "viewerpass", "role": "viewer", "token": "viewer-token"},
}


class User:
    def __init__(self, username: str, role: str):
        self.username = username
        self.role = role


def _find_user_by_token(token: str | None) -> Optional[User]:
    if not token:
        return None
    for username, data in USERS.items():
        if data.get("token") == token:
            return User(username=username, role=data["role"])
    return None


def get_current_user(authorization: str | None = Header(None)) -> User:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth scheme")
    user = _find_user_by_token(token.strip())
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user


def require_roles(user: User, allowed: List[str]) -> None:
    if user.role not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
