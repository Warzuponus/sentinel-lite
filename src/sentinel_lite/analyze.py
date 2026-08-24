"""High-level analyze orchestration. Task 008 / 009."""

from __future__ import annotations

from pathlib import Path

from sentinel_lite.detectors import run_all_detectors
from sentinel_lite.models import AnalysisConfig, AuthEvent, Finding
from sentinel_lite.parsers import parse_json_login_file, parse_ssh_auth_file


def collect_log_paths(path: str | Path) -> list[Path]:
    """Expand a file or directory into sorted log file paths."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)
    if p.is_file():
        return [p]
    files = sorted(
        f for f in p.rglob("*") if f.is_file() and not f.name.startswith(".")
    )
    return files


def analyze_path(path: str | Path, config: AnalysisConfig) -> list[Finding]:
    """Parse logs under path and run all detectors."""
    log_paths = collect_log_paths(path)
    events: list[AuthEvent] = []
    for lp in log_paths:
        name = lp.name.lower()
        if name.endswith(".jsonl") or "json" in name:
            events.extend(parse_json_login_file(lp))
        else:
            events.extend(parse_ssh_auth_file(lp))
    return run_all_detectors(events, config)
