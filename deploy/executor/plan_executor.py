from __future__ import annotations

import json
import os
import shutil
import subprocess
import urllib.request
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List

from deploy.executor.execution_plan import ExecutionPlan
from deploy.executor.host_inspector import HostInspector


@dataclass
class ExecutionStep:
    name: str
    ok: bool
    details: str = ""


@dataclass
class ExecutionResult:
    ok: bool
    steps: List[ExecutionStep] = field(default_factory=list)
    rollback_pending: bool = False
    log_path: str | None = None


class ExecutionPlanExecutor:
    def __init__(self, inspector: HostInspector | None = None):
        self.inspector = inspector or HostInspector()
        self._systemd_reloaded = False

    def _check_precondition(self, precondition) -> ExecutionStep:
        check_type = precondition.type
        value = precondition.value
        if check_type == "path_exists":
            result = self.inspector.check_path_exists(value)
        elif check_type == "path_writable":
            result = self.inspector.check_path_writable(value)
        elif check_type == "port_free":
            result = self.inspector.check_port_free(int(value))
        elif check_type == "docker_available":
            result = self.inspector.check_docker_available()
        elif check_type == "docker_daemon":
            result = self.inspector.check_docker_daemon()
        elif check_type == "docker_compose":
            result = self.inspector.check_docker_compose()
        elif check_type == "systemd_available":
            result = self.inspector.check_systemd_available()
        elif check_type == "systemd_pid1":
            result = self.inspector.check_systemd_pid1()
        elif check_type == "selinux_enforcing":
            result = self.inspector.check_selinux_enforcing()
        elif check_type == "apparmor_enabled":
            result = self.inspector.check_apparmor_enabled()
        elif check_type == "ufw_active":
            result = self.inspector.check_ufw_active()
        elif check_type == "dns_configured":
            result = self.inspector.check_dns_configured()
        elif check_type == "swap_available":
            result = self.inspector.check_swap_available()
        elif check_type == "disk_free":
            result = self.inspector.check_disk_free(value)
        elif check_type == "mount_noexec":
            result = self.inspector.check_mount_noexec(value)
        elif check_type == "docker_rootless":
            result = self.inspector.check_docker_rootless()
        elif check_type == "time_sync":
            result = self.inspector.check_time_sync()
        elif check_type == "ipv4_available":
            result = self.inspector.check_ipv4_available()
        elif check_type == "file_exists":
            result = self.inspector.check_file_exists(value)
        elif check_type == "memory_available":
            try:
                required = float(value)
            except Exception:
                return ExecutionStep(
                    name="precondition:memory_available",
                    ok=False,
                    details="invalid required_gb",
                )
            result = self.inspector.check_memory_available(required)
        elif check_type == "capacity_sufficient":
            try:
                memory = float(value.get("memory_gb"))
                required = float(value.get("required_gb"))
                ok = memory >= required and memory >= 2.0
                details = f"memory_gb={memory} required_gb={required}"
            except Exception:
                return ExecutionStep(
                    name="precondition:capacity_sufficient",
                    ok=False,
                    details="invalid capacity payload",
                )
            return ExecutionStep(
                name="precondition:capacity_sufficient",
                ok=ok,
                details=details,
            )
        else:
            return ExecutionStep(
                name=f"precondition:{check_type}",
                ok=False,
                details="unknown precondition type",
            )
        return ExecutionStep(
            name=f"precondition:{check_type}",
            ok=bool(result.get("ok")),
            details=str(result.get("details", "")),
        )

    def _execute_action(self, action) -> ExecutionStep:
        action_type = action.type
        params: Dict[str, Any] = action.params or {}

        if action_type == "mkdir":
            path = params.get("path")
            if not path:
                return ExecutionStep(name="action:mkdir", ok=False, details="missing path")
            os.makedirs(path, exist_ok=True)
            return ExecutionStep(name="action:mkdir", ok=True, details=path)

        if action_type == "chown":
            path = params.get("path")
            uid = params.get("uid")
            gid = params.get("gid")
            recursive = bool(params.get("recursive", True))
            if not path:
                return ExecutionStep(name="action:chown", ok=False, details="missing path")
            if uid is None or gid is None:
                return ExecutionStep(name="action:chown", ok=False, details="missing uid/gid")
            try:
                if isinstance(uid, str):
                    import pwd

                    uid = pwd.getpwnam(uid).pw_uid
                if isinstance(gid, str):
                    import grp

                    gid = grp.getgrnam(gid).gr_gid
            except Exception as exc:
                return ExecutionStep(name="action:chown", ok=False, details=f"resolve uid/gid failed: {exc}")
            try:
                if recursive and os.path.isdir(path):
                    for root, dirs, files in os.walk(path):
                        os.chown(root, int(uid), int(gid))
                        for entry in dirs:
                            os.chown(os.path.join(root, entry), int(uid), int(gid))
                        for entry in files:
                            os.chown(os.path.join(root, entry), int(uid), int(gid))
                else:
                    os.chown(path, int(uid), int(gid))
            except Exception as exc:
                return ExecutionStep(name="action:chown", ok=False, details=str(exc))
            return ExecutionStep(name="action:chown", ok=True, details=path)

        if action_type == "write_file":
            path = params.get("path")
            content = params.get("content")
            template = params.get("template")
            if template and content is None:
                context = params.get("context", {})
                content = self._render_template(template, context)
            if path is None or content is None:
                return ExecutionStep(
                    name="action:write_file",
                    ok=False,
                    details="missing path/content",
                )
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(content)
            return ExecutionStep(name="action:write_file", ok=True, details=path)

        if action_type == "symlink":
            source = params.get("source")
            target = params.get("target")
            if not source or not target:
                return ExecutionStep(name="action:symlink", ok=False, details="missing source/target")
            if os.path.lexists(target):
                os.remove(target)
            os.symlink(source, target)
            return ExecutionStep(name="action:symlink", ok=True, details=f"{source} -> {target}")

        if action_type == "setup_panel_venv":
            panel_root = params.get("panel_root")
            requirements = params.get("requirements") or []
            if not panel_root:
                return ExecutionStep(name="action:setup_panel_venv", ok=False, details="missing panel_root")
            venv_dir = os.path.join(panel_root, ".venv")
            python_bin = os.path.join(venv_dir, "bin", "python")
            pip_bin = os.path.join(venv_dir, "bin", "pip")
            try:
                if not os.path.exists(python_bin):
                    result = subprocess.run(
                        ["python3", "-m", "venv", venv_dir],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode != 0:
                        message = (result.stderr or result.stdout or "").strip()
                        if (
                            "No module named venv" in message
                            and os.geteuid() == 0
                            and shutil.which("apt-get")
                        ):
                            subprocess.run(["apt-get", "update"], check=False)
                            subprocess.run(["apt-get", "install", "-y", "python3-venv"], check=True)
                            subprocess.run(["python3", "-m", "venv", venv_dir], check=True)
                        else:
                            return ExecutionStep(
                                name="action:setup_panel_venv",
                                ok=False,
                                details=f"venv creation failed: {message or 'unknown error'}",
                            )
                if not os.path.exists(pip_bin):
                    subprocess.run([python_bin, "-m", "ensurepip", "--upgrade"], check=False)
                if not os.path.exists(pip_bin):
                    return ExecutionStep(
                        name="action:setup_panel_venv",
                        ok=False,
                        details="pip missing in venv",
                    )
                req_file = os.path.join(panel_root, "backend", "requirements.txt")
                if os.path.exists(req_file):
                    cmd = [pip_bin, "install", "-r", req_file]
                elif requirements:
                    cmd = [pip_bin, "install", *requirements]
                else:
                    return ExecutionStep(
                        name="action:setup_panel_venv",
                        ok=True,
                        details="no requirements specified",
                    )
                env = os.environ.copy()
                env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
                env["PIP_NO_INPUT"] = "1"
                subprocess.run(cmd, check=True, env=env)
            except subprocess.CalledProcessError as exc:
                return ExecutionStep(
                    name="action:setup_panel_venv",
                    ok=False,
                    details=f"venv setup failed: {exc}",
                )
            except Exception as exc:
                return ExecutionStep(
                    name="action:setup_panel_venv",
                    ok=False,
                    details=f"venv setup failed: {exc}",
                )
            return ExecutionStep(name="action:setup_panel_venv", ok=True, details=venv_dir)

        if action_type == "copy_map":
            source = params.get("source")
            target = params.get("target")
            overwrite = params.get("overwrite", False)
            if not source or not target:
                return ExecutionStep(name="action:copy_map", ok=False, details="missing source/target")
            if not os.path.exists(source):
                return ExecutionStep(name="action:copy_map", ok=False, details="source missing")
            if os.path.exists(target):
                if overwrite:
                    if os.path.isdir(target):
                        shutil.rmtree(target)
                    else:
                        os.remove(target)
                else:
                    return ExecutionStep(
                        name="action:copy_map",
                        ok=False,
                        details="target exists and overwrite disabled",
                    )
            os.makedirs(os.path.dirname(target), exist_ok=True)
            if os.path.isdir(source):
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
            return ExecutionStep(name="action:copy_map", ok=True, details=f"{source} -> {target}")

        if action_type == "download_file":
            url = params.get("url")
            target = params.get("target")
            overwrite = params.get("overwrite", False)
            if not url or not target:
                return ExecutionStep(name="action:download_file", ok=False, details="missing url/target")
            if os.path.exists(target) and not overwrite:
                return ExecutionStep(
                    name="action:download_file",
                    ok=False,
                    details="target exists and overwrite disabled",
                )
            os.makedirs(os.path.dirname(target), exist_ok=True)
            try:
                self._download_file(url, target)
            except Exception as exc:
                self._log_source_issue(
                    issue_type="download_file",
                    url=url,
                    target=target,
                    error=str(exc),
                )
                return ExecutionStep(name="action:download_file", ok=False, details=str(exc))
            return ExecutionStep(name="action:download_file", ok=True, details=target)

        if action_type == "systemd_enable_now":
            service = params.get("service")
            compose_dir = params.get("compose_dir")
            compose_service = params.get("compose_service", "")
            panel_root = params.get("panel_root")
            panel_port = params.get("panel_port")
            if not service:
                return ExecutionStep(name="action:systemd_enable_now", ok=False, details="missing service")
            try:
                if not self._systemd_reloaded:
                    subprocess.run(["systemctl", "daemon-reload"], check=True)
                    self._systemd_reloaded = True
                start = subprocess.run(
                    ["systemctl", "enable", "--now", service],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                active = subprocess.run(["systemctl", "is-active", "--quiet", service])
                if start.returncode != 0 or active.returncode != 0:
                    fallback_step = self._fallback_start_service(
                        service=service,
                        compose_dir=compose_dir,
                        compose_service=compose_service,
                        panel_root=panel_root,
                        panel_port=panel_port,
                        error=(start.stderr or start.stdout or "").strip(),
                    )
                    if fallback_step is not None:
                        return fallback_step
                    err = (start.stderr or start.stdout or "").strip()
                    return ExecutionStep(
                        name="action:systemd_enable_now",
                        ok=False,
                        details=err or f"{service} not active after start",
                    )
            except subprocess.CalledProcessError as exc:
                fallback_step = self._fallback_start_service(
                    service=service,
                    compose_dir=compose_dir,
                    compose_service=compose_service,
                    panel_root=panel_root,
                    panel_port=panel_port,
                    error=str(exc),
                )
                if fallback_step is not None:
                    return fallback_step
                return ExecutionStep(
                    name="action:systemd_enable_now",
                    ok=False,
                    details=str(exc),
                )
            return ExecutionStep(name="action:systemd_enable_now", ok=True, details=service)

        return ExecutionStep(
            name=f"action:{action_type}",
            ok=False,
            details="unsupported action type",
        )

    def _fallback_start_service(
        self,
        *,
        service: str,
        compose_dir: str | None,
        compose_service: str,
        panel_root: str | None,
        panel_port: int | None,
        error: str,
    ) -> ExecutionStep | None:
        if compose_dir and shutil.which("docker"):
            compose_cmd = self._resolve_compose_command()
            if compose_cmd is None:
                return ExecutionStep(
                    name="action:systemd_enable_now",
                    ok=False,
                    details="fallback failed: docker compose not available",
                )
            try:
                if shutil.which("systemctl"):
                    subprocess.run(["systemctl", "start", "docker"], check=False, capture_output=True, text=True)
                cmd = [*compose_cmd, "up", "-d"]
                if compose_service:
                    cmd.append(compose_service)
                subprocess.run(
                    cmd,
                    cwd=compose_dir,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                return ExecutionStep(
                    name="action:systemd_enable_now",
                    ok=True,
                    details=f"{service} not active; started via docker compose fallback",
                )
            except subprocess.TimeoutExpired:
                return ExecutionStep(
                    name="action:systemd_enable_now",
                    ok=True,
                    details=f"{service} not active; docker compose up timed out",
                )
            except subprocess.CalledProcessError as exc:
                detail = (exc.stderr or exc.stdout or str(exc)).strip()
                return ExecutionStep(
                    name="action:systemd_enable_now",
                    ok=False,
                    details=f"fallback failed: {detail}",
                )
        if panel_root and panel_port:
            venv_python = os.path.join(panel_root, ".venv", "bin", "python")
            if os.path.isfile(venv_python):
                log_dir = os.path.join(panel_root, "logs")
                os.makedirs(log_dir, exist_ok=True)
                log_path = os.path.join(log_dir, "panel_no_systemd.log")
                cmd = (
                    f"nohup {venv_python} -m uvicorn backend.main:app "
                    f"--host 0.0.0.0 --port {panel_port} > {log_path} 2>&1 &"
                )
                subprocess.run(["/bin/sh", "-c", cmd], cwd=panel_root, check=False)
                return ExecutionStep(
                    name="action:systemd_enable_now",
                    ok=True,
                    details=f"{service} not active; started without systemd",
                )
        if error:
            return None
        return None

    def _resolve_compose_command(self) -> List[str] | None:
        if shutil.which("docker"):
            try:
                result = subprocess.run(
                    ["docker", "compose", "version"],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    return ["docker", "compose"]
            except Exception:
                pass
        if shutil.which("docker-compose"):
            try:
                result = subprocess.run(
                    ["docker-compose", "version"],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    return ["docker-compose"]
            except Exception:
                pass
        return None

    def _download_file(self, url: str, target: str) -> None:
        request = urllib.request.Request(url, headers={"User-Agent": "mc-panel"})
        with urllib.request.urlopen(request, timeout=30) as response:
            with open(target, "wb") as handle:
                shutil.copyfileobj(response, handle)

    def _log_source_issue(self, *, issue_type: str, url: str, target: str, error: str) -> None:
        base_dir = os.environ.get("MC_PANEL_ROOT") or os.getcwd()
        log_dir = os.environ.get("MC_PANEL_LOG_DIR") or os.path.join(base_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "plugin_download.log")
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": issue_type,
            "url": url,
            "target": target,
            "error": error,
        }
        try:
            with open(log_path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, ensure_ascii=True))
                handle.write("\n")
        except Exception:
            return

        if str(os.environ.get("MC_PANEL_LOG_PUSH", "")).lower() not in ("1", "true", "yes"):
            return
        self._push_log(log_path, base_dir)

    def _push_log(self, log_path: str, base_dir: str) -> None:
        if not shutil.which("git"):
            return
        branch = os.environ.get("MC_PANEL_LOG_BRANCH", "logs")
        worktree = os.environ.get("MC_PANEL_LOG_WORKTREE") or os.path.join(base_dir, ".logs-worktree")
        log_rel = os.path.relpath(log_path, base_dir)
        log_target = os.path.join(worktree, log_rel)
        try:
            if not os.path.isdir(worktree):
                subprocess.run(
                    ["git", "-C", base_dir, "worktree", "add", "-B", branch, worktree],
                    check=False,
                    capture_output=True,
                    text=True,
                )
            os.makedirs(os.path.dirname(log_target), exist_ok=True)
            shutil.copy2(log_path, log_target)
            subprocess.run(
                ["git", "-C", worktree, "add", log_rel],
                check=False,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "-C", worktree, "commit", "-m", "Update plugin download log"],
                check=False,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "-C", worktree, "push", "origin", branch],
                check=False,
                capture_output=True,
                text=True,
            )
        except Exception:
            return

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))
        template_path = os.path.join(base_dir, template_name)
        if not os.path.exists(template_path):
            raise RuntimeError(f"Template not found: {template_name}")
        with open(template_path, "r", encoding="utf-8") as handle:
            raw = handle.read()
        rendered = raw
        for key, value in context.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
        return rendered

    def execute(self, plan: ExecutionPlan) -> ExecutionResult:
        steps: List[ExecutionStep] = []
        executed_actions: List[ExecutionStep] = []

        for pre in plan.preconditions:
            step = self._check_precondition(pre)
            steps.append(step)
            if pre.required and not step.ok:
                result = ExecutionResult(ok=False, steps=steps, rollback_pending=False)
                result.log_path = self._write_log(plan, result)
                return result

        for action in plan.actions:
            step = self._execute_action(action)
            steps.append(step)
            executed_actions.append(step)
            if not step.ok:
                result = ExecutionResult(ok=False, steps=steps, rollback_pending=bool(executed_actions))
                result.log_path = self._write_log(plan, result)
                return result

        result = ExecutionResult(ok=True, steps=steps)
        result.log_path = self._write_log(plan, result)
        return result

    def _write_log(self, plan: ExecutionPlan, result: ExecutionResult) -> str | None:
        instance_dir = None
        for action in plan.actions:
            if action.type == "mkdir":
                instance_dir = action.params.get("path")
                break
        if not instance_dir:
            return None
        try:
            os.makedirs(instance_dir, exist_ok=True)
            log_path = os.path.join(instance_dir, "execution_result.json")
            payload = {
                "ok": result.ok,
                "rollback_pending": result.rollback_pending,
                "steps": [
                    {"name": step.name, "ok": step.ok, "details": step.details}
                    for step in result.steps
                ],
                "plan": plan.to_dict(),
            }
            with open(log_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2, ensure_ascii=True)
                handle.write("\n")
            return log_path
        except Exception:
            return None
