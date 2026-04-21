"""AI news fetcher + dedupper for morning-brief.

Pulls curated RSS/Atom feeds, filters to items published in the last 48 hours
that haven't been seen before, records the new hashes, and returns the
survivors as JSON for the agent to summarise.

Design notes:
- stdlib only (urllib + xml.etree + sqlite3). No feedparser or requests — keeps
  this portable across Windows/macOS/Linux without a venv.
- Each feed is wrapped in try/except. If a feed 404s, times out, or returns
  malformed XML, it's silently skipped and surfaced in `feed_errors`. The
  brief must still run.
- SHA-256 content-hash dedup (source|url|title) in a local SQLite file. Rows
  older than 30 days are pruned on every fetch.
- Auto-marks: `fetch` inserts the new items into the seen-table before
  returning, so tomorrow's run won't re-surface them. If the brief crashes
  after the fetch, at most one day's news is lost — acceptable trade-off for
  a one-command contract to the brief composer.

Pattern credit: content-hash dedup idea reimplemented from
github.com/iain-services/claude-pulse (MIT-ish, no LICENSE file — treated as
design reference, no code copied).

Usage:
  python ai_news.py fetch [--limit N]   # fetch, dedup, emit JSON to stdout
  python ai_news.py stats               # print DB row count + latest seen_at
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
DB_PATH = SCRIPTS_DIR / "_state" / "ai_news_seen.db"
WINDOW_HOURS = 48
FETCH_TIMEOUT = 10
PRUNE_DAYS = 30
USER_AGENT = "ai_news_fetcher/1.0 (+morning-brief)"

# Curated feeds. Each tuple is (display_name, url). Any feed that 404s,
# times out, or returns malformed XML is skipped silently and listed in
# the JSON `feed_errors` key so the agent can note source-unreachable
# patterns over time.
FEEDS: list[tuple[str, str]] = [
    # Verified-working feeds. To add more: append a (name, url) tuple. If a
    # feed 404s at runtime it's skipped silently and listed in `feed_errors`.
    ("Simon Willison", "https://simonwillison.net/atom/everything/"),
    (
        "HN - AI/LLM",
        "https://hnrss.org/newest?q=AI+OR+LLM+OR+anthropic+OR+claude&points=20",
    ),
    ("arXiv cs.AI", "http://export.arxiv.org/rss/cs.AI"),
    # Anthropic + DeepMind + OpenAI public RSS URLs are undocumented at the
    # time of writing (2026-04-21). Simon Willison covers all three at high
    # signal; HN catches announcements within hours. Add direct feeds here
    # if/when the vendors publish authoritative RSS endpoints.
]

NAMESPACES = {
    "atom": "http://www.w3.org/2005/Atom",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
}


def item_hash(source: str, url: str, title: str) -> str:
    """Short stable hash for dedup. 16 hex chars = 64 bits, collisions vanishingly rare."""
    return hashlib.sha256(f"{source}|{url}|{title}".encode("utf-8")).hexdigest()[:16]


def ensure_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS seen (
            hash TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            title TEXT,
            url TEXT,
            seen_at TEXT NOT NULL
        )"""
    )
    cutoff = (datetime.now(timezone.utc) - timedelta(days=PRUNE_DAYS)).isoformat()
    conn.execute("DELETE FROM seen WHERE seen_at < ?", (cutoff,))
    conn.commit()
    return conn


def strip_html(text: str) -> str:
    if not text:
        return ""
    # collapse whitespace after removing tags
    no_tags = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", no_tags).strip()


def parse_date(s: str) -> str | None:
    """Best-effort parse → ISO-UTC string. None if unparseable."""
    if not s:
        return None
    try:
        dt = parsedate_to_datetime(s)
        if dt is not None:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError):
        pass
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError):
        return None


def fetch_feed(name: str, url: str) -> list[dict]:
    """Return parsed items or [] on any failure."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            body = resp.read()
    except (urllib.error.URLError, TimeoutError, Exception):
        return []

    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return []

    items: list[dict] = []

    # RSS 2.0 / RDF — <item> elements anywhere under root
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = (
            item.findtext("pubDate")
            or item.findtext("dc:date", namespaces=NAMESPACES)
            or ""
        ).strip()
        desc = item.findtext("description") or ""
        if not title or not link:
            continue
        items.append(
            {
                "source": name,
                "title": title,
                "url": link,
                "published_raw": pub,
                "snippet": strip_html(desc)[:240],
            }
        )

    # Atom — <entry> elements
    for entry in root.findall("atom:entry", namespaces=NAMESPACES):
        title = (entry.findtext("atom:title", namespaces=NAMESPACES) or "").strip()
        link_el = entry.find("atom:link", namespaces=NAMESPACES)
        link = link_el.get("href") if link_el is not None else ""
        pub = (
            entry.findtext("atom:published", namespaces=NAMESPACES)
            or entry.findtext("atom:updated", namespaces=NAMESPACES)
            or ""
        ).strip()
        summary = (
            entry.findtext("atom:summary", namespaces=NAMESPACES)
            or entry.findtext("atom:content", namespaces=NAMESPACES)
            or ""
        )
        if not title or not link:
            continue
        items.append(
            {
                "source": name,
                "title": title,
                "url": link,
                "published_raw": pub,
                "snippet": strip_html(summary)[:240],
            }
        )

    for it in items:
        it["id"] = item_hash(it["source"], it["url"], it["title"])
        it["published_utc"] = parse_date(it.get("published_raw", ""))
    return items


def cmd_fetch(args: argparse.Namespace) -> int:
    conn = ensure_db()
    seen: set[str] = {row[0] for row in conn.execute("SELECT hash FROM seen")}
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=WINDOW_HOURS)

    all_items: list[dict] = []
    errors: list[str] = []
    for name, url in FEEDS:
        items = fetch_feed(name, url)
        if not items:
            errors.append(name)
            continue
        all_items.extend(items)

    fresh: list[dict] = []
    for it in all_items:
        if it["id"] in seen:
            continue
        pub = it.get("published_utc")
        if pub:
            try:
                dt = datetime.fromisoformat(pub)
                if dt < cutoff:
                    continue
            except ValueError:
                pass  # keep if date unparseable
        fresh.append(it)

    # Most recent first; undated items fall to the end.
    fresh.sort(key=lambda i: i.get("published_utc") or "", reverse=True)
    limit = max(1, args.limit)
    fresh = fresh[:limit]

    # Record as seen BEFORE emitting. If the caller drops the output, we still
    # don't re-surface tomorrow — items are meant to be consumed immediately.
    now_iso = now.isoformat()
    rows = [
        (it["id"], it["source"], it["title"][:400], it["url"][:500], now_iso)
        for it in fresh
    ]
    if rows:
        conn.executemany(
            "INSERT OR IGNORE INTO seen(hash, source, title, url, seen_at) "
            "VALUES (?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()

    output = {
        "fetched_at": now_iso,
        "feed_errors": errors,
        "item_count": len(fresh),
        "items": [
            {
                "id": it["id"],
                "source": it["source"],
                "title": it["title"],
                "url": it["url"],
                "published_utc": it.get("published_utc"),
                "snippet": it["snippet"],
            }
            for it in fresh
        ],
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    conn = ensure_db()
    (count,) = conn.execute("SELECT COUNT(*) FROM seen").fetchone()
    (latest,) = conn.execute("SELECT MAX(seen_at) FROM seen").fetchone()
    by_source = list(
        conn.execute(
            "SELECT source, COUNT(*) FROM seen GROUP BY source ORDER BY 2 DESC"
        )
    )
    print(f"DB path:        {DB_PATH}")
    print(f"Seen rows:      {count}")
    print(f"Latest seen_at: {latest}")
    print(f"Prune window:   {PRUNE_DAYS} days")
    print("By source:")
    for src, n in by_source:
        print(f"  {n:>5}  {src}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_fetch = sub.add_parser("fetch", help="fetch + dedup + emit JSON of unseen items")
    p_fetch.add_argument("--limit", type=int, default=20)
    p_fetch.set_defaults(func=cmd_fetch)

    p_stats = sub.add_parser("stats", help="show DB stats")
    p_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
