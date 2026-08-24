# Task 004 — Time window helpers

```yaml
status: done
depends_on: [001]
budget_attempts: 8
worker_model: qwen3.6:27b
worker_provider: ollama-launch
parallel_with: [003]
completed_attempt: runs/004/attempt-1
reviewer_verdict: approved
```

## Goal

Implement deterministic windowing utilities used by detectors.

## Context

Module: `src/sentinel_lite/time_window.py`

### `in_window(events, get_ts=, end=, window_seconds=)`

Return events where:

```text
(end - timedelta(seconds=window_seconds)) < ts <= end
```

Sorted ascending by timestamp.

### `group_by(events, key=)`

Return `dict[str, list[T]]` preserving first-seen key order and encounter order within groups.

### `sliding_fail_clusters(timestamps, threshold=, window_seconds=)`

Given sorted or unsorted timestamps, find clusters where at least `threshold` events fall inside some window of `window_seconds`.

Return list of `(window_start, window_end, count)`:

- `window_start`: timestamp of the first event in that qualifying group  
- `window_end`: timestamp of the last event included in that group  
- `count`: number of events in the group  

Recommended algorithm: sort ascending; for each index `i`, expand `j` while `ts[j] - ts[i] <= window`; if `j-i+1 >= threshold`, record cluster. Avoid reporting pure sub-clusters if easier to report every `i` that starts a qualifying window—**tests only require `len(clusters) >= 1` and count/window constraints on the first cluster for the happy path**, and `[]` when impossible.

### `window_start_iso`

Already useful for fingerprints; keep working for naive and aware datetimes as documented in source.

## In scope

- `src/sentinel_lite/time_window.py`
- `tests/test_time_window.py`

## Out of scope

- Detectors  
- I/O  

## Success criteria

1. `pytest tests/test_time_window.py -q` exits 0  

## Commands

```bash
pytest tests/test_time_window.py -q
```

## Budget

- Max 8 attempts  

## Done report

Describe cluster algorithm briefly for the reviewer.
