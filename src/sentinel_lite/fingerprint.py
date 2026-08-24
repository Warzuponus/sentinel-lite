"""Stable finding fingerprints for dedupe and golden tests."""

from __future__ import annotations

import hashlib


def make_fingerprint(
    rule_id: str,
    *,
    src_ip: str | None = None,
    username: str | None = None,
    window_start: str | None = None,
    version: int = 1,
) -> str:
    """Create a deterministic fingerprint.

    Fingerprint v1 material: ``v{version}|{rule_id}|{src_ip}|{username}|{window_start}``
    Missing optional parts become empty strings. Returns hex sha256 digest.
    """
    parts = [
        f"v{version}",
        rule_id,
        src_ip or "",
        username or "",
        window_start or "",
    ]
    material = "|".join(parts)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()
