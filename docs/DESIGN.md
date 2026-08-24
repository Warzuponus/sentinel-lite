# Design: sentinel-lite

## Problem

Security teams and labs need a **small, understandable detection pipeline** for authentication abuse patterns. Full SIEMs are heavy. This project delivers a **minimal offline analyzer** that:

- Ingests common auth log shapes  
- Emits structured findings  
- Is fully testable with golden fixtures  

It is also a **vehicle for multi-agent coding**: strong models plan and review; local models implement against tests.

## Goals

1. Correct detection of three auth abuse patterns on fixture data.  
2. Stable, documented schema for events and findings.  
3. CLI suitable for lab demos and CI.  
4. Task decomposition that a mid-size local coding model can finish without redesigning the system.

## Non-goals (v1)

- Real-time streaming, agents that block IPs in production  
- Machine learning / UEBA  
- Multi-tenant SaaS, UI dashboards  
- Full syslog/RFC5424 universality  
- ATT&CK coverage beyond optional tags on the three rules  
- Writing custom cryptography  

## Users

| User | Need |
|------|------|
| Lab student / blue teamer | Run analyzer on sample logs, see findings |
| Detection engineer | Extend rules with clear tests |
| Multi-agent experimenter | Measure local-model task success rate |

## Product shape

```text
logs (files/dir) → parsers → [AuthEvent] → detectors → [Finding] → JSON + summary
                              ↑
                         AnalysisConfig (YAML)
```

## Detection narratives (fixtures)

### Brute force

Attacker `203.0.113.50` tries password for `admin` six times in ~80 seconds.  
**Expect:** `auth.brute_force`.

### Password spray

Attacker `203.0.113.77` tries one password against six usernames.  
**Expect:** `auth.password_spray` (not necessarily “only” that rule if brute also matches volume—prefer spray fixture designed so distinct-user logic is the primary test; single-user brute fixture must **not** raise spray).

### Success after failures

Four failures then success for `root` from `203.0.113.99`.  
**Expect:** `auth.success_after_fail` (critical).

### Clean day

Legitimate users; one failed password then immediate success (below thresholds).  
**Expect:** no findings.

## Configuration philosophy

Thresholds live in YAML (`config.example.yaml`). Detectors **must not** hardcode production policy numbers without reading config (defaults may match example file).

## Extensibility (later, not v1 tasks)

- Additional parsers (Windows Event XML, cloud IdP CSV)  
- Sigma-lite rule pack  
- SQLite finding store  
- Secret scanner as a sibling package  

## Success metrics for the product

- All golden e2e tests pass  
- Findings are triage-friendly (evidence lines present)  
- Config change alters detector sensitivity without code edits  

## Success metrics for the multi-agent experiment

Documented in `docs/ORCHESTRATION.md`.
