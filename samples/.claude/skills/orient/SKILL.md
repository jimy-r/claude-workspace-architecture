---
name: orient
description: Use at the start of a new session when the user says "orient", "/orient", or asks to get up to speed on the workspace. Produces a briefing of active state, in-flight work, open questions, staleness flags, and a recommended next action.
---

# Orient

## Purpose

Bring Claude up to speed on the workspace quickly and deterministically at session start, without burning context on speculative exploration. Output is a concise briefing the user can redirect.

## Iron Law

**Read the fixed file set below. Do not wander.** If a listed file doesn't exist, note it and move on — don't improvise replacements.

## Procedure

### 1. Read (in parallel)

- `<workspace>/CLAUDE.md` — working context
- `<workspace>/tasks/todo.md` — current implementation plan
- `<workspace>/tasks/lessons.md` — self-improvement rules to apply this session
- `<workspace>/tasks/To Do Notes.md` — master task list (scan active sections; skip completed table)
- `<workspace>/tasks/To Do Questions.md` — open questions (skip REMOVED / COMPLETED / RESOLVED)

### 2. Freshness scan

For each project folder with a `CONTEXT.md` or `PLAN.md`, check mtime. Flag anything older than 30 days as potentially stale.

### 3. Produce the briefing

Output **under 300 words**, structured:

- **Active state** — one line on where the workspace is right now.
- **In-flight work** — anything with an open plan or checklist that isn't closed.
- **Open questions** — unresolved items needing user input.
- **Staleness flags** — any CONTEXT.md / PLAN.md older than 30 days.
- **Lessons active this session** — one-line summary per lessons.md entry.
- **Recommended next action** — one task with a one-sentence tradeoff. Present as "I'd pick X because Y; alternatives are Z" — something the user can redirect.

## Rules

- Do NOT read source code beyond the file set above.
- Do NOT fire subagents — the file set is small and bounded.
- Do NOT write to any file — this is read-only.
- If a listed file is missing, note it in the briefing as a structural flag — don't skip silently.
- End with one question: "Want depth on any of these, or start on the recommended next action?"
