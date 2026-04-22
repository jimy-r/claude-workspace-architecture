"""
Count pending + reminded entries in tasks/HEARTBEAT_REVIEWS.md.

Used by the heartbeat at cycle start to enforce Rule 15 in HEARTBEAT.md:
if the active queue is >= CAP (10), pause all new `has-default` builds
this cycle — classify every new task as `needs-intent` with a "review
queue is at capacity" note until the user drains via `/review-queue`.

Usage:
    python review_queue.py
        -> prints current depth (int) on stdout
        -> exit 0 if depth < CAP
        -> exit 1 if depth >= CAP (cap reached)

    python -m heartbeat.review_queue
        -> same behaviour, importable as a module
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REVIEWS_PATH = Path(__file__).resolve().parents[2] / "tasks" / "HEARTBEAT_REVIEWS.md"

CAP = 10

_ENTRY_RE = re.compile(
    r"^\s*-\s+\d{4}-\d{2}-\d{2}\s*\|\s*(pending|reminded)\s*\|",
    re.MULTILINE,
)


def count_active() -> int:
    """Return the count of pending + reminded entries in the review queue."""
    if not REVIEWS_PATH.exists():
        return 0

    content = REVIEWS_PATH.read_text(encoding="utf-8")
    # Scope to the `## Active reviews` section only.
    parts = content.split("## Active reviews", 1)
    if len(parts) < 2:
        return 0
    body = parts[1]

    return len(_ENTRY_RE.findall(body))


def is_capped() -> bool:
    """Return True if the review queue is at or above the cap."""
    return count_active() >= CAP


def main() -> int:
    depth = count_active()
    print(depth)
    return 0 if depth < CAP else 1


if __name__ == "__main__":
    sys.exit(main())
