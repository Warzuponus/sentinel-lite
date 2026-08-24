# Detection rules

Default thresholds match `config.example.yaml` / `default_config()`.

---

## auth.brute_force

| | |
|--|--|
| **Title** | Authentication brute force |
| **Severity** | `high` (config) |
| **MITRE** | T1110.001 (optional tag) |

### Logic

1. Consider only events with `result == failure`.  
2. Group by `src_ip`.  
3. If there exists a set of ≥ `fail_threshold` failures from that IP whose timestamps all lie within `window_seconds` (sliding window), emit a finding.  
4. Username may vary; brute force is **IP-centric**.  
5. Evidence: sample of contributing raw lines (cap at e.g. 10).

### Positive fixture

`tests/fixtures/ssh/brute_force_single_ip.log`

### Negative

`tests/fixtures/ssh/clean_day.log` → no brute_force finding.

---

## auth.password_spray

| | |
|--|--|
| **Title** | Password spray |
| **Severity** | `high` |
| **MITRE** | T1110.003 (optional) |

### Logic

1. Consider failures only.  
2. Group by `src_ip`.  
3. Within any window of `window_seconds`, if **distinct usernames** ≥ `user_threshold`, emit finding.  
4. Single-username high volume should **not** count as spray (distinct count = 1).

### Positive

`tests/fixtures/ssh/password_spray.log`

### Negative

`tests/fixtures/ssh/brute_force_single_ip.log` → no password_spray  
`tests/fixtures/ssh/clean_day.log` → none

---

## auth.success_after_fail

| | |
|--|--|
| **Title** | Success after failed attempts |
| **Severity** | `critical` |
| **MITRE** | T1078 / T1110 (optional) |

### Logic

1. For each success event, look backward within `window_seconds` for failures with the **same username**.  
2. If `require_same_ip` is true, failures must share the success event’s `src_ip`. Default **false** in example config (still same username).  
3. If failure count ≥ `fail_threshold`, emit finding.  
4. Fingerprint around success timestamp + username (+ ip).

### Positive

`tests/fixtures/ssh/success_after_fails.log`

### Negative

`tests/fixtures/ssh/clean_day.log` (only one prior fail for charlie)

---

## Overlap policy

The same log may theoretically trigger multiple rules (e.g. high-volume spray also looks like brute force by fail count). That is **allowed**. Golden tests assert **presence** of the primary rule for each fixture, not exclusivity, except where a test explicitly asserts empty for a rule.

## Dedupe

`run_all_detectors` must unique findings by `fingerprint` (keep first).
