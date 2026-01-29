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
import subprocess
import sys
from pathlib import Path
from typing import Optional

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
from backend.runtime.inventory import get_inventory, set_inventory


DEFAULT_INSTANCE_FILE = Path.home() / ".mcic_default"


def _load_default_instance() -> Optional[str]:
    if DEFAULT_INSTANCE_FILE.exists():
        value = DEFAULT_INSTANCE_FILE.read_text(encoding="utf-8", errors="ignore").strip()
        return value or None
    return None


def _save_default_instance(value: str) -> None:
    DEFAULT_INSTANCE_FILE.write_text(value.strip(), encoding="utf-8")


def _list_instance_dirs(base_dir: str) -> list[Path]:
    base = Path(base_dir)
    if not base.exists():
        return []
    result = []
    for entry in base.iterdir():
        if not entry.is_dir():
            continue
        if (entry / "config.json").exists():
            result.append(entry)
    return sorted(result)


def _load_config(instance_dir: Path) -> dict:
    path = instance_dir / "config.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except json.JSONDecodeError:
        return {}


def _resolve_instance_name(instance_dir: Path, cfg: dict | None = None) -> str:
    cfg = cfg or {}
    name = ((cfg.get("instance") or {}).get("name")) if isinstance(cfg, dict) else None
    return name or instance_dir.name


def _resolve_instance_dir(args) -> Path:
    base_dir = getattr(args, "base_dir", None) or os.environ.get("MC_PANEL_BASE_DIR", "/opt/mc-instances")
    if getattr(args, "instance_dir", None):
        return Path(args.instance_dir)
    if getattr(args, "instance", None):
        return Path(base_dir) / args.instance
    env_value = os.environ.get("MCIC_INSTANCE") or os.environ.get("MC_PANEL_INSTANCE")
    if env_value:
        if "/" in env_value:
            return Path(env_value)
        return Path(base_dir) / env_value
    default_value = _load_default_instance()
    if default_value:
        if "/" in default_value:
            return Path(default_value)
        return Path(base_dir) / default_value
    candidates = _list_instance_dirs(base_dir)
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise SystemExit("No instances found. Use --instance or --instance-dir.")
    names = ", ".join(p.name for p in candidates)
    raise SystemExit(f"Multiple instances found. Use --instance. Available: {names}")


def _container_name(instance_dir: Path) -> str:
    cfg = _load_config(instance_dir)
    name = _resolve_instance_name(instance_dir, cfg)
    return f"{name}-minecraft"


def _systemctl_action(action: str, service: str) -> bool:
    result = subprocess.run(["systemctl", action, service], check=False)
    return result.returncode == 0


def _docker_compose_action(instance_dir: Path, instance_name: str, action: str) -> int:
    compose_cmd = None
    if subprocess.run(["docker", "compose", "version"], check=False, capture_output=True).returncode == 0:
        compose_cmd = ["docker", "compose"]
    elif subprocess.run(["docker-compose", "version"], check=False, capture_output=True).returncode == 0:
        compose_cmd = ["docker-compose"]
    if not compose_cmd:
        return 127
    if action == "up":
        cmd = compose_cmd + ["-p", instance_name, "up", "-d", "minecraft"]
    elif action == "down":
        cmd = compose_cmd + ["-p", instance_name, "stop", "minecraft"]
    elif action == "restart":
        cmd = compose_cmd + ["-p", instance_name, "restart", "minecraft"]
    else:
        return 2
    return subprocess.run(cmd, cwd=str(instance_dir), check=False).returncode


def _rcon_exec(instance_dir: Path, command: str) -> str:
    container = _container_name(instance_dir)
    result = subprocess.run(
        ["docker", "exec", "-i", container, "rcon-cli", command],
        check=False,
        capture_output=True,
        text=True,
    )
    return (result.stdout or result.stderr or "").strip()


def _parse_ports(instance_dir: Path) -> dict:
    compose_path = instance_dir / "docker-compose.yml"
    if not compose_path.exists():
        return {}
    ports = {}
    for line in compose_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip().strip('"').strip("'")
        if stripped.startswith("-") and ":" in stripped:
            mapping = stripped.lstrip("-").strip()
            if ":" not in mapping:
                continue
            host, container = mapping.split(":", 1)
            if host.isdigit() and container.isdigit():
                ports[int(container)] = int(host)
    return ports


def _add_instance_args(parser):
    parser.add_argument("--instance-dir", help="Instance directory (optional)")
    parser.add_argument("--instance", help="Instance name (optional)")
    parser.add_argument(
        "--base-dir",
        default=os.environ.get("MC_PANEL_BASE_DIR", "/opt/mc-instances"),
        help="Base directory where instances are stored",
    )


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
        "Provide expected players to improve recommendations.": "设置预期人数可提升推荐准确性。",
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
        "=== Execution Plan (apply) ===": "=== 执行计划（apply）===",
        "Mode": "模式",
        "Review": "评审",
        "Preconditions": "前置检查",
        "Actions": "执行动作",
        "Notes": "备注",
        "Required": "必需",
        "Optional": "可选",
        "Execution Summary": "执行结果",
        "Instance": "实例",
        "MC": "MC",
        "Panel": "面板",
        "Map": "地图",
        "RCON": "RCON",
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


def _first_ipv4(text: str) -> str | None:
    for token in (text or "").split():
        if re.match(r"^\\d+\\.\\d+\\.\\d+\\.\\d+$", token):
            if token.startswith("127."):
                continue
            return token
    return None


def _guess_host_ip() -> str:
    candidates = [
        ["hostname", "-I"],
        ["ip", "route", "get", "1.1.1.1"],
        ["ip", "-4", "addr", "show"],
    ]
    for cmd in candidates:
        try:
            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
            )
            pick = _first_ipv4(result.stdout)
            if pick:
                return pick
        except Exception:
            continue
    return "127.0.0.1"


def _guess_public_ip() -> str | None:
    env_value = os.environ.get("MC_PANEL_PUBLIC_IP")
    if env_value:
        return env_value.strip()
    try:
        result = subprocess.run(
            ["curl", "-fsS", "https://api.ipify.org"],
            check=False,
            capture_output=True,
            text=True,
            timeout=2,
        )
        text = (result.stdout or "").strip()
        if re.match(r"^\\d+\\.\\d+\\.\\d+\\.\\d+$", text):
            return text
    except Exception:
        pass
    return None


def _extract_context(plan) -> dict:
    for action in getattr(plan, "actions", []):
        if action.type != "write_file":
            continue
        context = (action.params or {}).get("context") or {}
        if context.get("INSTANCE_NAME") and context.get("INSTANCE_DIR"):
            return context
    return {}


def print_execution_plan(plan) -> None:
    lang = os.environ.get("MC_PANEL_LANG", "en")
    label = "=== Execution Plan (apply) ===" if getattr(plan, "mode", "") == "apply" else "=== Execution Plan (dry-run) ==="
    print(_label(lang, label))
    print(f"{_label(lang, 'Mode')}: {getattr(plan, 'mode', '')}")
    print(f"{_label(lang, 'Review')}: {getattr(plan, 'review_level', '')}")

    notes = getattr(plan, "meta", {}).get("port_notes", [])
    if notes:
        print(f"\n{_label(lang, 'Notes')}:")
        for note in notes:
            print(f"- {note}")

    print(f"\n{_label(lang, 'Preconditions')}:")
    for pre in getattr(plan, "preconditions", []):
        req = _label(lang, "Required") if pre.required else _label(lang, "Optional")
        print(f"- [{req}] {pre.type} {pre.value}")

    print(f"\n{_label(lang, 'Actions')}:")
    for action in getattr(plan, "actions", []):
        params = action.params or {}
        if action.type == "mkdir":
            detail = params.get("path", "")
        elif action.type == "write_file":
            detail = params.get("path", "")
        elif action.type == "download_file":
            detail = params.get("target", "")
        elif action.type == "systemd_enable_now":
            detail = params.get("service", "")
        else:
            detail = ""
        suffix = f" {detail}" if detail else ""
        print(f"- {action.type}{suffix}")
    print()


def print_execution_summary(plan, claims) -> None:
    lang = os.environ.get("MC_PANEL_LANG", "en")
    context = _extract_context(plan)
    ports = getattr(plan, "meta", {}).get("resolved_ports", {})
    host_ip = _guess_host_ip()
    public_ip = _guess_public_ip()
    display_ip = public_ip or host_ip
    instance_dir = context.get("INSTANCE_DIR", "")
    mc_port = ports.get("mc_port") or context.get("MC_PORT")
    panel_port = ports.get("panel_port") or context.get("PANEL_PORT")
    map_port = ports.get("map_port") or context.get("MAP_PORT")
    rcon_port = ports.get("rcon_port") or context.get("RCON_PORT")
    panel_enabled = str(claims.params.get("panel.enable", "false")).lower() in ("true", "1", "yes", "y")
    map_plugin = claims.params.get("map.plugin")

    print(f"\n{_label(lang, 'Execution Summary')}:")
    if instance_dir:
        print(f"- {_label(lang, 'Instance')}: {instance_dir}")
    if public_ip and public_ip != host_ip:
        print(f"- Public IP: {public_ip}")
        print(f"- Private IP: {host_ip}")
    if mc_port:
        print(f"- {_label(lang, 'MC')}: {display_ip}:{mc_port}")
    if panel_enabled and panel_port:
        print(f"- {_label(lang, 'Panel')}: http://{display_ip}:{panel_port}/")
    if map_plugin and map_port:
        print(f"- {_label(lang, 'Map')}: http://{display_ip}:{map_port}/")
    if rcon_port:
        print(f"- {_label(lang, 'RCON')}: {display_ip}:{rcon_port}")
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
            default="1.21.11",
            help="Minecraft version for rule lookup (default: 1.21.11)",
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

    mcic_ls = sub.add_parser("ls")
    mcic_ls.add_argument(
        "--base-dir",
        default=os.environ.get("MC_PANEL_BASE_DIR", "/opt/mc-instances"),
        help="Base directory where instances are stored",
    )

    mcic_use = sub.add_parser("use")
    mcic_use.add_argument("instance", help="Instance name or path")
    mcic_use.add_argument(
        "--base-dir",
        default=os.environ.get("MC_PANEL_BASE_DIR", "/opt/mc-instances"),
        help="Base directory where instances are stored",
    )

mcic_tui = sub.add_parser(
        "tui",
        help="Run CLI deploy flow (backup when panel is unavailable)",
    )
    mcic_tui.add_argument(
        "mode",
        nargs="?",
        choices=("plan", "apply"),
        default="apply",
        help="Run plan or apply (default: apply)",
    )
    mcic_tui.add_argument(
        "tui_args",
        nargs=argparse.REMAINDER,
        help="Arguments passed to deploy CLI (e.g. --version/--profile/--import-*)",
    )

    for name in ("up", "down", "restart", "status", "logs", "ports", "players", "op", "deop", "tp", "kick", "ban", "unban", "inv", "inv-export", "inv-import", "map", "map-reload", "diag"):
        p = sub.add_parser(name)
        _add_instance_args(p)
        if name in ("op", "deop", "kick", "ban", "unban", "inv", "inv-export", "inv-import", "tp"):
            p.add_argument("player", help="Player name")
        if name == "op":
            p.add_argument("level", nargs="?", help="OP level (optional, ignored in modern versions)")
        if name == "tp":
            p.add_argument("x")
            p.add_argument("y")
            p.add_argument("z")
        if name in ("kick", "ban"):
            p.add_argument("reason", nargs=argparse.REMAINDER)
        if name == "inv-export":
            p.add_argument("--out", help="Output file path")
        if name == "inv-import":
            p.add_argument("file", help="JSON file path")

    args = parser.parse_args()

    # mcic commands
    if args.command == "ls":
        instances = _list_instance_dirs(args.base_dir)
        for entry in instances:
            print(entry.name)
        return 0

    if args.command == "use":
        value = args.instance
        base_dir = args.base_dir
        if "/" not in value:
            value = str(Path(base_dir) / value)
        _save_default_instance(value)
        print(f"Default instance set to {value}")
        return 0

    if args.command == "tui":
        mode = args.mode or "apply"
        cmd = [sys.executable, "-m", "deploy.cli", mode]
        if mode == "apply":
            cmd.append("--apply")
        if getattr(args, "tui_args", None):
            cmd += args.tui_args
        return subprocess.run(cmd, check=False).returncode

    if args.command in ("up", "down", "restart", "status", "logs", "ports", "players", "op", "deop", "tp", "kick", "ban", "unban", "inv", "inv-export", "inv-import", "map", "map-reload", "diag"):
        instance_dir = _resolve_instance_dir(args)
        cfg = _load_config(instance_dir)
        instance_name = _resolve_instance_name(instance_dir, cfg)
        service_name = f"instance-{instance_name}"

        if args.command in ("up", "down", "restart"):
            action = "start" if args.command == "up" else "stop" if args.command == "down" else "restart"
            if _systemctl_action(action, f"{service_name}.service"):
                print(f"{action} ok")
                return 0
            fallback = _docker_compose_action(instance_dir, instance_name, args.command if args.command != "up" else "up")
            if fallback == 0:
                print(f"{action} ok (docker compose)")
                return 0
            raise SystemExit(f"Failed to {action} instance ({instance_name})")

        if args.command == "status":
            container = _container_name(instance_dir)
            result = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], check=False, capture_output=True, text=True)
            running = container in (result.stdout or "").splitlines()
            print(json.dumps({"instance": instance_name, "running": running}, ensure_ascii=True))
            return 0

        if args.command == "logs":
            subprocess.run(["docker", "logs", "--tail", "200", _container_name(instance_dir)], check=False)
            return 0

        if args.command == "ports":
            ports = _parse_ports(instance_dir)
            print(json.dumps(ports, ensure_ascii=True, indent=2))
            return 0

        if args.command == "players":
            print(_rcon_exec(instance_dir, "list"))
            return 0

        if args.command in ("op", "deop", "kick", "ban", "unban", "tp"):
            if args.command == "op":
                cmd = f"op {args.player}"
            elif args.command == "deop":
                cmd = f"deop {args.player}"
            elif args.command == "tp":
                cmd = f"tp {args.player} {args.x} {args.y} {args.z}"
            elif args.command == "kick":
                reason = " ".join(args.reason) if args.reason else ""
                cmd = f"kick {args.player} {reason}".strip()
            elif args.command == "ban":
                reason = " ".join(args.reason) if args.reason else ""
                cmd = f"ban {args.player} {reason}".strip()
            else:
                cmd = f"pardon {args.player}"
            print(_rcon_exec(instance_dir, cmd))
            if args.command == "op" and getattr(args, "level", None):
                print("Note: OP level is ignored by modern servers.")
            return 0

        if args.command == "inv":
            payload = get_inventory(str(instance_dir), args.player)
            print(json.dumps(payload, ensure_ascii=True, indent=2))
            return 0

        if args.command == "inv-export":
            payload = get_inventory(str(instance_dir), args.player)
            items = payload.get("items", [])
            output = json.dumps(items, ensure_ascii=True, indent=2)
            if args.out:
                Path(args.out).write_text(output, encoding="utf-8")
            else:
                print(output)
            return 0

        if args.command == "inv-import":
            raw = Path(args.file).read_text(encoding="utf-8")
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"Invalid JSON: {exc}")
            items = data.get("items") if isinstance(data, dict) else data
            if not isinstance(items, list):
                raise SystemExit("Invalid inventory JSON: expected list of items or {items:[...]}")
            result = set_inventory(str(instance_dir), args.player, items)
            print(json.dumps(result, ensure_ascii=True, indent=2))
            return 0

        if args.command == "map":
            ports = _parse_ports(instance_dir)
            map_port = ports.get(8100, 8100)
            host = _guess_host_ip()
            print(f"http://{host}:{map_port}/")
            return 0

        if args.command == "map-reload":
            print(_rcon_exec(instance_dir, "bluemap reload"))
            return 0

        if args.command == "diag":
            info = {
                "base_dir": str(instance_dir.parent),
                "instance": instance_name,
                "container": _container_name(instance_dir),
            }
            print(json.dumps(info, ensure_ascii=True, indent=2))
            return 0

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
    print_execution_summary(plan, claims)
    return 0


if __name__ == "__main__":
    sys.exit(main())

