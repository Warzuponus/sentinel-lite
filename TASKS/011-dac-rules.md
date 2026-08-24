# Task 011 — Detection-as-Code rule pack + explain CLI

```yaml
status: done
depends_on: [010]
budget_attempts: 8
worker_model: llamacpp-qwen/Qwen3.8-27B-UD-Q5_K_XL
completed_attempt: runs/011/attempt-1
reviewer_verdict: approved
```

## Goal

Load YAML detection documents from `rules/`, lint them, and print analyst explanations. Do **not** change detector matching logic.

## Context

Planner already added:

- `rules/auth.brute_force.yml`
- `rules/auth.password_spray.yml`
- `rules/auth.success_after_fail.yml`
- `tests/test_dac_rules.py` (RED until you implement)

### Schema (required keys)

Every YAML file must have:

- `id` (str, must match filename stem, one of the three allowed rule IDs)
- `title` (non-empty str)
- `severity` (`low` | `medium` | `high` | `critical`)
- `mitre` (str, e.g. `T1110.001`)
- `explanation` (non-empty str)
- `false_positives` (list of str, may be empty)
- `positive_fixture` (str path)
- `negative_fixture` (str path)

### CLI

```
sentinel-lite rules list
sentinel-lite rules lint [--rules-dir DIR]
sentinel-lite rules explain <rule_id> [--rules-dir DIR]
```

| Condition | Exit |
|-----------|------|
| list / lint / explain success | 0 |
| lint finds invalid rule | 1 |
| explain unknown id | 1 |
| no subcommand | 2 |

`list` prints one line per rule containing `id` and `title`.
`explain` prints `title`, `severity`, `mitre`, `explanation`, and each false-positive note.
`lint` prints `ok` on success.

Default `--rules-dir` is `rules` relative to cwd (the repo root when tests run).

## In scope

- `src/sentinel_lite/dac.py` (create)
- `src/sentinel_lite/cli.py` (add `rules` subcommands only)
- `rules/*.yml` (already written — do not rewrite explanations unless lint requires a missing key)
- `tests/test_dac_rules.py` (fix only if a true test bug; document why)

## Out of scope

- Changing `AuthEvent` / `Finding` / detector algorithms
- New dependencies
- Network calls
- New rule IDs
- Rewriting README except a short “Rules CLI” snippet if you have leftover budget

## Success criteria

1. `pytest tests/test_dac_rules.py -q` exits 0
2. `pytest -q` still exits 0 (no regressions)
3. `python -m sentinel_lite.cli rules lint` exits 0 from repo root
4. `python -m sentinel_lite.cli rules explain auth.brute_force` prints `T1110.001`

## Commands

```bash
source .venv/bin/activate
pytest tests/test_dac_rules.py -q
pytest -q
```

## Budget

- Max 8 attempts
- If the same traceback repeats 3 times, stop and write an escalation report

## Done report

Write `runs/011/attempt-1/report.md` with status, files changed, commands, residual risks.
