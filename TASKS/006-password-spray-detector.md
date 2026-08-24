# Task 006 — Password spray detector

```yaml
status: done
reviewer_verdict: approved
completed_attempt: runs/006/attempt-1
depends_on: [002, 004]
budget_attempts: 10
worker_model: qwen3.6:27b
worker_provider: ollama-launch
parallel_with: [005, 007]
```

## Goal

Implement `detect_password_spray` (`auth.password_spray`).

## Context

- **Implement in:** `src/sentinel_lite/detectors/password_spray.py` only  
- Do **not** edit `detectors/__init__.py` or other detector modules  
- Config: `config.detectors["password_spray"]`  
  - `user_threshold` (default 5)  
  - `window_seconds` (default 600)  
  - `enabled`, `severity`  
- Count **distinct usernames** with failures per `src_ip` inside a window  
- Single-user brute fixture must return **no** spray findings  
- Rule id exactly: `auth.password_spray`  
- Use `make_fingerprint` and non-empty `evidence`  
- Prefer `time_window` helpers  

## In scope

- `src/sentinel_lite/detectors/password_spray.py`
- `tests/detectors/test_password_spray.py` (prefer not to change)

## Out of scope

- Changing brute_force or success_after_fail modules  

## Success criteria

1. `pytest tests/detectors/test_password_spray.py -q` exits 0  
2. No files modified outside in-scope paths  

## Commands

```bash
pytest tests/detectors/test_password_spray.py -q
```

## Budget

- Max 10 attempts  

## Done report

Explain how distinct usernames are counted in the window.
