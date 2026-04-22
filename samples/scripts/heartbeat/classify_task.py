"""
Classify a task bullet into has-default / needs-intent / out-of-scope.

Order of checks (first match wins):
1. Rejection-history gate — if a circuit breaker is triggered (>=3 prior rejections),
   force `needs-intent` regardless of keyword signals.
2. out-of-scope — personal / judgement-heavy domains (health, finance, creative).
3. needs-intent — explicit scope-TBD markers or multi-option decisions.
4. has-default — clear buildable verbs (investigate, review, research, draft, etc.).
5. Fallback — `needs-intent` (conservative default).

Usage:
    python classify_task.py "<task bullet text>"
        -> prints: has-default | needs-intent | out-of-scope

    python classify_task.py --file <path-to-notes.md>
        -> prints one classification per bullet in the file

    python -m heartbeat.classify_task "<text>"
        -> same as first form, importable as a module
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# --- heuristics ---------------------------------------------------------------

OUT_OF_SCOPE_PATTERNS = [
    r"\bhealth\b",
    r"\bpathology\b",
    r"\bmedication\b",
    r"\bimmunisation\b",
    r"\bnutrition\b",
    r"\bblood\s+test\b",
    r"\bcpap\b",
    r"\bsleep\b",
    r"\bbp\s+monitor\b",
    r"\bomron\b",
    r"\bfitness\b",
    r"\bchapter\b",
    r"\breview\s+of\s+the\s+book\b",
    r"\bmanuscript\b",
    r"\btax\b",
    r"\bsuper\b",
    r"\bretirement\b",
    r"\bbank\s+reconciliation\b",
]

NEEDS_INTENT_PATTERNS = [
    r"\bscope\s+tbd\b",
    r"scope\s+tbd",
    r"\btbd\b",
    r"\bdirections?\s+(?:noted|possible|were)\b",
    r"possible\s+directions",
    r"heartbeat\s+to\s+confirm",
    r"\bconfirm\s+(?:intent|scope|source)\b",
    r"\bclarify\b",
    r"\bwhich\s+(?:one|option|approach|direction)\b",
    r"\(\s*(?:[A-D]\s*\)|or\s+)",  # A) B) C) list or "or X"
]

HAS_DEFAULT_PATTERNS = [
    r"\binvestigate\b",
    r"\bsummari[sz]e\b",
    r"\bdraft\b",
    r"\bresearch\b",
    r"\breview\b",
    r"\baudit\b",
    r"\bimplement\b",
    r"\badd\b",
    r"\bextend\b",
    r"\bexpand\b",
    r"\bscaffold\b",
    r"\brefactor\b",
    r"\bupgrade\b",
    r"\brotate\b",
    r"\bverify\b",
    r"\bcheck\b",
    r"\bclean\b",
    r"\bresolve\b",
    r"\bfix\b",
    r"\bmigrate\b",
]


def classify(text: str, rejection_count: int = 0) -> str:
    """
    Classify a task bullet.

    Args:
        text: the task bullet text (without leading `- `).
        rejection_count: prior rejection count from HEARTBEAT_REJECTIONS.md for this task.

    Returns:
        One of: "has-default", "needs-intent", "out-of-scope".
    """
    if rejection_count >= 3:
        return "needs-intent"

    lowered = text.lower()

    for pattern in OUT_OF_SCOPE_PATTERNS:
        if re.search(pattern, lowered):
            return "out-of-scope"

    for pattern in NEEDS_INTENT_PATTERNS:
        if re.search(pattern, lowered):
            return "needs-intent"

    for pattern in HAS_DEFAULT_PATTERNS:
        if re.search(pattern, lowered):
            return "has-default"

    return "needs-intent"


# --- bullet extraction --------------------------------------------------------

BULLET_RE = re.compile(r"^\s*-\s+(.+)$")
STRUCK_PREFIX = ("~~", "[x]", "[X]")


def iter_bullets(text: str):
    """
    Yield (line_number, bullet_content) tuples for each active bullet
    in a markdown file. Skips struck-through bullets.
    """
    for n, line in enumerate(text.splitlines(), start=1):
        m = BULLET_RE.match(line)
        if not m:
            continue
        content = m.group(1).strip()
        if any(content.startswith(p) for p in STRUCK_PREFIX):
            continue
        yield n, content


# --- CLI ----------------------------------------------------------------------


def _classify_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for line_no, bullet in iter_bullets(text):
        label = classify(bullet)
        # Truncate to keep output scannable.
        snippet = bullet[:90] + ("..." if len(bullet) > 90 else "")
        print(f"[{label:>14}] L{line_no:>4}  {snippet}")


def main(argv: list[str]) -> int:
    if not argv:
        print("Usage: python classify_task.py <text> | --file <path>", file=sys.stderr)
        return 1

    if argv[0] == "--file":
        if len(argv) < 2:
            print("Usage: python classify_task.py --file <path>", file=sys.stderr)
            return 1
        path = Path(argv[1])
        if not path.exists():
            print(f"File not found: {path}", file=sys.stderr)
            return 1
        _classify_file(path)
        return 0

    text = " ".join(argv)
    print(classify(text))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
