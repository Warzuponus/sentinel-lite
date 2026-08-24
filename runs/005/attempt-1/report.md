# Task 005 done report
- Status: green
- Attempts: 1
- Files changed: src/sentinel_lite/detectors/brute_force.py
- Commands run: pytest tests/detectors/test_brute_force.py -q (exit 0, 3/3 passed)
- Residual risks / ambiguities: none
- Notes for reviewer: implementation follows RULES.md exactly — failures only, group by src_ip, sliding window clusters via time_window helpers, fingerprint via make_fingerprint v1, evidence capped at 10 raw lines

## Sample finding (brute_force_single_ip.log fixture)
- rule_id: auth.brute_force
- severity: high
- title: Authentication brute force
- description: "6 failed auth attempts from 203.0.113.50 within 300s window."
- timestamp: 2024-01-15T10:00:01Z (cluster start)
- src_ip: 203.0.113.50
- fingerprint: sha256 hex of "v1|auth.brute_force|203.0.113.50||2024-01-15T10:00:01Z"
- mitre: ["T1110.001"]
- evidence: 6 raw syslog lines (Failed password for admin from 203.0.113.50 ...)
