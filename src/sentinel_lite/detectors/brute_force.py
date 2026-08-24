"""Brute force detector. Task 005. Rule: auth.brute_force"""

from __future__ import annotations

from collections.abc import Sequence

from sentinel_lite.fingerprint import make_fingerprint
from sentinel_lite.models import AnalysisConfig, AuthEvent, AuthResult, Finding, Severity
from sentinel_lite.time_window import group_by, sliding_fail_clusters, window_start_iso


def detect_brute_force(
    events: Sequence[AuthEvent],
    config: AnalysisConfig,
) -> list[Finding]:
    """Detect repeated failures from one IP. Task 005. Rule: auth.brute_force"""
    bf_cfg = config.detectors.get("brute_force", {})
    if not bf_cfg.get("enabled", True):
        return []

    threshold: int = bf_cfg.get("fail_threshold", 5)
    window: int = bf_cfg.get("window_seconds", 300)
    severity_str: str = bf_cfg.get("severity", "high")
    fp_version: int = config.output.get("fingerprint_version", 1)

    # 1. Failures only
    failures = [e for e in events if e.result == AuthResult.FAILURE]
    if not failures:
        return []

    # 2. Group by src_ip
    by_ip = group_by(failures, key=lambda e: e.src_ip)

    findings: list[Finding] = []
    for ip, ip_events in by_ip.items():
        timestamps = [e.timestamp for e in ip_events]
        clusters = sliding_fail_clusters(
            timestamps, threshold=threshold, window_seconds=window
        )
        if not clusters:
            continue

        # One finding per cluster (usually one for a single-IP brute force)
        for cluster_start, cluster_end, count in clusters:
            ws = window_start_iso(cluster_start)
            fp = make_fingerprint(
                "auth.brute_force",
                src_ip=ip,
                window_start=ws,
                version=fp_version,
            )

            # Collect evidence lines for events within this cluster window
            cluster_events = [
                e
                for e in ip_events
                if cluster_start <= e.timestamp <= cluster_end
            ]
            evidence = [e.raw for e in cluster_events[:10]]

            findings.append(
                Finding(
                    rule_id="auth.brute_force",
                    severity=Severity(severity_str),
                    title="Authentication brute force",
                    description=(
                        f"{count} failed auth attempts from {ip} within "
                        f"{window}s window."
                    ),
                    timestamp=cluster_start,
                    src_ip=ip,
                    evidence=evidence,
                    fingerprint=fp,
                    mitre=["T1110.001"],
                )
            )

    return findings
