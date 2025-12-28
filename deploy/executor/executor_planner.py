from __future__ import annotations

import os
from typing import Any, Dict, List

from deploy.executor.execution_plan import Action, ExecutionPlan, Precondition


DEFAULT_BASE_DIR = "/opt/mc-instances"


def _parse_int(value) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _pick_server_port(params: dict) -> int | None:
    candidates = [
        params.get("server-port"),
        params.get("minecraft.server_port"),
        params.get("network.mc_port"),
    ]
    for item in candidates:
        port = _parse_int(item)
        if port is not None:
            return port
    return None


def _needs_docker(params: dict) -> bool:
    return any(key.startswith("docker.") for key in params.keys())


def build_execution_plan(
    *,
    claims,
    review,
    host_facts: List[Dict[str, Any]],
    mode: str = "dry-run",
) -> ExecutionPlan:
    params = getattr(claims, "params", {}) or {}
    review_level = None
    if isinstance(review, dict):
        review_level = review.get("level")
    if review_level is None:
        review_level = getattr(review, "level", None)
    if review_level is None:
        review_level = getattr(review, "summary", {}).get("level")
    review_level = review_level or "allow"

    base_dir = os.environ.get("MC_PANEL_BASE_DIR", DEFAULT_BASE_DIR)
    preconditions: List[Precondition] = [
        Precondition(type="path_exists", value=base_dir, required=True),
        Precondition(type="path_writable", value=base_dir, required=True),
    ]

    port = _pick_server_port(params)
    if port is not None:
        preconditions.append(Precondition(type="port_free", value=port, required=True))

    if _needs_docker(params):
        preconditions.append(Precondition(type="docker_available", value="docker", required=True))

    # Actions remain declarative in Phase 12.1.
    actions: List[Action] = []

    plan = ExecutionPlan(
        mode=mode,
        review_level=review_level,
        preconditions=preconditions,
        actions=actions,
    )
    plan.finalize()
    return plan
