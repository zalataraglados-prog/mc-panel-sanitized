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


class InventoryItem(BaseModel):
    slot: int
    id: str
    count: int
    meta: Optional[Dict[str, Any]] = None


class PlayerInventoryResponse(BaseModel):
    player: str
    supported: bool
    items: List[InventoryItem] = []
    message: Optional[str] = None


class PlayerInventoryUpdateRequest(BaseModel):
    player: str
    items: List[InventoryItem]
    instance_dir: Optional[str] = None


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


class RulesUpdateRequest(BaseModel):
    entries: List[RuleEntry]
    instance_dir: Optional[str] = None


class InstancesResponse(BaseModel):
    instances: List[Dict[str, Any]]


class MapStatusResponse(BaseModel):
    source: Optional[str]
    available: Dict[str, bool]
    y_min: int
    y_max: int
    supports_y: bool


class MapConfigFile(BaseModel):
    name: str
    content: str


class MapConfigResponse(BaseModel):
    plugin: Optional[str]
    files: List[MapConfigFile]


class MapConfigUpdateRequest(BaseModel):
    plugin: Optional[str]
    files: List[MapConfigFile]
    instance_dir: Optional[str] = None


class MapReloadResponse(BaseModel):
    plugin: Optional[str]
    status: str
