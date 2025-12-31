from __future__ import annotations

from datetime import datetime, timedelta
import re
from pathlib import Path
from typing import Optional

from backend.runtime.log_streamer import tail_log

_JOIN_RE = re.compile(r"]:\s*(?P<name>\S+)\s+joined the game")
_LEAVE_RE = re.compile(r"]:\s*(?P<name>\S+)\s+left the game")
_TIME_RE = re.compile(r"^\[(?P<time>\d{2}:\d{2}:\d{2})\]")


def get_session_seconds(log_path: Path, player_name: str, *, window_lines: int = 2000) -> int:
    if not log_path.exists():
        return 0
    lines = tail_log(str(log_path), lines=window_lines)
    last_join: Optional[datetime] = None
    last_leave: Optional[datetime] = None
    now = datetime.now()
    for line in lines:
        time_match = _TIME_RE.search(line)
        if not time_match:
            continue
        time_str = time_match.group("time")
        try:
            time_part = datetime.strptime(time_str, "%H:%M:%S").time()
        except ValueError:
            continue
        timestamp = datetime.combine(now.date(), time_part)
        if timestamp > now:
            timestamp -= timedelta(days=1)
        join_match = _JOIN_RE.search(line)
        if join_match and join_match.group("name") == player_name:
            last_join = timestamp
            continue
        leave_match = _LEAVE_RE.search(line)
        if leave_match and leave_match.group("name") == player_name:
            last_leave = timestamp
    if last_join and (not last_leave or last_join > last_leave):
        return max(0, int((now - last_join).total_seconds()))
    return 0
