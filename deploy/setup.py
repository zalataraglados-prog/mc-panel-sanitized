#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path


def _bootstrap_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root))


_bootstrap_path()

from deploy.core.environment import EnvironmentChecker  # noqa: E402
from deploy.core.instance_namer import InstanceNamer  # noqa: E402
from deploy.core.port_scanner import PortScanner  # noqa: E402
from deploy.core.config_model import ConfigModel  # noqa: E402
from deploy.core.composer import Composer  # noqa: E402
from deploy.core.systemd_gen import SystemdGenerator  # noqa: E402
from deploy.core.deployer import Deployer  # noqa: E402


BASE_INST_DIR = "/opt/mc-instances"
DEFAULT_PANEL_SRC = "/opt/mc-panel-sanitized/web-panel"


def _read_input(prompt: str) -> str:
    if sys.stdin and sys.stdin.isatty():
        try:
            return input(prompt)
        except EOFError:
            return ""
    tty_path = "CON" if os.name == "nt" else "/dev/tty"
    try:
        with open(tty_path, "r") as tty:
            print(prompt, end="", flush=True)
            return tty.readline()
    except Exception:
        return ""


def _require_root() -> None:
    if hasattr(os, "geteuid"):
        if os.geteuid() != 0:
            print("Please run with sudo/root privileges.")
            sys.exit(1)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minecraft instance setup")
    parser.add_argument("--name", help="Instance name")
    parser.add_argument("--auto", action="store_true", help="Auto-assign ports")
    parser.add_argument("--mc-port", type=int, help="Minecraft server port")
    parser.add_argument("--panel-port", type=int, help="Panel port")
    parser.add_argument("--panel-path", default=DEFAULT_PANEL_SRC, help="Web panel source path")
    parser.add_argument("--base-dir", default=BASE_INST_DIR, help="Base instance directory")
    return parser.parse_args()


def _choose_instance_name(base_dir: str, name_arg: str | None) -> str:
    if name_arg:
        clean = InstanceNamer.sanitize(name_arg)
        if not clean:
            clean = InstanceNamer.auto_generate(base_dir)
        return InstanceNamer.handle_conflict(base_dir, clean)
    return InstanceNamer.ask_name(base_dir)


def _choose_ports(args: argparse.Namespace) -> tuple[int, int]:
    if args.auto:
        mc_port = PortScanner.find_free()
        panel_port = PortScanner.find_free(start_port=15000)
        return mc_port, panel_port

    mc_port = args.mc_port
    panel_port = args.panel_port

    if mc_port is None:
        auto_choice = _read_input("Auto-assign ports? [Y/n]: ").strip().lower()
        if auto_choice in ("", "y", "yes"):
            mc_port = PortScanner.find_free()
            panel_port = PortScanner.find_free(start_port=15000)
            return mc_port, panel_port
        val = _read_input("Minecraft port [25565]: ").strip()
        mc_port = int(val) if val.isdigit() else 25565

    if panel_port is None:
        val = _read_input("Panel port [15000]: ").strip()
        panel_port = int(val) if val.isdigit() else 15000

    return mc_port, panel_port


def main() -> None:
    _require_root()
    args = _parse_args()

    print("[INFO] Minecraft setup starting")

    env = EnvironmentChecker()
    print("[INFO] Checking runtime environment...")
    env.ensure_all()
    print("[INFO] Environment OK")

    base_dir = args.base_dir
    os.makedirs(base_dir, exist_ok=True)

    instance_name = _choose_instance_name(base_dir, args.name)
    mc_port, panel_port = _choose_ports(args)

    inst_dir = os.path.join(base_dir, instance_name)
    os.makedirs(inst_dir, exist_ok=True)
    print(f"[INFO] Instance directory created: {inst_dir}")

    cfg_obj = ConfigModel.auto_generate(inst_dir, instance_name, mc_port, panel_port)
    cfg_obj.data.setdefault("panel", {})
    cfg_obj.data["panel"]["build_path"] = args.panel_path
    cfg_obj.save()

    composer = Composer(cfg=cfg_obj, instance_dir=inst_dir, web_panel_path=args.panel_path)
    composer.generate()

    systemd = SystemdGenerator(cfg_obj.instance_name, inst_dir)
    systemd.generate()

    dp = Deployer(cfg_obj.instance_name, inst_dir)
    print("[INFO] Deploying instance...")
    dp.run()


if __name__ == "__main__":
    main()
