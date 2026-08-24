"""Shared pytest fixtures for sentinel-lite."""

from __future__ import annotations

from pathlib import Path

import pytest

from sentinel_lite.config import default_config
from sentinel_lite.models import AnalysisConfig

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES


@pytest.fixture
def ssh_fixtures(fixtures_dir: Path) -> Path:
    return fixtures_dir / "ssh"


@pytest.fixture
def json_fixtures(fixtures_dir: Path) -> Path:
    return fixtures_dir / "json_login"


@pytest.fixture
def config() -> AnalysisConfig:
    return default_config()
