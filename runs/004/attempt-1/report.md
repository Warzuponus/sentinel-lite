# Task 004 done report
- Status: green
- Attempts: 1
- Files changed: src/sentinel_lite/time_window.py
- Commands run: pytest tests/test_time_window.py -q
- Residual risks / ambiguities: none
- Notes for reviewer:
  - `in_window`: filters with half-open interval (end-window, end] via strict less-than on cutoff, then sorts ascending by timestamp.
  - `group_by`: standard dict-based grouping preserving first-seen key order and encounter order within groups.
  - `sliding_fail_clusters`: two-pointer algorithm on sorted timestamps. For each start index i, expand j while ts[j]-ts[i] <= window. If count >= threshold, record cluster and skip past j to avoid sub-cluster overlap. Returns [] when no cluster meets the threshold.
