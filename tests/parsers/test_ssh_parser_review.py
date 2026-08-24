"""Task 002b — review send-back: robustness and API hygiene for SSH parser."""

from __future__ import annotations

import sentinel_lite.parsers as parsers
from sentinel_lite.models import AuthResult
from sentinel_lite.parsers import parse_ssh_auth_line


def test_module_does_not_export_public_ssh_regex_constants():
    """Regex patterns must be private (leading underscore), not public API."""
    assert not hasattr(parsers, "SSH_FAIL_RE")
    assert not hasattr(parsers, "SSH_ACCEPT_RE")
    assert hasattr(parsers, "_SSH_FAIL_RE")
    assert hasattr(parsers, "_SSH_ACCEPT_RE")


def test_invalid_calendar_date_returns_none_not_raise():
    """Malformed day-of-month must not crash the parser (return None)."""
    # Feb 30 is never valid
    line = (
        "Feb 30 12:00:00 webssh sshd[1]: "
        "Failed password for admin from 203.0.113.50 port 22 ssh2"
    )
    assert parse_ssh_auth_line(line) is None


def test_syslog_double_space_day_parses():
    """Classic syslog pads single-digit days with an extra space: 'Jan  5'."""
    line = (
        "Jan  5 10:00:01 webssh sshd[1001]: "
        "Failed password for admin from 203.0.113.50 port 51234 ssh2"
    )
    ev = parse_ssh_auth_line(line)
    assert ev is not None
    assert ev.timestamp.day == 5
    assert ev.timestamp.month == 1
    assert ev.username == "admin"
    assert ev.result == AuthResult.FAILURE


def test_trailing_garbage_after_ssh2_does_not_match():
    """Auth patterns should not match when junk follows the ssh2 token."""
    line = (
        "Jan 15 10:00:01 webssh sshd[1001]: "
        "Failed password for admin from 203.0.113.50 port 51234 ssh2 EXTRA"
    )
    assert parse_ssh_auth_line(line) is None


def test_original_suite_patterns_still_work():
    """Sanity: core accepted/failed lines still parse after hygiene changes."""
    fail = (
        "Jan 15 10:00:01 webssh sshd[1001]: "
        "Failed password for admin from 203.0.113.50 port 51234 ssh2"
    )
    ok = (
        "Jan 15 10:05:00 webssh sshd[1007]: "
        "Accepted password for alice from 198.51.100.10 port 42000 ssh2"
    )
    assert parse_ssh_auth_line(fail) is not None
    assert parse_ssh_auth_line(ok) is not None
