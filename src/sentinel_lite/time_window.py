"""Time-window helpers for detectors.

Task 004 owns sliding/session window utilities. Implementations must support
an injectable ``now`` for deterministic tests (no wall-clock dependency).
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from datetime import datetime, timedelta
from typing import TypeVar

T = TypeVar("T")


def in_window(
    events: Sequence[T],
    *,
    get_ts: Callable[[T], datetime],
    end: datetime,
    window_seconds: int,
) -> list[T]:
    """Return events with timestamp in (end - window, end], sorted by time ascending."""
    cutoff = end - timedelta(seconds=window_seconds)
    result = [ev for ev in events if cutoff < get_ts(ev) <= end]
    result.sort(key=get_ts)
    return result


def group_by(
    events: Iterable[T],
    key: Callable[[T], str],
) -> dict[str, list[T]]:
    """Group events by key, preserving first-seen key order and encounter order."""
    result: dict[str, list[T]] = {}
    for ev in events:
        k = key(ev)
        if k not in result:
            result[k] = []
        result[k].append(ev)
    return result


def sliding_fail_clusters(
    timestamps: Sequence[datetime],
    *,
    threshold: int,
    window_seconds: int,
) -> list[tuple[datetime, datetime, int]]:
    """Find clusters where ``threshold`` timestamps fall within ``window_seconds``.

    For each index i in sorted timestamps, find the largest j such that
    ts[j] - ts[i] <= window_seconds. If j - i + 1 >= threshold, record a cluster.
    Consecutive qualifying starts that overlap are merged — only distinct cluster
    starts are reported.
    """
    if not timestamps:
        return []

    sorted_ts = sorted(timestamps)
    n = len(sorted_ts)
    clusters: list[tuple[datetime, datetime, int]] = []
    i = 0
    while i < n:
        # Expand j forward while within window
        j = i
        delta = timedelta(seconds=window_seconds)
        while j + 1 < n and (sorted_ts[j + 1] - sorted_ts[i]) <= delta:
            j += 1
        count = j - i + 1
        if count >= threshold:
            clusters.append((sorted_ts[i], sorted_ts[j], count))
            # Skip past this cluster to avoid sub-clusters
            i = j + 1
        else:
            i += 1
    return clusters


def window_start_iso(ts: datetime) -> str:
    """Canonical ISO-8601 UTC string for fingerprint window anchors."""
    if ts.tzinfo is None:
        # Treat naive as UTC for lab fixtures.
        return ts.strftime("%Y-%m-%dT%H:%M:%SZ")
    from datetime import timezone

    return ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
