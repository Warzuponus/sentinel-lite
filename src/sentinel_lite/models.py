"""Core data models for events and findings.

Task 001 owns this module. Implementations must preserve field names and types
so detectors and golden tests remain stable. See docs/FINDING_SCHEMA.md.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AuthResult(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    UNKNOWN = "unknown"


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuthEvent(BaseModel):
    """Normalized authentication event produced by parsers."""

    timestamp: datetime
    src_ip: str
    username: str
    result: AuthResult
    service: str
    raw: str
    # Optional metadata (port, hostname, parser name, etc.)
    extras: dict[str, Any] = Field(default_factory=dict)

    model_config = {"extra": "forbid"}


class Finding(BaseModel):
    """A single detection finding. Schema is law — do not invent alternate shapes."""

    rule_id: str
    severity: Severity
    title: str
    description: str
    timestamp: datetime
    src_ip: str | None = None
    username: str | None = None
    evidence: list[str] = Field(default_factory=list)
    fingerprint: str
    mitre: list[str] = Field(default_factory=list)
    extras: dict[str, Any] = Field(default_factory=dict)

    model_config = {"extra": "forbid"}


class AnalysisConfig(BaseModel):
    """Loaded from YAML config. Detectors read thresholds from here."""

    version: int = 1
    detectors: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)

    model_config = {"extra": "allow"}
