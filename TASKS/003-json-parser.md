# Task 003 — JSON-lines login parser

```yaml
status: done
depends_on: [001]
budget_attempts: 8
worker_model: qwen3.6:27b
worker_provider: ollama-launch
parallel_with: [004]
completed_attempt: runs/003/attempt-1
reviewer_verdict: approved
```

## Goal

Parse NDJSON/JSONL login events into `AuthEvent`.

## Context

Line schema (all required):

```json
{"ts": "2024-01-15T10:00:01Z", "ip": "...", "user": "...", "ok": true, "svc": "webapp"}
```

Mapping:

| JSON | AuthEvent |
|------|-----------|
| `ts` | `timestamp` (timezone-aware preferred) |
| `ip` | `src_ip` |
| `user` | `username` |
| `ok` true/false | `success` / `failure` |
| `svc` | `service` |
| full line | `raw` |

Invalid JSON, missing fields, or empty line → `None`.

## In scope

- `src/sentinel_lite/parsers/__init__.py` (`parse_json_login_line`, `parse_json_login_file`)
- `tests/parsers/test_json_parser.py`

## Out of scope

- SSH parser changes (unless accidental breakage—don't)  
- Pretty-printed multi-line JSON  

## Success criteria

1. `pytest tests/parsers/test_json_parser.py -q` exits 0  
2. File read uses UTF-8  

## Commands

```bash
pytest tests/parsers/test_json_parser.py -q
```

## Budget

- Max 8 attempts  

## Done report

Note timestamp parsing library choices (`datetime.fromisoformat` OK; beware `Z` suffix on older Python—3.11+ handles or replace Z with +00:00).
