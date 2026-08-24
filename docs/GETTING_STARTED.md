# Getting started

## 1. Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q                     # full suite should be green
sentinel-lite rules test
```

## 2. Read in this order

1. [README.md](../README.md) — what the project is  
2. [DESIGN.md](DESIGN.md) — product goals and detection MVP  
3. [ARCHITECTURE.md](ARCHITECTURE.md) — modules and data flow  
4. [FINDING_SCHEMA.md](FINDING_SCHEMA.md) — data contracts  
5. [RULES.md](RULES.md) — detection semantics  
6. [ORCHESTRATION.md](ORCHESTRATION.md) — multi-agent process  
7. [AGENTS.md](../AGENTS.md) — hard rules for agents  
8. Next open file in [TASKS/](../TASKS/)

## 3. Human path (no local model yet)

1. Open the next pending file in `TASKS/` (001–012 are done on `main`).  
2. Implement until its success commands pass.  
3. Commit (optional) and mark task status in the task file header.  
4. Proceed in dependency order.

## 4. Local-model worker path

**Recommended (configured for `qwen3.6:27b` via Ollama + Hermes):**

```bash
source .venv/bin/activate
./scripts/run_local_worker.sh 002          # first implementable task
# artifacts → runs/002/attempt-N/
```

Details: [`LOCAL_MODELS.md`](LOCAL_MODELS.md).

Manual path:

1. Point your agent at the repo root with `AGENTS.md` in context.  
2. Feed **one** task brief + only relevant failing pytest output.  
3. Enforce file allowlist in tooling if possible (or reject diffs that escape it).  
4. Stop at budget; package `runs/00N/` for cloud review.

### Suggested worker system prompt (short)

```text
You are a coding worker on sentinel-lite. Follow AGENTS.md.
Implement only the current task brief. Do not modify files outside In scope.
Run the exact success commands. Stop when green or budget is exhausted.
Do not add dependencies. Do not change Finding/AuthEvent schema.
```

## 5. Cloud planner / reviewer path

**Plan:** keep the DAG in `TASKS/`; refine briefs when workers fail for ambiguity.  
**Review:** use the checklist in `AGENTS.md`; prefer new test cases over vague nits.

## 6. Definition of “MVP done”

- `pytest` fully green  
- `sentinel-lite analyze tests/fixtures/ssh/ -o /tmp/f.json` works  
- Clean day → `[]`  
- Each attack fixture raises the expected `rule_id`  
- No network required  

## 7. Optional metrics (for the coding experiment)

Track per task in `runs/`:

| Metric | Meaning |
|--------|---------|
| attempts_to_green | Worker loop iterations |
| human_lines_touched | Lines you edited by hand |
| review_sendbacks | Cloud rejections |
| scope_violations | Escapes from allowlist |

These measure whether **sealed tasks + tests** make local models effective—not whether AI can “code in general.”
