#!/usr/bin/env python3
"""
MC-PANEL CLI (v1.0)

Commands:
  deploy plan
  deploy apply
"""

import argparse
import os
import sys

from deploy.claims_codec import Claims, decode_claims
from deploy.context import InstanceContext
from deploy.core.environment import EnvironmentChecker
from deploy.core.instance_namer import InstanceNamer
from deploy.core.port_scanner import PortScanner
from deploy.loader import load_rules
from deploy.planner.planner import plan as plan_apply
from deploy.executor.executor import Executor, ExecutorError
from deploy.deployment.model import Deployment, DeploymentStatus
from deploy.deployment.store import save_deployment
from deploy.web.review_adapter import review_to_dict


# ────────────────────────────────────────
# Claims construction
# ────────────────────────────────────────


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


# ────────────────────────────────────────
# Review output
# ────────────────────────────────────────


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


# ────────────────────────────────────────
# Main
# ────────────────────────────────────────


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

    # 0) Environment check (apply only)
    env = EnvironmentChecker()
    env.ensure_all()

    # 0) Instance context
    base_path = "/opt/mc-instances"

    namer = InstanceNamer()
    instance_name = namer.ask_name(base_path)
    if not instance_name:
        instance_name = namer.auto_generate(base_path)

    instance_dir = f"{base_path}/{instance_name}"
    os.makedirs(instance_dir, exist_ok=True)

    scanner = PortScanner()
    mc_port = scanner.find_free()
    panel_port = scanner.find_free(start_port=15000)

    ctx = InstanceContext(
        instance_name=instance_name,
        instance_dir=instance_dir,
        mc_port=mc_port,
        panel_port=panel_port,
    )

    # 4) Apply: execute via executor
    deployment = Deployment(
        claims={"profile": claims.profile, "params": claims.params},
        plan_review=review_payload,
    )
    deployment.set_status(DeploymentStatus.APPLYING, note="apply started")
    save_deployment(deployment, os.path.join(ctx.instance_dir, "deployment.json"))

    executor = Executor()

    try:
        result = executor.apply(
            context=ctx,
            claims=claims,
            plan_review=apply_plan,
        )
    except ExecutorError as e:
        deployment.set_status(DeploymentStatus.FAILED, note=str(e))
        save_deployment(deployment, os.path.join(ctx.instance_dir, "deployment.json"))
        print(f"\n❌ Deployment failed: {e}")
        return 1

    deployment.set_status(DeploymentStatus.RUNNING, note="apply completed")
    save_deployment(deployment, os.path.join(ctx.instance_dir, "deployment.json"))

    # 5) Execution result
    print("\n✅ Deployment succeeded")
    print(f"Deployment ID: {deployment.deployment_id}")
    print(f"Transaction ID: {result.tx.tx_id}")
    print(f"Steps executed: {len(result.tx.steps)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
