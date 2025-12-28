from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass
class Precondition:
    type: str
    value: Any
    required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "value": self.value,
            "required": self.required,
        }


@dataclass
class Action:
    type: str
    params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "params": self.params,
        }


@dataclass
class ExecutionPlan:
    mode: str
    review_level: str
    preconditions: List[Precondition] = field(default_factory=list)
    actions: List[Action] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

    def _hash_payload(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "review_level": self.review_level,
            "preconditions": [item.to_dict() for item in self.preconditions],
            "actions": [item.to_dict() for item in self.actions],
            "meta": {
                "plan_version": self.meta.get("plan_version", 1),
            },
        }

    def deterministic_hash(self) -> str:
        payload = json.dumps(self._hash_payload(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def finalize(self) -> None:
        self.meta.setdefault("plan_version", 1)
        self.meta["generated_at"] = datetime.now(timezone.utc).isoformat()
        self.meta["deterministic_hash"] = self.deterministic_hash()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "review_level": self.review_level,
            "preconditions": [item.to_dict() for item in self.preconditions],
            "actions": [item.to_dict() for item in self.actions],
            "meta": self.meta,
        }
