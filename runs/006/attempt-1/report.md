# Task 006 done report
- Status: green
- Attempts: 1
- Files changed: src/sentinel_lite/detectors/password_spray.py
- Commands run: pytest tests/detensors/test_password_spray.py -q
- Residual risks / ambiguities: none
- Notes for reviewer: see below

## How distinct usernames are counted in the window

1. Filter events to failures only (`AuthResult.FAILURE`).
2. Group failures by `src_ip` using `time_window.group_by`.
3. For each IP, build a dict mapping each username to its list of failure timestamps. The number of keys in this dict is the count of **distinct usernames** that failed from that IP.
4. If distinct users < `user_threshold`, skip — not a spray.
5. Run `sliding_fail_clusters` over all failure timestamps for that IP with threshold = number of distinct users. This ensures the distinct-user failures actually fit within a single `window_seconds` window (not spread across days).
6. When a qualifying cluster is found, collect evidence lines for events inside the window and emit one `Finding` with rule `auth.password_spray`.

### Why brute-force-single-user does not trigger spray
The brute force fixture has 6 failures from one IP but all against `admin`. Distinct username count = 1, which is below the default threshold of 5, so it correctly returns no findings.

### Why clean_day does not trigger spray
Only one failure event exists (charlie from a different IP), so no IP reaches the distinct-user threshold.
