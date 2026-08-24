# Security policy

sentinel-lite is a **lab detector**. It is not a production SIEM and must not be pointed at live customer or household logs without a redaction step you control.

## Please do

- Use the synthetic fixtures under `tests/fixtures/` (RFC 5737 documentation IPs).
- Keep real logs, API keys, and SIEM credentials out of issues, PRs, and `runs/`.
- Treat `config.yaml` as local-only (it is gitignored).

## Please don't

- Open issues that paste production `auth.log` or JSON login streams.
- Add network clients, exploit tooling, or live blocking to this repo.
- Commit findings produced from real systems.

## Reporting a vulnerability in this repo

Email the maintainer via GitHub or open a **private** security advisory on the repository. Do not file a public issue for a suspected vuln.
