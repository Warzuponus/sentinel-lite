# Local models (worker)

## Hardware baseline

- AMD RX 7900 XTX (24 GB VRAM), ROCm
- 64 GB system RAM
- Ollama at `http://127.0.0.1:11434`

## Primary worker

| Setting | Value |
|---------|--------|
| Model | `qwen3.6:27b` |
| Quant | Q4_K_M (~17 GB weights) |
| Hermes provider | `ollama-launch` |
| Hermes aliases | `local`, `worker` → `ollama-launch/qwen3.6:27b` |

## Run a sealed task

From the repo root:

```bash
# Task 002 (default)
./scripts/run_local_worker.sh 002

# Explicit task id
./scripts/run_local_worker.sh 005

# Dry-run: print prompt only
./scripts/run_local_worker.sh 002 --print-prompt
```

The script:

1. Loads `TASKS/00N-*.md` and `AGENTS.md`
2. Invokes **Hermes** with `--provider ollama-launch -m qwen3.6:27b`
3. Logs under `runs/00N/attempt-K/`
4. Expects the agent to implement, run the task’s pytest command, and write a done report

## Manual Hermes invocation

```bash
source .venv/bin/activate

hermes chat \
  --provider ollama-launch \
  -m qwen3.6:27b \
  -t terminal,file,code_execution \
  --reasoning none \
  --yolo \
  --max-turns 40 \
  -q "$(cat runs/002/attempt-N/prompt.md)"
```

**Note:** Always pass `-t terminal,file,code_execution`. Without explicit toolsets (or with plan-only narration), the model may describe code without writing files. Prefer `--reasoning none` for worker loops on this model.

Or use the alias (if resolved by Hermes):

```bash
hermes chat -m worker --yolo -q "..."
```

## Verify GPU is used

```bash
watch -n1 rocm-smi
# During a run, VRAM should be ~18–22 GB used
ollama ps
```

## Alternatives

| Model | When |
|-------|------|
| `qwen2.5-coder:32b` | Stronger pure coding (pull first) |
| `qwen2.5-coder:14b` | Faster retries |
| `laguna-xs-2.1` | Already installed; general agent, not first pick |

```bash
ollama pull qwen2.5-coder:32b
# then: MODEL=qwen2.5-coder:32b ./scripts/run_local_worker.sh 002
```
