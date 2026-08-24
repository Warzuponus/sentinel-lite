# Sealed tasks

Execute **in dependency order**. Update `status` in each file header as you go.

| ID | Title | Depends | Status |
|----|--------|---------|--------|
| 001 | Models and config | — | done (baseline) |
| 002 | SSH parser | 001 | done (qwen3.6:27b, attempt-3) |
| 002b | SSH parser review send-back | 002 | done (attempt-1) |
| 003 | JSON parser | 001 | done (parallel, attempt-1) |
| 004 | Time windows | 001 | done (parallel, attempt-1) |
| 005 | Brute force detector | 002, 004 | done (attempt-1) |
| 006 | Password spray detector | 002, 004 | done (attempt-1) |
| 007 | Success after fail | 002, 004 | done (after 007b) |
| 007b | Success after fail fix | 007 | done (attempt-1) |
| 008 | Run all + analyze_path | 002, 003, 005–007 | done (attempt-1) |
| 009 | CLI | 008 | done (attempt-1) |
| 010 | Golden e2e | 008, 009 | done (attempt-1, no code changes) |
| 011 | DAC rule pack + explain | 010 | done (llamacpp-qwen, attempt-1) |
| 012 | rules test fixture contract | 011 | done (llamacpp-qwen, attempt-1) |

**MVP complete:** full `pytest` green. See `docs/EXPERIMENT_REPORT.md`.

## Worker instructions

1. Read `../AGENTS.md`  
2. Open exactly one pending task whose dependencies are `done`  
3. Run only that task’s **Commands** until green or budget exhausted  
4. Write `../runs/<id>/attempt-K/report.md`  
5. Request cloud review before starting the next task (recommended)

## Parallelism

002, 003, and 004 may run **in parallel** after 001 (different modules).  
005, 006, and 007 may run **in parallel** after 002+004 (separate detector files).  
008 waits for detectors + both parsers.
