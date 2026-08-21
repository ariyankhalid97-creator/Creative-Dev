# Lex HQ — Agent Registry & Control Contract

This defines the agent **hierarchy**, the **connected projects**, and the shared
**control-center contract** every agent obeys. Lex (the head) owns this file.

## Hierarchy

```
            YOU (Anas) ── approves everything that matters
                │
          ┌─────▼─────┐
          │    LEX     │  head / coordinator (this is "me" in Claude Code)
          │ triages ·  │  routes tasks · enforces approval gates · reports
          └─────┬─────┘
        ┌───────┴────────┐
   ┌────▼────┐      ┌─────▼─────┐
   │  SCOUT  │      │  HERALD   │        (add more workers over time)
   │ research│      │  email +  │
   │ scrape ➜│      │ outreach  │
   │ sheet   │      │ (gated)   │
   └─────────┘      └───────────┘
```

## Roster

| Agent | Role | Home | Claude subagent | Sends/outbound? |
|-------|------|------|-----------------|-----------------|
| **Lex** | Head — coordinate, route, gate, report | `lex\` | `lex` | No (delegates) |
| **Scout** | Research + scrape → spreadsheet | `agents\scout\` | `scout` | No |
| **Herald** | Check email, prepare follow-ups/outreach | `agents\herald\` | `herald` | **Only after your approval** |

Each agent keeps its own `memory\` and `history\` and follows the 3-phase cycle in
`lex\AGENT.md` (bootstrap → execute → record).

## Connected projects

| Project | Path | Manifest |
|---------|------|----------|
| **Tedt** — hood-cleaning AI-report outreach campaign | `D:\Anas\Tedt` | `projects\tedt.md` |

## Control-center contract (how agents and the UI talk)

The **filesystem is the database.** The dashboard (`control\server.py`) serves and
mutates these JSON files; agents read/write the same files directly. Any file dropped
in these folders shows up in the UI on the next refresh.

### Task — `control\tasks\<id>.json`
```json
{
  "id": "t-YYYYMMDD-xxxx", "title": "...", "detail": "...",
  "project": "tedt|null", "assignee": "lex|scout|herald|auto",
  "priority": "normal|high",
  "status": "inbox|queued|running|blocked|done|failed",
  "createdAt": "ISO", "updatedAt": "ISO",
  "updates": [ { "at": "ISO", "by": "lex", "text": "..." } ],
  "result": "..."
}
```
Lifecycle: **inbox** (created) → you hit **Start** → **queued** → agent runs → **running**
→ needs your OK → **blocked** → you approve → **running** → **done** (or **failed**).

### Approval — `control\approvals\<id>.json`  ← the gate
```json
{
  "id": "a-YYYYMMDD-xxxx", "taskId": "t-...", "agent": "herald",
  "action": "send-email|post|delete|spend|other",
  "title": "...", "summary": "...",
  "preview": "the exact content that would go out (full email text, etc.)",
  "status": "pending|approved|rejected",
  "createdAt": "ISO", "decidedAt": null, "decidedNote": null
}
```
An agent that needs to do anything outbound or irreversible **writes a pending approval,
sets its task to `blocked`, and STOPS.** It only proceeds after `status` becomes
`approved`.

### Activity event — `control\activity\<ts>-<agent>.json`
```json
{ "id": "e-...", "at": "ISO", "agent": "scout", "type": "info|task|approval|error",
  "text": "...", "taskId": "t-...optional" }
```
Append-only (one file per event, so parallel agents never clobber each other).

## Lex's coordination rules (the head)
1. Read the task inbox + queue, `CONTEXT.md`, and recent history first.
2. Route each queued task to the right worker (or handle it directly). Post an activity
   event when you pick it up.
3. Let workers run to their approval gate; **never bypass a gate.**
4. Surface pending approvals to Anas, apply his decision, then continue.
5. Record to history + `CONTEXT.md`, then report and ask for the next step.
