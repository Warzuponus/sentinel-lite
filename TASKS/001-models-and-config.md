# Task 001 — Models, config, fingerprint

```yaml
status: done
depends_on: []
budget_attempts: 4
```

## Goal

Establish stable `AuthEvent`, `Finding`, config loading, and fingerprint helpers so all later tasks share one contract.

## Context

- `docs/FINDING_SCHEMA.md`
- `src/sentinel_lite/models.py`
- `src/sentinel_lite/config.py`
- `src/sentinel_lite/fingerprint.py`
- `config.example.yaml`

## In scope

- `src/sentinel_lite/models.py`
- `src/sentinel_lite/config.py`
- `src/sentinel_lite/fingerprint.py`
- `tests/test_models.py`
- `config.example.yaml` (threshold docs only)

## Out of scope

- Parsers, detectors, CLI behavior

## Success criteria

1. `pytest tests/test_models.py -q` exits 0  
2. Models reject unknown fields (`extra=forbid`)  
3. `make_fingerprint` is deterministic and 64-char hex  
4. `default_config()` and `load_config(config.example.yaml)` work  

## Commands

```bash
pytest tests/test_models.py -q
```

## Notes

**Baseline implementation is already present** in the repo. Worker should only touch this task if tests fail after environment setup. Mark complete once the command is green.

## Budget

- Max 4 attempts  
- Escalate if pydantic version issues  

## Done report

Confirm pytest green; note any env caveats.
