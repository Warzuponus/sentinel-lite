# Data contracts

## AuthEvent

Normalized authentication attempt.

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | `datetime` | When the attempt occurred |
| `src_ip` | `str` | Source IP (string form) |
| `username` | `str` | Target or authenticating user |
| `result` | `AuthResult` | `success` \| `failure` \| `unknown` |
| `service` | `str` | e.g. `sshd`, `webapp` |
| `raw` | `str` | Original line (trimmed) |
| `extras` | `dict` | Optional metadata only |

**Rules:**

- `extra="forbid"` on the model — unknown fields rejected.  
- Parsers set `result` from line semantics; never leave success/failure as unknown when the line is clear.

## AuthResult

Enum string values: `success`, `failure`, `unknown`.

## Severity

Enum: `info`, `low`, `medium`, `high`, `critical`.

## Finding

| Field | Type | Description |
|-------|------|-------------|
| `rule_id` | `str` | Stable ID (see RULES.md) |
| `severity` | `Severity` | From config for that rule |
| `title` | `str` | Short human title |
| `description` | `str` | One-paragraph summary |
| `timestamp` | `datetime` | Representative time (e.g. last event in window) |
| `src_ip` | `str \| null` | Primary actor IP when applicable |
| `username` | `str \| null` | Primary user when applicable |
| `evidence` | `list[str]` | Raw lines or compact summaries (non-empty if alerted) |
| `fingerprint` | `str` | Hex sha256 from `make_fingerprint` |
| `mitre` | `list[str]` | Optional technique IDs |
| `extras` | `dict` | Counts, thresholds, etc. |

## Fingerprint v1

Material:

```text
v1|{rule_id}|{src_ip}|{username}|{window_start}
```

Missing optional parts → empty string. Digest = SHA-256 hex (64 chars).

**Guidance:**

| Rule | src_ip | username | window_start |
|------|--------|----------|--------------|
| brute_force | yes | optional (often empty or first user) | first event ISO in cluster |
| password_spray | yes | empty | first event ISO in cluster |
| success_after_fail | yes if known | yes | success event ISO |

## AnalysisConfig

Loaded from YAML. Structure:

```yaml
version: 1
detectors:
  brute_force: { enabled, fail_threshold, window_seconds, severity }
  password_spray: { enabled, user_threshold, window_seconds, severity }
  success_after_fail: { enabled, fail_threshold, window_seconds, require_same_ip, severity }
output:
  fingerprint_version: 1
```

Access in code via `config.detectors["brute_force"][...]`.

## JSON output (CLI)

Array of Finding objects (`model_dump(mode="json")`). Timestamps as ISO-8601 strings.
