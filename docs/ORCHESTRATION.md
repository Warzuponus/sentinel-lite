# Multi-agent orchestration

## Purpose

Validate that a **cloud planner/reviewer** plus **local implementer loop** can build a real cybersecurity tool when work is sealed behind tests.

## Control loop

```text
┌────────────────────────────────────────────────────────────┐
│ 1. Planner selects next TASK with deps satisfied           │
│ 2. Worker runs implement → test loop (budget N)            │
│ 3. Artifacts written under runs/00N/attempt-K/             │
│ 4. Reviewer approves or rewrites brief                     │
│ 5. On approve: mark task complete; unlock dependents       │
└────────────────────────────────────────────────────────────┘
```

## Task state

Suggested header fields in each `TASKS/*.md`:

```yaml
status: pending | in_progress | review | done | blocked
depends_on: [001]
```

Update status as you go (human or controller script).

## Run artifact layout

```text
runs/
  002/
    attempt-1/
      prompt_snip.md      # optional: what worker saw
      test.log            # pytest output
      report.md           # done / escalate report
    attempt-2/
      ...
```

## Budgets (defaults)

| Task type | Max attempts |
|-----------|--------------|
| Parser / pure function | 8 |
| Detector | 10 |
| CLI / e2e glue | 8 |

Escalate after **3 identical failures** even if budget remains.

## What the cloud model should write

- DESIGN and RULES updates when semantics change  
- New fixtures + tests **before** asking local models for detectors  
- Send-back briefs with concrete failing assertion names  

## What the local model should write

- Function bodies in allowlisted files  
- Minimal helpers colocated in those files  
- Not: new top-level packages, Docker, CI rewrites (unless tasked)

## Minimal controller (optional, later)

A script can:

1. Parse `status` / `depends_on` from TASKS  
2. Shell out to local agent CLI with brief path  
3. Run success commands  
4. Stop and notify for review  

This repo does **not** require a controller to start—manual orchestration is enough for the first experiment.

## Metrics log (suggested CSV)

```text
task_id,attempts,status,sendbacks,human_minutes,notes
002,4,done,1,5,timezone ambiguity fixed in brief
```

## Failure modes and fixes

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Worker edits everything | Allowlist not enforced | Reject diff; tighten brief |
| Tests pass but rule wrong | Weak tests | Reviewer adds negative fixture |
| Infinite refactors | No budget | Hard stop + escalate |
| Flaky times | Wall clock / year | Enforce year 2024 rule in RULES/parser brief |
