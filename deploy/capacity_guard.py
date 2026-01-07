from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple


@dataclass
class CapacityEstimate:
    players: int
    memory_gb: float
    view_distance: int
    required_gb: float


def _parse_int(value) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _parse_memory_gb(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None
    raw = value.strip().upper()
    if raw.endswith("GB"):
        raw = raw[:-2]
    if raw.endswith("G"):
        try:
            return float(raw[:-1])
        except ValueError:
            return None
    if raw.endswith("MB"):
        raw = raw[:-2]
    if raw.endswith("M"):
        try:
            return float(raw[:-1]) / 1024.0
        except ValueError:
            return None
    return None


def _resolve_players(params: dict) -> int | None:
    for key in ("deploy.expected_players", "max-players", "server.properties.max-players"):
        value = params.get(key)
        parsed = _parse_int(value)
        if parsed is not None:
            return parsed
    return None


def _resolve_view_distance(params: dict) -> int | None:
    for key in ("minecraft.view_distance", "view-distance"):
        value = params.get(key)
        parsed = _parse_int(value)
        if parsed is not None:
            return parsed
    return None


def estimate_capacity(params: dict) -> CapacityEstimate | None:
    memory_gb = _parse_memory_gb(params.get("docker.env.MEMORY"))
    players = _resolve_players(params)
    if memory_gb is None or players is None:
        return None
    view_distance = _resolve_view_distance(params) or 10

    base_gb = 2.0
    per_player_gb = 0.10
    vd_penalty_gb = max(0, view_distance - 10) * 0.15
    required_gb = base_gb + (players * per_player_gb) + vd_penalty_gb

    return CapacityEstimate(
        players=players,
        memory_gb=memory_gb,
        view_distance=view_distance,
        required_gb=required_gb,
    )


def capacity_status(estimate: CapacityEstimate) -> Tuple[str, Dict[str, Any]]:
    required = estimate.required_gb
    memory = estimate.memory_gb

    if memory < 2.0:
        return "block", _as_payload(estimate)
    if memory < required * 0.85:
        return "block", _as_payload(estimate)
    if memory <= required:
        return "warn", _as_payload(estimate)
    return "allow", _as_payload(estimate)


def _as_payload(estimate: CapacityEstimate) -> Dict[str, Any]:
    return {
        "players": estimate.players,
        "memory_gb": estimate.memory_gb,
        "view_distance": estimate.view_distance,
        "required_gb": round(estimate.required_gb, 2),
    }
