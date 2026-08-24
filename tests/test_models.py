"""Task 001 — core models and fingerprint helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from sentinel_lite.config import default_config, load_config
from sentinel_lite.fingerprint import make_fingerprint
from sentinel_lite.models import AuthEvent, AuthResult, Finding, Severity


def test_auth_event_roundtrip():
    ev = AuthEvent(
        timestamp=datetime(2024, 1, 15, 10, 0, 1, tzinfo=timezone.utc),
        src_ip="203.0.113.50",
        username="admin",
        result=AuthResult.FAILURE,
        service="sshd",
        raw="Failed password for admin from 203.0.113.50",
    )
    data = ev.model_dump(mode="json")
    restored = AuthEvent.model_validate(data)
    assert restored.src_ip == "203.0.113.50"
    assert restored.result == AuthResult.FAILURE


def test_auth_event_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        AuthEvent(
            timestamp=datetime(2024, 1, 15, 10, 0, 1, tzinfo=timezone.utc),
            src_ip="1.2.3.4",
            username="u",
            result=AuthResult.SUCCESS,
            service="sshd",
            raw="x",
            not_a_field=True,  # type: ignore[call-arg]
        )


def test_finding_requires_fingerprint():
    f = Finding(
        rule_id="auth.brute_force",
        severity=Severity.HIGH,
        title="Brute force",
        description="Repeated failures",
        timestamp=datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
        src_ip="203.0.113.50",
        username="admin",
        evidence=["line1"],
        fingerprint=make_fingerprint(
            "auth.brute_force", src_ip="203.0.113.50", username="admin"
        ),
    )
    assert len(f.fingerprint) == 64


def test_fingerprint_stable():
    a = make_fingerprint("auth.brute_force", src_ip="1.1.1.1", username="a")
    b = make_fingerprint("auth.brute_force", src_ip="1.1.1.1", username="a")
    c = make_fingerprint("auth.brute_force", src_ip="1.1.1.1", username="b")
    assert a == b
    assert a != c


def test_default_config_has_detectors():
    cfg = default_config()
    assert cfg.detectors["brute_force"]["fail_threshold"] == 5
    assert cfg.detectors["password_spray"]["user_threshold"] == 5
    assert cfg.detectors["success_after_fail"]["fail_threshold"] == 3


def test_load_config_example(tmp_path):
    example = Path(__file__).resolve().parents[1] / "config.example.yaml"
    cfg = load_config(example)
    assert cfg.version == 1
    assert "brute_force" in cfg.detectors
