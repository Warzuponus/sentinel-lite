"""Detection-as-Code pack tests (Task 011). Planner-owned; start RED."""

from __future__ import annotations

from pathlib import Path

import pytest

from sentinel_lite.cli import main
from sentinel_lite.dac import RuleValidationError, explain_rule, lint_rules, load_rules

REPO = Path(__file__).resolve().parents[1]
RULES = REPO / "rules"


def test_load_three_allowed_rules() -> None:
    rules = load_rules(RULES)
    ids = {r.id for r in rules}
    assert ids == {
        "auth.brute_force",
        "auth.password_spray",
        "auth.success_after_fail",
    }


def test_lint_clean_pack() -> None:
    problems = lint_rules(RULES)
    assert problems == []


def test_lint_rejects_missing_title(tmp_path: Path) -> None:
    bad = tmp_path / "auth.brute_force.yml"
    bad.write_text("id: auth.brute_force\nseverity: high\n", encoding="utf-8")
    problems = lint_rules(tmp_path)
    assert problems
    with pytest.raises(RuleValidationError):
        load_rules(tmp_path)


def test_explain_contains_mitre_and_narrative() -> None:
    text = explain_rule("auth.brute_force", RULES)
    assert "T1110.001" in text
    assert "IP-centric" in text
    assert "Shared NAT" in text


def test_cli_list_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["rules", "list", "--rules-dir", str(RULES)])
    assert code == 0
    out = capsys.readouterr().out
    assert "auth.brute_force" in out
    assert "Authentication brute force" in out


def test_cli_lint_ok() -> None:
    assert main(["rules", "lint", "--rules-dir", str(RULES)]) == 0


def test_cli_explain_unknown_id() -> None:
    assert main(["rules", "explain", "auth.not_a_rule", "--rules-dir", str(RULES)]) == 1


def test_cli_explain_brute_force(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["rules", "explain", "auth.brute_force", "--rules-dir", str(RULES)])
    assert code == 0
    out = capsys.readouterr().out
    assert "T1110.001" in out
    assert "Authentication brute force" in out
