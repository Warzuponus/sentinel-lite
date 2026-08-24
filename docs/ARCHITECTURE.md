# Architecture

## Package map

```text
src/sentinel_lite/
  models.py          # AuthEvent, Finding, Severity, AnalysisConfig
  config.py          # load_config, default_config
  fingerprint.py     # make_fingerprint (stable)
  time_window.py     # windowing helpers for detectors
  parsers/
    __init__.py      # SSH + JSON parsers
  detectors/
    __init__.py      # brute_force, spray, success_after_fail, run_all
  analyze.py         # collect paths + analyze_path
  cli.py             # argparse entrypoint
```

## Data flow

```text
                    ┌──────────────┐
                    │ config YAML  │
                    └──────┬───────┘
                           ▼
┌─────────┐  parse   ┌───────────┐  detect  ┌──────────┐  dump  ┌─────────────┐
│ log file│ ───────► │ AuthEvent │ ───────► │ Finding  │ ─────► │ findings.json│
└─────────┘          └───────────┘          └──────────┘        └─────────────┘
```

1. **CLI** resolves config (file or defaults) and path.  
2. **analyze.collect_log_paths** expands directories.  
3. **parsers** turn lines into `AuthEvent` (skip noise → `None`).  
4. **detectors.run_all_detectors** runs enabled rules, dedupes by fingerprint.  
5. **CLI** serializes findings JSON and prints a short human summary.

## Boundaries

| Module | May import | Must not |
|--------|------------|----------|
| `models` | pydantic | parsers, detectors, cli |
| `fingerprint` | stdlib | detectors (detectors import fingerprint) |
| `parsers` | models | detectors, cli |
| `time_window` | stdlib | models optional; no I/O |
| `detectors` | models, config fields, time_window, fingerprint | cli, argparse |
| `analyze` | parsers, detectors, models | heavy CLI formatting |
| `cli` | analyze, config | detection logic inline |

## Timestamp conventions

| Source | Rule |
|--------|------|
| SSH syslog lines without year | Default year **2024** (lab constant) |
| SSH times | Naive local-lab timestamps OK; store as `datetime` (naive allowed for SSH) |
| JSON `ts` | ISO-8601; prefer timezone-aware UTC |
| Window math | Compare datetimes consistently within a single parser stream |

Workers must not call external NTP or locale-dependent parsing that breaks CI.

## Error handling

- Unparseable line → skip (not crash).  
- Missing file → CLI non-zero exit.  
- Invalid config → fail fast with clear error.  
- Empty log → empty findings list.

## Testing layers

| Layer | Location |
|-------|----------|
| Schema / config | `tests/test_models.py` |
| Parsers | `tests/parsers/` |
| Windows | `tests/test_time_window.py` |
| Detectors | `tests/detectors/` |
| E2E / CLI | `tests/e2e/` |
| Fixtures | `tests/fixtures/` |

## Deployment model

Library + console script only. No daemon in v1.
