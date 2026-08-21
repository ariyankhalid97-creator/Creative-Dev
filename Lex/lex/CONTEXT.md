# Lex — Working Memory (CONTEXT)

> Hot state. Lex loads this FIRST on every task. Keep it compact and current.
> Last updated: 2026-08-21 (Lex HQ built + Tedt connected)

## Owner
- **Name:** Anas
- **Contact:** ariyankhalid97@gmail.com
- **Setup:** Anas talks to Claude Code (Lex, the head); Lex routes tasks to worker agents and enforces approval gates; Anas approves anything outbound. Monitored via the control dashboard.

## Machine
- **OS:** Windows 11 Pro (10.0.26200)
- **Shell:** PowerShell (primary); Bash (POSIX) also available. Use `python` (not `python3`).
- **Project root / HQ:** `D:\Anas\Lex`

## Hierarchy (see `lex/registry.md`)
- **Lex** (head) → **Scout** (research/scrape → spreadsheet), **Herald** (email + outreach, gated).
- Control center: `control/server.py` → dashboard at http://localhost:8787. Filesystem = database (tasks/approvals/activity JSON).

## Active projects
- **Lex HQ** — the hierarchical agent system + dashboard. Status: operational.
- **Tedt** — hood-cleaning AI-report outreach campaign (`D:\Anas\Tedt`, manifest `projects/tedt.md`). Connected 2026-08-21. 30 leads; outreach waves; follow-ups due 2026-08-24.

## Current state
- Lex HQ built and verified: Scout + Herald registered; dashboard live; API create/start/approval paths tested. Tedt connected with 3 seeded real tasks + 1 sample approval demonstrating the gate.
- Email is **drafts-first** (Gmail not yet authorized) — nothing sends without Anas's approval.

## Recent changes (newest first)
- 2026-08-21 — Built Lex HQ: Scout + Herald workers, control dashboard (tasks/approvals/activity), connected Tedt, seeded real workload. Verified server + endpoints.
- 2026-08-21 — Captured read-only environment baseline → `memory/environment.md`.
- 2026-08-21 — Lex workspace scaffolded.

## Open threads / next
- **Tedt follow-ups due 2026-08-24** (Herald, drafts-first) — prepare + gate.
- **Decide email send mode:** stay drafts-first, or authorize Gmail for one-click send of approved messages (one-time setup by Anas).
- **Optional:** wire an autonomous runner so hitting "Start" launches a headless Claude run without the chat.

## Preferences & conventions
- Anas wants a low-friction workflow: he approves the important things; agents do the legwork and never send/post without a click.
