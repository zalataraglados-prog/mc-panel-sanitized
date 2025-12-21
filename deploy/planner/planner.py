from dataclasses import dataclass, field
from typing import List, Set

from deploy.mapper.mappings import (
    PARAMETER_MAPPINGS,
    is_mod_param,
    is_plugin_param,
)
from deploy.mapper.profiles import PROFILE_OVERRIDES


@dataclass
class PlanMessage:
    message: str
    code: str | None = None


@dataclass
class PlanSummary:
    level: str


@dataclass
class CapabilityResult:
    capability_id: str
    status: str


@dataclass
class ApplyPlan:
    target: str
    summary: PlanSummary
    capability_results: List[CapabilityResult] = field(default_factory=list)
    warnings: List[PlanMessage] = field(default_factory=list)
    blocks: List[PlanMessage] = field(default_factory=list)


def _validate_profile(profile: str) -> List[PlanMessage]:
    if profile in PROFILE_OVERRIDES:
        return []
    return [PlanMessage(message=f"Unknown profile: {profile}")]


def _is_reserved_param(key: str) -> bool:
    return key in {"edition", "stack.type", "runtime.java"}


def _validate_params(params: dict) -> List[PlanMessage]:
    blocks = []
    for key in params.keys():
        if _is_reserved_param(key) or is_plugin_param(key) or is_mod_param(key):
            continue
        if key not in PARAMETER_MAPPINGS:
            blocks.append(PlanMessage(message=f"Unknown parameter: {key}"))
    return blocks


def _capabilities_from_params(params: dict, claims) -> List[CapabilityResult]:
    seen: Set[str] = set()
    results = []
    for key in params.keys():
        if _is_reserved_param(key) or is_plugin_param(key) or is_mod_param(key):
            continue
        if key not in PARAMETER_MAPPINGS:
            continue
        cap = claims.param_capability(key)
        if cap in seen:
            continue
        seen.add(cap)
        results.append(CapabilityResult(capability_id=cap, status="applied"))
    return results


def _validate_edition_rules(params: dict) -> List[PlanMessage]:
    blocks = []
    edition = params.get("edition", "java")
    if edition != "bedrock":
        return blocks

    for key in ("docker.env.MEMORY", "minecraft.view_distance"):
        if key in params:
            blocks.append(
                PlanMessage(
                    code="bedrock_param_not_supported",
                    message=(
                        f"Parameter '{key}' is not applicable to Bedrock Edition."
                    ),
                )
            )
    return blocks


def _validate_stack_rules(params: dict) -> List[PlanMessage]:
    blocks = []
    stack_type = params.get("stack.type")
    if stack_type is None:
        return blocks

    allowed = {"vanilla", "paper", "fabric", "forge", "neoforge"}
    if stack_type not in allowed:
        blocks.append(
            PlanMessage(
                code="stack_invalid",
                message=f"Unknown server stack type: {stack_type}",
            )
        )
        return blocks

    has_plugins = any(is_plugin_param(key) for key in params.keys())
    has_mods = any(is_mod_param(key) for key in params.keys())

    if stack_type in {"vanilla", "fabric", "forge"} and has_plugins:
        blocks.append(
            PlanMessage(
                code="stack_param_conflict",
                message=f"Plugins are not supported on {stack_type} server stack.",
            )
        )
    if stack_type in {"vanilla", "paper"} and has_mods:
        blocks.append(
            PlanMessage(
                code="stack_param_conflict",
                message=f"Mods are not supported on {stack_type} server stack.",
            )
        )

    return blocks


def _parse_mc_major(version: str) -> int | None:
    if version.startswith("1."):
        parts = version.split(".")
        if len(parts) >= 2 and parts[1].isdigit():
            return int(parts[1])
    return None


def _parse_java_runtime(value) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        if value == "auto":
            return None
        if value.isdigit():
            return int(value)
    return None


def _validate_runtime_rules(params: dict) -> List[PlanMessage]:
    blocks = []
    runtime_value = params.get("runtime.java", "auto")
    runtime = _parse_java_runtime(runtime_value)
    if runtime is None and runtime_value not in (None, "auto"):
        blocks.append(
            PlanMessage(
                code="runtime_invalid",
                message=f"Unsupported runtime.java value: {runtime_value}",
            )
        )
        return blocks

    version = params.get("minecraft.version")
    if not isinstance(version, str):
        return blocks

    major = _parse_mc_major(version)
    if major is None or runtime is None:
        return blocks

    if major == 16 and runtime > 16:
        blocks.append(
            PlanMessage(
                code="runtime_incompatible",
                message="Java version above 16 is not supported for Minecraft 1.16.x.",
            )
        )
    if major == 17 and runtime == 8:
        blocks.append(
            PlanMessage(
                code="runtime_incompatible",
                message="Java 8 is not supported for Minecraft 1.17.x.",
            )
        )
    if major >= 20 and runtime < 17:
        blocks.append(
            PlanMessage(
                code="runtime_incompatible",
                message="Java 17 or higher is required for Minecraft 1.20.x.",
            )
        )

    return blocks


def plan(claims) -> ApplyPlan:
    """
    Produce an ApplyPlan from Claims.
    """

    blocks = []
    blocks.extend(_validate_profile(claims.profile))
    blocks.extend(_validate_params(claims.params))
    blocks.extend(_validate_edition_rules(claims.params))
    blocks.extend(_validate_stack_rules(claims.params))
    blocks.extend(_validate_runtime_rules(claims.params))

    level = "block" if blocks else "allow"
    summary = PlanSummary(level=level)
    capability_results = _capabilities_from_params(claims.params, claims)

    return ApplyPlan(
        target="instance",
        summary=summary,
        capability_results=capability_results,
        warnings=[],
        blocks=blocks,
    )
