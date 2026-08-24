# Task 002 — OpenSSH auth.log parser

```yaml
status: done
depends_on: [001]
budget_attempts: 8
worker_model: qwen3.6:27b
worker_provider: ollama-launch
completed_attempt: runs/002/attempt-3
```

## Goal

Parse OpenSSH-style auth log lines into `AuthEvent` records; skip noise safely.

## Context

- Fixtures: `tests/fixtures/ssh/`
- API: `parse_ssh_auth_line`, `parse_ssh_auth_file` in `src/sentinel_lite/parsers/__init__.py`
- Syslog lines **without year** → use year **2024**
- Support:
  - `Failed password for USER from IP port N ssh2`
  - `Failed password for invalid user USER from IP port N ssh2`
  - `Accepted password for USER from IP port N ssh2`
  - `Accepted publickey for USER from IP port N ssh2`
- `service` must be `"sshd"`
- Non-matching lines → `None` (do not raise)

## In scope

- `src/sentinel_lite/parsers/__init__.py` (SSH-related functions only; leave JSON stubs raising NotImplementedError)
- `tests/parsers/test_ssh_parser.py` (add cases only if needed to clarify)

## Out of scope

- JSON parser (Task 003)
- Detectors
- Changing AuthEvent schema
- Full rsyslog/journald support

## Success criteria

1. `pytest tests/parsers/test_ssh_parser.py -q` exits 0  
2. No modifications outside in-scope paths  
3. File parser skips noise lines without crashing  

## Commands

```bash
pytest tests/parsers/test_ssh_parser.py -q
```

## Implementation hints

- `re` with explicit patterns is fine  
- Strip lines; ignore empties  
- Port may be captured into `extras["port"]` optionally  
- Timestamps: parse `Jan 15 10:00:01` → `datetime(2024, 1, 15, 10, 0, 1)` (naive OK)

## Budget

- Max 8 attempts  
- Escalate if same error 3×  

## Done report

List patterns supported; note any ambiguous sshd message types skipped.
