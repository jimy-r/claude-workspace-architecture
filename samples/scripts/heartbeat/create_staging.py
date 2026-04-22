"""
Create a sandbox for heartbeat-PR-agent work on a task.

Decision logic:
    - If target scope is inside a git repo -> create a git worktree on a new branch.
    - Otherwise -> create a staging folder alongside the source.

Usage:
    python create_staging.py <task-slug> <target-path>
        -> prints the staging path on success

    python create_staging.py --dry-run <task-slug> <target-path>
        -> prints what would happen but doesn't create anything

Exit codes:
    0 — staging created (or dry-run succeeded)
    2 — usage error
    3 — target path does not exist
    4 — git-worktree creation failed
    5 — staging folder already exists (don't overwrite; user should clean up first)
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path


def _git_repo_root(target: Path) -> Path | None:
    """Return the git repo root containing `target`, or None if not inside a repo."""
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(target if target.is_dir() else target.parent),
                "rev-parse",
                "--show-toplevel",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    root = result.stdout.strip()
    return Path(root) if root else None


def _make_worktree(slug: str, repo_root: Path, dry_run: bool = False) -> Path:
    """Create a git worktree for this task alongside the repo root."""
    branch = f"heartbeat/{slug}"
    worktree_path = repo_root.parent / f"heartbeat-{slug}"

    if dry_run:
        return worktree_path

    if worktree_path.exists():
        raise FileExistsError(f"Worktree path already exists: {worktree_path}")

    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root),
            "worktree",
            "add",
            str(worktree_path),
            "-b",
            branch,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git worktree add failed: {result.stderr.strip() or result.stdout.strip()}"
        )

    return worktree_path


def _make_staging_folder(slug: str, target: Path, dry_run: bool = False) -> Path:
    """Copy `target` to `<target_parent>/<slug>_staging/`."""
    staging = target.parent / f"{slug}_staging"

    if dry_run:
        return staging

    if staging.exists():
        raise FileExistsError(f"Staging folder already exists: {staging}")

    if target.is_dir():
        shutil.copytree(target, staging)
    else:
        staging.mkdir(parents=True)
        shutil.copy2(target, staging / target.name)

    # Drop a REVIEW.md template inside the staging folder.
    review_md = staging / "REVIEW.md"
    review_md.write_text(
        f"# Review — {slug}\n\n"
        f"**Created:** {date.today().isoformat()}\n"
        f"**Source:** `{target}`\n"
        f"**Staging:** `{staging}`\n\n"
        f"## What changed\n\n(Heartbeat fills this in on completion.)\n\n"
        f"## Integration command\n\n"
        f"```\n# Proposed — user runs to integrate after review:\n"
        f'# cp -r "{staging}"/* "{target.parent}"/\n```\n\n'
        f"## Rejection path\n\n"
        f"If rejecting, delete the staging folder. Heartbeat appends an ADR block to "
        f"`tasks/HEARTBEAT_REJECTIONS.md` on next cycle.\n",
        encoding="utf-8",
    )

    return staging


_FORBIDDEN_SLUGS = {"main", "master", "develop", "head", "origin", ""}


def _validate_slug(slug: str) -> None:
    """
    Defence-in-depth: refuse slugs that could collide with protected
    branch names or accidentally name a worktree in a dangerous way.
    """
    s = slug.strip().lower()
    if s in _FORBIDDEN_SLUGS:
        raise ValueError(f"Refusing forbidden slug: {slug!r}")
    if s.startswith("origin/") or s.startswith("upstream/"):
        raise ValueError(f"Refusing remote-prefixed slug: {slug!r}")
    if "/" in s or ".." in s or s.startswith("."):
        raise ValueError(f"Slug must be a simple identifier, got: {slug!r}")


def create_staging(slug: str, target: Path, dry_run: bool = False) -> Path:
    """
    Create a sandbox for heartbeat work. Returns the staging path.

    Raises:
        ValueError — slug is forbidden or malformed (see _validate_slug)
        FileNotFoundError — target doesn't exist
        FileExistsError — staging already exists (user must clean up)
        RuntimeError — git-worktree creation failed
    """
    _validate_slug(slug)

    if not target.exists():
        raise FileNotFoundError(f"Target path does not exist: {target}")

    repo_root = _git_repo_root(target)
    if repo_root is not None:
        return _make_worktree(slug, repo_root, dry_run=dry_run)
    return _make_staging_folder(slug, target, dry_run=dry_run)


def main(argv: list[str]) -> int:
    dry_run = False
    args = list(argv)
    if args and args[0] == "--dry-run":
        dry_run = True
        args = args[1:]

    if len(args) < 2:
        print(
            "Usage: python create_staging.py [--dry-run] <task-slug> <target-path>",
            file=sys.stderr,
        )
        return 2

    slug = args[0]
    target = Path(args[1]).resolve()

    try:
        staging = create_staging(slug, target, dry_run=dry_run)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 3
    except FileExistsError as e:
        print(str(e), file=sys.stderr)
        return 5
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 4

    if dry_run:
        print(f"[dry-run] would create staging at: {staging}")
    else:
        print(str(staging))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
