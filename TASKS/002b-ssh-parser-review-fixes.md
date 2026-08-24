# Task 002b — Review send-back: SSH parser cleanup

```yaml
status: done
depends_on: [002]
budget_attempts: 8
worker_model: qwen3.6:27b
worker_provider: ollama-launch
kind: review_sendback
parent_task: 002
completed_attempt: runs/002b/attempt-1
reviewer_verdict: approved
```

## Goal

Address cloud reviewer findings on Task 002 SSH parser. Keep all existing Task 002 behavior; harden and tidy only.

## Reviewer findings (fix these)

1. **Private regex names** — rename module-level `SSH_FAIL_RE` / `SSH_ACCEPT_RE` to `_SSH_FAIL_RE` / `_SSH_ACCEPT_RE`. Do not leave public aliases.
2. **Invalid dates must not raise** — if `datetime(...)` would fail (e.g. Feb 30), return `None` from the line parser (catch `ValueError`), never crash `parse_ssh_auth_file`.
3. **Misleading comment** — remove or rewrite the comment that claims fail must be checked before accept “because both match sshd”. That reason is wrong; either delete the comment or state a correct reason (e.g. independent patterns; order is arbitrary).
4. **EOL anchor** — auth regexes must not match when trailing garbage follows `ssh2` (e.g. `... ssh2 EXTRA` → `None`). Anchor the end of the match (e.g. `\s*$` after `ssh2` or equivalent).
5. **Optional DRY** — a small private helper to build `AuthEvent` for fail/accept is welcome but not required if tests pass.

## Context

- Implementation: `src/sentinel_lite/parsers/__init__.py`
- Existing tests (must stay green): `tests/parsers/test_ssh_parser.py`
- New review tests: `tests/parsers/test_ssh_parser_review.py` (**do not weaken or delete assertions**)

## In scope

- `src/sentinel_lite/parsers/__init__.py` (SSH-related code only; leave JSON stubs as NotImplementedError)
- `tests/parsers/test_ssh_parser_review.py` only if a true test bug is found (document why) — prefer fixing code, not tests

## Out of scope

- JSON parser (Task 003)
- Detectors, CLI, schema changes
- New dependencies
- Expanding supported sshd message types beyond current patterns

## Success criteria

1. `pytest tests/parsers/test_ssh_parser.py tests/parsers/test_ssh_parser_review.py -q` exits 0  
2. No files modified outside in-scope paths  
3. JSON functions still raise `NotImplementedError`  
4. Public names `SSH_FAIL_RE` / `SSH_ACCEPT_RE` are gone  

## Commands

```bash
pytest tests/parsers/test_ssh_parser.py tests/parsers/test_ssh_parser_review.py -q
```

## Budget

- Max 8 attempts  
- Escalate if same error 3×  

## Done report

Write to the attempt `report.md`:

- Status green | escalated  
- List each finding (1–4) and how it was addressed  
- Confirm both test modules green  
