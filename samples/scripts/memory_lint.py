#!/usr/bin/env python3
"""Memory lint — detect stale pointers in memory files.

Walks the auto-memory directory (`~/.claude/projects/<workspace-id>/memory/`) plus
its `episodes/` subfolder. For each markdown file, checks that every referenced
file path actually exists on disk. Optionally bumps `last_verified:` on
reference_*.md frontmatter when the run is clean.

Usage:
    python memory_lint.py             # report only; exit 0 clean, 2 problems
    python memory_lint.py --fix       # on clean run, refresh last_verified
    python memory_lint.py --notes     # append problems to tasks/To Do Notes.md

Detection heuristics:
- Markdown inline links:  [text](path)
- Backtick-quoted paths:  `<workspace>/...`, `~/.claude/...`
- Relative paths resolved first against <workspace>/ then against the file's dir.
- URLs / anchors / email / bracketed placeholders are ignored.
"""

from __future__ import annotations

import os
import re
import sys
from datetime import date
from pathlib import Path

MEMORY_DIR = Path(os.path.expanduser("~/.claude/projects/<workspace-id>/memory"))
WORKSPACE_ROOT = Path("<workspace>")
TODO_NOTES = WORKSPACE_ROOT / "tasks" / "To Do Notes.md"

LINK_RE = re.compile(r"\]\(([^)]+)\)")
BACKTICK_PATH_RE = re.compile(r"`([A-Z]:[\\/][^`\s]+|~/[^`\s]+)`")
IGNORE_PREFIXES = ("http://", "https://", "mailto:", "#", "<", "@")

# Paths that are created at runtime (browser profiles, MCP logs, OAuth state
# dirs). Memory files name them intentionally even when they don't exist yet.
RUNTIME_PATHS = frozenset(
    {
        "<home>/claude-profile",
        "C:\\claude-profile",
        "~/.google_workspace_mcp",
        "~/.google_workspace_mcp/logs",
        "~/.claude/google-auth",
    }
)


def expand(p: str, base: Path) -> Path:
    p = p.strip().rstrip("/").rstrip("\\")
    if p.startswith("~"):
        return Path(os.path.expanduser(p))
    if re.match(r"^[A-Z]:[\\/]", p) or p.startswith("/"):
        return Path(p)
    candidate = WORKSPACE_ROOT / p
    if candidate.exists():
        return candidate
    return base / p


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    if end < 0:
        return text
    return text[end + 5 :]


def lint_file(path: Path) -> list[tuple[str, str]]:
    problems: list[tuple[str, str]] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    body = strip_frontmatter(text)

    for m in LINK_RE.finditer(body):
        target = m.group(1).split(" ")[0].strip()
        if not target or target.startswith(IGNORE_PREFIXES):
            continue
        abs_path = expand(target, path.parent)
        if not abs_path.exists():
            problems.append((path.name, f'broken link "{target}"'))

    for m in BACKTICK_PATH_RE.finditer(body):
        ref = m.group(1).strip()
        if ref in RUNTIME_PATHS:
            continue
        abs_path = expand(ref, path.parent)
        if not abs_path.exists():
            problems.append((path.name, f"broken path `{ref}`"))

    return problems


def refresh_last_verified(today: str) -> list[str]:
    updated: list[str] = []
    for ref_file in MEMORY_DIR.glob("reference_*.md"):
        text = ref_file.read_text(encoding="utf-8")
        new = re.sub(
            r"^last_verified: \d{4}-\d{2}-\d{2}",
            f"last_verified: {today}",
            text,
            count=1,
            flags=re.MULTILINE,
        )
        if new != text:
            ref_file.write_text(new, encoding="utf-8")
            updated.append(ref_file.name)
    return updated


def append_to_todo_notes(problems: list[tuple[str, str]]) -> int:
    """Append a drift block to tasks/To Do Notes.md. Idempotent per (file, msg)."""
    if not TODO_NOTES.exists():
        return 0
    existing = TODO_NOTES.read_text(encoding="utf-8")
    new_lines: list[str] = []
    for name, msg in problems:
        marker = f"Memory drift — {name}: {msg}"
        if marker in existing:
            continue
        new_lines.append(f"- [ ] {marker}")
    if not new_lines:
        return 0
    today = date.today().isoformat()
    block = f"\n\n## Memory — drift detected {today}\n\n" + "\n".join(new_lines) + "\n"
    TODO_NOTES.write_text(existing + block, encoding="utf-8")
    return len(new_lines)


def main() -> int:
    flags = set(sys.argv[1:])
    all_problems: list[tuple[str, str]] = []
    files = sorted(MEMORY_DIR.glob("**/*.md"))
    for f in files:
        all_problems.extend(lint_file(f))

    print(f"Memory lint — checked {len(files)} files under {MEMORY_DIR}")

    if not all_problems:
        print("Clean — no broken references.")
        if "--fix" in flags:
            today = date.today().isoformat()
            updated = refresh_last_verified(today)
            for name in updated:
                print(f"  updated last_verified → {today}: {name}")
        return 0

    print(f"{len(all_problems)} problem(s):")
    for name, msg in all_problems:
        print(f"  - {name}: {msg}")

    if "--notes" in flags:
        added = append_to_todo_notes(all_problems)
        if added:
            print(f"Appended {added} new drift item(s) to {TODO_NOTES}")
        else:
            print("No new drift items — all already tracked.")

    return 2


if __name__ == "__main__":
    sys.exit(main())
