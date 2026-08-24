"""Password spray detector. Task 006. Rule: auth.password_spray"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import timedelta

from sentinel_lite.fingerprint import make_fingerprint
from sentinel_lite.models import AnalysisConfig, AuthEvent, Finding, AuthResult, Severity
from sentinel_lite.time_window import group_by, sliding_fail_clusters, window_start_iso


def detect_password_spray(
    events: Sequence[AuthEvent],
    config: AnalysisConfig,
) -> list[Finding]:
    """Detect many distinct usernames targeted by one IP inside a time window.

    Password spray = an IP fails against >= user_threshold *distinct* usernames
    within window_seconds.  Single-user brute force (many fails for one user)
    does not trigger this rule.
    """
    spray_cfg = config.detectors.get("password_spray", {})
    if not spray_cfg.get("enabled", True):
        return []

    user_threshold: int = spray_cfg.get("user_threshold", 5)
    window_seconds: int = spray_cfg.get("window_seconds", 600)
    severity = Severity(spray_cfg.get("severity", "high"))

    # Keep only failed auth events
    failures = [e for e in events if e.result == AuthResult.FAILURE]

    # Group failures by source IP
    by_ip = group_by(failures, key=lambda e: e.src_ip)

    findings: list[Finding] = []

    for ip, ip_events in by_ip.items():
        # Collect distinct usernames and their failure timestamps per user
        user_timestamps: dict[str, list] = {}
        for ev in ip_events:
            user_timestamps.setdefault(ev.username, []).append(ev.timestamp)

        # Count how many distinct users failed — need >= threshold distinct users
        if len(user_timestamps) < user_threshold:
            continue

        # Collect all failure timestamps for this IP (across all users)
        all_ts = sorted(ev.timestamp for ev in ip_events)

        # Use sliding window to find a cluster where enough events occur
        clusters = sliding_fail_clusters(
            all_ts, threshold=len(user_timestamps), window_seconds=window_seconds
        )

        if not clusters:
            continue

        # At least one window has enough failures spanning >= user_threshold users
        cluster_start, cluster_end, count = clusters[0]

        # Gather evidence lines for events in this window
        delta = timedelta(seconds=window_seconds)
        evidence = []
        usernames_in_window = set()
        for ev in ip_events:
            if cluster_start <= ev.timestamp <= cluster_start + delta:
                usernames_in_window.add(ev.username)
                evidence.append(
                    f"{ev.timestamp.isoformat()} {ev.src_ip} "
                    f"Failed password for {ev.username}"
                )

        findings.append(
            Finding(
                rule_id="auth.password_spray",
                severity=severity,
                title="Password spray attack detected",
                description=(
                    f"{ip} failed against "
                    f"{len(usernames_in_window)} distinct usernames "
                    f"within {window_seconds}s window"
                ),
                timestamp=cluster_start,
                src_ip=ip,
                evidence=evidence,
                fingerprint=make_fingerprint(
                    "auth.password_spray",
                    src_ip=ip,
                    window_start=window_start_iso(cluster_start),
                ),
                mitre=["T1110.003"],
                extras={
                    "distinct_users": len(usernames_in_window),
                    "usernames": sorted(usernames_in_window),
                    "total_failures": count,
                },
            )
        )

    return findings
