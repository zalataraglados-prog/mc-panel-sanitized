from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import socket
import struct
from typing import List
import re

from backend.runtime.ansi import strip_ansi

@dataclass
class RCONResponse:
    request_id: int
    response_type: int
    payload: str


class RCONClient:
    def __init__(self, host: str, port: int, password: str, enabled: bool = True, timeout: float = 2.0):
        self.host = host
        self.port = port
        self.password = password
        self.enabled = enabled
        self.timeout = timeout

    def execute(self, command: str) -> str:
        if not self.enabled:
            return "RCON disabled"
        try:
            with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
                sock.settimeout(self.timeout)
                auth_id = 1
                self._send_packet(sock, auth_id, 3, self.password)
                auth_resp = self._recv_packet(sock)
                if not auth_resp or auth_resp.request_id == -1:
                    return "RCON auth failed"
                self._send_packet(sock, auth_id + 1, 2, command)
                response = self._recv_packet(sock)
                if not response:
                    return "RCON no response"
                return strip_ansi(response.payload)
        except (OSError, socket.timeout) as exc:
            return f"RCON error: {exc}"

    def list_players(self) -> List[str]:
        if not self.enabled:
            return []
        response = self.execute("list")
        return _parse_player_list(response)

    def get_player_position(self, name: str) -> dict:
        if not self.enabled:
            return {"x": 0.0, "y": 0.0, "z": 0.0}
        response = self.execute(f"data get entity {name} Pos")
        match = re.search(r"\[([-\d.]+)d?,\s*([-\d.]+)d?,\s*([-\d.]+)d?\]", response)
        if not match:
            return {"x": 0.0, "y": 0.0, "z": 0.0}
        return {"x": float(match.group(1)), "y": float(match.group(2)), "z": float(match.group(3))}

    @classmethod
    def from_instance_dir(cls, instance_dir: str) -> "RCONClient":
        base_dir = Path(instance_dir)
        props = _read_server_properties(base_dir)
        enabled = props.get("enable-rcon", "false").lower() == "true"
        host = "127.0.0.1"
        config = _read_instance_config(base_dir)
        port = None
        if isinstance(config.get("network"), dict):
            port = config["network"].get("rcon_port")
        if port is None:
            port = _read_compose_rcon_port(base_dir)
        if port is None:
            port = props.get("rcon.port", "25575")
        port = int(port)
        password = props.get("rcon.password", "change-me")
        return cls(host, port, password, enabled=enabled)

    @staticmethod
    def _send_packet(sock: socket.socket, request_id: int, packet_type: int, payload: str) -> None:
        data = payload.encode("utf-8")
        body = struct.pack("<ii", request_id, packet_type) + data + b"\x00\x00"
        sock.sendall(struct.pack("<i", len(body)) + body)

    @staticmethod
    def _recv_packet(sock: socket.socket) -> RCONResponse | None:
        header = _recv_exact(sock, 4)
        if not header:
            return None
        (length,) = struct.unpack("<i", header)
        body = _recv_exact(sock, length)
        if not body or len(body) < 10:
            return None
        request_id, response_type = struct.unpack("<ii", body[:8])
        payload = body[8:-2].decode("utf-8", errors="ignore")
        return RCONResponse(request_id=request_id, response_type=response_type, payload=payload)


def _recv_exact(sock: socket.socket, length: int) -> bytes:
    chunks = []
    remaining = length
    while remaining > 0:
        chunk = sock.recv(remaining)
        if not chunk:
            break
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def _parse_player_list(response: str) -> List[str]:
    if "There are" not in response:
        return []
    parts = response.split(":", 1)
    if len(parts) != 2:
        return []
    names = [name.strip() for name in parts[1].split(",") if name.strip()]
    return names


def _read_server_properties(instance_dir: Path) -> dict:
    path = instance_dir / "data" / "server.properties"
    if not path.exists():
        return {}
    result = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def _read_instance_config(instance_dir: Path) -> dict:
    path = instance_dir / "config.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _read_compose_rcon_port(instance_dir: Path) -> int | None:
    path = instance_dir / "docker-compose.yml"
    if not path.exists():
        return None
    pattern = re.compile(r'^\s*-\s*"?(\d+):25575"?')
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        match = pattern.match(line)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
    return None
