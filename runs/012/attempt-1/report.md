# Task 012 done report
- Status: green
- Attempts: 1
- Files changed:
  - `src/sentinel_lite/dac.py` — added `RuleTestResult` dataclass and
    `test_rules(rules_dir, config=None, repo_root=None)`. `analyze_path` /
    `default_config` are imported inside the function to keep the module's
    import graph as before; `AnalysisConfig` is a `TYPE_CHECKING` import.
  - `src/sentinel_lite/cli.py` — added `rules test` subcommand
    (`--rules-dir` via the shared subparser loop). Prints one `PASS <id>`
    per rule, `FAIL <id>: <problems joined by '; '>` for failures; returns
    0 only if every rule passed.
- Commands run:
  - `pytest tests/test_dac_rules_test.py -q` → 4 passed
  - `pytest -q` → 56 passed
  - `python -m sentinel_lite.cli rules test` (repo root) →
    `PASS auth.brute_force`, `PASS auth.password_spray`,
    `PASS auth.success_after_fail`, exit 0
- Residual risks / ambiguities:
  - Pytest collected `sentinel_lite.dac.test_rules` as a test item on the
    first run ("fixture 'rules_dir' not found") because the planner-specified
    name starts with `test_`. Fixed in-module with
    `test_rules.__test__ = False` (plus a `# type: ignore` for pyright).
    This is the standard pytest escape hatch; no test files or conftest were
    touched.
  - Invalid-pack case (not covered by planner tests): `test_rules` returns
    one failed `RuleTestResult` per rule id found in the pack (falling back
    to all allowed ids if none can be parsed), each carrying the
    `RuleValidationError` text as its problem.
- Notes for reviewer:
  - Detectors, YAML rules, fixtures, and existing tests are unchanged.
  - `test_rules` never raises for fixture/analysis problems; all failures
    land in `problems` with `passed=False`, per the brief.
  - Negative-fixture check is rule-scoped (zero findings with that
    `rule_id`), matching the password_spray YAML whose negative fixture is
    the brute_force log (which legitimately fires `auth.brute_force`).
