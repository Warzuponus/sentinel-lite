"""CLI entrypoint for sentinel-lite. Task 009 owns this module."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sentinel_lite.analyze import analyze_path
from sentinel_lite.config import default_config, load_config
from sentinel_lite.dac import (
    RuleValidationError,
    explain_rule,
    lint_rules,
    load_rules,
    test_rules,
)

DEFAULT_RULES_DIR = "rules"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sentinel-lite",
        description="Lab-bound auth log threat detector",
    )
    sub = parser.add_subparsers(dest="command")

    analyze = sub.add_parser("analyze", help="Analyze log files or directories")
    analyze.add_argument("path", help="Log file or directory of logs")
    analyze.add_argument(
        "-c",
        "--config",
        default=None,
        help="Path to config YAML (default: built-in defaults)",
    )
    analyze.add_argument(
        "-o",
        "--output",
        default="findings.json",
        help="Write findings JSON to this path",
    )
    analyze.add_argument(
        "--json-stdout",
        action="store_true",
        help="Also print findings JSON to stdout",
    )

    rules = sub.add_parser("rules", help="Manage Detection-as-Code rule documents")
    rules_sub = rules.add_subparsers(dest="rules_command")
    for name, help_text in (
        ("list", "List loaded rules (id + title)"),
        ("lint", "Validate rule documents; print 'ok' on success"),
        ("explain", "Print a rule explanation"),
        ("test", "Run each rule's positive/negative fixtures"),
    ):
        sub_p = rules_sub.add_parser(name, help=help_text)
        sub_p.add_argument(
            "--rules-dir",
            default=DEFAULT_RULES_DIR,
            help=f"Directory of rule YAML files (default: {DEFAULT_RULES_DIR})",
        )
    rules_sub.choices["explain"].add_argument(
        "rule_id", help="Rule ID to explain"
    )
    return parser


def _run_rules(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    """Dispatch sentinel-lite rules <list|lint|explain>."""
    rules_command = getattr(args, "rules_command", None)
    if rules_command is None:
        parser._subparsers.choices["rules"].print_help()
        return 2
    rules_dir = getattr(args, "rules_dir", DEFAULT_RULES_DIR)

    if rules_command == "list":
        try:
            rules = load_rules(rules_dir)
        except RuleValidationError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        for rule in rules:
            print(f"{rule.id}\t{rule.title}")
        return 0

    if rules_command == "lint":
        problems = lint_rules(rules_dir)
        if problems:
            for problem in problems:
                print(problem, file=sys.stderr)
            return 1
        print("ok")
        return 0

    if rules_command == "explain":
        try:
            print(explain_rule(args.rule_id, rules_dir))
        except RuleValidationError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        return 0

    if rules_command == "test":
        results = test_rules(rules_dir)
        failed = [r for r in results if not r.passed]
        for rule in results:
            if rule.passed:
                print(f"PASS {rule.rule_id}")
            else:
                print(f"FAIL {rule.rule_id}: {'; '.join(rule.problems)}")
        return 1 if failed else 0

    parser.error(f"Unknown rules command: {rules_command}")
    return 2


def main(argv: list[str] | None = None) -> int:
    """CLI main entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 2
    if args.command == "rules":
        return _run_rules(args, parser)
    if args.command == "analyze":
        try:
            if args.config is not None:
                config = load_config(args.config)
            else:
                config = default_config()

            findings = analyze_path(args.path, config)
            payload = [f.model_dump(mode="json") for f in findings]

            out_path = Path(args.output)
            out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

            if args.json_stdout:
                print(json.dumps(payload, indent=2))

            print(f"Findings: {len(findings)}", file=sys.stderr)
            return 0
        except FileNotFoundError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
