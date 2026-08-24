"""Task 010 — golden end-to-end expectations on fixture sets."""

from __future__ import annotations

import json
from pathlib import Path

from sentinel_lite.analyze import analyze_path


def _rule_ids(path: Path, config) -> set[str]:
    return {f.rule_id for f in analyze_path(path, config)}


def test_golden_brute_force(ssh_fixtures, config):
    ids = _rule_ids(ssh_fixtures / "brute_force_single_ip.log", config)
    assert "auth.brute_force" in ids


def test_golden_spray(ssh_fixtures, config):
    ids = _rule_ids(ssh_fixtures / "password_spray.log", config)
    assert "auth.password_spray" in ids


def test_golden_success_after(ssh_fixtures, config):
    ids = _rule_ids(ssh_fixtures / "success_after_fails.log", config)
    assert "auth.success_after_fail" in ids


def test_golden_clean(ssh_fixtures, config):
    ids = _rule_ids(ssh_fixtures / "clean_day.log", config)
    assert ids == set()


def test_findings_json_serializable(ssh_fixtures, config):
    findings = analyze_path(ssh_fixtures / "brute_force_single_ip.log", config)
    payload = [f.model_dump(mode="json") for f in findings]
    # Must be JSON-serializable for CLI output
    raw = json.dumps(payload)
    assert "auth.brute_force" in raw
