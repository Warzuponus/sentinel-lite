# sentinel-lite multi-agent experiment report

**Date:** 2026-08-07 → 2026-08-08  
**Project:** Lab auth-log threat detector (`sentinel-lite`)  
**Worker model:** `qwen3.6:27b` (Q4_K_M, Ollama, 100% GPU)  
**Hardware:** AMD Threadripper PRO 3945WX (12c/24t), 64 GB RAM, **Radeon RX 7900 XTX 24 GB**, ROCm  
**Agent runner:** Hermes (`terminal,file,code_execution`, `--reasoning none`, `--yolo`)  
**Planner / reviewer:** Cloud model (Grok) — sealed tasks, review send-backs, orchestration  

**Final status:** **MVP complete.** `pytest -q` → **44/44 passed.** CLI works on fixtures.

---

## 1. What was built

Offline pipeline:

```text
logs → parsers (SSH + JSONL) → AuthEvent[] → detectors → Finding[] → findings.json
```

Detectors:

| Rule ID | Behavior |
|---------|----------|
| `auth.brute_force` | ≥N failures / IP / window |
| `auth.password_spray` | ≥N distinct usernames failing from one IP / window |
| `auth.success_after_fail` | success after ≥N prior fails for same user |

Entry points:

```bash
source .venv/bin/activate
pytest -q
sentinel-lite analyze tests/fixtures/ssh/ -o findings.json
```

---

## 2. Task outcomes

| Task | Description | Green attempt | Post-test | Notes |
|------|-------------|---------------|-----------|--------|
| 001 | Models / config | baseline | pass | Scaffold, not local model |
| 002 | SSH parser | attempt-3 | pass | attempt-2 plan-only (no tools) |
| 002b | Review send-back | attempt-1 | pass | Private regex, dates, EOL |
| 003 | JSON parser | attempt-1 | pass | Parallel with 004 |
| 004 | Time windows | attempt-1 | pass | Parallel with 003 |
| 005 | Brute force | attempt-1 | pass | Parallel trio |
| 006 | Password spray | attempt-1 | pass | Parallel trio |
| 007 | Success after fail | attempt-1 | **fail** | Indentation dead-code |
| 007b | Send-back fix | attempt-1 | pass | ~1 min after clear brief |
| 008 | run_all + analyze | attempt-1 | pass | Sequential |
| 009 | CLI | attempt-1 | pass | Sequential |
| 010 | Golden e2e | attempt-1 | pass | Already green; verify only |

### Success rates (local worker)

| Metric | Value |
|--------|--------|
| Implementable tasks (002–010 + send-backs) | 12 run attempts with hermes |
| First-attempt green (post_test=0) | 9 / 11 meaningful attempts* |
| Send-backs required | 2 (002b quality, 007b bug) |
| Human implementation of product code | ~0 (scaffold + review tests only) |
| Full suite tests | **44 passed** |

\*Excludes 002 attempt-2 (tool config failure, not model coding failure). Includes 007 fail then 007b success.

---

## 3. Wall-clock metrics (from `runs/*/attempt-*/meta.txt`)

| Task | Duration (s) | Hermes duration | Tool calls | Parallel cohort |
|------|-------------:|-----------------|----------:|-----------------|
| 002-3 | 97 | 1m 14s | 12 | solo |
| 002b | 99 | 1m 37s | 17 | solo |
| 003 | 397 | 6m 35s | 15 | dual w/ 004 |
| 004 | 352 | 5m 51s | 11 | dual w/ 003 |
| 005 | 763 | 12m 41s | 24 | trio |
| 006 | 773 | 12m 51s | 27 | trio |
| 007 | 1023 | 17m 2s | 80 | trio (failed) |
| 007b | 74 | 1m 12s | 11 | solo |
| 008 | 121 | 1m 59s | 16 | solo |
| 009 | 171 | 2m 48s | 16 | solo |
| 010 | 42 | 40s | 6 | solo |

**Green-task wall time sum (sequential equivalent of green runs):** ~2889 s ≈ **48 min** of agent time.  
**All attempts including fails:** ~4077 s ≈ **68 min** of agent wall.

**Calendar time with parallelism:** dual (003+004) and trio (005–007) overlapped, so wall clock for those phases was closer to **max(cohort)** than **sum(cohort)**.

Raw data: `runs/metrics.json`, `runs/metrics.csv`.

---

## 4. Token generation speed (Ollama `qwen3.6:27b` on 7900 XTX)

Measured via Ollama `/api/generate` (`num_predict` fixed, `temperature=0`).

### 4.1 Solo throughput

| Run | Prompt tokens | Gen tokens | Gen tok/s | Wall (s) |
|-----|--------------:|-----------:|----------:|---------:|
| Cold-ish 128 pred | 23 | 128 | **~37.4** | ~9.6 |
| Hot 64 pred | ~ | 64 | **~37.9** | ~3.3 |

**Takeaway:** Steady generation is about **37–38 tokens/s** for this 27B Q4 model on a single 7900 XTX with Ollama/ROCm. Prompt eval often **90–150 tok/s**.

### 4.2 Concurrent generates (same model, one GPU)

Hot re-test (model already loaded):

| Concurrency | Wall for batch (s) | Per-job reported gen tok/s | Interpretation |
|-------------|-------------------:|---------------------------:|----------------|
| 1 | ~3.3 | ~37.9 | Baseline |
| 2 | ~4.4 | ~37.5 each | Batch wall ≈ slowest job; **not** 2× solo wall |
| 3 | ~6.2 | ~37.5 each | Batch wall grows with N; still **serialized decode** |

An earlier dual run during concurrent Task 008 load showed **~47 s** wall for two 128-token jobs — evidence that **competing agent load + queueing** inflates wall time even when per-job “eval_tps” still reports ~37.

**Takeaway:**

1. **Decode is effectively single-stream on this setup** for a 27B model filling ~18–20 GB VRAM.  
2. Reported `eval_tps` per job can stay ~37 while **latency multiplies** under concurrency.  
3. Do **not** expect 2–3 agents to each get 37 tok/s of simultaneous decode.

### 4.3 Why multi-agent still helped wall clock

Hermes agents spend substantial time on **tools** (read/patch/pytest), which is **CPU/disk**, not GPU decode.

```text
Agent A: [generate] → [pytest 0.4s] → [generate] → ...
Agent B:     [generate] → [pytest] → [generate] ...
                 ↑ while A is in pytest, B can use the GPU
```

Observed:

| Cohort | Sequential sum | Observed cohort wall (≈ max) | Speedup |
|--------|---------------:|-----------------------------:|--------:|
| 003+004 | ~749 s | ~397 s | **~1.9×** |
| 005+006+007 | ~2560 s | ~1023 s | **~2.5×** (007 long/failed) |

So **parallel agents improve calendar time** when work interleaves tool I/O with generation, even though **token decode is serialized**.

---

## 5. Parallelism lessons

### What worked

1. **Module isolation before parallel work** — detectors split into `brute_force.py` / `password_spray.py` / `success_after_fail.py` so three agents did not fight one file.  
2. **003 vs 004** — different files (`parsers` JSON vs `time_window`) → clean dual.  
3. **Sealed briefs + pytest success commands** — objective done criteria.  
4. **Review send-backs with failing tests** — 002b and 007b fixed fast once findings were concrete.

### What failed / hurt

1. **First Hermes run without explicit toolsets** — model narrated code, zero file writes. Fixed with `-t terminal,file,code_execution`.  
2. **Same-file parallel edits** — would have corrupted detectors; prevented by split.  
3. **007 indentation bug** — tests should have caught it (they did); model still “exited 0” from Hermes while post_test failed — **orchestrator post_test gate is essential**.  
4. **Scaffold test bug** (`second=60` in time_window test) — planner fixed mid-run; workers can thrash on bad tests.  
5. **Triple concurrent 27B** — longer individual tasks (especially 007 with 80 tool calls) under contention.

### Recommendations

| Goal | Recommendation |
|------|----------------|
| Max quality per task | Solo agent, full GPU |
| Max calendar throughput | 2 agents on **disjoint files**; accept ~same tok/s serial decode |
| Avoid | 3+ heavy coding agents on one 24 GB card for 27B |
| Always | post_test after agent exit; review with extra negative tests |

---

## 6. Quality / review findings (summary)

| Area | Verdict |
|------|---------|
| SSH parser (+002b) | Approve — robust enough for lab |
| JSON parser | Approve |
| Time windows | Approve |
| Brute force / spray | Approve |
| Success after fail | Approve after 007b |
| run_all / analyze / CLI | Approve |
| Golden e2e | All rule IDs + clean day |

Non-blocking nits left for v1.1:

- Honor `enabled: false` in success_after_fail explicitly  
- Spray detector could re-check distinct users **inside** window before emit  
- CLI could print `Findings: N` to stderr (optional polish)  
- JSON file open could use `errors="replace"` like SSH  

---

## 7. Architecture verdict (experiment hypothesis)

> Can a cloud model plan + review while a local model implements sealed tasks with a test loop?

**Yes, for this scope.**

Evidence:

- Local model produced almost all implementation  
- Cloud model owned design, task DAG, review tests, send-backs  
- First-attempt green rate high on well-scoped pure functions  
- Failures were operational (tools) or classic bugs (indent), recoverable with sealed send-backs  

What the local model needed most:

1. File allowlists  
2. Exact pytest commands  
3. Fixtures as truth  
4. Explicit tool enablement  
5. Small modules (no multi-agent same-file fights)  

---

## 8. How to reproduce a task run

```bash
source .venv/bin/activate
./scripts/run_local_worker.sh 005 --max-turns 40
# artifacts → runs/005/attempt-N/
```

Docs: `docs/LOCAL_MODELS.md`, `docs/ORCHESTRATION.md`, `AGENTS.md`.

---

## 9. Limitations of this report’s metrics

- Hermes logs did not expose token counts / tok/s per agent turn; generation speed comes from **Ollama API microbenchmarks**, not full multi-turn sessions.  
- Dual/triple agent wall times include tool time, prompt size variance, and Ollama queueing — not pure decode.  
- No formal statistical repeats (n=1 per concurrency point).  
- `eval_tps` from Ollama is **per completed job**, not “aggregate GPU tok/s under multi-stream.”  

For stricter measurement later: log `eval_count`/`eval_duration` every Ollama call, and record `rocm-smi` time series during dual/triple agent runs.

---

## 10. Bottom line

| Question | Answer |
|----------|--------|
| Project done & fully tested? | **Yes — 44/44 tests, CLI demo OK** |
| Local 27B viable as worker? | **Yes**, with sealed tasks + tools |
| Parallel agents worth it? | **Yes for wall clock** if files disjoint; **no free tok/s multiplier** |
| Gen speed on 7900 XTX? | **~37–38 tok/s** solo for this model/quant |
| Multi-request effect? | **Serialize decode**; wall ≈ queue; tool overlap still helps agents |

Artifacts to review tomorrow:

- `docs/EXPERIMENT_REPORT.md` (this file)  
- `runs/metrics.csv` / `runs/metrics.json`  
- `runs/*/attempt-*/report.md`  
- `TASKS/README.md`  
