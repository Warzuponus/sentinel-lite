# Task 002b done report
- Status: green
- Attempts: 1
- Files changed: src/sentinel_lite/parsers/__init__.py
- Commands run: pytest tests/parsers/test_ssh_parser.py tests/parsers/test_ssh_parser_review.py -q

## Reviewer findings addressed

1. **Private regex names** — Renamed `SSH_FAIL_RE` → `_SSH_FAIL_RE` and `SSH_ACCEPT_RE` → `_SSH_ACCEPT_RE`. Updated all internal references. No public aliases left.
2. **Invalid dates must not raise** — Wrapped `datetime(...)` call in `_parse_syslog_timestamp` with `try/except ValueError`, returning `None` on invalid calendar dates (e.g. Feb 30).
3. **Misleading comment** — Replaced "must check before accepted since both match sshd" with "independent patterns; order is arbitrary".
4. **EOL anchor** — Appended `\s*$` to both `_SSH_FAIL_RE` and `_SSH_ACCEPT_RE` patterns so trailing garbage after `ssh2` no longer matches.

## Verification
- Both test modules pass: 12/12 tests green, exit code 0.
- JSON functions remain `NotImplementedError`.
- Original Task 002 behavior preserved (positives and negatives in existing suite still pass).

## Residual risks / ambiguities
- None identified. All findings addressed minimally without scope creep.

## Notes for reviewer
- No files outside the in-scope allowlist were touched.
- The `\s*$` anchor handles trailing whitespace before end of line while rejecting non-whitespace junk tokens after `ssh2`.
