# Task 008 — Run all detectors + analyze_path

```yaml
status: done
completed_attempt: runs/008/attempt-1
reviewer_verdict: approved

depends_on: [002, 003, 005, 006, 007]
budget_attempts: 8
worker_model: qwen3.6:27b
worker_provider: ollama-launch
```

## Goal

Wire parsers and detectors into `run_all_detectors` and `analyze_path`.

## Context

### `run_all_detectors(events, config)`

1. If detector enabled, call it.  
2. Concatenate findings.  
3. Dedupe by `fingerprint` (preserve first occurrence order).  
4. Return list.

### `analyze_path(path, config)`

1. `collect_log_paths` (already stubbed with real implementation—keep/fix).  
2. Parse each file:  
   - If name suggests JSON (`*.jsonl` or `"json" in name`) → JSON parser  
   - Else → SSH parser  
3. Combine events (stable order: file sort order, then line order).  
4. `return run_all_detectors(events, config)`.

Also implement `iter_events_from_paths` if still stubbed.

## In scope

- `src/sentinel_lite/detectors/__init__.py` (`run_all_detectors`)
- `src/sentinel_lite/analyze.py`
- `src/sentinel_lite/parsers/__init__.py` (dispatcher only if needed)
- `tests/detectors/test_run_all.py`

## Out of scope

- CLI argparse (Task 009)

## Success criteria

1. `pytest tests/detectors/test_run_all.py -q` exits 0  

## Commands

```bash
pytest tests/detectors/test_run_all.py -q
```

## Budget

- Max 8 attempts  

## Done report

Confirm dedupe behavior with a sentence.
