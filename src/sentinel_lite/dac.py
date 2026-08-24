"""Detection-as-Code loader (Task 011).

Loads, validates, and explains planner-owned YAML rule documents from a
rules directory. Rule semantics live in the YAML files; this module only
loads, lints, and formats them.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from sentinel_lite.models import AnalysisConfig

ALLOWED_RULE_IDS = frozenset(
    {
        "auth.brute_force",
        "auth.password_spray",
        "auth.success_after_fail",
    }
)

ALLOWED_SEVERITIES = frozenset({"low", "medium", "high", "critical"})

REQUIRED_KEYS = (
    "id",
    "title",
    "severity",
    "mitre",
    "explanation",
    "false_positives",
    "positive_fixture",
    "negative_fixture",
)


class RuleValidationError(Exception):
    """Raised when a rule document fails validation."""


@dataclass(frozen=True)
class Rule:
    """A validated Detection-as-Code rule document."""

    id: str
    title: str
    severity: str
    mitre: str
    explanation: str
    false_positives: list[str]
    positive_fixture: str
    negative_fixture: str


@dataclass(frozen=True)
class RuleTestResult:
    """Outcome of testing one rule's fixtures against the detectors."""

    rule_id: str
    passed: bool
    problems: list[str]


def _iter_rule_files(rules_dir: Path) -> list[Path]:
    return sorted(
        [p for p in rules_dir.iterdir() if p.suffix in (".yml", ".yaml") and p.is_file()]
    )


def _validate(doc: object, path: Path) -> list[str]:
    """Validate one parsed YAML document; return problem strings (empty = ok)."""
    problems: list[str] = []
    name = path.name

    if not isinstance(doc, dict):
        return [f"{name}: top-level YAML must be a mapping"]

    for key in REQUIRED_KEYS:
        if key not in doc:
            problems.append(f"{name}: missing required key '{key}'")
    if problems:
        return problems

    rule_id = doc["id"]
    if not isinstance(rule_id, str) or not rule_id:
        problems.append(f"{name}: 'id' must be a non-empty string")
        return problems

    if rule_id not in ALLOWED_RULE_IDS:
        problems.append(
            f"{name}: id '{rule_id}' is not one of the allowed rule IDs "
            f"({', '.join(sorted(ALLOWED_RULE_IDS))})"
        )

    if path.stem != rule_id:
        problems.append(f"{name}: id '{rule_id}' does not match filename stem '{path.stem}'")

    title = doc["title"]
    if not isinstance(title, str) or not title.strip():
        problems.append(f"{name}: 'title' must be a non-empty string")

    severity = doc["severity"]
    if severity not in ALLOWED_SEVERITIES:
        problems.append(
            f"{name}: severity '{severity}' must be one of "
            f"{sorted(ALLOWED_SEVERITIES)}"
        )

    mitre = doc["mitre"]
    if not isinstance(mitre, str) or not mitre.strip():
        problems.append(f"{name}: 'mitre' must be a non-empty string")

    explanation = doc["explanation"]
    if not isinstance(explanation, str) or not explanation.strip():
        problems.append(f"{name}: 'explanation' must be a non-empty string")

    fps = doc["false_positives"]
    if not isinstance(fps, list) or any(not isinstance(x, str) for x in fps):
        problems.append(f"{name}: 'false_positives' must be a list of strings")

    for key in ("positive_fixture", "negative_fixture"):
        value = doc[key]
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{name}: '{key}' must be a non-empty string")

    return problems


def _parse_rule(doc: dict, path: Path) -> Rule:
    return Rule(
        id=doc["id"],
        title=doc["title"],
        severity=doc["severity"],
        mitre=doc["mitre"],
        explanation=doc["explanation"],
        false_positives=list(doc["false_positives"]),
        positive_fixture=doc["positive_fixture"],
        negative_fixture=doc["negative_fixture"],
    )


def load_rules(rules_dir: Path | str) -> list[Rule]:
    """Load and validate all rule documents in *rules_dir*.

    Raises RuleValidationError on the first invalid file (with all of that
    file's problems joined).
    """
    rules_dir = Path(rules_dir)
    if not rules_dir.is_dir():
        raise RuleValidationError(f"rules directory not found: {rules_dir}")

    rules: list[Rule] = []
    for path in _iter_rule_files(rules_dir):
        try:
            raw = path.read_text(encoding="utf-8")
            doc = yaml.safe_load(raw)
        except (OSError, yaml.YAMLError) as exc:
            raise RuleValidationError(f"{path.name}: cannot parse YAML: {exc}") from exc

        problems = _validate(doc, path)
        if problems:
            raise RuleValidationError("; ".join(problems))
        rules.append(_parse_rule(doc, path))  # type: ignore[arg-type]
    return rules


def lint_rules(rules_dir: Path | str) -> list[str]:
    """Lint all rule documents; return problem strings (empty = clean).

    Never raises for validation problems.
    """
    rules_dir = Path(rules_dir)
    if not rules_dir.is_dir():
        return [f"rules directory not found: {rules_dir}"]

    problems: list[str] = []
    for path in _iter_rule_files(rules_dir):
        try:
            raw = path.read_text(encoding="utf-8")
            doc = yaml.safe_load(raw)
        except (OSError, yaml.YAMLError) as exc:
            problems.append(f"{path.name}: cannot parse YAML: {exc}")
            continue
        problems.extend(_validate(doc, path))
    return problems


def explain_rule(rule_id: str, rules_dir: Path | str) -> str:
    """Return a human-readable explanation for *rule_id*.

    Raises RuleValidationError if the id is unknown or the pack is invalid.
    """
    rules = load_rules(rules_dir)
    for rule in rules:
        if rule.id == rule_id:
            lines = [
                f"{rule.title} ({rule.id})",
                "",
                f"severity: {rule.severity}",
                f"mitre: {rule.mitre}",
                "",
                rule.explanation.strip(),
                "",
                "Known false positives:",
            ]
            if rule.false_positives:
                lines.extend(f"- {fp}" for fp in rule.false_positives)
            else:
                lines.append("- (none documented)")
            return "\n".join(lines)
    known = ", ".join(sorted(r.id for r in rules))
    raise RuleValidationError(f"unknown rule id '{rule_id}' (known: {known})")


def test_rules(
    rules_dir: Path | str,
    config: "AnalysisConfig | None" = None,
    repo_root: Path | str | None = None,
) -> list[RuleTestResult]:
    """For each loaded rule:

    - analyze positive_fixture (path relative to repo_root, default cwd)
      and require at least one Finding with finding.rule_id == rule.id
    - analyze negative_fixture and require zero Findings with that rule_id

    Never raises for a failed assertion — put text in problems and
    passed=False. Invalid pack / missing fixture file → that rule
    passed=False with a problem.
    """
    from sentinel_lite.analyze import analyze_path
    from sentinel_lite.config import default_config

    if config is None:
        config = default_config()
    root = Path(repo_root) if repo_root is not None else Path.cwd()

    results: list[RuleTestResult] = []
    rules_dir = Path(rules_dir)

    try:
        rules = load_rules(rules_dir)
    except RuleValidationError as exc:
        # Invalid pack: report every known rule id as failed, plus the
        # validation failure as the problem.
        ids: list[str] = []
        try:
            for path in _iter_rule_files(rules_dir):
                doc = yaml.safe_load(path.read_text(encoding="utf-8"))
                if isinstance(doc, dict) and isinstance(doc.get("id"), str):
                    ids.append(doc["id"])
        except (OSError, yaml.YAMLError):
            pass
        if not ids:
            ids = sorted(ALLOWED_RULE_IDS)
        for rule_id in ids:
            results.append(
                RuleTestResult(
                    rule_id=rule_id,
                    passed=False,
                    problems=[f"invalid rule pack: {exc}"],
                )
            )
        return results

    for rule in rules:
        problems: list[str] = []

        pos_path = root / rule.positive_fixture
        if not pos_path.is_file():
            problems.append(f"positive fixture not found: {pos_path}")
        else:
            try:
                findings = analyze_path(pos_path, config)
            except Exception as exc:  # noqa: BLE001 - report, never raise
                problems.append(f"positive fixture analysis failed: {exc}")
            else:
                matched = [f for f in findings if f.rule_id == rule.id]
                if not matched:
                    problems.append(
                        f"positive fixture {rule.positive_fixture} did not "
                        f"produce a finding for rule '{rule.id}'"
                    )

        neg_path = root / rule.negative_fixture
        if not neg_path.is_file():
            problems.append(f"negative fixture not found: {neg_path}")
        else:
            try:
                findings = analyze_path(neg_path, config)
            except Exception as exc:  # noqa: BLE001 - report, never raise
                problems.append(f"negative fixture analysis failed: {exc}")
            else:
                spurious = [f for f in findings if f.rule_id == rule.id]
                if spurious:
                    problems.append(
                        f"negative fixture {rule.negative_fixture} produced "
                        f"{len(spurious)} unexpected finding(s) for rule "
                        f"'{rule.id}'"
                    )

        results.append(
            RuleTestResult(
                rule_id=rule.id,
                passed=not problems,
                problems=problems,
            )
        )
    return results


# Not a pytest test despite the name (planner-specified API); stop pytest
# from trying to collect it when imported by tests.
test_rules.__test__ = False  # type: ignore[attr-defined]
