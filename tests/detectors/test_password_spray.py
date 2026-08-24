"""Task 006 — password spray detector."""

from __future__ import annotations

from sentinel_lite.detectors import detect_password_spray
from sentinel_lite.parsers import parse_ssh_auth_file


def test_detects_spray(ssh_fixtures, config):
    events = parse_ssh_auth_file(ssh_fixtures / "password_spray.log")
    findings = detect_password_spray(events, config)
    assert len(findings) >= 1
    f = findings[0]
    assert f.rule_id == "auth.password_spray"
    assert f.src_ip == "203.0.113.77"
    assert f.severity.value == "high"


def test_clean_day_no_spray(ssh_fixtures, config):
    events = parse_ssh_auth_file(ssh_fixtures / "clean_day.log")
    findings = detect_password_spray(events, config)
    assert findings == []


def test_single_user_brute_not_spray(ssh_fixtures, config):
    """Many fails against one user should not count as spray (distinct users)."""
    events = parse_ssh_auth_file(ssh_fixtures / "brute_force_single_ip.log")
    findings = detect_password_spray(events, config)
    assert findings == []
