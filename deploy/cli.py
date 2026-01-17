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
import re
import sys

from deploy.claims_codec import (
    Claims,
    decode_claims,
    decode_compact,
    decode_minimal,
    is_minimal_string,
    is_compact_string,
    peek_version,
    peek_version_min,
)
from deploy.executor.executor_planner import build_execution_plan
from deploy.executor.host_inspector import HostInspector
from deploy.executor.plan_executor import ExecutionPlanExecutor
from deploy.loader import load_rules_bundle
from deploy.panel_manager import install_panel, uninstall_panel
from deploy.planner.planner import plan as plan_apply
from deploy.web.review_adapter import review_to_dict
from deploy.utils.cli_log import log_event


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


def _translate_message(message: str, lang: str) -> str:
    if lang != "zh" or not isinstance(message, str):
        return message
    replacements = {
        "Multiple performance parameters adjusted; consider raising memory or lowering view/simulation distance.": "已同时调整多个性能相关参数，建议增加内存或降低视距/模拟距离。",
        "Configured memory is insufficient for expected players; increase memory or reduce load.": "配置内存不足以支撑预期人数，建议增加内存或降低负载。",
        "Configured memory may be insufficient for expected players; consider increasing memory.": "配置内存可能不足以支撑预期人数，建议增加内存。",
        "Return to default to reduce risk.": "建议恢复默认值以降低风险。",
        "Lowering this value typically improves stability and TPS.": "降低该参数通常可提升稳定性与 TPS。",
        "Increase memory or reduce players/view distance to avoid lag.": "建议增加内存或降低人数/视距以避免卡顿。",
        "Expected player count not set; recommendations may be conservative.": "未设置预期人数，推荐可能偏保守。",
        "Provide expected players to improve recommendations.": "设置预期人数可提高推荐准确性。",
        "View distance may be too high for allocated memory.": "视距可能超出当前内存承受范围。",
        "Reduce view distance for stability.": "建议降低视距以提升稳定性。",
        "Player capacity may be too high for allocated memory.": "最大玩家数可能超出当前内存承受范围。",
        "Lower max players for stability.": "建议降低最大玩家数以提升稳定性。",
        "Simulation distance exceeds view distance.": "模拟距离大于视距。",
        "Align simulation distance with view distance.": "建议将模拟距离与视距对齐。",
    }
    if message in replacements:
        return replacements[message]
    patterns = [
        (
            r"^Medium-risk parameter '(.+)' deviates from default; use default unless you understand the impact\.$",
            "中风险参数 '{param}' 偏离默认值；除非清楚影响，否则建议恢复默认。",
        ),
        (
            r"^High-risk parameter '(.+)' deviates from default; use default unless you understand the impact\.$",
            "高风险参数 '{param}' 偏离默认值；除非清楚影响，否则建议恢复默认。",
        ),
        (r"^Novice-sensitive parameter '(.+)' was explicitly set\.$", "新手敏感参数 '{param}' 被显式设置。"),
        (r"^Player-scope parameter '(.+)' should be set via gamerule\.$", "玩家范围参数 '{param}' 应通过 gamerule 设置。"),
        (r"^World-scope parameter '(.+)' is not applicable to Bedrock Edition\.$", "世界范围参数 '{param}' 不适用于 Bedrock 版。"),
        (r"^Invalid boolean value for '(.+)'\.$", "参数 '{param}' 的布尔值无效。"),
        (r"^Invalid integer value for '(.+)'\.$", "参数 '{param}' 的整数值无效。"),
        (r"^Value for '(.+)' below recommended minimum \((.+)\)\.$", "参数 '{param}' 低于推荐最小值（{extra}）。"),
        (r"^Value for '(.+)' above recommended maximum \((.+)\)\.$", "参数 '{param}' 高于推荐最大值（{extra}）。"),
        (r"^Value for '(.+)' does not align with step (.+)\.$", "参数 '{param}' 不符合步长 {extra}。"),
    ]
    for pattern, template in patterns:
        match = re.match(pattern, message)
        if match:
            param = match.group(1)
            extra = match.group(2) if match.lastindex and match.lastindex >= 2 else ""
            return template.format(param=param, extra=extra)
    return message


def _label(lang: str, text: str) -> str:
    if lang != "zh":
        return text
    mapping = {
        "=== Apply Plan Review ===": "=== 部署评审 ===",
        "Target": "目标",
        "Level": "级别",
        "Source: imported claims": "来源：导入配置",
        "Warnings:": "警告：",
        "Blocked:": "阻止：",
        "Recommendations:": "建议：",
        "=== Execution Plan (dry-run) ===": "=== 执行计划（dry-run）===",
        "parameter": "参数",
    }
    return mapping.get(text, text)


def print_review(apply_plan, claims: Claims | None = None):
    lang = os.environ.get("MC_PANEL_LANG", "en")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print(f"\n{_label(lang, '=== Apply Plan Review ===')}")
    print(f"{_label(lang, 'Target')}: {apply_plan.target}")
    print(f"{_label(lang, 'Level')}:  {apply_plan.summary.level}")
    if claims and getattr(claims, "imported_from_string", False):
        print(_label(lang, "Source: imported claims"))
    print()

    for result in apply_plan.capability_results:
        status = result.status.upper()
        print(f"- {result.capability_id:30} {status}")

    if apply_plan.warnings:
        print(f"\n{_label(lang, 'Warnings:')}")
        for w in apply_plan.warnings:
            print(f"  [WARN] {_translate_message(w.message, lang)}")

    if apply_plan.blocks:
        print(f"\n{_label(lang, 'Blocked:')}")
        for b in apply_plan.blocks:
            print(f"  [BLOCK] {_translate_message(b.message, lang)}")

    if getattr(apply_plan, "recommendations", None):
        print(f"\n{_label(lang, 'Recommendations:')}")
        for r in apply_plan.recommendations:
            param = getattr(r, "param", None)
            reason = getattr(r, "reason", None)
            suggested = getattr(r, "suggested", None)
            label = param or _label(lang, "parameter")
            reason = _translate_message(reason, lang) if isinstance(reason, str) else reason
            if suggested is not None:
                print(f"  [REC] {label} -> {suggested}: {reason}")
            else:
                print(f"  [REC] {label}: {reason}")

    print()


def print_execution_plan(plan) -> None:
    payload = plan.to_dict()
    lang = os.environ.get("MC_PANEL_LANG", "en")
    print(_label(lang, "=== Execution Plan (dry-run) ==="))
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
            "--rules-ref",
            default=None,
            help="Override rules repository ref (tag/commit/branch)",
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
        p.add_argument(
            "--import-file",
            help="Import claims from file path",
        )
        p.add_argument(
            "--import-format",
            choices=("auto", "full", "compact", "min"),
            default="auto",
            help="Claims string format (default: auto)",
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
                "--no-review",
                action="store_true",
                help="Skip review output (use when review is already printed)",
            )
            p.add_argument(
                "--confirm-warn",
                action="store_true",
                help="Confirm execution when review level is warn",
            )

    list_parser = sub.add_parser("instances")
    list_parser.add_argument(
        "--base-dir",
        default=os.environ.get("MC_PANEL_BASE_DIR", "/opt/mc-instances"),
        help="Base directory where instances are stored",
    )

    panel_parser = sub.add_parser("panel")
    panel_sub = panel_parser.add_subparsers(dest="panel_command", required=True)
    panel_install = panel_sub.add_parser("install")
    panel_install.add_argument("--instance-dir", help="Target instance directory")
    panel_install.add_argument(
        "--base-dir",
        default=os.environ.get("MC_PANEL_BASE_DIR", "/opt/mc-instances"),
        help="Base directory where instances are stored",
    )
    panel_install.add_argument("--panel-port", type=int, help="Override panel port")
    panel_install.add_argument("--no-start", action="store_true", help="Do not start service immediately")
    panel_install.add_argument("--no-build", action="store_true", help="Skip frontend build step")
    panel_install.add_argument(
        "--panel-root",
        default=os.environ.get("MC_PANEL_ROOT"),
        help="Panel repository root (default: auto-detect)",
    )

    panel_uninstall = panel_sub.add_parser("uninstall")
    panel_uninstall.add_argument("--instance-dir", help="Target instance directory")
    panel_uninstall.add_argument(
        "--base-dir",
        default=os.environ.get("MC_PANEL_BASE_DIR", "/opt/mc-instances"),
        help="Base directory where instances are stored",
    )

    args = parser.parse_args()

    claims = None
    rules_bundle = None
    if args.command == "instances":
        inspector = HostInspector()
        result = inspector.list_instances(args.base_dir)
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0

    if args.command == "panel":
        if args.panel_command == "install":
            service = install_panel(
                instance_dir=args.instance_dir,
                base_dir=args.base_dir,
                panel_port=args.panel_port,
                start=not args.no_start,
                build_frontend=not args.no_build,
                panel_root=args.panel_root,
            )
            print(f"Panel service installed: {service}")
            return 0
        if args.panel_command == "uninstall":
            service = uninstall_panel(
                instance_dir=args.instance_dir,
                base_dir=args.base_dir,
            )
            print(f"Panel service removed: {service}")
            return 0
        raise SystemExit("Unknown panel command.")

    if args.command in ("plan", "apply"):
        import_string = None
        if args.import_string and args.import_file:
            raise SystemExit("--import-string cannot be combined with --import-file")
        if args.import_string:
            import_string = args.import_string.strip()
        elif args.import_file:
            with open(args.import_file, "r", encoding="utf-8") as handle:
                import_string = handle.read().strip()

        if import_string:
            if args.set:
                raise SystemExit("--import-string cannot be combined with --set")
            format_choice = args.import_format
            if format_choice == "auto":
                if is_compact_string(import_string):
                    format_choice = "compact"
                elif is_minimal_string(import_string):
                    format_choice = "min"
                else:
                    format_choice = "full"

            if format_choice == "compact":
                rules_bundle = load_rules_bundle(
                    peek_version(import_string),
                    base_url=args.rules_base_url,
                    rules_ref=args.rules_ref,
                )
                params = decode_compact(import_string, rules_bundle.get("catalog"))
            elif format_choice == "min":
                rules_bundle = load_rules_bundle(
                    peek_version_min(import_string),
                    base_url=args.rules_base_url,
                    rules_ref=args.rules_ref,
                )
                params = decode_minimal(import_string, rules_bundle.get("catalog"))
            else:
                rules_bundle = load_rules_bundle(
                    args.version,
                    base_url=args.rules_base_url,
                    rules_ref=args.rules_ref,
                )
                params = decode_claims(import_string)
            profile = args.profile or "normal"
            claims = Claims(params=params, profile=profile, imported=True)
        else:
            claims = load_claims_from_args(args)
            rules_bundle = load_rules_bundle(
                args.version,
                base_url=args.rules_base_url,
                rules_ref=args.rules_ref,
            )

        setattr(claims, "catalog", rules_bundle.get("catalog"))
        setattr(claims, "taxonomy", rules_bundle.get("taxonomy"))
        setattr(claims, "usability", rules_bundle.get("usability"))
    else:
        claims = Claims(params={}, profile="normal")

    apply_plan = plan_apply(claims)
    if getattr(claims, "imported_from_string", False):
        setattr(apply_plan, "imported_claims", True)

    # 3) Review
    if not (args.command == "apply" and getattr(args, "no_review", False)):
        print_review(apply_plan, claims=claims)
    review_payload = review_to_dict(apply_plan)
    log_event("review", review_payload)

    if args.command == "plan":
        return 0

    if args.command == "instances":
        inspector = HostInspector()
        base_dir = args.base_dir
        result = inspector.list_instances(base_dir)
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0

    lang = os.environ.get("MC_PANEL_LANG", "en")
    if apply_plan.summary.level == "block":
        if lang == "zh":
            print("已被评审阻止，无法执行 apply。")
        else:
            print("Apply is blocked by planner review.")
        return 1

    if args.apply:
        if apply_plan.summary.level == "warn" and not args.confirm_warn:
            if lang == "zh":
                print("当前为 warn 级别，执行 apply 需要 --confirm-warn。")
            else:
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
    panel_enabled = str(claims.params.get("panel.enable", "false")).lower() in ("true", "1", "yes", "y")
    if panel_enabled:
        host_facts.append(inspector.check_service_exists("mc-panel.service"))

    plan = build_execution_plan(
        claims=claims,
        review=review_payload,
        host_facts=host_facts,
        mode=mode,
    )
    print_execution_plan(plan)
    log_event("execution_plan", plan.to_dict())

    if not args.apply:
        return 0

    executor = ExecutionPlanExecutor(inspector=inspector)
    result = executor.execute(plan)
    if not result.ok:
        if lang == "zh":
            print("执行失败。")
        else:
            print("Execution failed.")
        for step in result.steps:
            status = "OK" if step.ok else "FAIL"
            print(f"- {step.name:24} {status} {step.details}")
        return 1

    if lang == "zh":
        print("执行成功。")
    else:
        print("Execution succeeded.")
    for step in result.steps:
        print(f"- {step.name:24} OK {step.details}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
