# Task 012 — rules test (fixture contract)

```yaml
status: done
depends_on: [011]
budget_attempts: 8
worker_model: llamacpp-qwen/Qwen3.8-27B-UD-Q5_K_XL
completed_attempt: runs/012/attempt-1
reviewer_verdict: approved
```

## Goal

Add `test_rules()` and `sentinel-lite rules test` so each YAML document's positive fixture must fire that `rule_id` and the negative fixture must not.

## In scope

- `src/sentinel_lite/dac.py` (add `test_rules` + `RuleTestResult`)
- `src/sentinel_lite/cli.py` (`rules test` only)
- `tests/test_dac_rules_test.py` (planner-owned; do not weaken)
- `runs/012/attempt-1/report.md`

## Out of scope

- New detectors, new rule IDs, new deps
- Changing YAML explanations
- Live logs / network

## API

```python
@dataclass(frozen=True)
class RuleTestResult:
    rule_id: str
    passed: bool
    problems: list[str]

def test_rules(rules_dir, config=None, repo_root=None) -> list[RuleTestResult]:
    """For each loaded rule:
    - analyze positive_fixture (path relative to repo_root, default cwd)
      and require at least one Finding with finding.rule_id == rule.id
    - analyze negative_fixture and require zero Findings with that rule_id
    Never raise for a failed assertion — put text in problems and passed=False.
    Invalid pack / missing fixture file → that rule passed=False with a problem.
    """
```

Use `sentinel_lite.config.default_config()` when config is None.
Use `sentinel_lite.analyze.analyze_path`.

CLI:

```
sentinel-lite rules test [--rules-dir DIR]
```

- Exit 0 if every rule passed; print one `PASS rule_id` line per rule
- Exit 1 if any failed; print `FAIL rule_id: ...` for failures
- `--rules-dir` on the subparser (same as list/lint/explain)

## Success criteria

1. `pytest tests/test_dac_rules_test.py -q` exits 0
2. `pytest -q` exits 0
3. `python -m sentinel_lite.cli rules test` exits 0 from repo root

## Commands

```bash
source .venv/bin/activate
pytest tests/test_dac_rules_test.py -q
pytest -q
```
