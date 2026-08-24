"""Threat detectors over normalized AuthEvent streams.

Individual detectors live in sibling modules so parallel agents can implement
005/006/007 without editing the same file.
"""

from __future__ import annotations

from collections.abc import Sequence

from sentinel_lite.detectors.brute_force import detect_brute_force
from sentinel_lite.detectors.password_spray import detect_password_spray
from sentinel_lite.detectors.success_after_fail import detect_success_after_fail
from sentinel_lite.models import AnalysisConfig, AuthEvent, Finding

__all__ = [
    "detect_brute_force",
    "detect_password_spray",
    "detect_success_after_fail",
    "run_all_detectors",
]


def run_all_detectors(
    events: Sequence[AuthEvent],
    config: AnalysisConfig,
) -> list[Finding]:
    """Run enabled detectors and return deduped findings. Task 008."""
    all_findings: list[Finding] = []

    if config.detectors.get("brute_force", {}).get("enabled", True):
        all_findings.extend(detect_brute_force(events, config))

    if config.detectors.get("password_spray", {}).get("enabled", True):
        all_findings.extend(detect_password_spray(events, config))

    if config.detectors.get("success_after_fail", {}).get("enabled", True):
        all_findings.extend(detect_success_after_fail(events, config))

    # Dedupe by fingerprint, preserving first-occurrence order
    seen: set[str] = set()
    deduped: list[Finding] = []
    for f in all_findings:
        if f.fingerprint not in seen:
            seen.add(f.fingerprint)
            deduped.append(f)

    return deduped
