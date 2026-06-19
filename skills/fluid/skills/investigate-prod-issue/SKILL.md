---
name: investigate-prod-issue
description: Use when investigating a production bug or user-reported issue in the Fluid app and you need to find the root cause from real data. Triggers on reports that include supporting evidence — a URL, short link, record ID, email, order/share token, or other PII — and an ask to determine the source/root cause. Covers read-only production DB access (no Docker) and scoped gcloud log queries.
---

# Investigate Prod Issue

## Overview

Find the root cause of a user-reported production issue from **read-only** evidence (prod DB read replica, gcloud logs) combined with reading the code. Evidence first, then code. Never guess; never write.

**REQUIRED BACKGROUND:** Use superpowers:systematic-debugging — establish root cause before proposing any fix.

## When to use

- A customer/teammate reports something "isn't working" and you're asked to find the source.
- The report includes an identifier you can look up: a URL / short link, record ID, email, token, slug, etc.
- You need to confirm whether the problem is a one-off or systemic.

Not for: bugs reproducible locally in the test suite, or changes verifiable without prod data.

## Read-only prod DB access (no Docker)

Connect directly with `psql` to the read replica. The credential lives in `~/.pgpass`
(entry `localhost:5433:fluid:read_only`), so **no password is needed on the command line and
nothing needs to be pasted into the prompt**:

```bash
psql -h localhost -p 5433 -U read_only -d fluid -c "<query>"
# expanded rows: add -x   | raw value: add -tc
```

- `connection refused` → the read-replica proxy/tunnel on `localhost:5433` isn't running; ask the user to start it.
- This is a read replica accessed through a **read-only role** — writes are impossible by design. Keep it that way: `SELECT` / `\d` only.
- Prefer `psql` over `rails console` (no app or Docker needed). Reach for rails console (via the `devcontainer` skill) only if you genuinely need ActiveRecord model logic.
- To rotate/repair the credential: edit the one line in `~/.pgpass` (keep it `chmod 600`).

## Hard rules

- **Read-only, always.** Inspect, never mutate. If a fix requires a write, propose it — don't run it.
- **Scope every query.** Filter by the specific company / record / time window. No unbounded scans.
- **Handle PII carefully.** Use supplied emails/IDs/PII only to locate records. Never paste PII into Artifacts, commits, PR bodies, Linear, or any external service, and don't persist it to files.

## Workflow

1. **Resolve the evidence to records.** Turn the supplied artifact into rows. (URL path / short code → token or slug → owning record. Email → user/contact. ID → the row.)
2. **Map the schema.** `\d <table>`; find candidate tables via `information_schema.tables` filtered by name.
3. **Pull the specific record(s).** Inspect the exact row(s) being complained about — every relevant column.
4. **Compare working vs broken.** Find a known-good analog and diff it against the broken one; group/aggregate to expose the pattern.
5. **Confirm scope.** One-off or systemic? Re-run the comparison across the company, all companies, and a time window.
6. **Tie to code.** Take the *distinguishing data attribute* and trace the code path that branches on it (cite `file:line`). The data tells you where to look.

## gcloud (scoped log evidence)

For request/error traces, query Cloud Logging read-only — always scoped and time-bounded:

```bash
gcloud logging read 'resource.type="<type>" AND <filter>' --project <PROJECT> --freshness=1d --limit=50
```

Confirm the project/service name with the user if unknown — don't guess.

## Presenting findings

Lead with the root cause in one line, then the evidence (a tight data table + `file:line` refs) and the scope. **Stop at root cause unless asked to fix** — many reports just want the source identified.
