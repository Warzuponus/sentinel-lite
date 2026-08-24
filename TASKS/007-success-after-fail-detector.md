# Task 007 — Success after fail detector

```yaml
status: done
reviewer_verdict: approved_after_007b
completed_attempt: runs/007/attempt-1
depends_on: [002, 004]
budget_attempts: 10
worker_model: qwen3.6:27b
worker_provider: ollama-launch
parallel_with: [005, 006]
```

## Goal

Implement `detect_success_after_fail` (`auth.success_after_fail`).

## Context

- **Implement in:** `src/sentinel_lite/detectors/success_after_fail.py` only  
- Do **not** edit `detectors/__init__.py` or other detector modules  
- Config: `config.detectors["success_after_fail"]`  
  - `fail_threshold` (default 3)  
  - `window_seconds` (default 900)  
  - `require_same_ip` (default false)  
  - `severity` → critical in example  
- For each **success**, count prior **failures** with same `username` in `(success_ts - window, success_ts]`  
- If `require_same_ip`, also match `src_ip`  
- Clean day has only one failure before charlie’s success → no alert  
- Rule id exactly: `auth.success_after_fail`  
- Use `make_fingerprint` and non-empty `evidence`  

## In scope

- `src/sentinel_lite/detectors/success_after_fail.py`
- `tests/detectors/test_success_after_fail.py` (prefer not to change)

## Out of scope

- Multi-hop correlation across devices  
- Other detectors  

## Success criteria

1. `pytest tests/detectors/test_success_after_fail.py -q` exits 0  
2. No files modified outside in-scope paths  

## Commands

```bash
pytest tests/detectors/test_success_after_fail.py -q
```

## Budget

- Max 10 attempts  

## Done report

Note handling of `require_same_ip`.
