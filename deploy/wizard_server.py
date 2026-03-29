#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
import os
import subprocess
import secrets
import tempfile
import threading
import time
import hmac
import hashlib
import signal
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from deploy.claims_codec.encode import encode_claims
from deploy.loader import load_rules_bundle

ROOT = Path(__file__).resolve().parents[1]
UI_DIR = ROOT / "deploy" / "wizard_ui"
STATE_FILE = Path("/tmp/mc_wizard_state.json")
LOG_PATH = Path("/var/log/mc-wizard.log")
TOKEN_PATH = ROOT / "deploy" / "wizard_token.txt"
PID_FILE = Path("/tmp/mc-wizard.pid")
PROGRESS_FILE = Path("/tmp/mc-wizard-progress.json")
WIZARD_TOKEN = None
TOKEN_TTL_SECONDS = 2 * 60 * 60
TOKEN_LOCK = threading.Lock()
NONCE_TTL_SECONDS = 120
NONCE_LOCK = threading.Lock()
NONCE_STORE = {}

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("LANG", "C.UTF-8")
os.environ.setdefault("LC_ALL", "C.UTF-8")


def _cli_env() -> dict:
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("LANG", "C.UTF-8")
    env.setdefault("LC_ALL", "C.UTF-8")
    return env


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def _terminate_existing(pid: int, timeout: float = 5.0) -> None:
    try:
        os.kill(pid, signal.SIGTERM)
    except Exception:
        return
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not _pid_alive(pid):
            return
        time.sleep(0.2)
    try:
        os.kill(pid, signal.SIGKILL)
    except Exception:
        return



def _load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_state(state):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _parse_params(text):
    params = {}
    for line in (text or "").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        params[key.strip()] = value.strip()
    return params




def _check_ports(ports):
    results = {}
    for p in ports:
        try:
            port = int(p)
        except Exception:
            continue
        if port <= 0 or port > 65535:
            results[str(port)] = {"free": False, "reason": "invalid"}
            continue
        s = None
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("0.0.0.0", port))
            results[str(port)] = {"free": True}
        except Exception as exc:
            results[str(port)] = {"free": False, "reason": str(exc)}
        finally:
            if s:
                try:
                    s.close()
                except Exception:
                    pass
    return results

def _build_claims(state):
    params = _parse_params(state.get("params_text", ""))
    extra = state.get("params") if isinstance(state, dict) else None
    if isinstance(extra, dict):
        for key, value in extra.items():
            if value is None:
                continue
            value = str(value).strip()
            if value == "":
                continue
            params[str(key).strip()] = value
    mode = state.get("import_mode")
    import_value = state.get("import_value")
    if mode == "paste" and import_value:
        return import_value
    if mode == "file" and import_value:
        try:
            return Path(import_value).read_text(encoding="utf-8").strip()
        except Exception:
            pass
    return encode_claims(params)


def _safe_version(value: str | None) -> str:
    version = (value or "1.21.11").strip()
    return version or "1.21.11"


def _safe_profile(value: str | None) -> str:
    profile = (value or "normal").strip().lower()
    if profile not in {"beginner", "normal", "advanced"}:
        return "normal"
    return profile


def _safe_action(value: str) -> str:
    action = (value or "").strip().lower()
    if action not in {"plan", "apply"}:
        raise ValueError("unsupported action")
    return action


def _write_claims_file(claims: str) -> Path:
    payload = (claims or "").replace("\x00", "")
    if len(payload) > 128 * 1024:
        payload = payload[: 128 * 1024]
    temp_dir = Path(tempfile.gettempdir()).resolve()
    temp_dir.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix="mcic-claims-", suffix=".txt", dir=str(temp_dir))
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(payload)
    return Path(name)


def _log_event(ip, action, extra=None):
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "ip": ip,
            "action": action,
        }
        if extra:
            payload.update(extra)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass

def _write_progress(payload):
    try:
        PROGRESS_FILE.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def _read_progress():
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _reset_progress():
    try:
        if PROGRESS_FILE.exists():
            PROGRESS_FILE.unlink()
    except Exception:
        pass


def _extract_instance_dir(output: str | None) -> str | None:
    if not output:
        return None
    for line in output.splitlines():
        if "/opt/mc-instances/" not in line:
            continue
        m = re.search(r"(/opt/mc-instances/[^\s'\"]+)", line)
        if m:
            return m.group(1).rstrip(",")
    return None


def _read_instance_name(instance_dir: str) -> str:
    try:
        cfg_path = Path(instance_dir) / "config.json"
        if cfg_path.exists():
            cfg = json.loads(cfg_path.read_text(encoding="utf-8", errors="ignore") or "{}")
            name = ((cfg.get("instance") or {}).get("name"))
            if name:
                return str(name)
    except Exception:
        pass
    return Path(instance_dir).name


def _collect_service_logs(service: str) -> str:
    chunks = []
    try:
        result = subprocess.run(["systemctl", "status", service, "--no-pager"], capture_output=True, text=True)
        chunks.append(result.stdout or result.stderr or "")
    except Exception:
        pass
    try:
        result = subprocess.run(["journalctl", "-u", service, "-n", "120", "--no-pager"], capture_output=True, text=True)
        chunks.append(result.stdout or result.stderr or "")
    except Exception:
        pass
    return "\n".join([c for c in chunks if c]).strip()


def _run_quiet(cmd: list[str], cwd: str | None = None) -> None:
    try:
        subprocess.run(cmd, cwd=cwd, check=False, capture_output=True, text=True)
    except Exception:
        return


def _teardown_instance(instance_dir: str) -> None:
    instance_name = _read_instance_name(instance_dir)
    service = instance_name if instance_name.endswith(".service") else f"{instance_name}.service"
    _run_quiet(["systemctl", "disable", "--now", service])
    _run_quiet(["systemctl", "stop", service])
    _run_quiet(["docker", "compose", "-p", instance_name, "-f", "docker-compose.yml", "down"], cwd=instance_dir)
    _run_quiet(["docker-compose", "-p", instance_name, "-f", "docker-compose.yml", "down"], cwd=instance_dir)


def _extract_cli_failure_reason(output: str | None) -> str:
    if not output:
        return "apply failed"
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    for line in reversed(lines):
        if line.startswith("- ") and "FAIL" in line:
            return line
    for line in reversed(lines):
        if "HTTP Error" in line or "Not Found" in line or "download" in line.lower():
            return line
    return lines[-1]


def _cleanup_failed(instance_dir: str | None = None) -> None:
    try:
        if Path("/tmp/mcic.lock").exists():
            Path("/tmp/mcic.lock").unlink()
    except Exception:
        pass
    if instance_dir:
        try:
            lock_path = Path(instance_dir) / ".mcic.lock"
            if lock_path.exists():
                lock_path.unlink()
        except Exception:
            pass
        try:
            _teardown_instance(instance_dir)
        except Exception:
            pass
    _reset_progress()


def _check_service_health(instance_dir: str) -> tuple[bool, str]:
    instance_name = _read_instance_name(instance_dir)
    service_name = instance_name
    if service_name.endswith(".service"):
        service_name = service_name[:-8]
    if service_name.startswith("instance-"):
        service = f"{service_name}.service"
    else:
        service = f"instance-{service_name}.service"
    try:
        state = subprocess.run(["systemctl", "is-active", service], capture_output=True, text=True).stdout.strip()
    except Exception:
        state = "unknown"
    restarts = 0
    try:
        raw = subprocess.run(["systemctl", "show", service, "-p", "NRestarts"], capture_output=True, text=True).stdout
        if raw and "=" in raw:
            restarts = int(raw.strip().split("=", 1)[1] or 0)
    except Exception:
        restarts = 0
    if state != "active" or restarts >= 3:
        logs = _collect_service_logs(service)
        return False, f"Service health check failed ({service}, state={state}, restarts={restarts}).\n{logs}"
    return True, ""


def _run_cli(action, state):
    action = _safe_action(action)
    version = _safe_version(state.get("version"))
    profile = _safe_profile(state.get("profile"))
    claims = _build_claims(state)
    claims_file = _write_claims_file(claims)
    if action == "plan":
        cmd = ["python3", "-m", "deploy.cli", "plan"]
    else:
        cmd = ["python3", "-m", "deploy.cli", "apply"]
    cmd.extend(["--version", version, "--profile", profile, "--import-file", str(claims_file)])
    if action == "apply":
        cmd.append("--apply")
        cmd.append("--confirm-warn")
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=_cli_env(),
            shell=False,
        )
    finally:
        try:
            claims_file.unlink()
        except Exception:
            pass
    output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    if proc.returncode == 0 and not output.strip():
        return 1, "no output from cli"
    return proc.returncode, output.strip()


def _run_cli_stream(action, state):
    action = _safe_action(action)
    version = _safe_version(state.get("version"))
    profile = _safe_profile(state.get("profile"))
    claims = _build_claims(state)
    claims_file = _write_claims_file(claims)

    if action == "plan":
        cmd = ["python3", "-m", "deploy.cli", "plan"]
    else:
        cmd = ["python3", "-m", "deploy.cli", "apply"]
    cmd.extend(["--version", version, "--profile", profile, "--import-file", str(claims_file)])

    if action == "apply":
        cmd.append("--apply")
        cmd.append("--confirm-warn")

    proc = subprocess.Popen(
        cmd,
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        env=_cli_env(),
        shell=False,
    )

    try:
        output_lines = []
        in_pre = False
        in_actions = False
        total_pre = 0
        total_actions = 0
        done = 0

        _write_progress({"status": "running", "percent": 1, "message": "starting"})

        if proc.stdout:
            for line in proc.stdout:
                output_lines.append(line)
                stripped = line.strip()

                if stripped.startswith("Preconditions") or stripped.startswith("前置检查"):
                    in_pre = True
                    in_actions = False
                    continue

                if stripped.startswith("Actions") or stripped.startswith("执行动作"):
                    in_actions = True
                    in_pre = False
                    continue

                if in_pre and stripped.startswith("-"):
                    total_pre += 1

                if in_actions and stripped.startswith("-"):
                    total_actions += 1

                if stripped.startswith("- precondition:") or stripped.startswith("- action:"):
                    done += 1
                    total = max(total_pre + total_actions, done)
                    percent = int(min(95, max(1, (done * 100) // total)))
                    _write_progress(
                        {
                            "status": "running",
                            "percent": percent,
                            "message": f"{done}/{total}",
                            "detail": stripped,
                        }
                    )

        proc.wait()

        output = "".join(output_lines)
        ok = proc.returncode == 0
        instance_dir = _extract_instance_dir(output)

        if ok and not output.strip():
            _cleanup_failed(instance_dir)
            _write_progress({"status": "failed", "percent": 95, "message": "failed", "detail": "no output from cli"})
            return 1, ""

        if ok:
            if instance_dir and not os.path.isdir(instance_dir):
                _cleanup_failed(instance_dir)
                _write_progress(
                    {
                        "status": "failed",
                        "percent": 95,
                        "message": "failed",
                        "detail": "instance dir missing (apply likely did not run)",
                    }
                )
                return 1, output.strip()
            if "Execution succeeded." not in output and "执行成功" not in output:
                detail = _extract_cli_failure_reason(output) or "apply did not report success"
                _cleanup_failed(instance_dir)
                _write_progress({"status": "failed", "percent": 95, "message": "failed", "detail": detail})
                return 1, output.strip()

        if not ok:
            detail = _extract_cli_failure_reason(output)
            _cleanup_failed(instance_dir)
            _write_progress({"status": "failed", "percent": 95, "message": "failed", "detail": detail})
            return 1, output.strip()

        if "RCON running at" not in output:
            _write_progress(
                {
                    "status": "waiting",
                    "percent": 95,
                    "message": "waiting for RCON banner...",
                    "detail": "RCON not ready yet",
                }
            )

        if instance_dir:
            deadline = time.time() + 10 * 60
            while True:
                healthy, _ = _check_service_health(instance_dir)
                if healthy:
                    break

                if time.time() > deadline:
                    _cleanup_failed(instance_dir)
                    _write_progress(
                        {
                            "status": "failed",
                            "percent": 95,
                            "message": "failed",
                            "detail": "timeout waiting for systemd active",
                        }
                    )
                    return 1, output.strip()

                _write_progress(
                    {
                        "status": "waiting",
                        "percent": 95,
                        "message": "waiting for systemd active...",
                        "detail": "service not active yet",
                    }
                )
                time.sleep(2)

        _write_progress({"status": "done", "percent": 100, "message": "done"})
        return 0, output.strip()
    finally:
        try:
            claims_file.unlink()
        except Exception:
            pass

def _generate_token():
    global WIZARD_TOKEN
    token = secrets.token_urlsafe(12)
    with TOKEN_LOCK:
        WIZARD_TOKEN = token
    try:
        TOKEN_PATH.write_text(token, encoding="utf-8")
    except Exception:
        pass
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": datetime.utcnow().isoformat() + "Z", "action": "otp", "ttl_seconds": TOKEN_TTL_SECONDS}, ensure_ascii=False) + "\n")
    except Exception:
        pass
    return token

def _write_pid():
    try:
        PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
    except Exception:
        pass

def _cleanup_pid():
    try:
        if PID_FILE.exists():
            PID_FILE.unlink()
    except Exception:
        pass

def _rotate_token_loop():
    while True:
        time.sleep(TOKEN_TTL_SECONDS)
        _generate_token()


def _issue_nonce(ip):
    nonce = secrets.token_urlsafe(16)
    with NONCE_LOCK:
        NONCE_STORE[ip] = {"nonce": nonce, "ts": time.time()}
    return nonce


def _consume_nonce(ip, nonce):
    now = time.time()
    with NONCE_LOCK:
        entry = NONCE_STORE.get(ip)
        if not entry:
            return False
        if entry.get("nonce") != nonce:
            return False
        if now - entry.get("ts", 0) > NONCE_TTL_SECONDS:
            NONCE_STORE.pop(ip, None)
            return False
        NONCE_STORE.pop(ip, None)
        return True


class Handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        parsed = urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self._send(200, b"", content_type="text/html; charset=utf-8")
            return
        self._send(404, b"")


    def _send(self, status=200, body=b"", content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body or b"")))
        self.end_headers()
        if body:
            self.wfile.write(body)
        self.close_connection = True
    def _get_token(self):
        header_token = self.headers.get("X-MCIC-OTP")
        if header_token:
            return header_token.strip()
        return None

    def _require_token(self, payload=None):
        token = self._get_token()
        if not token and payload:
            token = (payload.get("otp") or "").strip()
        with TOKEN_LOCK:
            current = WIZARD_TOKEN
        # legacy OTP header/body
        if token:
            if not current or token != current:
                self._send(401, json.dumps({"error": "Invalid or missing OTP"}).encode("utf-8"))
                return False
            return True
        # signature flow
        nonce = self.headers.get("X-MCIC-NONCE", "").strip()
        sig = self.headers.get("X-MCIC-OTP-SIG", "").strip()
        if not current or not nonce or not sig:
            self._send(401, json.dumps({"error": "Invalid or missing OTP"}).encode("utf-8"))
            return False
        if not _consume_nonce(self.client_address[0], nonce):
            self._send(401, json.dumps({"error": "Invalid or missing OTP"}).encode("utf-8"))
            return False
        host = (self.headers.get("Host") or "").strip()
        msg = f"{nonce}:{host}".encode("utf-8")
        expected = hmac.new(current.encode("utf-8"), msg, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            self._send(401, json.dumps({"error": "Invalid or missing OTP"}).encode("utf-8"))
            return False
        return True


    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type,X-MCIC-OTP,X-MCIC-NONCE,X-MCIC-OTP-SIG")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            if parsed.path == "/api/wizard/state":
                state = _load_state()
                panel_url = os.environ.get("MC_PANEL_URL") or "http://127.0.0.1:15000/"
                state.setdefault("panel_url", panel_url)
                self._send(200, json.dumps(state, ensure_ascii=False).encode("utf-8"))
                return
            if parsed.path == "/api/wizard/nonce":
                nonce = _issue_nonce(self.client_address[0])
                host = (self.headers.get("Host") or "").strip()
                payload = {"nonce": nonce, "ttl_seconds": NONCE_TTL_SECONDS, "host": host}
                self._send(200, json.dumps(payload, ensure_ascii=False).encode("utf-8"))
                return
            if parsed.path == "/api/wizard/progress":
                data = _read_progress()
                self._send(200, json.dumps(data, ensure_ascii=False).encode("utf-8"))
                return
            if parsed.path == "/api/wizard/logs":
                qs = parse_qs(parsed.query or "")
                tail = int(qs.get("tail", ["120"])[0] or 120)
                lines = []
                if LOG_PATH.exists():
                    try:
                        lines = LOG_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
                    except Exception:
                        lines = []
                payload = {"lines": lines[-tail:], "count": len(lines)}
                self._send(200, json.dumps(payload, ensure_ascii=False).encode("utf-8"))
                return
    
        if parsed.path == "/api/wizard/ports":
            qs = parse_qs(parsed.query or "")
            ports = []
            raw = qs.get("ports", [])
            if raw:
                for item in raw:
                    ports.extend([p for p in item.split(",") if p])
            results = _check_ports(ports)
            self._send(200, json.dumps({"ports": results}, ensure_ascii=False).encode("utf-8"))
            return
        if parsed.path == "/api/wizard/catalog":
            try:
                query = urlparse(self.path).query
                version = "1.21.11"
                for part in query.split("&"):
                    if part.startswith("version="):
                        version = part.split("=", 1)[1] or version
                bundle = load_rules_bundle(version)
                payload = {
                    "version": version,
                    "catalog": bundle.get("catalog", {}),
                    "taxonomy": bundle.get("taxonomy", {}),
                    "usability": bundle.get("usability", {}),
                }
                self._send(200, json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            except Exception as exc:
                self._send(500, json.dumps({"error": str(exc)}).encode("utf-8"))
            return


        # --- serve static files for wizard UI ---
        if parsed.path == "/" or parsed.path == "/index.html":
            index_path = UI_DIR / "index.html"
            if index_path.exists():
                data = index_path.read_bytes()
                self._send(200, data, content_type="text/html; charset=utf-8")
                return

        # Serve wizard_script.js
        if parsed.path == "/wizard_script.js":
            js_path = UI_DIR / "wizard_script.js"
            if js_path.exists():
                data = js_path.read_bytes()
                self._send(200, data, content_type="application/javascript; charset=utf-8")
                return
            self._send(404, json.dumps({"error": "Not Found"}).encode("utf-8"))
            return

        # Serve favicon.ico (optional)
        if parsed.path == "/favicon.ico":
            ico_path = UI_DIR / "favicon.ico"
            if ico_path.exists():
                data = ico_path.read_bytes()
                self._send(200, data, content_type="image/x-icon")
                return
            self._send(404, json.dumps({"error": "Not Found"}).encode("utf-8"))
            return

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b""
        try:
            payload = json.loads(raw.decode("utf-8")) if raw else {}
        except Exception:
            payload = {}

        if parsed.path in ("/api/wizard/state", "/api/wizard/plan", "/api/wizard/apply"):
            if not self._require_token(payload):
                return

        if parsed.path == "/api/wizard/state":
            state = _load_state()
            state.update(payload)
            _save_state(state)
            _log_event(self.client_address[0], "state", {"profile": state.get("profile")})
            self._send(200, json.dumps({"ok": True}).encode("utf-8"))
            return

        if parsed.path == "/api/wizard/plan":
            code, output = _run_cli("plan", payload)
            _log_event(self.client_address[0], "plan", {"version": payload.get("version")})
            self._send(200, json.dumps({"ok": code == 0, "output": output}).encode("utf-8"))
            return

        if parsed.path == "/api/wizard/apply":
            code, output = _run_cli_stream("apply", payload)
            _log_event(self.client_address[0], "apply", {"version": payload.get("version")})
            self._send(200, json.dumps({"ok": code == 0, "output": output}).encode("utf-8"))
            return

        self._send(404, json.dumps({"error": "Not Found"}).encode("utf-8"))


def main():
    global WIZARD_TOKEN
    port = int(os.environ.get("MC_PANEL_WIZARD_PORT", "15001"))
    # clean stale pid file / terminate previous instance if needed
    try:
        if PID_FILE.exists():
            try:
                pid = int(PID_FILE.read_text(encoding="utf-8", errors="ignore").strip() or 0)
            except Exception:
                pid = 0
            if pid and _pid_alive(pid):
                _terminate_existing(pid)
            _cleanup_pid()
    except Exception:
        pass

    _generate_token()
    _write_pid()
    rotator = threading.Thread(target=_rotate_token_loop, daemon=True)
    rotator.start()
    host = os.environ.get("MC_PANEL_WIZARD_HOST", "0.0.0.0").strip() or "0.0.0.0"
    server = HTTPServer((host, port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        try:
            server.server_close()
        except Exception:
            pass
        _cleanup_pid()


if __name__ == "__main__":
    main()
