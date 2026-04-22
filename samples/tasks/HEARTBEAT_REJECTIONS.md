# Heartbeat Rejections — Durable Memory (ADR-style)

> **What this is:** a durable log of every rejection of heartbeat-built work. This file is the canonical reference for "don't try this again" — both heartbeat and any future agent check it before attempting related work.
>
> **Heartbeat procedure — before classifying any task:**
> 1. Grep this file for the task title / slug / substring match (via `<workspace>/scripts/heartbeat/check_rejections.py`).
> 2. If matched → read the prior rejection block(s), incorporate the "Lesson for future attempts" into the current build approach; do not repeat the rejected pattern.
> 3. If ≥ 3 rejections matched (circuit breaker) → force `needs-intent` classification. Heartbeat surfaces the history and asks the user for direction rather than attempting a fourth speculative build.
>
> **When to append a block:**
> - User deletes a staging folder without integrating.
> - User closes a PR without merge.
> - User leaves an explicit reject / redirect comment on a `REVIEW.md`, PR, or draft.
>
> **Block format:**
> ```markdown
> ## YYYY-MM-DD — <task title or slug>
>
> **Attempted:** <one-line summary of what heartbeat built>
> **Rejected because:** <user's reason, captured at rejection time>
> **Lesson for future attempts:** <what shape of build would be different>
> ```
>
> **Archival threshold:** when this file exceeds 200 lines, rotate the oldest half to `tasks/HEARTBEAT_REJECTIONS_archive.md`. Matches the `todo.md` / `todo-archive.md` rhythm.
>
> **Pattern reference:** Architecture Decision Records (Michael Nygard). Analogous to Dependabot's ignored-versions list and the "failed approaches" file pattern in research notebooks.

---

## Rejections

(No rejections recorded yet. Heartbeat will append blocks here as work is rejected under the new build-first flow.)
