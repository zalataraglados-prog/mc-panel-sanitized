from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time
import uuid


class DeploymentStatus(str, Enum):
    PLANNED = "planned"
    APPLYING = "applying"
    RUNNING = "running"
    FAILED = "failed"


@dataclass
class Deployment:
    claims: Dict[str, Any]
    plan_review: Dict[str, Any]
    status: DeploymentStatus = DeploymentStatus.PLANNED
    deployment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    updated_at: Optional[float] = None
    logs: List[str] = field(default_factory=list)

    def set_status(self, status: DeploymentStatus, *, note: Optional[str] = None):
        self.status = status
        self.updated_at = time.time()
        if note:
            self.logs.append(note)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.deployment_id,
            "status": self.status.value,
            "claims": self.claims,
            "plan_review": self.plan_review,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "logs": list(self.logs),
        }
