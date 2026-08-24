# Task 002 done report
- Status: green
- Attempts: 1
- Files changed: src/sentinel_lite/parsers/__init__.py
- Commands run: pytest tests/parsers/test_ssh_parser.py -q
- Residual risks / ambiguities: none
- Notes for reviewer: all 7 tests pass on first attempt. Patterns supported below.

---

## Supported patterns (positive matches)

- `Failed password for USER from IP port N ssh2`
- `Failed password for invalid user USER from IP port N ssh2`
- `Accepted password for USER from IP port N ssh2`
- `Accepted publickey for USER from IP port N ssh2`

## Skipped (return None, no exception)

- Comments (`# ...`)
- Arbitrary non-log text
- Non-sshd syslog lines (e.g. systemd session messages)
- Empty / whitespace-only lines
- Lines lacking a valid `Mon DD HH:MM:SS` timestamp prefix
