# Task 007b — Review send-back: success_after_fail indentation bug

```yaml
status: done
reviewer_verdict: approved
completed_attempt: runs/007b/attempt-1
depends_on: [007]
budget_attempts: 8
worker_model: qwen3.6:27b
worker_provider: ollama-launch
kind: review_sendback
parent_task: 007
```

## Goal

Fix `detect_success_after_fail` so the positive fixture produces findings. Root cause is almost certainly **dead code after `continue`** (wrong indentation).

## Reviewer finding

In `src/sentinel_lite/detectors/success_after_fail.py`, the success-handling body is indented **under** `continue`, so it never runs:

```python
for ev in events:
    if ev.result != AuthResult.SUCCESS:
        continue

        if require_same_ip:   # ← unreachable (dead code)
            ...
```

The success path must run for every `AuthResult.SUCCESS` event (not be nested under `continue`).

Also ensure:

1. `from collections.abc import Sequence` is imported if used in annotations (or keep annotations consistent).
2. Config `enabled` honored: if `success_after_fail.enabled` is false, return `[]`.
3. Prior failures window: `(success_ts - window_seconds) < fail_ts <= success_ts`
4. Same username; if `require_same_ip`, same `src_ip` too
5. `rule_id == "auth.success_after_fail"`, non-empty evidence, fingerprint via `make_fingerprint`
6. Clean day still returns no findings

## In scope

- `src/sentinel_lite/detectors/success_after_fail.py`
- Prefer not to edit tests

## Out of scope

- Other detectors, parsers, CLI

## Success criteria

1. `pytest tests/detectors/test_success_after_fail.py -q` exits 0  
2. No files outside in-scope  

## Commands

```bash
pytest tests/detectors/test_success_after_fail.py -q
```

## Budget

- Max 8 attempts  

## Done report

Confirm the indentation fix and that both tests pass.
