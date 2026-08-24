"""Task 003 — JSON-lines login parser."""

from __future__ import annotations

from datetime import timezone

from sentinel_lite.models import AuthResult
from sentinel_lite.parsers import parse_json_login_file, parse_json_login_line


def test_parse_failure_line():
    line = (
        '{"ts": "2024-01-15T10:00:01Z", "ip": "203.0.113.50", '
        '"user": "admin", "ok": false, "svc": "webapp"}'
    )
    ev = parse_json_login_line(line)
    assert ev is not None
    assert ev.username == "admin"
    assert ev.src_ip == "203.0.113.50"
    assert ev.result == AuthResult.FAILURE
    assert ev.service == "webapp"
    assert ev.timestamp.tzinfo is not None
    assert ev.timestamp.astimezone(timezone.utc).hour == 10


def test_parse_success_line():
    line = (
        '{"ts": "2024-01-15T10:05:00Z", "ip": "198.51.100.10", '
        '"user": "alice", "ok": true, "svc": "webapp"}'
    )
    ev = parse_json_login_line(line)
    assert ev is not None
    assert ev.result == AuthResult.SUCCESS


def test_parse_invalid_json_returns_none():
    assert parse_json_login_line("not json") is None
    assert parse_json_login_line("{}") is None
    assert parse_json_login_line("") is None


def test_parse_file(json_fixtures):
    events = parse_json_login_file(json_fixtures / "brute_force.jsonl")
    assert len(events) == 7
    assert sum(1 for e in events if e.result == AuthResult.FAILURE) == 6
