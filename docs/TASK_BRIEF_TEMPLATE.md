# Task NNN — Title

```yaml
status: pending
depends_on: []
budget_attempts: 8
```

## Goal

One sentence outcome.

## Context

Pointers to DESIGN / RULES / files.

## In scope

- `path/to/file.py`
- `tests/...`

## Out of scope

- Explicit exclusions

## Success criteria

1. `pytest path -q` exits 0  
2. No files modified outside in scope  
3. …

## Commands

```bash
pytest path/to/tests -q
```

## Examples / notes

Concrete I/O.

## Budget

- Max attempts  
- Escalate if same error ×3  

## Done report

See AGENTS.md.
