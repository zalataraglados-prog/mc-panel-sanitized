#!/usr/bin/env python3
"""
MC-PANEL CLI (v1.0)

Commands:
  deploy plan
  deploy apply
"""

import argparse
import json
import os
import sys

from deploy.claims_codec import Claims, decode_claims
from deploy.executor.executor_planner import build_execution_plan
from deploy.executor.host_inspector import HostInspector
from deploy.executor.plan_executor import ExecutionPlanExecutor
from deploy.loader import load_rules
from deploy.planner.planner import plan as plan_apply
from deploy.web.review_adapter import review_to_dict


def load_claims_from_args(args) -> Claims:
    params = {}

    if args.set:
        for kv in args.set:
            if "=" not in kv:
                raise ValueError(f"Invalid --set '{kv}', expected key=value")
            key, value = kv.split("=", 1)
            params[key] = value

    profile = args.profile or "normal"
    return Claims(
        params=params,
        profile=profile,
        imported=False,
    )


def print_review(apply_plan, claims: Claims | None = None):
    print("\n=== Apply Plan Review ===")
    print(f"Target: {apply_plan.target}")
    print(f"Level:  {apply_plan.summary.level}")
    if claims and getattr(claims, "imported_from_string", False):
        print("Source: imported claims")
    print()

    for result in apply_plan.capability_results:
        status = result.status.upper()
        print(f"- {result.capability_id:30} {status}")

    if apply_plan.warnings:
        print("\nWarnings:")
        for w in apply_plan.warnings:
            print(f"  [WARN] {w.message}")

    if apply_plan.blocks:
        print("\nBlocked:")
        for b in apply_plan.blocks:
            print(f"  [BLOCK] {b.message}")

    if getattr(apply_plan, "recommendations", None):
        print("\nRecommendations:")
        for r in apply_plan.recommendations:
            param = getattr(r, "param", None)
            reason = getattr(r, "reason", None)
            suggested = getattr(r, "suggested", None)
            label = param or "parameter"
            if suggested is not None:
                print(f"  [REC] {label} -> {suggested}: {reason}")
            else:
                print(f"  [REC] {label}: {reason}")

    print()


def print_execution_plan(plan) -> None:
    payload = plan.to_dict()
    print("=== Execution Plan (dry-run) ===")
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    print()


def _parse_port(value):
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _resolve_server_port(params: dict) -> int | None:
    for key in ("server-port", "minecraft.server_port", "network.mc_port"):
        if key in params:
            port = _parse_port(params.get(key))
            if port is not None:
                return port
    return None


def main():
    parser = argparse.ArgumentParser(prog="deploy")

    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("plan", "apply"):
        p = sub.add_parser(name)
        p.add_argument(
            "--version",
            default="1.21.4",
            help="Minecraft version for rule lookup (default: 1.21.4)",
        )
        p.add_argument(
            "--rules-base-url",
            default=None,
            help="Override rules repository base URL",
        )
        p.add_argument(
            "--profile",
            choices=("beginner", "normal", "advanced"),
            default=None,
            help="Configuration profile",
        )
        p.add_argument(
            "--set",
            action="append",
            help="Set parameter (key=value), repeatable",
        )
        p.add_argument(
            "--import-string",
            help="Import claims from base64url string",
        )
        if name == "apply":
            mode_group = p.add_mutually_exclusive_group()
            mode_group.add_argument(
                "--dry-run",
                action="store_true",
                help="Generate execution plan only (default)",
            )
            mode_group.add_argument(
                "--apply",
                action="store_true",
                help="Execute deployment (not available in Phase 12.1)",
            )
            p.add_argument(
                "--confirm-warn",
                action="store_true",
                help="Confirm execution when review level is warn",
            )

    args = parser.parse_args()

    # 1) Load Claims
    if args.import_string:
        if args.set or args.profile is not None:
            raise SystemExit("--import-string cannot be combined with --set or --profile")
        params = decode_claims(args.import_string)
        claims = Claims(params=params, profile="normal", imported=True)
    else:
        claims = load_claims_from_args(args)

    # 2) Planner
    catalog, taxonomy = load_rules(args.version, base_url=args.rules_base_url)
    setattr(claims, "catalog", catalog)
    setattr(claims, "taxonomy", taxonomy)

    apply_plan = plan_apply(claims)
    if getattr(claims, "imported_from_string", False):
        setattr(apply_plan, "imported_claims", True)

    # 3) Review
    print_review(apply_plan, claims=claims)
    review_payload = review_to_dict(apply_plan)

    if args.command == "plan":
        return 0

    if apply_plan.summary.level == "block":
        print("Apply is blocked by planner review.")
        return 1

    if args.apply:
        if apply_plan.summary.level == "warn" and not args.confirm_warn:
            print("Apply requires --confirm-warn when review level is warn.")
            return 1

    mode = "apply" if args.apply else "dry-run"
    inspector = HostInspector()
    base_dir = os.environ.get("MC_PANEL_BASE_DIR", "/opt/mc-instances")
    host_facts = [
        inspector.check_path_exists(base_dir),
        inspector.check_path_writable(base_dir),
    ]
    server_port = _resolve_server_port(claims.params)
    if server_port is not None:
        host_facts.append(inspector.check_port_free(server_port))
    if any(key.startswith("docker.") for key in claims.params.keys()):
        host_facts.append(inspector.check_docker_available())

    plan = build_execution_plan(
        claims=claims,
        review=review_payload,
        host_facts=host_facts,
        mode=mode,
    )
    print_execution_plan(plan)

    if not args.apply:
        return 0

    executor = ExecutionPlanExecutor(inspector=inspector)
    result = executor.execute(plan)
    if not result.ok:
        print("Execution failed.")
        for step in result.steps:
            status = "OK" if step.ok else "FAIL"
            print(f"- {step.name:24} {status} {step.details}")
        return 1

    print("Execution succeeded.")
    for step in result.steps:
        print(f"- {step.name:24} OK {step.details}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
