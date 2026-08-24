"""Task 008 — orchestrate detectors and dedupe."""

from __future__ import annotations

from sentinel_lite.analyze import analyze_path
from sentinel_lite.detectors import run_all_detectors
from sentinel_lite.parsers import parse_ssh_auth_file


def test_run_all_on_brute_fixture(ssh_fixtures, config):
    events = parse_ssh_auth_file(ssh_fixtures / "brute_force_single_ip.log")
    findings = run_all_detectors(events, config)
    rule_ids = {f.rule_id for f in findings}
    assert "auth.brute_force" in rule_ids
    # fingerprints unique
    fps = [f.fingerprint for f in findings]
    assert len(fps) == len(set(fps))


def test_run_all_clean(ssh_fixtures, config):
    events = parse_ssh_auth_file(ssh_fixtures / "clean_day.log")
    findings = run_all_detectors(events, config)
    assert findings == []


def test_analyze_path_directory(ssh_fixtures, config):
    findings = analyze_path(ssh_fixtures / "clean_day.log", config)
    assert findings == []
