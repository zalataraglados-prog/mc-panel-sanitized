from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    role: str


class UserEntry(BaseModel):
    username: str
    role: str


class UserCreateRequest(BaseModel):
    username: str
    password: str
    role: str


class UserUpdateRequest(BaseModel):
    password: Optional[str] = None
    role: Optional[str] = None


class UserListResponse(BaseModel):
    users: List[UserEntry]


class StatusResponse(BaseModel):
    running: bool
    players: int
    tps: float
    mspt: float
    ping: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    rcon_ok: bool
    rcon_message: str
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
    online: bool = True
    last_seen: Optional[str] = None
    role: Optional[str] = None


class InventoryItem(BaseModel):
    slot: int
    id: str
    count: int
    meta: Optional[Dict[str, Any]] = None


class PlayerInventoryResponse(BaseModel):
    player: str
    supported: bool
    provider: Optional[str] = None
    editable: bool = False
    items: List[InventoryItem] = Field(default_factory=list)
    message: Optional[str] = None
    raw: Optional[str] = None


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


class ClaimsExportResponse(BaseModel):
    claims_string: str
    params: Dict[str, Any]
    version: str
    instance_dir: str
    format: str = "full"


class RconHealthResponse(BaseModel):
    ok: bool
    message: str
    instance_dir: str


class InstancesResponse(BaseModel):
    instances: List[Dict[str, Any]]


class MapStatusResponse(BaseModel):
    source: Optional[str]
    available: Dict[str, bool]
    y_min: int
    y_max: int
    supports_y: bool


class MapMetaResponse(BaseModel):
    source: Optional[str]
    tile_size: Optional[int] = None
    scale: Optional[float] = None
    origin: Optional[Dict[str, float]] = None
    start_location: Optional[str] = None
    maps: List[Dict[str, str]] = Field(default_factory=list)


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


class SummaryResponse(BaseModel):
    status: StatusResponse
    players: List[PlayerInfo]
    map_status: MapStatusResponse
