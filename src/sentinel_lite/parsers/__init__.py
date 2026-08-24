"""Log parsers that emit normalized AuthEvent streams."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Iterator
from datetime import datetime
from pathlib import Path

from sentinel_lite.models import AuthEvent, AuthResult

# --- Task 002: OpenSSH auth.log parser ---

_SYSLOG_TS_RE = re.compile(
    r"^(\w{3})\s+(\d{1,2})\s+(\d{2}):(\d{2}):(\d{2})"
)

_SSH_FAIL_RE = re.compile(
    r"sshd\[\d+\]: Failed password for (?:invalid user )?(\S+) from (\S+) port (\d+) ssh2\s*$"
)

_SSH_ACCEPT_RE = re.compile(
    r"sshd\[\d+\]: Accepted (?:password|publickey) for (\S+) from (\S+) port (\d+) ssh2\s*$"
)

_MONTH_MAP = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}


def _parse_syslog_timestamp(raw: str) -> datetime | None:
    """Parse 'Mon DD HH:MM:SS' → naive datetime with year 2024."""
    m = _SYSLOG_TS_RE.match(raw)
    if not m:
        return None
    month_str, day, hour, minute, second = m.groups()
    month = _MONTH_MAP.get(month_str)
    if month is None:
        return None
    try:
        return datetime(2024, month, int(day), int(hour), int(minute), int(second))
    except ValueError:
        return None


def parse_ssh_auth_line(line: str) -> AuthEvent | None:
    """Parse a single OpenSSH auth.log-style line. Task 002."""
    stripped = line.strip()
    if not stripped:
        return None

    ts = _parse_syslog_timestamp(stripped)
    if ts is None:
        return None

    # Try failed password first, then accepted (independent patterns; order is arbitrary)
    fail_m = _SSH_FAIL_RE.search(stripped)
    if fail_m:
        username, src_ip, port = fail_m.groups()
        return AuthEvent(
            timestamp=ts,
            src_ip=src_ip,
            username=username,
            result=AuthResult.FAILURE,
            service="sshd",
            raw=stripped,
            extras={"port": int(port)},
        )

    accept_m = _SSH_ACCEPT_RE.search(stripped)
    if accept_m:
        username, src_ip, port = accept_m.groups()
        return AuthEvent(
            timestamp=ts,
            src_ip=src_ip,
            username=username,
            result=AuthResult.SUCCESS,
            service="sshd",
            raw=stripped,
            extras={"port": int(port)},
        )

    return None


def parse_ssh_auth_file(path: str | Path) -> list[AuthEvent]:
    """Parse an OpenSSH auth log file. Task 002."""
    events: list[AuthEvent] = []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            ev = parse_ssh_auth_line(line)
            if ev is not None:
                events.append(ev)
    return events


def parse_json_login_line(line: str) -> AuthEvent | None:
    """Parse a single JSON login event line. Task 003."""
    stripped = line.strip()
    if not stripped:
        return None
    try:
        data = json.loads(stripped)
    except (json.JSONDecodeError, ValueError):
        return None

    # All five fields are required
    for key in ("ts", "ip", "user", "ok", "svc"):
        if key not in data:
            return None

    try:
        ts_raw = str(data["ts"])
        # Python 3.11+ handles 'Z' suffix, but be safe across versions
        if ts_raw.endswith("Z"):
            ts_raw = ts_raw[:-1] + "+00:00"
        timestamp = datetime.fromisoformat(ts_raw)
    except (ValueError, TypeError):
        return None

    return AuthEvent(
        timestamp=timestamp,
        src_ip=str(data["ip"]),
        username=str(data["user"]),
        result=AuthResult.SUCCESS if data["ok"] else AuthResult.FAILURE,
        service=str(data["svc"]),
        raw=stripped,
        extras={},
    )


def parse_json_login_file(path: str | Path) -> list[AuthEvent]:
    """Parse a JSON-lines login log file. Task 003."""
    events: list[AuthEvent] = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            ev = parse_json_login_line(line)
            if ev is not None:
                events.append(ev)
    return events


def iter_events_from_paths(paths: Iterable[str | Path]) -> Iterator[AuthEvent]:
    """Dispatch by extension/name and yield events. Task 008 may flesh out."""
    for path in paths:
        p = Path(path)
        name = p.name.lower()
        if name.endswith(".jsonl") or "json" in name:
            yield from parse_json_login_file(p)
        else:
            yield from parse_ssh_auth_file(p)
