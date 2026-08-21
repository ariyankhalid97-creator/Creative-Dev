# Environment — Baseline Snapshot

> Read-only baseline of Anas's machine, captured on Lex's first run.
> Captured: 2026-08-21 14:15 (+05:00, Pakistan Standard Time)
> Method: non-destructive PowerShell queries (`Get-CimInstance`, `Get-Command`, `Get-ChildItem`). Nothing installed or modified.

## Machine
| Field | Value |
|-------|-------|
| OS | Microsoft Windows 11 Pro |
| OS version | 10.0.26200 (build 26200) |
| Architecture | 64-bit |
| Computer name | DESKTOP-9MVQ6CS |
| Local user | PC |
| Time zone | Pakistan Standard Time (UTC+05:00) |
| Machine date-time at capture | 2026-08-21 14:15:27 (+05:00) |

## Shells
| Shell | Version | Notes |
|-------|---------|-------|
| Windows PowerShell | 5.1.26100.9168 (Desktop edition) | Primary shell. This is 5.1 — no `&&`/`||`, ternary, or `??`; use `;` + `if ($?)`. |
| Bash (Git Bash / POSIX) | available | Ships with Git install; use for POSIX scripts. |

## Dev tools
| Tool | Status | Version | Path |
|------|--------|---------|------|
| git | present | 2.53.0.windows.2 | `C:\Program Files\Git\cmd\git.exe` |
| node | present | v24.13.0 | `C:\Program Files\nodejs\node.exe` |
| npm | present | 11.6.2 | `C:\Program Files\nodejs\npm.ps1` |
| python | present | 3.11.6 | `C:\Users\PC\AppData\Local\Programs\Python\Python311\python.exe` |
| pip | present | 26.2.1 (for python 3.11) | `C:\Users\PC\AppData\Local\Programs\Python\Python311\Scripts\pip.exe` |
| python3 | NOT a real interpreter | — | `...\WindowsApps\python3.exe` (Microsoft Store app-execution-alias stub only) |

**Note on Python:** invoke the interpreter as **`python`** (3.11.6). The `python3` command resolves only to the Windows Store alias stub and prints "Python was not found…" — do not rely on it.

## Project root — `D:\Anas\Lex` (top level)
| Type | Name | Purpose |
|------|------|---------|
| DIR | `.claude` | Claude Code config (holds `agents/lex.md` subagent definition). |
| DIR | `lex` | Lex workspace — `AGENT.md`, `CONTEXT.md`, `memory/`, `history/`, `README.md`. |

_No files at the root level; only these two directories._
