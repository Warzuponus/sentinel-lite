"""Task 007 — success after failures detector."""

from __future__ import annotations

from sentinel_lite.detectors import detect_success_after_fail
from sentinel_lite.parsers import parse_ssh_auth_file


def test_detects_success_after_fails(ssh_fixtures, config):
    events = parse_ssh_auth_file(ssh_fixtures / "success_after_fails.log")
    findings = detect_success_after_fail(events, config)
    assert len(findings) >= 1
    f = findings[0]
    assert f.rule_id == "auth.success_after_fail"
    assert f.username == "root"
    assert f.severity.value == "critical"


def test_clean_day_no_alert(ssh_fixtures, config):
    """One fail then quick success is under fail_threshold (3)."""
    events = parse_ssh_auth_file(ssh_fixtures / "clean_day.log")
    findings = detect_success_after_fail(events, config)
    assert findings == []
