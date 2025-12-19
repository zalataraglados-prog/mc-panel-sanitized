"""
Legacy Config Mapper (with Profile Overlays)

Maps approved Claims parameters into legacy ConfigModel config,
then applies profile-based overlays.

Deterministic, side-effect free.
"""

import copy
from typing import Dict

from .mappings import PARAMETER_MAPPINGS
from .profiles import PROFILE_OVERRIDES


def map_claims_to_legacy_config(
    *,
    claims,
    base_config: Dict,
    apply_plan
) -> Dict:
    legacy_config = copy.deepcopy(base_config)

    allowed_capabilities = {
        result.capability_id
        for result in apply_plan.capability_results
        if result.status in ("applied", "degraded")
    }

    # 1️⃣ Apply explicit Claims parameters
    for param_key, param_value in claims.params.items():
        mapping = PARAMETER_MAPPINGS.get(param_key)
        if not mapping:
            continue

        capability_id = claims.param_capability(param_key)
        if capability_id not in allowed_capabilities:
            continue

        _apply_mapping(
            legacy_config=legacy_config,
            path=mapping,
            value=param_value,
        )

    # 2️⃣ Apply profile-based overrides
    _apply_profile_overrides(
        legacy_config=legacy_config,
        profile=claims.profile,
        allowed_capabilities=allowed_capabilities,
    )

    return legacy_config


def _apply_profile_overrides(
    *,
    legacy_config: Dict,
    profile: str,
    allowed_capabilities: set
):
    overrides = PROFILE_OVERRIDES.get(profile)
    if not overrides:
        return

    for param_key, value in overrides.items():
        mapping = PARAMETER_MAPPINGS.get(param_key)
        if not mapping:
            continue

        # Profile overrides must still respect capability permission
        capability_id = _infer_capability_from_param(param_key)
        if capability_id not in allowed_capabilities:
            continue

        if value is None:
            _remove_mapping(legacy_config, mapping)
        else:
            _apply_mapping(legacy_config, mapping, value)


def _apply_mapping(*, legacy_config: Dict, path: tuple, value):
    current = legacy_config
    for key in path[:-1]:
        if key not in current or not isinstance(current[key], dict):
            return
        current = current[key]
    current[path[-1]] = value


def _remove_mapping(*, legacy_config: Dict, path: tuple):
    current = legacy_config
    for key in path[:-1]:
        if key not in current or not isinstance(current[key], dict):
            return
        current = current[key]
    current.pop(path[-1], None)


def _infer_capability_from_param(param_key: str) -> str:
    """
    Infer capability_id from canonical param key.

    This must stay consistent with Planner definitions.
    """
    return param_key.split(".", 1)[0]