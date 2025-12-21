from dataclasses import dataclass, field
from typing import List, Set

from deploy.mapper.mappings import PARAMETER_MAPPINGS
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


def _validate_params(params: dict) -> List[PlanMessage]:
    blocks = []
    for key in params.keys():
        if key == "edition":
            continue
        if key not in PARAMETER_MAPPINGS:
            blocks.append(PlanMessage(message=f"Unknown parameter: {key}"))
    return blocks


def _capabilities_from_params(params: dict, claims) -> List[CapabilityResult]:
    seen: Set[str] = set()
    results = []
    for key in params.keys():
        if key == "edition":
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
    edition = params.get("edition")
    if edition != "bedrock":
        return blocks

    for key in ("docker.env.MEMORY", "minecraft.view_distance"):
        if key in params:
            blocks.append(
                PlanMessage(
                    code="bedrock_param_not_supported",
                    message=f"{key} is not applicable to Bedrock Edition",
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
