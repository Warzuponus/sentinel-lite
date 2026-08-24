#!/usr/bin/env python3
"""Build a sealed-task worker prompt for the local model."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def find_task(task_id: str) -> Path:
    # Support numeric ids (002), alphanumeric send-backs (002b), and full stems.
    raw = task_id.strip()
    tid = raw.zfill(3) if raw.isdigit() else raw
    matches = sorted(ROOT.joinpath("TASKS").glob(f"{tid}-*.md"))
    matches = [m for m in matches if m.name != "README.md"]
    if not matches and raw.isdigit():
        matches = sorted(ROOT.joinpath("TASKS").glob(f"{int(raw):03d}-*.md"))
        matches = [m for m in matches if m.name != "README.md"]
    if not matches:
        raise SystemExit(f"No task file for id {task_id!r} under TASKS/")
    return matches[0]


def extract_commands(brief: str) -> list[str]:
    """Pull bash commands from ## Commands fenced block."""
    m = re.search(r"## Commands\s*```(?:bash)?\s*\n(.*?)```", brief, re.S)
    if not m:
        return []
    lines = []
    for line in m.group(1).splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            lines.append(line)
    return lines


def extract_in_scope(brief: str) -> list[str]:
    m = re.search(r"## In scope\s*\n(.*?)(?:\n## |\Z)", brief, re.S)
    if not m:
        return []
    paths = []
    for line in m.group(1).splitlines():
        line = line.strip()
        if line.startswith("- `") and line.endswith("`"):
            paths.append(line[3:-1].split()[0].rstrip("`"))
        elif line.startswith("- "):
            # bare path
            paths.append(line[2:].split()[0])
    return paths


def run_baseline(commands: list[str]) -> str:
    if not commands:
        return "(no commands in brief)"
    chunks = []
    for cmd in commands:
        proc = subprocess.run(
            cmd,
            shell=True,
            cwd=ROOT,
            capture_output=True,
            text=True,
            env={**dict(**{k: v for k, v in __import__("os").environ.items()}), "PYTHONPATH": str(ROOT / "src")},
        )
        # Prefer venv pytest
        chunks.append(
            f"$ {cmd}\nexit={proc.returncode}\n"
            f"--- stdout ---\n{proc.stdout[-6000:]}\n"
            f"--- stderr ---\n{proc.stderr[-4000:]}"
        )
    return "\n\n".join(chunks)


def build_prompt(task_path: Path, *, include_baseline: bool = True) -> str:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    brief = task_path.read_text(encoding="utf-8")
    commands = extract_commands(brief)
    in_scope = extract_in_scope(brief)
    baseline = run_baseline(commands) if include_baseline else "(skipped)"

    # Seed in-scope file contents (truncate large files)
    file_blobs = []
    for rel in in_scope:
        # strip trailing comments from brief paths like `file.py` (foo)
        rel = rel.strip("`")
        path = ROOT / rel
        if not path.is_file():
            # try if path had trailing note
            continue
        text = path.read_text(encoding="utf-8")
        if len(text) > 12000:
            text = text[:12000] + "\n... [truncated] ..."
        file_blobs.append(f"### {rel}\n```\n{text}\n```")

    files_section = "\n\n".join(file_blobs) if file_blobs else "(no in-scope files readable yet)"

    return f"""# Local worker assignment — sentinel-lite

You are the **local coding worker**. Follow AGENTS.md strictly.
Implement **only this sealed task**. Do not redesign the project.

## Hard rules
1. Touch **only** files listed under **In scope** in the task brief.
2. Loop: edit → run success commands → fix until green or budget exhausted.
3. Do not add dependencies. Do not change AuthEvent/Finding schema.
4. Leave JSON parser stubs as NotImplementedError if this is Task 002.
5. When done (green or escalated), write a done report to the path given below.
6. Prefer the smallest change that makes tests pass.

## Repo root
{ROOT}

## Use a Python environment
Prefer:
```bash
source {ROOT}/.venv/bin/activate
export PYTHONPATH={ROOT}/src
```
Or run: `{ROOT}/.venv/bin/pytest ...`

## Success commands (must exit 0)
{chr(10).join(f"- `{c}`" for c in commands) or "- (see brief)"}

## Current test output (before your changes)
```
{baseline}
```

## Task brief
{brief}

## AGENTS.md (summary — full rules apply)
{agents[:4000]}

## In-scope file contents (current)
{files_section}

## Done report path
Write when finished:
`{ROOT}/runs/{task_path.stem.split("-")[0]}/attempt-CURRENT/report.md`

Use this format:
```markdown
# Task done report
- Status: green | escalated
- Attempts: N
- Files changed: ...
- Commands run: ...
- Residual risks / ambiguities: ...
- Notes for reviewer: ...
```

## Execution order (required)
1. Use tools to open/edit in-scope files (do not only print code in chat).
2. Implement the missing functions.
3. Run the success commands via the terminal tool.
4. If tests fail, fix and re-run until green (within budget).
5. Write the done report file with a file/write tool.

Begin now. Use tools immediately.
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("task_id", help="Task id, e.g. 002 or 2")
    ap.add_argument("-o", "--output", type=Path, help="Write prompt to file")
    ap.add_argument("--no-baseline", action="store_true", help="Skip running tests for baseline log")
    args = ap.parse_args()
    task = find_task(args.task_id)
    prompt = build_prompt(task, include_baseline=not args.no_baseline)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(prompt, encoding="utf-8")
        print(args.output)
    else:
        sys.stdout.write(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
