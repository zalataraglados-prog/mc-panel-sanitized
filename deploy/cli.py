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
from deploy.core.config_model import ConfigModel
from deploy.core.environment import EnvironmentChecker
from deploy.core.instance_namer import InstanceNamer
from deploy.core.port_scanner import PortScanner
from deploy.planner.planner import plan as plan_apply
from deploy.mapper.legacy_config_mapper import map_claims_to_legacy_config
from deploy.executor.executor import Executor, ExecutorError


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

    return Claims(
        params=params,
        profile=args.profile,
    )


# ────────────────────────────────────────
# Review output
# ────────────────────────────────────────


def print_review(apply_plan):
    print("\n=== Apply Plan Review ===")
    print(f"Target: {apply_plan.target}")
    print(f"Level:  {apply_plan.summary.level}")
    print()

    for result in apply_plan.capability_results:
        status = result.status.upper()
        print(f"- {result.capability_id:30} {status}")

    if apply_plan.warnings:
        print("\nWarnings:")
        for w in apply_plan.warnings:
            print(f"  ⚠️ {w.message}")

    if apply_plan.blocks:
        print("\nBlocked:")
        for b in apply_plan.blocks:
            print(f"  ⛔ {b.message}")

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
            "--profile",
            choices=("beginner", "normal", "advanced"),
            default="normal",
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
        claims = decode_claims(args.import_string)
    else:
        claims = load_claims_from_args(args)

    # 2) Planner
    apply_plan = plan_apply(claims)

    # 3) Review
    print_review(apply_plan)

    if args.command == "plan":
        return 0

    # 0) Environment check (apply only)
    env = EnvironmentChecker()
    env.ensure_all()

    # 0) Instance context
    base_path = "/opt/mc-instances"
    panel_src_dir = "/opt/mc-panel-sanitized/web-panel"

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

    # 4) Apply: generate config, map claims, execute
    config_path = os.path.join(ctx.instance_dir, "config.json")
    cfg = ConfigModel(path=config_path)
    cfg.data = ConfigModel.generate_default(
        ctx.instance_name,
        ctx.instance_dir,
        ctx.mc_port,
        ctx.panel_port,
    )
    cfg.data.setdefault("panel", {})
    cfg.data["panel"]["build_path"] = panel_src_dir

    legacy_config = map_claims_to_legacy_config(
        claims=claims,
        base_config=cfg.data,
        apply_plan=apply_plan,
    )
    cfg.data = legacy_config
    cfg.data.setdefault("panel", {})
    cfg.data["panel"]["build_path"] = panel_src_dir
    cfg.save()

    executor = Executor(ctx=ctx)

    try:
        tx = executor.execute(
            apply_plan=apply_plan,
            cfg=cfg,
        )
    except ExecutorError as e:
        print(f"\n❌ Deployment failed: {e}")
        return 1

    # 5) Execution result
    print("\n✅ Deployment succeeded")
    print(f"Transaction ID: {tx.tx_id}")
    print(f"Steps executed: {len(tx.steps)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
