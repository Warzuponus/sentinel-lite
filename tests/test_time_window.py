"""Task 004 — time window helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sentinel_lite.time_window import group_by, in_window, sliding_fail_clusters


def _ts(minute: int, second: int = 0) -> datetime:
    return datetime(2024, 1, 15, 10, minute, second, tzinfo=timezone.utc)


def test_in_window_inclusive_end_exclusive_start_edge():
    items = [
        ("a", _ts(0, 0)),
        ("b", _ts(1, 0)),
        ("c", _ts(5, 0)),
    ]
    end = _ts(5, 0)
    # window 300s → (10:00:00, 10:05:00] — if start is exclusive of end-window,
    # document: events with ts > end - window and ts <= end
    got = in_window(
        items,
        get_ts=lambda x: x[1],
        end=end,
        window_seconds=300,
    )
    labels = [x[0] for x in got]
    # 10:00:00 is exactly end-300; use (end - window, end] so 10:00:00 excluded
    # 10:01 and 10:05 included
    assert labels == ["b", "c"]


def test_group_by_preserves_order():
    events = [("u1", 1), ("u2", 2), ("u1", 3)]
    g = group_by(events, key=lambda x: x[0])
    assert list(g.keys()) == ["u1", "u2"]
    assert g["u1"] == [("u1", 1), ("u1", 3)]


def test_sliding_fail_clusters_finds_threshold():
    # 6 failures within 5 minutes (15s apart)
    base = _ts(0, 0)
    stamps = [base + timedelta(seconds=i * 15) for i in range(6)]
    clusters = sliding_fail_clusters(stamps, threshold=5, window_seconds=300)
    assert len(clusters) >= 1
    start, end, count = clusters[0]
    assert count >= 5
    assert end - start <= timedelta(seconds=300)


def test_sliding_fail_clusters_no_match():
    stamps = [_ts(0, 0), _ts(10, 0), _ts(20, 0)]
    clusters = sliding_fail_clusters(stamps, threshold=5, window_seconds=300)
    assert clusters == []
