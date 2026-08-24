"""Load analysis configuration from YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from sentinel_lite.models import AnalysisConfig


def load_config(path: str | Path) -> AnalysisConfig:
    """Load and validate config from a YAML file."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ValueError(f"Config root must be a mapping, got {type(data).__name__}")
    return AnalysisConfig.model_validate(data)


def default_config() -> AnalysisConfig:
    """Return built-in defaults matching config.example.yaml."""
    data: dict[str, Any] = {
        "version": 1,
        "detectors": {
            "brute_force": {
                "enabled": True,
                "fail_threshold": 5,
                "window_seconds": 300,
                "severity": "high",
            },
            "password_spray": {
                "enabled": True,
                "user_threshold": 5,
                "window_seconds": 600,
                "severity": "high",
            },
            "success_after_fail": {
                "enabled": True,
                "fail_threshold": 3,
                "window_seconds": 900,
                "require_same_ip": False,
                "severity": "critical",
            },
        },
        "output": {"fingerprint_version": 1},
    }
    return AnalysisConfig.model_validate(data)
