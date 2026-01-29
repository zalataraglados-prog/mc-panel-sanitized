#!/usr/bin/env python3
import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

from deploy.claims_codec.encode import encode_claims
from deploy.loader import load_rules_bundle

ROOT = Path(__file__).resolve().parents[1]
UI_DIR = ROOT / "deploy" / "wizard_ui"
STATE_FILE = Path("/tmp/mc_wizard_state.json")


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


def _run_cli(action, state):
    version = state.get("version") or "1.21.4"
    profile = state.get("profile") or "normal"
    claims = _build_claims(state)
    cmd = ["python3", "-m", "deploy.cli", action, "--version", version, "--profile", profile, "--import-string", claims]
    if action == "apply":
        cmd.append("--confirm-warn")
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    return proc.returncode, output.strip()


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

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
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
                    version = "1.21.4"
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

        if parsed.path == "/api/wizard/state":
            state = _load_state()
            state.update(payload)
            _save_state(state)
            self._send(200, json.dumps({"ok": True}).encode("utf-8"))
            return

        if parsed.path == "/api/wizard/plan":
            code, output = _run_cli("plan", payload)
            self._send(200, json.dumps({"ok": code == 0, "output": output}).encode("utf-8"))
            return

        if parsed.path == "/api/wizard/apply":
            code, output = _run_cli("apply", payload)
            self._send(200, json.dumps({"ok": code == 0, "output": output}).encode("utf-8"))
            return

        self._send(404, json.dumps({"error": "Not Found"}).encode("utf-8"))


def main():
    port = int(os.environ.get("MC_PANEL_WIZARD_PORT", "15001"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Wizard running on http://0.0.0.0:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
