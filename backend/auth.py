import json
import secrets
from pathlib import Path
from threading import RLock
from typing import Dict, List, Optional

from fastapi import HTTPException, Header, status
from backend.logging import get_logger

DEFAULT_USERS: Dict[str, Dict[str, str]] = {
    "owner": {"password": "ownerpass", "role": "owner", "token": "owner-token"},
    "admin": {"password": "adminpass", "role": "admin", "token": "admin-token"},
    "mod": {"password": "modpass", "role": "mod", "token": "mod-token"},
    "viewer": {"password": "viewerpass", "role": "viewer", "token": "viewer-token"},
}

USER_DB_PATH = Path(__file__).resolve().parent / "data" / "users.json"
LOGGER = get_logger(__name__)
_CACHE_LOCK = RLock()
_USERS_CACHE: Dict[str, Dict[str, str]] | None = None
_TOKEN_INDEX: Dict[str, tuple[str, str]] = {}
_USERS_MTIME_NS: int | None = None


def _clone_users(data: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    return {username: dict(record) for username, record in data.items()}


def _build_token_index(data: Dict[str, Dict[str, str]]) -> Dict[str, tuple[str, str]]:
    index: Dict[str, tuple[str, str]] = {}
    for username, record in data.items():
        token = (record.get("token") or "").strip()
        role = (record.get("role") or "").strip()
        if token and role:
            index[token] = (username, role)
    return index


def _current_users_mtime_ns() -> int | None:
    try:
        return USER_DB_PATH.stat().st_mtime_ns
    except FileNotFoundError:
        return None


def _refresh_cache(data: Dict[str, Dict[str, str]]) -> None:
    global _USERS_CACHE, _TOKEN_INDEX, _USERS_MTIME_NS
    cloned = _clone_users(data)
    _USERS_CACHE = cloned
    _TOKEN_INDEX = _build_token_index(cloned)
    _USERS_MTIME_NS = _current_users_mtime_ns()


def _ensure_user_db() -> Dict[str, Dict[str, str]]:
    if USER_DB_PATH.exists():
        try:
            return json.loads(USER_DB_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            LOGGER.warning("users.json is invalid JSON; recreating default users")
    USER_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    USER_DB_PATH.write_text(json.dumps(DEFAULT_USERS, ensure_ascii=False, indent=2), encoding="utf-8")
    LOGGER.info("Initialized users database with default users")
    return _clone_users(DEFAULT_USERS)


def _save_users(data: Dict[str, Dict[str, str]]) -> None:
    with _CACHE_LOCK:
        USER_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        USER_DB_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        _refresh_cache(data)
    LOGGER.info("Persisted users database (%d users)", len(data))


def _load_users(force_reload: bool = False) -> Dict[str, Dict[str, str]]:
    with _CACHE_LOCK:
        current_mtime = _current_users_mtime_ns()
        if not force_reload and _USERS_CACHE is not None and _USERS_MTIME_NS == current_mtime:
            return _USERS_CACHE
        users = _ensure_user_db()
        _refresh_cache(users)
        LOGGER.info("Loaded users database from disk (%d users)", len(_USERS_CACHE or {}))
        return _USERS_CACHE or {}


class User:
    def __init__(self, username: str, role: str):
        self.username = username
        self.role = role


def _find_user_by_token(token: str | None) -> Optional[User]:
    clean_token = (token or "").strip()
    if not clean_token:
        return None
    _load_users()
    with _CACHE_LOCK:
        match = _TOKEN_INDEX.get(clean_token)
    if not match:
        return None
    username, role = match
    return User(username=username, role=role)


def get_current_user(authorization: str | None = Header(None)) -> User:
    if not authorization:
        LOGGER.warning("Authentication failed: missing Authorization header")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        LOGGER.warning("Authentication failed: invalid auth scheme '%s'", scheme or "<empty>")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth scheme")
    user = _find_user_by_token(token.strip())
    if not user:
        LOGGER.warning("Authentication failed: invalid token")
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
        LOGGER.warning(
            "Authorization denied: user=%s role=%s allowed=%s",
            user.username,
            user.role,
            ",".join(allowed),
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")


def list_users() -> Dict[str, Dict[str, str]]:
    return _clone_users(_load_users())


def create_or_update_user(username: str, password: str, role: str) -> Dict[str, str]:
    users = _clone_users(_load_users())
    is_update = username in users
    token = users.get(username, {}).get("token") or secrets.token_hex(16)
    users[username] = {"password": password, "role": role, "token": token}
    _save_users(users)
    LOGGER.info(
        "User %s: username=%s role=%s",
        "updated" if is_update else "created",
        username,
        role,
    )
    return users[username]


def delete_user(username: str) -> None:
    users = _clone_users(_load_users())
    if username in users:
        users.pop(username)
        _save_users(users)
        LOGGER.info("User deleted: username=%s", username)
