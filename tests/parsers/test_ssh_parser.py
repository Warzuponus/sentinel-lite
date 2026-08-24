"""Task 002 — OpenSSH auth.log parser."""

from __future__ import annotations

from datetime import datetime

import pytest

from sentinel_lite.models import AuthResult
from sentinel_lite.parsers import parse_ssh_auth_file, parse_ssh_auth_line


def test_parse_failed_password():
    line = (
        "Jan 15 10:00:01 webssh sshd[1001]: "
        "Failed password for admin from 203.0.113.50 port 51234 ssh2"
    )
    ev = parse_ssh_auth_line(line)
    assert ev is not None
    assert ev.username == "admin"
    assert ev.src_ip == "203.0.113.50"
    assert ev.result == AuthResult.FAILURE
    assert ev.service == "sshd"
    assert ev.raw == line.strip()
    assert isinstance(ev.timestamp, datetime)
    # Lab default year for syslog without year: 2024
    assert ev.timestamp.year == 2024
    assert ev.timestamp.month == 1
    assert ev.timestamp.day == 15
    assert ev.timestamp.hour == 10
    assert ev.timestamp.minute == 0
    assert ev.timestamp.second == 1


def test_parse_accepted_password():
    line = (
        "Jan 15 10:05:00 webssh sshd[1007]: "
        "Accepted password for alice from 198.51.100.10 port 42000 ssh2"
    )
    ev = parse_ssh_auth_line(line)
    assert ev is not None
    assert ev.username == "alice"
    assert ev.src_ip == "198.51.100.10"
    assert ev.result == AuthResult.SUCCESS


def test_parse_accepted_publickey():
    line = (
        "Jan 15 08:00:01 webssh sshd[4001]: "
        "Accepted publickey for alice from 198.51.100.10 port 41001 ssh2"
    )
    ev = parse_ssh_auth_line(line)
    assert ev is not None
    assert ev.result == AuthResult.SUCCESS
    assert ev.username == "alice"


def test_parse_invalid_user_failure():
    line = (
        "Jan 15 13:00:02 webssh sshd[5001]: "
        "Failed password for invalid user noone from 203.0.113.1 port 1 ssh2"
    )
    ev = parse_ssh_auth_line(line)
    assert ev is not None
    assert ev.username == "noone"
    assert ev.result == AuthResult.FAILURE
    assert ev.src_ip == "203.0.113.1"


def test_parse_noise_returns_none():
    assert parse_ssh_auth_line("# comment") is None
    assert parse_ssh_auth_line("not a log line at all") is None
    assert parse_ssh_auth_line(
        "Jan 15 13:00:01 webssh systemd[1]: Started Session 42 of user alice."
    ) is None


def test_parse_file_brute_force(ssh_fixtures):
    events = parse_ssh_auth_file(ssh_fixtures / "brute_force_single_ip.log")
    assert len(events) == 7
    failures = [e for e in events if e.result == AuthResult.FAILURE]
    assert len(failures) == 6
    assert all(e.src_ip == "203.0.113.50" for e in failures)


def test_parse_file_skips_noise(ssh_fixtures):
    events = parse_ssh_auth_file(ssh_fixtures / "invalid_and_noise.log")
    assert len(events) == 1
    assert events[0].username == "noone"
