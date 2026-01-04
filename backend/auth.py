import json
import secrets
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import Depends, HTTPException, Header, status

DEFAULT_USERS: Dict[str, Dict[str, str]] = {
    "owner": {"password": "ownerpass", "role": "owner", "token": "owner-token"},
    "admin": {"password": "adminpass", "role": "admin", "token": "admin-token"},
    "mod": {"password": "modpass", "role": "mod", "token": "mod-token"},
    "viewer": {"password": "viewerpass", "role": "viewer", "token": "viewer-token"},
}

USER_DB_PATH = Path(__file__).resolve().parent / "data" / "users.json"


def _ensure_user_db() -> Dict[str, Dict[str, str]]:
    if USER_DB_PATH.exists():
        try:
            return json.loads(USER_DB_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    USER_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    USER_DB_PATH.write_text(json.dumps(DEFAULT_USERS, ensure_ascii=False, indent=2), encoding="utf-8")
    return dict(DEFAULT_USERS)


def _save_users(data: Dict[str, Dict[str, str]]) -> None:
    USER_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    USER_DB_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_users() -> Dict[str, Dict[str, str]]:
    return _ensure_user_db()


class User:
    def __init__(self, username: str, role: str):
        self.username = username
        self.role = role


def _find_user_by_token(token: str | None) -> Optional[User]:
    if not token:
        return None
    for username, data in _load_users().items():
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


def get_user_from_optional(authorization: str | None, token: str | None) -> User:
    if authorization:
        return get_current_user(authorization)
    user = _find_user_by_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user


def require_roles(user: User, allowed: List[str]) -> None:
    if user.role not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")


def list_users() -> Dict[str, Dict[str, str]]:
    return _load_users()


def create_or_update_user(username: str, password: str, role: str) -> Dict[str, str]:
    users = _load_users()
    token = users.get(username, {}).get("token") or secrets.token_hex(16)
    users[username] = {"password": password, "role": role, "token": token}
    _save_users(users)
    return users[username]


def delete_user(username: str) -> None:
    users = _load_users()
    if username in users:
        users.pop(username)
        _save_users(users)
