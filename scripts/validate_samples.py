#!/usr/bin/env python3
"""Validate sample files have expected frontmatter and no identifying content.

Runs in CI. Fails the job if any sample file is malformed, missing required
frontmatter, or contains patterns that suggest machine-specific paths or
personal email addresses slipped in.

Design notes
------------
- This script is public. Forbidden-pattern checks are deliberately generic
  (shape-based, not string-based). Maintainers keep concrete identifier lists
  in private notes, not here.
- Checks are shallow on purpose: this is a pre-review smoke test, not a full
  static analysis. Human review still catches things the regexes miss.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print(
        "ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr
    )
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "samples"

# Files that must contain YAML frontmatter with specific required fields.
# Key is a glob relative to samples/, value is the set of required frontmatter keys.
REQUIRED_FRONTMATTER: dict[str, set[str]] = {
    "roles/example-*.md": {"name", "description", "role_version"},
    "example-project/.claude/agents/*.md": {"name", "description"},
    ".claude/skills/*/SKILL.md": {"name", "description"},
}

# Files to skip entirely (templates, READMEs, the generic CONTEXT example).
SKIP: set[str] = {
    "roles/_template.md",
    "README.md",
    "CLAUDE.md.example",
    "CONTEXT.md.example",
    "tasks/README.md",
    "tasks/To-Do-Notes.example.md",
    "example-project/CONTEXT.md",
}

# Generic patterns that suggest identifying content may have slipped in.
# Shape-based: no specific names, emails, or business strings are encoded here.
FORBIDDEN_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"[A-Z]:[/\\]Users[/\\][A-Za-z0-9_.-]+", re.IGNORECASE),
        "Windows user-specific path",
    ),
    (re.compile(r"(?<![A-Za-z0-9])/home/[A-Za-z0-9_.-]+/"), "Unix home-directory path"),
    (
        re.compile(r"(?<![A-Za-z0-9])/Users/[A-Za-z0-9_.-]+/"),
        "macOS home-directory path",
    ),
    (
        re.compile(
            r"\b[A-Za-z0-9._%+-]+@(?!example\.(com|org|net)|noreply\.|users\.noreply\.github\.com)"
            r"(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}\b"
        ),
        "Concrete email address (use a placeholder or <user>@example.com)",
    ),
]


def parse_frontmatter(text: str) -> dict | None:
    """Extract YAML frontmatter from a markdown file, or return None if absent."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    raw = text[4:end]
    try:
        parsed = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ValueError(f"Malformed YAML frontmatter: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError("Frontmatter must parse to a mapping")
    return parsed


def find_required_fields(rel_path: str) -> set[str] | None:
    """Return the set of required frontmatter keys for the given path, or None if not required."""
    from fnmatch import fnmatch

    for pattern, required in REQUIRED_FRONTMATTER.items():
        if fnmatch(rel_path, pattern):
            return required
    return None


def scan_file(path: Path) -> list[str]:
    """Return a list of error strings for this file (empty if clean)."""
    errors: list[str] = []
    rel = path.relative_to(SAMPLES).as_posix()

    if rel in SKIP:
        return errors

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return [f"Cannot decode as UTF-8: {exc}"]

    required = find_required_fields(rel)
    if required is not None:
        try:
            fm = parse_frontmatter(text)
        except ValueError as exc:
            errors.append(str(exc))
            fm = None
        if fm is None:
            errors.append("Missing YAML frontmatter")
        else:
            missing = required - set(fm.keys())
            if missing:
                errors.append(f"Missing required frontmatter fields: {sorted(missing)}")

    for pattern, label in FORBIDDEN_PATTERNS:
        for match in pattern.finditer(text):
            line_no = text.count("\n", 0, match.start()) + 1
            errors.append(f"{label} detected at line {line_no}: {match.group(0)!r}")

    return errors


def main() -> int:
    if not SAMPLES.exists():
        print(f"ERROR: samples/ not found at {SAMPLES}", file=sys.stderr)
        return 2

    all_errors: list[tuple[str, list[str]]] = []
    markdown_files = sorted(SAMPLES.rglob("*.md"))

    for path in markdown_files:
        errors = scan_file(path)
        if errors:
            all_errors.append((path.relative_to(ROOT).as_posix(), errors))

    if all_errors:
        print(
            f"\n{len(all_errors)} sample file(s) failed validation:\n", file=sys.stderr
        )
        for path, errors in all_errors:
            print(f"  {path}", file=sys.stderr)
            for err in errors:
                print(f"    - {err}", file=sys.stderr)
        print(file=sys.stderr)
        return 1

    print(f"OK — validated {len(markdown_files)} sample file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
