from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    role: str


class StatusResponse(BaseModel):
    running: bool
    players: int
    tps: float
    mspt: float
    ping: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    instance_dir: str
    updated_at: datetime


class MetricsPoint(BaseModel):
    timestamp: float
    value: float


class PlaybackResponse(BaseModel):
    entries: List[str]


class PlayerInfo(BaseModel):
    name: str
    uuid: str
    skin_url: str
    session_seconds: int
    position: Dict[str, float]
    role: Optional[str] = None


class CommandRequest(BaseModel):
    command: str
    channel: str = "console"
    target: Optional[str] = None
    instance_dir: Optional[str] = None


class ControlRequest(BaseModel):
    action: str
    instance_dir: Optional[str] = None


class RuleEntry(BaseModel):
    key: str
    value: str


class RulesResponse(BaseModel):
    entries: List[RuleEntry]


class InstancesResponse(BaseModel):
    instances: List[Dict[str, Any]]
