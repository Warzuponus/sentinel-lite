"""Task 012: rules test fixture contract. Planner-owned; start RED."""

from __future__ import annotations

import tempfile
from pathlib import Path

from sentinel_lite.cli import main
from sentinel_lite.dac import test_rules

REPO = Path(__file__).resolve().parents[1]
RULES = REPO / "rules"


def test_real_pack_all_pass() -> None:
    results = test_rules(RULES, repo_root=REPO)
    assert {r.rule_id for r in results} == {
        "auth.brute_force",
        "auth.password_spray",
        "auth.success_after_fail",
    }
    assert all(r.passed for r in results), [r for r in results if not r.passed]


def test_brute_force_negative_on_clean_is_enforced() -> None:
    """If someone pointed brute_force positive at clean_day, test_rules must fail."""
    # Use a temp pack that copies brute_force YAML but swaps positive → clean_day
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        src = RULES / "auth.brute_force.yml"
        text = src.read_text(encoding="utf-8")
        text = text.replace(
            "positive_fixture: tests/fixtures/ssh/brute_force_single_ip.log",
            "positive_fixture: tests/fixtures/ssh/clean_day.log",
        )
        (tmp / "auth.brute_force.yml").write_text(text, encoding="utf-8")
        results = test_rules(tmp, repo_root=REPO)
        assert len(results) == 1
        assert results[0].rule_id == "auth.brute_force"
        assert results[0].passed is False
        assert results[0].problems


def test_missing_fixture_is_failure(tmp_path: Path) -> None:
    (tmp_path / "auth.brute_force.yml").write_text(
        (RULES / "auth.brute_force.yml")
        .read_text(encoding="utf-8")
        .replace(
            "positive_fixture: tests/fixtures/ssh/brute_force_single_ip.log",
            "positive_fixture: tests/fixtures/ssh/does_not_exist.log",
        ),
        encoding="utf-8",
    )
    results = test_rules(tmp_path, repo_root=REPO)
    assert results[0].passed is False


def test_cli_rules_test_ok() -> None:
    assert main(["rules", "test", "--rules-dir", str(RULES)]) == 0
