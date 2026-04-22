# Heartbeat Reviews — Active Queue

> **What this is:** one-line-per-entry log of sandboxed work the heartbeat has built and is waiting for the user to integrate.
>
> **Heartbeat behaviour:**
> - On completion of a `has-default` task → append a `pending` entry.
> - Next cycle ≥ 7 days old with no status change → flip to `reminded` and surface prominently in morning brief.
> - Next cycle ≥ 14 days old with no status change → move to `tasks/HEARTBEAT_REVIEWS_archive.md` with status `not-integrated, archived`.
>
> **User actions:**
> - **Integrate** → merge the PR / run the integration command inside `REVIEW.md` / delete staging and accept. Heartbeat removes the entry on next cycle.
> - **Reject** → delete the staging folder / close the PR without merge. Heartbeat appends an ADR block to `tasks/HEARTBEAT_REJECTIONS.md` and removes the entry on next cycle.
> - **Redirect** → leave a note in the `REVIEW.md` or PR comment; heartbeat picks it up next cycle and iterates (counts toward rejection if the next attempt is also rejected).
>
> **Format:**
> ```
> - YYYY-MM-DD | <status> | <task-slug> | <staging-location> | <one-line summary>
> ```
>
> **Statuses:** `pending` · `reminded` (7+ days, morning brief surfaces this) · (archived entries live in `HEARTBEAT_REVIEWS_archive.md`).
>
> Morning brief reads this file and includes a `## Awaiting your review` section listing every `pending` and `reminded` entry.

---

## Active reviews

(No active reviews yet. Heartbeat will populate this section when the first `has-default` task is completed under the new flow.)
