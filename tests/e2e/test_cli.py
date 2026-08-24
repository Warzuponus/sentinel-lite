"""Task 009 — CLI analyze command."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sentinel_lite.cli import main


def test_cli_help_exits_zero_or_two():
    # no command → help, exit 2
    assert main([]) == 2


def test_cli_analyze_writes_json(ssh_fixtures, tmp_path, monkeypatch):
    out = tmp_path / "findings.json"
    code = main(
        [
            "analyze",
            str(ssh_fixtures / "clean_day.log"),
            "-o",
            str(out),
        ]
    )
    assert code == 0
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data == []
