import json
import random
from typing import Any, Dict, List, Tuple

from deploy.claims_codec.decode import Claims
from deploy.loader import load_rules_bundle
from deploy.planner.planner import plan


def _defaults_from_catalog(catalog: dict) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    for section in ("server_properties", "gamerule"):
        entries = catalog.get(section, {}).get("entries", {})
        for key, meta in entries.items():
            if "default" in meta:
                params[key] = meta["default"]
    return params


def _sample_variants(value: Any) -> List[Any]:
    if isinstance(value, bool):
        return [not value]
    if isinstance(value, int):
        return [value + 1, max(0, value - 1), value + 5]
    if isinstance(value, str):
        return ["custom-value"]
    return []


def _risk_keys(taxonomy: dict) -> List[Tuple[str, dict]]:
    keys: List[Tuple[str, dict]] = []
    for section in ("server_properties", "gamerule"):
        entries = taxonomy.get(section, {}).get("entries", {})
        for key, meta in entries.items():
            if meta.get("risk") in ("medium", "high"):
                keys.append((key, meta))
    return keys


def _run_single_param_tests(params: Dict[str, Any], catalog: dict, taxonomy: dict) -> Dict[str, int]:
    counts = {"tested": 0, "warned": 0, "recommended": 0}
    for key, meta in _risk_keys(taxonomy):
        if key not in params:
            continue
        base = params[key]
        for candidate in _sample_variants(base):
            counts["tested"] += 1
            test_params = dict(params)
            test_params[key] = candidate
            claims = Claims(params=test_params, profile="normal")
            setattr(claims, "catalog", catalog)
            setattr(claims, "taxonomy", taxonomy)
            result = plan(claims)
            if result.warnings:
                counts["warned"] += 1
            if result.recommendations:
                counts["recommended"] += 1
            break
    return counts


def _capacity_cases(catalog: dict, taxonomy: dict, base: Dict[str, Any]) -> List[Tuple[str, str]]:
    cases = []
    inputs = [
        ("case_50_players_4g", 50, "4G", 10, "block"),
        ("case_20_players_4g", 20, "4G", 10, "warn"),
        ("case_10_players_4g", 10, "4G", 10, "allow"),
    ]
    for name, players, mem, view_distance, expect in inputs:
        params = dict(base)
        params["deploy.expected_players"] = players
        params["docker.env.MEMORY"] = mem
        params["view-distance"] = view_distance
        claims = Claims(params=params, profile="normal")
        setattr(claims, "catalog", catalog)
        setattr(claims, "taxonomy", taxonomy)
        result = plan(claims)
        cases.append((name, result.summary.level, expect))
    return cases


def _random_sampling(params: Dict[str, Any], catalog: dict, taxonomy: dict, count: int) -> Dict[str, int]:
    keys = list(params.keys())
    summary = {"tested": 0, "warned": 0, "blocked": 0}
    for _ in range(count):
        pick = random.sample(keys, k=min(3, len(keys)))
        test_params = dict(params)
        for key in pick:
            test_params[key] = _sample_variants(test_params[key])[0]
        claims = Claims(params=test_params, profile="normal")
        setattr(claims, "catalog", catalog)
        setattr(claims, "taxonomy", taxonomy)
        result = plan(claims)
        summary["tested"] += 1
        if result.summary.level == "warn":
            summary["warned"] += 1
        if result.summary.level == "block":
            summary["blocked"] += 1
    return summary


def main() -> None:
    version = "1.21.11"
    bundle = load_rules_bundle(version)
    catalog = bundle.get("catalog", {})
    taxonomy = bundle.get("taxonomy", {})

    base_params = _defaults_from_catalog(catalog)
    base_params["edition"] = "java"
    base_params["stack.type"] = "paper"

    risk_counts = _run_single_param_tests(base_params, catalog, taxonomy)
    capacity = _capacity_cases(catalog, taxonomy, base_params)
    random_summary = _random_sampling(base_params, catalog, taxonomy, count=2000)

    report = {
        "version": version,
        "risk_param_tests": risk_counts,
        "capacity_cases": [{"case": name, "got": got, "expect": expect} for name, got, expect in capacity],
        "random_sampling": random_summary,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
