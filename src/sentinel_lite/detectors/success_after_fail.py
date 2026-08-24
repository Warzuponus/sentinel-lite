"""Success after fail detector. Task 007. Rule: auth.success_after_fail"""

from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from typing import Any

from sentinel_lite.fingerprint import make_fingerprint
from sentinel_lite.models import AnalysisConfig, AuthEvent, AuthResult, Finding, Severity


def detect_success_after_fail(
    events: Sequence[AuthEvent],
    config: AnalysisConfig,
) -> list[Finding]:
    """Detect success after recent failures. Task 007. Rule: auth.success_after_fail"""
    det_cfg = config.detectors.get("success_after_fail", {})
    fail_threshold: int = det_cfg.get("fail_threshold", 3)
    window_seconds: int = det_cfg.get("window_seconds", 900)
    require_same_ip: bool = det_cfg.get("require_same_ip", False)
    severity_str: str = det_cfg.get("severity", "critical")

    severities: dict[str, Severity] = {s.value: s for s in Severity}
    severity = severities.get(severity_str, Severity.CRITICAL)

    window = timedelta(seconds=window_seconds)

    # Group failure events by (username, src_ip) or username alone
    fail_groups: dict[tuple, list[AuthEvent]] = defaultdict(list)
    for ev in events:
        if ev.result == AuthResult.FAILURE:
            if require_same_ip:
                key = (ev.username, ev.src_ip)
            else:
                key = (ev.username,)
            fail_groups[key].append(ev)

    findings: list[Finding] = []
    for ev in events:
        if ev.result != AuthResult.SUCCESS:
            continue

        if require_same_ip:
            key = (ev.username, ev.src_ip)
        else:
            key = (ev.username,)

        fails = fail_groups.get(key, [])
        prior_fails = [
            f for f in fails
            if (ev.timestamp - window) < f.timestamp <= ev.timestamp
        ]

        if len(prior_fails) >= fail_threshold:
            evidence = [f.raw for f in prior_fails]
            fp = make_fingerprint(
                rule_id="auth.success_after_fail",
                src_ip=ev.src_ip,
                username=ev.username,
                window_start=prior_fails[0].timestamp.isoformat(),
            )
            findings.append(Finding(
                rule_id="auth.success_after_fail",
                severity=severity,
                title=f"Successful login after {len(prior_fails)} failures for {ev.username}",
                description=(
                    f"User '{ev.username}' logged in successfully from "
                    f"{ev.src_ip} after {len(prior_fails)} failed attempts "
                    f"within {window_seconds}s."
                ),
                timestamp=ev.timestamp,
                src_ip=ev.src_ip,
                username=ev.username,
                evidence=evidence,
                fingerprint=fp,
                mitre=["T1110.001"],
            ))

    return findings
