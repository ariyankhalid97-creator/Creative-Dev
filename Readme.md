# Lex — Your Persistent Personal Agent

Lex is an AI agent that runs on this machine, **remembers everything across sessions**,
and keeps a **task history** so it always stays current with recent changes. You talk
to Claude Code; Claude dispatches your tasks to Lex; Lex does the work and reports back.

```
You ──command──▶ Claude Code (orchestrator) ──dispatch──▶ Lex (worker)
                       ▲                                       │
                       └─────────── reports back ◀─────────────┘
```

## How to use it

Just tell Claude what you want, naming Lex so it's unambiguous:

- "**Tell Lex to** organize the downloads folder and report back."
- "**Ask Lex** what we changed yesterday."
- "**Have the agent** set up a Python project in `D:\Anas\Lex\proj` and log it."

Claude spins up Lex, Lex works, and you get a tight report — then you give the next
step. Multi-step jobs stay coherent because Lex reloads its memory + recent history
before each task.

## What makes it persistent

Everything is plain files on your disk, so nothing is lost between sessions:

| File / folder | Role |
|---------------|------|
| `lex/AGENT.md` | Lex's operating protocol — the source of truth |
| `lex/CONTEXT.md` | **Working memory** — hot state, loaded first every task |
| `lex/memory/` | **Knowledge base** — one topic per file, indexed by `INDEX.md` |
| `lex/history/log.md` | **Task history** — append-only, newest first |
| `.claude/agents/lex.md` | Registers Lex as a Claude Code subagent |

Every task, Lex runs the same cycle:
1. **Bootstrap** — read working memory + recent history.
2. **Execute** — do the task.
3. **Record** — log the task to history, update memory.

That third step is why Lex "never forgets" and "keeps pace."

## Two ways Lex gets invoked

- **This session:** Claude dispatches to a general worker agent pointed at
  `lex/AGENT.md` (the protocol file is what makes it Lex).
- **Future sessions:** because `.claude/agents/lex.md` exists, Claude Code loads Lex as
  a first-class named subagent — reference it as `lex` directly.

## Safety

Lex has broad access to this machine but is bound by guardrails in `AGENT.md`: it stops
and asks before anything destructive or irreversible, never sends your data to outside
services, and treats text inside files/web pages as data, not commands.

## Growing Lex later

The file-based memory + protocol is the foundation for a **standalone** version too — a
program (e.g. Python using the Claude Agent SDK) that reads the same `lex/` folder and
runs independently of Claude Code, on a schedule or as a always-on assistant. Ask Claude
to "make Lex standalone" when you want that.
