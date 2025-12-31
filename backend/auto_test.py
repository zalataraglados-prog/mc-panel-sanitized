import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional


def _request(
    method: str,
    url: str,
    token: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    data = None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


def _safe_call(label: str, func):
    try:
        result = func()
        print(f"[OK] {label}")
        return result
    except urllib.error.HTTPError as err:
        print(f"[HTTP {err.code}] {label}: {err.read().decode('utf-8')}")
    except Exception as err:  # noqa: BLE001
        print(f"[ERR] {label}: {err}")
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="MC Panel API auto interaction test.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Backend base URL.")
    parser.add_argument("--username", default="owner", help="Login username.")
    parser.add_argument("--password", default="ownerpass", help="Login password.")
    parser.add_argument("--instance-dir", default="", help="Instance dir override.")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    login = _safe_call(
        "auth/login",
        lambda: _request(
            "POST",
            f"{base_url}/api/auth/login",
            payload={"username": args.username, "password": args.password},
        ),
    )
    if not login or "token" not in login:
        return 1

    token = login["token"]

    instances = _safe_call(
        "instances",
        lambda: _request("GET", f"{base_url}/api/instances", token=token),
    ) or {}
    instance_dir = args.instance_dir
    if not instance_dir:
        for item in instances.get("instances", []) if isinstance(instances, dict) else []:
            if isinstance(item, dict) and item.get("path"):
                instance_dir = item["path"]
                break

    instance_query = f"?instance_dir={urllib.parse.quote(instance_dir)}" if instance_dir else ""

    _safe_call("status", lambda: _request("GET", f"{base_url}/api/status{instance_query}", token=token))
    _safe_call("metrics", lambda: _request("GET", f"{base_url}/api/metrics?window=60", token=token))
    _safe_call("players", lambda: _request("GET", f"{base_url}/api/players{instance_query}", token=token))
    _safe_call("rules", lambda: _request("GET", f"{base_url}/api/rules{instance_query}", token=token))
    _safe_call("templates", lambda: _request("GET", f"{base_url}/api/command-templates", token=token))

    _safe_call(
        "command",
        lambda: _request(
            "POST",
            f"{base_url}/api/command",
            token=token,
            payload={"command": "list", "instance_dir": instance_dir or None},
        ),
    )

    rules = _safe_call("rules (refresh)", lambda: _request("GET", f"{base_url}/api/rules{instance_query}", token=token))
    if isinstance(rules, dict) and rules.get("entries"):
        first = rules["entries"][0]
        if isinstance(first, dict) and "key" in first and "value" in first:
            _safe_call(
                "rules update",
                lambda: _request(
                    "PUT",
                    f"{base_url}/api/rules",
                    token=token,
                    payload={
                        "entries": [{"key": first["key"], "value": first["value"]}],
                        "instance_dir": instance_dir or None,
                    },
                ),
            )

    map_status = _safe_call(
        "map status",
        lambda: _request("GET", f"{base_url}/api/map/status{instance_query}", token=token),
    )
    if isinstance(map_status, dict) and map_status.get("enabled"):
        map_config = _safe_call(
            "map config",
            lambda: _request("GET", f"{base_url}/api/map/config{instance_query}", token=token),
        )
        if isinstance(map_config, dict) and map_config.get("files"):
            _safe_call(
                "map config writeback",
                lambda: _request(
                    "PUT",
                    f"{base_url}/api/map/config",
                    token=token,
                    payload={
                        "files": map_config.get("files", []),
                        "instance_dir": instance_dir or None,
                    },
                ),
            )
            _safe_call(
                "map reload",
                lambda: _request(
                    "POST",
                    f"{base_url}/api/map/reload",
                    token=token,
                    payload={"instance_dir": instance_dir or None},
                ),
            )

    print("[DONE] Auto interaction script completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
