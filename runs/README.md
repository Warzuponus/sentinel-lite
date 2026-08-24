# Agent run artifacts

Published here:

```text
runs/
  metrics.csv / metrics.json   # experiment rollup
  00N/attempt-K/
    report.md                  # worker done-report
    meta.txt                   # model / timing (paths sanitized)
```

**Not published** (gitignored): `hermes.log`, `post_test.log`, generated `prompt.md`, and `runs/parallel/` PIDs. Those can contain local absolute paths. Reproduce a task with `./scripts/run_local_worker.sh 00N` — artifacts land in a new `attempt-K/` locally.

See `docs/ORCHESTRATION.md` for the done-report format and `docs/EXPERIMENT_REPORT.md` for results.
