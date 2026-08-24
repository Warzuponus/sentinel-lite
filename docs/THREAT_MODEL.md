# Threat model (lab tool)

## Assets

- Correctness of detections (trust in findings)  
- Integrity of schema and fingerprints  
- Developer machine (dependency/supply chain hygiene)  
- Privacy of any real logs someone might feed in later  

## In-scope threats (tool as analyzer)

| Threat | Mitigation in design |
|--------|----------------------|
| False sense of security | Docs state MVP limits; clean fixtures required |
| Path traversal via CLI path | Resolve paths carefully; only read files; no write outside `-o` |
| Log-line injection into reports | Treat `raw` as data; JSON-encode output |
| ReDoS in parsers | Prefer simple splits/regex with anchors; avoid catastrophic patterns |
| Dependency confusion | Pin known libs only (pydantic, pyyaml) |

## Out-of-scope adversaries

- Attacking remote production systems  
- Evading enterprise EDR  
- Supplying real malware samples  

## Abuses we do **not** facilitate

This project must not grow into:

- Credential stuffing engines against live targets  
- Exploit kit generation  
- C2 frameworks  

Reviewers should reject PRs/tasks that add such capabilities.

## Data handling

- Fixtures use documentation IPs only.  
- If analyzing real logs: keep them local, scrub before sharing agent logs, never commit.  
- `config.yaml` is gitignored for local overrides.

## Trust boundaries

```text
[untrusted log files] → parsers → [AuthEvent] → detectors → [Finding] → [user]
         │
         └── do not execute content of logs as code
```
