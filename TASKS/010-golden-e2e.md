# Task 010 — Golden e2e hardening

```yaml
status: done
depends_on: [008, 009]
budget_attempts: 8
worker_model: qwen3.6:27b
completed_attempt: runs/010/attempt-1
reviewer_verdict: approved
```

## Goal

Make full golden suite green; fix residual integration gaps only.

## Context

`tests/e2e/test_golden.py` asserts rule presence on attack fixtures and empty set on clean day; JSON serializable findings.

If anything fails:

- Prefer fixing detector/analyze bugs over deleting assertions  
- Do not weaken clean_day to allow noise  

## In scope

- Any file required to fix e2e failures **after** 008/009  
- Prefer: `detectors/__init__.py`, `analyze.py`, `cli.py`  
- `tests/e2e/test_golden.py` only if a true test bug is found (document why)

## Out of scope

- New rule types  
- New dependencies  

## Success criteria

1. `pytest tests/e2e/ -q` exits 0  
2. Full suite: `pytest -q` exits 0  

## Commands

```bash
pytest tests/e2e/ -q
pytest -q
```

## Budget

- Max 8 attempts  

## Done report

Paste summary of full pytest result; list any known limitations for v1.1.
