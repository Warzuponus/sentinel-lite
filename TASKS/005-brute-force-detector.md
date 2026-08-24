# Task 005 — Brute force detector

```yaml
status: done
reviewer_verdict: approved
completed_attempt: runs/005/attempt-1
depends_on: [002, 004]
budget_attempts: 10
worker_model: qwen3.6:27b
worker_provider: ollama-launch
parallel_with: [006, 007]
```

## Goal

Implement `detect_brute_force` per `docs/RULES.md` (`auth.brute_force`).

## Context

- **Implement in:** `src/sentinel_lite/detectors/brute_force.py` only  
- Package re-exports via `detectors/__init__.py` (do **not** edit `__init__.py`)  
- Config key: `config.detectors["brute_force"]`  
  - `enabled` (if false, return `[]`)  
  - `fail_threshold` (default 5)  
  - `window_seconds` (default 300)  
  - `severity` (string → `Severity`)  
- Failures only; group by `src_ip`  
- Use `make_fingerprint` and non-empty `evidence`  
- Prefer helpers from `time_window` (`group_by`, `sliding_fail_clusters`, `window_start_iso`)  
- Rule id exactly: `auth.brute_force`  
- Title example: `Authentication brute force`  
- MITRE optional: `mitre=["T1110.001"]`

## In scope

- `src/sentinel_lite/detectors/brute_force.py`
- `tests/detectors/test_brute_force.py` (only if needed to clarify — prefer fixing code)

## Out of scope

- `detectors/__init__.py`, other detector modules  
- Spray / success_after_fail logic  
- CLI  

## Success criteria

1. `pytest tests/detectors/test_brute_force.py -q` exits 0  
2. No files modified outside in-scope paths  

## Commands

```bash
pytest tests/detectors/test_brute_force.py -q
```

## Budget

- Max 10 attempts  

## Done report

Include sample finding fields for the brute_force fixture.
