#!/usr/bin/env python3
import json
import os
import subprocess
import secrets
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

from deploy.claims_codec.encode import encode_claims
from deploy.loader import load_rules_bundle

ROOT = Path(__file__).resolve().parents[1]
UI_DIR = ROOT / "deploy" / "wizard_ui"
STATE_FILE = Path("/tmp/mc_wizard_state.json")
LOG_PATH = Path("/var/log/mc-wizard.log")
TOKEN_PATH = ROOT / "deploy" / "wizard_token.txt"
WIZARD_TOKEN = None
TOKEN_TTL_SECONDS = 2 * 60 * 60
TOKEN_LOCK = threading.Lock()


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


def _build_claims(state):
    params = _parse_params(state.get("params_text", ""))
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


def _run_cli(action, state):
    version = state.get("version") or "1.21.11"
    profile = state.get("profile") or "normal"
    claims = _build_claims(state)
    cmd = ["python3", "-m", "deploy.cli", action, "--version", version, "--profile", profile, "--import-string", claims]
    if action == "apply":
        cmd.append("--confirm-warn")
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    return proc.returncode, output.strip()


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
            f.write(json.dumps({"ts": datetime.utcnow().isoformat() + "Z", "action": "otp", "otp": token, "ttl_seconds": TOKEN_TTL_SECONDS}, ensure_ascii=False) + \"\n\")
    except Exception:
        pass
    return token


def _rotate_token_loop():
    while True:
        time.sleep(TOKEN_TTL_SECONDS)
        _generate_token()


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
        self.end_headers()
        if body:
            self.wfile.write(body)
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
        if not current or not token or token != current:
            self._send(401, json.dumps({"error": "Invalid or missing OTP"}).encode("utf-8"))
            return False
        return True


    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type,X-MCIC-OTP")
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
            self._send(404, json.dumps({"error": "Not Found"}).encode("utf-8"))
            return

        if parsed.path == "/" or parsed.path == "/index.html":
            index_path = UI_DIR / "index.html"
            if index_path.exists():
                data = index_path.read_bytes()
                self._send(200, data, content_type="text/html; charset=utf-8")
                return
        self._send(404, json.dumps({"error": "Not Found"}).encode("utf-8"))

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
            code, output = _run_cli("apply", payload)
            _log_event(self.client_address[0], "apply", {"version": payload.get("version")})
            self._send(200, json.dumps({"ok": code == 0, "output": output}).encode("utf-8"))
            return

        self._send(404, json.dumps({"error": "Not Found"}).encode("utf-8"))


def main():
    global WIZARD_TOKEN
    port = int(os.environ.get("MC_PANEL_WIZARD_PORT", "15001"))
    _generate_token()
    print(f"Wizard running on http://0.0.0.0:{port}")
    rotator = threading.Thread(target=_rotate_token_loop, daemon=True)
    rotator.start()
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
