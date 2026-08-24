#!/usr/bin/env bash
# Run a sealed sentinel-lite task with local Ollama model via Hermes.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TASK_ID="${1:-002}"
shift || true

PRINT_PROMPT=0
MAX_TURNS="${MAX_TURNS:-40}"
MODEL="${MODEL:-qwen3.6:27b}"
PROVIDER="${PROVIDER:-ollama-launch}"
HERMES_BIN="${HERMES_BIN:-hermes}"
# terminal+file required for real coding; quiet mode previously caused plan-only no-tool runs
TOOLSETS="${TOOLSETS:-terminal,file,code_execution}"
REASONING="${REASONING:-none}"
QUIET_FLAG=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --print-prompt) PRINT_PROMPT=1; shift ;;
    --max-turns) MAX_TURNS="$2"; shift 2 ;;
    --model) MODEL="$2"; shift 2 ;;
    --provider) PROVIDER="$2"; shift 2 ;;
    --toolsets) TOOLSETS="$2"; shift 2 ;;
    --reasoning) REASONING="$2"; shift 2 ;;
    --quiet) QUIET_FLAG=(-Q); shift ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ ! -d "$ROOT/.venv" ]]; then
  python3 -m venv "$ROOT/.venv"
  # shellcheck disable=SC1091
  source "$ROOT/.venv/bin/activate"
  pip install -e ".[dev]" -q
else
  # shellcheck disable=SC1091
  source "$ROOT/.venv/bin/activate"
fi

export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

# Resolve task id for paths (numeric → zero-pad; send-backs like 002b kept as-is)
if [[ "$TASK_ID" =~ ^[0-9]+$ ]]; then
  TASK_NUM="$(printf '%03d' "$((10#$TASK_ID))")"
else
  TASK_NUM="$TASK_ID"
fi
RUN_BASE="$ROOT/runs/$TASK_NUM"
mkdir -p "$RUN_BASE"
ATTEMPT=1
while [[ -d "$RUN_BASE/attempt-$ATTEMPT" ]]; do
  ATTEMPT=$((ATTEMPT + 1))
done
ATTEMPT_DIR="$RUN_BASE/attempt-$ATTEMPT"
mkdir -p "$ATTEMPT_DIR"

PROMPT_FILE="$ATTEMPT_DIR/prompt.md"
python3 "$ROOT/scripts/build_worker_prompt.py" "$TASK_NUM" -o "$PROMPT_FILE"

# Fix done-report path inside prompt for this attempt
sed -i "s|attempt-CURRENT|attempt-$ATTEMPT|g" "$PROMPT_FILE"

echo "=== sentinel-lite local worker ==="
echo "task:     $TASK_NUM"
echo "model:    $MODEL"
echo "provider: $PROVIDER"
echo "toolsets: $TOOLSETS"
echo "reasoning:$REASONING"
echo "attempt:  $ATTEMPT"
echo "prompt:   $PROMPT_FILE"
echo "logs:     $ATTEMPT_DIR"
echo

if [[ "$PRINT_PROMPT" -eq 1 ]]; then
  echo "(--print-prompt: not invoking Hermes)"
  wc -c "$PROMPT_FILE"
  exit 0
fi

# Preflight Ollama
if ! curl -sf "http://127.0.0.1:11434/api/tags" >/dev/null; then
  echo "ERROR: Ollama not reachable at 127.0.0.1:11434" >&2
  exit 1
fi

if ! command -v "$HERMES_BIN" >/dev/null 2>&1; then
  echo "ERROR: hermes not found in PATH" >&2
  exit 1
fi

LOG_FILE="$ATTEMPT_DIR/hermes.log"
META_FILE="$ATTEMPT_DIR/meta.txt"
{
  echo "started_at=$(date -Iseconds)"
  echo "model=$MODEL"
  echo "provider=$PROVIDER"
  echo "toolsets=$TOOLSETS"
  echo "reasoning=$REASONING"
  echo "max_turns=$MAX_TURNS"
  echo "task=$TASK_NUM"
  echo "attempt=$ATTEMPT"
} >"$META_FILE"

echo "Invoking Hermes (yolo, toolsets=$TOOLSETS, max-turns=$MAX_TURNS)..."
set +e
# Prepend a hard tool-use instruction — qwen sometimes narrates without calling tools
WORKER_QUERY="$(cat <<EOF
CRITICAL: You are a coding agent with tools. You MUST use terminal/file tools to edit code and run tests. Do not only describe the plan. Do not stop until tests pass or you are blocked.

$(cat "$PROMPT_FILE")
EOF
)"
"$HERMES_BIN" chat \
  --provider "$PROVIDER" \
  -m "$MODEL" \
  -t "$TOOLSETS" \
  --reasoning "$REASONING" \
  --yolo \
  --max-turns "$MAX_TURNS" \
  --source tool \
  "${QUIET_FLAG[@]}" \
  -q "$WORKER_QUERY" \
  2>&1 | tee "$LOG_FILE"
HERMES_RC=${PIPESTATUS[0]}
set -e

echo "finished_at=$(date -Iseconds)" >>"$META_FILE"
echo "hermes_exit=$HERMES_RC" >>"$META_FILE"

# Capture post-run test status
SUCCESS_CMD_FILE="$ATTEMPT_DIR/post_test.log"
# Extract pytest command from task if present
TASK_FILE=$(ls "$ROOT/TASKS/${TASK_NUM}-"*.md 2>/dev/null | head -1 || true)
if [[ -n "${TASK_FILE:-}" ]]; then
  # Prefer pytest from task brief; fall back to common path pattern
  PYTEST_CMD=$(
    python3 -c '
import re, sys
from pathlib import Path
t = Path(sys.argv[1]).read_text()
m = re.search(r"## Commands\s*```(?:bash)?\s*\n(.*?)```", t, re.S)
if m:
    for line in m.group(1).splitlines():
        line = line.strip()
        if line.startswith("pytest"):
            print(line)
            break
' "$TASK_FILE"
  )
  if [[ -z "${PYTEST_CMD:-}" ]]; then
    PYTEST_CMD="pytest -q"
  fi
  echo "Running success command: $PYTEST_CMD"
  set +e
  # shellcheck disable=SC2086
  eval "$PYTEST_CMD" >"$SUCCESS_CMD_FILE" 2>&1
  TEST_RC=$?
  set -e
  echo "post_test_exit=$TEST_RC" >>"$META_FILE"
  echo "post_test_log=$SUCCESS_CMD_FILE" >>"$META_FILE"
  if [[ $TEST_RC -eq 0 ]]; then
    echo "STATUS: tests GREEN"
  else
    echo "STATUS: tests still FAILING (see $SUCCESS_CMD_FILE)"
  fi
fi

# Ensure a report stub exists if agent forgot
REPORT="$ATTEMPT_DIR/report.md"
if [[ ! -f "$REPORT" ]]; then
  cat >"$REPORT" <<EOF
# Task ${TASK_NUM} done report
- Status: unknown (agent did not write report)
- Hermes exit: $HERMES_RC
- See: hermes.log, post_test.log, meta.txt
- Notes for reviewer: Inspect hermes.log and git/file diffs for in-scope paths.
EOF
fi

echo
echo "Artifacts in $ATTEMPT_DIR"
exit "$HERMES_RC"
