# sentinel-lite

[![tests](https://github.com/Warzuponus/sentinel-lite/actions/workflows/test.yml/badge.svg)](https://github.com/Warzuponus/sentinel-lite/actions/workflows/test.yml)

**Lab-bound authentication log threat detector** and a working example of **multi-agent Detection-as-Code**: a cloud planner writes sealed tasks, a local model implements against tests, a reviewer checks scope.

This is **not** a SIEM. It is a small, offline pipeline you can finish — or extend — by delegating one task at a time to a weaker/local model.

| Layer | Role |
|--------|------|
| **Cloud model (e.g. Grok)** | Plan architecture, write sealed task briefs, review completed work |
| **Local model agent** | Implement code against tests in a tight loop until green |
| **Tests + fixtures + YAML rules** | Objective success criteria (no subjective “looks good”) |

Experiment write-up: [`docs/EXPERIMENT_REPORT.md`](docs/EXPERIMENT_REPORT.md).

## What it does

1. **Parse** auth logs (OpenSSH `auth.log`-style lines + JSON-lines app logins).
2. **Normalize** into `AuthEvent` records.
3. **Detect**:
   - `auth.brute_force` — many failures from one IP in a time window
   - `auth.password_spray` — many distinct usernames from one IP
   - `auth.success_after_fail` — success after recent failures (possible compromise)
4. **Emit** JSON findings with stable fingerprints for dedupe and golden tests.
5. **Declare** those detections as YAML under `rules/` and prove them with `sentinel-lite rules test`.

**Out of scope:** live packet capture, ML anomaly models, firewall blocking, exploit tooling, cloud API calls, production deployment.

All tests run **offline** against synthetic fixtures under `tests/fixtures/` (RFC 5737 documentation IPs).

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

pytest -q
sentinel-lite analyze tests/fixtures/ssh/ -o findings.json
sentinel-lite rules test
```

Optional config:

```bash
cp config.example.yaml config.yaml
sentinel-lite analyze tests/fixtures/ssh/ -c config.yaml -o findings.json
```

## Repository layout

```text
sentinel-lite/
├── README.md                 # You are here
├── AGENTS.md                 # Rules for planner / worker / reviewer agents
├── pyproject.toml
├── config.example.yaml
├── rules/                    # Detection-as-Code YAML pack
├── docs/                     # Design, schema, orchestration, experiment report
├── TASKS/                    # Sealed work packages (001–012)
├── scripts/                  # Local Hermes worker launcher
├── src/sentinel_lite/        # Implementation
├── tests/                    # Unit, detector, e2e + fixtures
└── runs/                     # Per-task done reports + metrics (logs stay local)
```

## Multi-agent workflow

1. **Planner (cloud)** reads `docs/DESIGN.md` and opens the next ready `TASKS/00N-*.md`.
2. **Worker (local)** implements only allowed files; loops: edit → run success commands → fix.
3. On green or budget exhaust: write a **done report** under `runs/`.
4. **Reviewer (cloud)** checks scope, safety, false-positive risk; approves or sends back an updated brief.

```bash
# From repo root — runs Hermes against a sealed task
./scripts/run_local_worker.sh 002

# Print prompt only (no model call)
./scripts/run_local_worker.sh 002 --print-prompt
```

Model notes: [`docs/LOCAL_MODELS.md`](docs/LOCAL_MODELS.md).  
Orchestration: [`docs/ORCHESTRATION.md`](docs/ORCHESTRATION.md) and [`AGENTS.md`](AGENTS.md).

## Safety

- Synthetic logs only.
- No credential harvesting, no offensive exploit development, no scanning of networks you do not own.
- Do not commit real production logs or secrets. See [`SECURITY.md`](SECURITY.md).

## License

MIT. See [`LICENSE`](LICENSE).
