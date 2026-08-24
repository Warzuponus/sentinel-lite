# Agent rules for sentinel-lite

This file is binding for **planner**, **worker**, and **reviewer** agents (human or model).

---

## Roles

### Planner (cloud / superior model)

- Own architecture, rule semantics, task DAG, and acceptance tests.
- Prefer updating `TASKS/*.md` and tests over writing large application code.
- Never assign a task whose dependencies are not marked complete.
- Success criteria must be **commands + observables**, not aesthetics.

### Worker (local model)

- Implement **one** sealed task at a time.
- Touch **only** files listed under **In scope** for that task.
- Loop on the task’s success commands until pass or budget exhausted.
- Do not redesign schema, add dependencies, or “improve” unrelated modules.
- If blocked 3 times with the same error → escalate (stop thrashing).

### Reviewer (cloud / superior model)

- Verify tests prove the rule (positives **and** negatives).
- Reject scope creep (files outside allowlist).
- Flag unsafe patterns: `eval`, `shell=True`, unbounded `rglob` on untrusted zips, real network calls in library code.
- On failure: return an **updated brief**, not “try harder.”

---

## Global constraints

1. **Language:** Python 3.11+, package under `src/sentinel_lite/`.
2. **Dependencies:** Only `pydantic`, `pyyaml`, and dev tools already in `pyproject.toml`. New runtime deps require planner approval in writing.
3. **Schema is law:** `AuthEvent` and `Finding` field names/types must not change without a new task that updates `docs/FINDING_SCHEMA.md` and all tests.
4. **Offline:** No network access required for tests. Do not add live HTTP/geo-IP/API clients in v1.
5. **Determinism:** Detectors must not depend on wall-clock `datetime.now()` for windowing logic used in tests; use event timestamps only (or injectable clocks if needed).
6. **Fingerprints:** Use `sentinel_lite.fingerprint.make_fingerprint` (v1). Do not invent alternate fingerprint schemes.
7. **Rule IDs:** Exactly  
   - `auth.brute_force`  
   - `auth.password_spray`  
   - `auth.success_after_fail`
8. **Safety:** Lab fixtures only. No exploit payloads, no credential stuffing against real hosts.

---

## Worker loop (mandatory)

```text
read TASKS/00N-*.md
while attempts < budget and not green:
    implement smallest change toward failing assertions
    run success commands from the brief
    if green: write runs/00N/attempt-K/report.md ; exit 0
    keep pytest output as next context
if not green: write escalation report ; exit 1
```

### Done report format

```markdown
# Task 00N done report
- Status: green | escalated
- Attempts: K
- Files changed: ...
- Commands run: ...
- Residual risks / ambiguities: ...
- Notes for reviewer: ...
```

---

## Reviewer checklist

- [ ] Success commands pass locally
- [ ] Diff limited to allowlist
- [ ] Positive fixture produces expected `rule_id`
- [ ] Clean/negative fixture produces no spurious finding for that rule
- [ ] Findings JSON-serializable (`model_dump(mode="json")`)
- [ ] No new dependencies without approval
- [ ] No schema drift
- [ ] Evidence fields non-empty when finding is raised

---

## Escalation triggers

- Same traceback 3 times
- Need to change files outside allowlist
- Tests contradict `docs/RULES.md`
- Missing fixture or ambiguous timestamp year/timezone

Escalate to planner with the failing log and a one-line hypothesis.
