from dataclasses import dataclass, field
from typing import Any, Dict, List, Set

from deploy.capacity_guard import capacity_status, estimate_capacity
from deploy.compat.modpack_matrix import MODPACK_STACK_COMPAT, normalize_loader
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
    param: str | None = None
    taxonomy: Dict[str, Any] | None = None


@dataclass
class PlanSummary:
    level: str


@dataclass
class CapabilityResult:
    capability_id: str
    status: str


@dataclass
class PlanRecommendation:
    param: str
    suggested: Any | None = None
    reason: str | None = None
    taxonomy: Dict[str, Any] | None = None


@dataclass
class ApplyPlan:
    target: str
    summary: PlanSummary
    capability_results: List[CapabilityResult] = field(default_factory=list)
    warnings: List[PlanMessage] = field(default_factory=list)
    blocks: List[PlanMessage] = field(default_factory=list)
    recommendations: List[PlanRecommendation] = field(default_factory=list)


def _validate_profile(profile: str) -> List[PlanMessage]:
    if profile in PROFILE_OVERRIDES:
        return []
    return [PlanMessage(message=f"Unknown profile: {profile}")]


def _is_reserved_param(key: str) -> bool:
    return key in {
        "edition",
        "stack.type",
        "runtime.java",
        "deploy.expected_players",
        "panel.enable",
        "panel.port",
        "map.plugin",
        "map.plugin_port",
        "map.render_interval",
        "map.plugin_url",
        "map.file",
        "map.target",
        "map.overwrite",
        "inventory.plugin",
        "inventory.plugin_url",
        "modpack.name",
        "modpack.loader",
        "modpack.type",
        "modpack.stack",
        "modpack.version",
        "modpack.source",
    }


def _validate_params(params: dict, catalog: dict | None = None) -> List[PlanMessage]:
    blocks = []
    catalog = catalog or {}
    for key in params.keys():
        if _is_reserved_param(key) or is_plugin_param(key) or is_mod_param(key):
            continue
        mapped = _map_claim_key(key, catalog)
        if key not in PARAMETER_MAPPINGS and not mapped:
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
                    taxonomy={"category": "compatibility", "scope": "world"},
                )
            )
    if stack_type in {"vanilla", "paper"} and has_mods:
            blocks.append(
                PlanMessage(
                    code="stack_param_conflict",
                    message=f"Mods are not supported on {stack_type} server stack.",
                    taxonomy={"category": "compatibility", "scope": "world"},
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


def _read_modpack_loader(params: dict) -> str | None:
    for key in ("modpack.loader", "modpack.type", "modpack.stack"):
        value = params.get(key)
        loader = normalize_loader(value)
        if loader:
            return loader
    return None


def _validate_modpack_rules(params: dict) -> List[PlanMessage]:
    blocks = []
    loader = _read_modpack_loader(params)
    if not loader:
        if params.get("modpack.name"):
            return [
                PlanMessage(
                    code="modpack_loader_missing",
                    message="Modpack name provided without loader; compatibility cannot be validated.",
                    taxonomy={"category": "compatibility", "scope": "world"},
                )
            ]
        return blocks

    stack_type = normalize_loader(params.get("stack.type"))
    compat = MODPACK_STACK_COMPAT.get(loader)
    if not compat:
        blocks.append(
            PlanMessage(
                code="modpack_loader_unknown",
                message=f"Unknown modpack loader: {loader}",
                taxonomy={"category": "compatibility", "scope": "world"},
            )
        )
        return blocks
    if not stack_type:
        blocks.append(
            PlanMessage(
                code="modpack_stack_missing",
                message="Modpack loader provided without stack.type.",
                taxonomy={"category": "compatibility", "scope": "world"},
            )
        )
        return blocks
    if stack_type not in compat:
        blocks.append(
            PlanMessage(
                code="modpack_stack_conflict",
                message=f"Modpack loader '{loader}' is not compatible with stack '{stack_type}'.",
                taxonomy={"category": "compatibility", "scope": "world"},
            )
        )
    return blocks


def _parse_int(value) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _parse_bool(value) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.lower()
        if lowered in ("true", "1"):
            return True
        if lowered in ("false", "0"):
            return False
    return None


def _validate_param_ranges(params: dict, catalog: dict | None, usability: dict | None) -> List[PlanMessage]:
    if not isinstance(catalog, dict):
        return []
    if not isinstance(usability, dict):
        usability = {}

    blocks: List[PlanMessage] = []

    server_entries = catalog.get("server_properties", {}).get("entries", {})
    gamerule_entries = catalog.get("gamerule", {}).get("entries", {})
    usab_server = usability.get("server_properties", {}).get("entries", {})
    usab_gamerule = usability.get("gamerule", {}).get("entries", {})

    for key, value in params.items():
        mapped = _map_claim_key(key, catalog)
        if not mapped:
            continue
        catalog_key, section = mapped
        if section == "server_properties":
            default = server_entries.get(catalog_key, {}).get("default")
            usage = usab_server.get(catalog_key, {}).get("usability", {})
        else:
            default = gamerule_entries.get(catalog_key, {}).get("default")
            usage = usab_gamerule.get(catalog_key, {}).get("usability", {})

        if isinstance(default, bool):
            parsed = _parse_bool(value)
            if parsed is None:
                blocks.append(
                    PlanMessage(
                        code="type_invalid",
                        message=f"Invalid boolean value for '{catalog_key}'.",
                        param=catalog_key,
                    )
                )
                continue
            numeric_value = None
        elif isinstance(default, int):
            parsed_int = _parse_int(value)
            if parsed_int is None:
                blocks.append(
                    PlanMessage(
                        code="type_invalid",
                        message=f"Invalid integer value for '{catalog_key}'.",
                        param=catalog_key,
                    )
                )
                continue
            numeric_value = parsed_int
        else:
            numeric_value = None

        rec_range = usage.get("recommended_range") or {}
        min_val = rec_range.get("min")
        max_val = rec_range.get("max")
        step_val = rec_range.get("step")

        if numeric_value is None:
            continue

        if isinstance(min_val, int) and numeric_value < min_val:
            blocks.append(
                PlanMessage(
                    code="range_violation",
                    message=f"Value for '{catalog_key}' below recommended minimum ({min_val}).",
                    param=catalog_key,
                )
            )
        if isinstance(max_val, int) and numeric_value > max_val:
            blocks.append(
                PlanMessage(
                    code="range_violation",
                    message=f"Value for '{catalog_key}' above recommended maximum ({max_val}).",
                    param=catalog_key,
                )
            )
        if isinstance(step_val, int) and isinstance(min_val, int):
            if (numeric_value - min_val) % step_val != 0:
                blocks.append(
                    PlanMessage(
                        code="range_violation",
                        message=f"Value for '{catalog_key}' does not align with step {step_val}.",
                        param=catalog_key,
                    )
                )

    return blocks


def _normalize_value(value, default):
    if isinstance(default, bool):
        if isinstance(value, str):
            if value.lower() == "true":
                return True
            if value.lower() == "false":
                return False
        return bool(value) if isinstance(value, bool) else value
    if isinstance(default, int):
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return value
    return value


def _map_claim_key(param_key: str, catalog: dict) -> tuple[str, str] | None:
    server_entries = catalog.get("server_properties", {}).get("entries", {})
    gamerule_entries = catalog.get("gamerule", {}).get("entries", {})

    if param_key in server_entries:
        return param_key, "server_properties"
    alt_key = param_key.replace("_", "-")
    if alt_key in server_entries:
        return alt_key, "server_properties"
    if param_key in gamerule_entries:
        return param_key, "gamerule"

    # Canonical mapping to server.properties keys
    if param_key.startswith("minecraft."):
        suffix = param_key.split(".", 1)[1]
        candidate = suffix.replace("_", "-")
        if candidate in server_entries:
            return candidate, "server_properties"
    if param_key.startswith("features."):
        suffix = param_key.split(".", 1)[1]
        candidate = suffix.replace("_", "-")
        if candidate in server_entries:
            return candidate, "server_properties"
    if param_key.startswith("security."):
        suffix = param_key.split(".", 1)[1]
        candidate = suffix.replace("_", "-")
        if candidate in server_entries:
            return candidate, "server_properties"
    if param_key.startswith("network."):
        suffix = param_key.split(".", 1)[1]
        mapping = {
            "mc_port": "server-port",
            "query_port": "query.port",
            "rcon_port": "rcon.port",
        }
        candidate = mapping.get(suffix)
        if candidate and candidate in server_entries:
            return candidate, "server_properties"

    return None


def _evaluate_taxonomy(claims) -> tuple[List[PlanMessage], List[PlanMessage], List[PlanRecommendation]]:
    catalog = getattr(claims, "catalog", None)
    taxonomy = getattr(claims, "taxonomy", None)
    if not isinstance(catalog, dict) or not isinstance(taxonomy, dict):
        return [], [], []

    warnings: List[PlanMessage] = []
    blocks: List[PlanMessage] = []
    recommendations: List[PlanRecommendation] = []

    params = claims.params or {}
    server_entries = catalog.get("server_properties", {}).get("entries", {})
    gamerule_entries = catalog.get("gamerule", {}).get("entries", {})
    tax_server = taxonomy.get("server_properties", {}).get("entries", {})
    tax_gamerule = taxonomy.get("gamerule", {}).get("entries", {})

    contexts = []
    for key, value in params.items():
        mapped = _map_claim_key(key, catalog)
        if not mapped:
            continue
        catalog_key, section = mapped
        if section == "server_properties":
            default = server_entries.get(catalog_key, {}).get("default")
            tax = tax_server.get(catalog_key)
        else:
            default = gamerule_entries.get(catalog_key, {}).get("default")
            tax = tax_gamerule.get(catalog_key)

        if not isinstance(tax, dict):
            continue

        contexts.append(
            {
                "claim_key": key,
                "catalog_key": catalog_key,
                "section": section,
                "value": value,
                "default": default,
                "taxonomy": tax,
            }
        )

    # Group by category for warning thresholds
    category_counts: Dict[str, int] = {}
    for ctx in contexts:
        cat = ctx["taxonomy"].get("category")
        if not cat:
            continue
        default = ctx["default"]
        value = _normalize_value(ctx["value"], default)
        changed = value != default
        if not changed:
            continue
        category_counts[cat] = category_counts.get(cat, 0) + 1

    for cat, count in category_counts.items():
        if count >= 3 or (cat == "performance" and count >= 2):
            warnings.append(
                PlanMessage(
                    code="category_heavy",
                    message=f"Multiple {cat} parameters adjusted; review combined impact.",
                    taxonomy={"category": cat},
                )
            )

    edition = params.get("edition", "java")

    profile = getattr(claims, "profile", "normal")

    for ctx in contexts:
        tax = ctx["taxonomy"]
        risk = tax.get("risk")
        sensitivity = tax.get("sensitivity")
        scope = tax.get("scope")

        default = ctx["default"]
        value = _normalize_value(ctx["value"], default)
        changed = value != default

        if scope == "player" and ctx["section"] != "gamerule":
            blocks.append(
                PlanMessage(
                    code="scope_conflict",
                    message=f"Player-scope parameter '{ctx['catalog_key']}' must be set via gamerule.",
                    param=ctx["catalog_key"],
                    taxonomy=tax,
                )
            )

        if scope == "world" and edition == "bedrock":
            blocks.append(
                PlanMessage(
                    code="scope_conflict",
                    message=f"World-scope parameter '{ctx['catalog_key']}' is not applicable to Bedrock Edition.",
                    param=ctx["catalog_key"],
                    taxonomy=tax,
                )
            )

        if not changed:
            continue

        if risk in ("medium", "high"):
            code = "high_risk_parameter" if risk == "high" else "medium_risk_parameter"
            label = "High-risk" if risk == "high" else "Medium-risk"
            warnings.append(
                PlanMessage(
                    code=code,
                    message=f"{label} parameter '{ctx['catalog_key']}' deviates from default.",
                    param=ctx["catalog_key"],
                    taxonomy=tax,
                )
            )
            recommendations.append(
                PlanRecommendation(
                    param=ctx["catalog_key"],
                    suggested=default,
                    reason="Risky value deviates from default.",
                    taxonomy=tax,
                )
            )
            if tax.get("category") == "performance":
                recommendations.append(
                    PlanRecommendation(
                        param=ctx["catalog_key"],
                        suggested=default,
                        reason="High performance impact; consider default value.",
                        taxonomy=tax,
                    )
                )

        if profile == "beginner" and sensitivity == "advanced":
            recommendations.append(
                PlanRecommendation(
                    param=ctx["catalog_key"],
                    suggested=default,
                    reason="Beginner profile set advanced parameter; consider default.",
                    taxonomy=tax,
                )
            )

        if sensitivity == "novice":
            warnings.append(
                PlanMessage(
                    code="novice_override",
                    message=f"Novice-sensitive parameter '{ctx['catalog_key']}' was explicitly set.",
                    param=ctx["catalog_key"],
                    taxonomy=tax,
                )
            )

    return warnings, blocks, recommendations


def plan(claims) -> ApplyPlan:
    """
    Produce an ApplyPlan from Claims.
    """

    blocks: List[PlanMessage] = []
    warnings: List[PlanMessage] = []
    recommendations: List[PlanRecommendation] = []
    blocks.extend(_validate_profile(claims.profile))
    blocks.extend(_validate_params(claims.params, getattr(claims, "catalog", None)))
    blocks.extend(_validate_edition_rules(claims.params))
    blocks.extend(_validate_stack_rules(claims.params))
    blocks.extend(_validate_modpack_rules(claims.params))
    blocks.extend(_validate_runtime_rules(claims.params))
    blocks.extend(
        _validate_param_ranges(
            claims.params,
            getattr(claims, "catalog", None),
            getattr(claims, "usability", None),
        )
    )

    tax_warnings, tax_blocks, tax_recs = _evaluate_taxonomy(claims)
    warnings.extend(tax_warnings)
    blocks.extend(tax_blocks)
    recommendations.extend(tax_recs)

    estimate = estimate_capacity(claims.params)
    if estimate:
        status, payload = capacity_status(estimate)
        if status == "block":
            blocks.append(
                PlanMessage(
                    code="capacity_block",
                    message="Configured memory is insufficient for expected players.",
                    taxonomy={"capacity": payload},
                )
            )
        elif status == "warn":
            warnings.append(
                PlanMessage(
                    code="capacity_warn",
                    message="Configured memory may be insufficient for expected players.",
                    taxonomy={"capacity": payload},
                )
            )
        recommendations.append(
            PlanRecommendation(
                param="docker.env.MEMORY",
                suggested=payload.get("required_gb"),
                reason="Increase memory or reduce players/view distance.",
                taxonomy={"capacity": payload},
            )
        )

    level = "block" if blocks else ("warn" if warnings else "allow")
    summary = PlanSummary(level=level)
    capability_results = _capabilities_from_params(claims.params, claims)

    return ApplyPlan(
        target="instance",
        summary=summary,
        capability_results=capability_results,
        warnings=warnings,
        blocks=blocks,
        recommendations=recommendations,
    )
