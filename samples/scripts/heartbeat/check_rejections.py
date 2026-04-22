"""
Check tasks/HEARTBEAT_REJECTIONS.md for prior rejection history on a task.

Called by the heartbeat at the start of task classification:
    1. Grep for prior rejections matching the task title / slug.
    2. Return the match count and the blocks themselves.
    3. Classifier uses match count as input to the circuit breaker
       (>=3 rejections forces `needs-intent`).

Usage:
    python check_rejections.py "<task title or slug>"
        -> prints matching rejection blocks + circuit-breaker status

    python -m heartbeat.check_rejections "<task title or slug>"
        -> same as above

Exit codes:
    0 — file read successfully (matches may be 0)
    2 — usage error
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REJECTIONS_PATH = (
    Path(__file__).resolve().parents[2] / "tasks" / "HEARTBEAT_REJECTIONS.md"
)

HEADER_RE = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\s+—\s+(.+?)\s*$")


def parse_blocks(content: str) -> list[dict]:
    """Parse ADR-style rejection blocks from HEARTBEAT_REJECTIONS.md."""
    blocks: list[dict] = []
    current: dict | None = None

    for line in content.splitlines():
        m = HEADER_RE.match(line)
        if m:
            if current:
                blocks.append(current)
            current = {"date": m.group(1), "title": m.group(2).strip(), "body": []}
            continue
        if current is not None:
            current["body"].append(line)

    if current:
        blocks.append(current)

    return blocks


def find_matches(query: str, blocks: list[dict]) -> list[dict]:
    """Return blocks whose title contains the query substring (case-insensitive)."""
    q = query.lower().strip()
    if not q:
        return []
    return [b for b in blocks if q in b["title"].lower()]


def count_rejections(query: str) -> int:
    """Return the count of rejection blocks matching the query. Zero if file missing."""
    if not REJECTIONS_PATH.exists():
        return 0
    content = REJECTIONS_PATH.read_text(encoding="utf-8")
    blocks = parse_blocks(content)
    return len(find_matches(query, blocks))


def main(argv: list[str]) -> int:
    if not argv:
        print("Usage: python check_rejections.py <task title or slug>", file=sys.stderr)
        return 2

    query = " ".join(argv).strip()

    if not REJECTIONS_PATH.exists():
        print(f"(no rejection history file at {REJECTIONS_PATH} — clean slate)")
        print("Circuit breaker: OK (0 prior rejections)")
        return 0

    content = REJECTIONS_PATH.read_text(encoding="utf-8")
    blocks = parse_blocks(content)
    matches = find_matches(query, blocks)

    if not matches:
        print(f"No prior rejections found for: {query}")
        print("Circuit breaker: OK (0 prior rejections)")
        return 0

    print(f"Found {len(matches)} prior rejection(s) for: {query}\n")
    for block in matches:
        print(f"## {block['date']} — {block['title']}")
        for line in block["body"]:
            print(line)
        print()

    status = "TRIGGERED" if len(matches) >= 3 else "OK"
    print(f"Circuit breaker: {status} ({len(matches)} prior rejections)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
