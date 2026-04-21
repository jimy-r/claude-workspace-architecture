# Changelog

Human-written record of notable changes. Complements GitHub's auto-generated release notes (configured in `.github/release.yml`) — this file captures the *why* and the *shape*, not every merged PR.

Format inspired by [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The project doesn't version releases on a schedule; entries are dated.

## [Unreleased]

### Changed
- **Morning-brief scheduled-task root cause fixed (`LogonType: Interactive only` → `Interactive/Background`).** A multi-day mystery — the daily brief appeared "delivered" but `schtasks /Query` showed every firing had actually crashed with `Last Result: 0xC000013A` (`STATUS_CONTROL_C_EXIT`) before producing any output; `scheduled-logs/` was empty for every run. Root cause: the `claude --print` CLI (Node.js) needs a real console handle to manage stdio. When a Task Scheduler task fires with `LogonType: Interactive only` (the default when a task is created without selecting "Run whether user is logged on or not") the PowerShell process launches in a detached/hidden session with no attached console; Node's stdio handshake fails and the process dies on a broken-pipe console signal before writing a byte — the wrapper's `Tee-Object` never gets any data to write. Fix: each Claude task's principal flipped via Task Scheduler → Properties → General → "Run whether user is logged on or not" + Windows password, which changes `LogonType` to `Password` (shown as `Interactive/Background` in `schtasks /Query`) and gives the task a proper batch-logon session with a valid console. Immediate effect — the first post-fix firing produced `Last Result: 0` and the expected log + brief file. Applied to all three live Claude tasks (`Morning Brief`, `Consolidate Memory`, `Heartbeat Monitor`). Documented in `META_ARCHITECTURE.md` §3 Automated infrastructure as a critical-setting note. (2026-04-21)
- **`morning-brief` SKILL.md delivery step rewritten** — before sending, the markdown is now passed through a new HTML renderer (`scripts/brief_render.py`); the email is then sent multipart (text + HTML) via `send_self_email.py --body-file <md> --html-file <html>`. Gmail / Apple Mail / Outlook render the styled newsletter; plain-text clients show the markdown. Metrics file now logs delivery mode as `sent-html` / `sent-text` / `drafted` to surface degraded-path days. Fallback chain: HTML render fails → text-only send; SMTP send fails → draft via MCP. (2026-04-21)
- **AI-news selection criteria refined** in `morning-brief` SKILL.md. Explicit quality bar ("major updates, technology breakthroughs, major thought pieces"); provider-official announcements promoted to the top of the selection priority order; skip list expanded (celebrity-CEO takes, pure hype, op-eds without novel insight, marketing round-ups, vendor benchmark-of-the-week, funding-round chatter unless the deal reshapes the landscape, incremental dot-releases). Global `--limit` raised 15 → 25 to accommodate the wider feed pool; `feed_errors` threshold raised 2 → 3. Token budget 2k → 3k input. (2026-04-21)

### Added
- **Heartbeat Monitor scheduled task registered** (OS-level scheduler). `schtasks /Query` confirmed the SKILL.md at `<home>/.claude/scheduled-tasks/heartbeat-monitor/` had never fired on its own — there was no binding. Registered with the same wrapper the other Claude tasks use, every 2h at :17 past. Paired decision: the `upgrade-audit` SKILL.md (same missing-binding situation) is intentionally kept **manual** — invoked on demand via the existing `audit.bat` launcher rather than scheduled — because its weekly cadence pairs well with active user attention. (2026-04-21)
- **`scripts/brief_render.py` — newsletter HTML renderer** for the daily brief. Parses the markdown brief and emits inline-CSS HTML with a section-aware template (masthead + local-weather strip + two-column appointments with bold time + AI-news cards with source-hostname badges + tasks grouped by `##` header with count badges + numbered open-questions with posted-date + overnight + attention + centred footer). Palette: warm off-white body, white card, deep navy primary, burnt-orange accent. System fonts for body + Georgia serif for the masthead. Max-width 640px, table-based layout for broadest email-client compatibility (Gmail, Apple Mail, Outlook, iOS Mail). Zero dependencies (stdlib only — `html`, `re`, `pathlib`, `argparse`, `dataclasses`). Called from the SKILL.md delivery step immediately after the markdown is written. (2026-04-21)
- **`send_self_email.py` extended with `--html-file`** for multipart/alternative delivery. When provided, the message is sent with both a `text/plain` body (the markdown) and a `text/html` part (the rendered newsletter). Backward compatible — existing text-only callers unchanged. The narrow Iron Law exception is untouched: still hardcoded to the user's own address, still refuses any other recipient. (2026-04-21)
- **AI news source pool expanded 3 → 10 feeds** (`scripts/ai_news.py`). Added OpenAI (`openai.com/news/rss.xml`), Google DeepMind (`deepmind.google/blog/rss.xml`), Google AI Blog (`blog.google/innovation-and-ai/technology/ai/rss/`), Google Research (`research.google/blog/rss/`), MIT Tech Review AI (`technologyreview.com/topic/artificial-intelligence/feed`), Wired AI (`wired.com/feed/tag/ai/latest/rss`), TechCrunch AI (`techcrunch.com/category/artificial-intelligence/feed/`). Anthropic has no public RSS — verified all candidate paths return 404; HN + Simon Willison cover announcements within hours. Added `PER_SOURCE_CAP = 6` so high-volume feeds (arXiv, HN) can't monopolise the pool at small `--limit` values; each source contributes at most 6 items before the global limit is applied. **Note to adopters:** `samples/scripts/ai_news.py` in this repo still ships the original 3-feed default; compare with `scripts/ai_news.py` in a real workspace for the expanded set. (2026-04-21)

### Changed
- **Phase 2.5c guardrails tightened after first-run drift** — the inaugural test run of the new per-section audit modified two files while simultaneously reporting zero auto-applies. Three drifts identified and fixed in `samples/.claude/agents/audit.md`: (1) tier enums gained an explicit *default-to-Tier-3* rule — content rewrites of existing SKILL.md files, feature additions to helper scripts, and refinements to existing scheduled-task orchestrators are all Tier 3 by construction (closes the "feels safe, not in the Tier 3 list either, so just do it" loophole); (2) the 24h-mtime guardrail now runs as a procedural per-write checklist immediately before every `Write`/`Edit` call, not just at orchestrator-decision time; (3) a reporting invariant requires every file modified to appear in the Phase 3 report under `### Auto-applied`, `### New capabilities this week`, or `### Safety guardrail activity` — the orchestrator maintains a write-log and cross-checks it before finalising. Added explicit subagent-boundary clause: `researcher` fan-outs are read-only and return proposed edits as data payloads; the audit orchestrator is the sole writer. (2026-04-21)
- **Weekly upgrade-audit upgraded with Phase 2.5c: per-section best-practice research + trust gradient for auto-apply.** The weekly audit agent (`samples/.claude/agents/audit.md`) fans out one `researcher` subagent per major META_ARCHITECTURE section and classifies each finding into Tier 1 (auto-apply silently — new canonical roles, defensive protection-blocklist additions, memory-hygiene prose, doc fixes), Tier 2 (auto-apply + surface under `### New capabilities this week` in the report — new workspace skill / subagent / Command Shortcut), or Tier 3 (approval needed, never auto-applied — new MCP server, new scheduled task, new hook, removal of any safeguard, Iron Law change). Rate-limit: max 5 Tier-1/Tier-2 applies per run; remainder queued under `### Deferred (rate-limit)`. Safety guardrails: validator-fail and 24h-user-edit checks downgrade to Tier 3; auto-apply disabled entirely if Phase 2.6 finds >3 CRITICAL security findings or if prior two weeks' Tier-2 additions haven't been mentioned in any subsequent user activity. Phase 3 report format updated to lead with auto-applied items. (2026-04-21)

### Added
- **`samples/` library expansion** — the `samples/` tree grew from 10 files to 52 files, turning the repo from "pattern sketches" into a fuller reference implementation. All 17 canonical roles (previously only `example-security-auditor.md`), 7 workspace skills (previously only `orient`), 3 custom subagents (`audit`, `heartbeat`, `researcher`), 4 scheduled-task SKILL.md files (including the full `morning-brief/` daily orchestrator), 10 Python/PowerShell helpers (RSS-dedup AI-news fetcher, email-rules engine, receipt pipeline, bill tracker, restic backup + verify, etc.), and the heartbeat agent's operational context (`tasks/HEARTBEAT.md`). Every file redacted through a staging script with path / identifier / vendor / geography substitutions; post-staging grep safety net verified clean against `bai.james` / `baija` / absolute paths / specific project names / specific vendor names. The minimal 5-step adoption scaffold (`CLAUDE.md.example`, `CONTEXT.md.example`, `example-project/`, the `_template.md` role, the `settings.example.json` hook config) remains intact — the new content is additive. `samples/README.md` rewritten with two-tier structure (minimal scaffold + full library). Root `README.md` updated to surface the broader content. Note: domain-flavoured content (Australian tax terms in `accountant.md`, Brisbane-shaped weather fetch in `morning-brief/SKILL.md`) remains as template to localise. Data files (actual email rules, services registry, task content) are NOT shipped — only schemas + consumers. (2026-04-21)
- **New workspace skill: `terse-mode`** — session-long output compression discipline. Iron Law: compress prose, preserve precision (never compresses tool arguments, code, errors, security warnings, research-brief claim grades, or final deliverable content). Invoke via "terse" / "/terse" / "terse mode"; release via "verbose" / "/verbose" / "normal mode". Pattern credit: `juliusbrussee/caveman` (design reference, not dependency — reimplemented ~30-line prompt natively). (2026-04-21)
- **New daily-brief pattern: AI news section** — sketch visible in `samples/.claude/scheduled-tasks/morning-brief/SKILL.md`. Generic `ai_news.py` helper (stdlib only — urllib + xml.etree + sqlite3, no pip dependencies) fetches curated RSS/Atom feeds, filters to last 48h, dedups via SHA-256 content-hash in SQLite, auto-marks returned items as seen. Feeds: Simon Willison, HN AI-tag, arXiv cs.AI (extensible). Pattern credit: `iain-services/claude-pulse` (design reference only). (2026-04-21)
- **Auto-routed workspace subagent wrapping `researcher`** — a workspace-level subagent at `<workspace>/.claude/agents/researcher.md` composes the canonical role via `@`-include. Its CSO-style description drives Claude Code's subagent picker to prefer it over `general-purpose` for research-shaped tasks (market/competitor scans, technical comparisons, regulatory/tax research, literature reviews, due diligence, fact-checking) without any manual `@`-invocation. User-global `CLAUDE.md` § Subagent Strategy gained an explicit preference directive. `.claude/agents/` is scanned at session launch, not hot-reloaded. (2026-04-20)
- **New canonical role: `researcher`** — evidence-based investigation across any domain, blending consulting-analyst structure (answer-first, MECE, Pyramid Principle), investigative-journalism fabrication guards (two-source rule, no composites), and academic systematic-review rigour (pre-committed criteria, dissent as data, graded evidence). v1.0.0, category `research`, default model `opus`, `requires_context: false` so it's invoked domain-agnostic without a project binding. Core constraints: primary-source preference, compound-attribute verification against fabrication, two-axis Admiralty-style source grading, `[observed]`/`[inferred]`/`[unverified]` claim tagging, quote-then-paraphrase on load-bearing claims. Passed adversarial pressure test (4-vector: authority + urgency + scope-minimisation + fabrication invitation) at initial deployment. Library count 16 → 17. (2026-04-20)
- `META_ARCHITECTURE.md` §8 **memory architecture hardening** — `episodes/` subfolder for one-off events (not always-loaded), `learned_on` / `last_verified` / `verify_by_checking` YAML frontmatter on `reference_*` memory files, a memory-lint script that walks memory + episodes and verifies referenced paths (runtime-created paths allowlisted), and a weekly `consolidate-memory` scheduled task that resolves contradictions, converts relative→absolute dates, merges duplicates, moves decayed episodes, and keeps `MEMORY.md` under its 200-line ceiling. Four-op discipline per fact (ADD / UPDATE / DELETE / NOOP). (2026-04-20)
- `META_ARCHITECTURE.md` §3 **OS-level scheduler workaround** — when Claude Code's built-in `scheduled-tasks` MCP is unconnected, SKILL.md files don't fire on their own. Documents a thin wrapper (`scripts/run-scheduled-skill.ps1`) that reads a SKILL.md and pipes it to `claude --print` as the prompt, invoked by OS-level Task Scheduler / cron / launchd entries. Includes the PS 5.1 native-CLI lesson as a reusable pattern. (2026-04-20)
- `SECURITY.md` — three-category security policy (privacy leaks / workflow vulns / docs weakening reader security) with public-vs-private reporting routes.
- `CHANGELOG.md` (this file).
- `ATTRIBUTION.md` — credit for patterns borrowed from other public repos.
- Diátaxis framing paragraph in `README.md` mapping the repo's docs across tutorial / how-to / reference / explanation quadrants.

### Changed
- **`link-check` workflow split into two modes** — on pull requests, lychee now checks only the `.md` files actually changed in the diff (via `git diff --name-only --diff-filter=ACMR`); on the weekly cron and manual dispatch it still runs against the full repo and auto-opens an Issue on failure. Rationale: whole-repo checks on every PR made contributors responsible for link rot they hadn't introduced, and flooded the maintainer's inbox with failure emails on unrelated PRs. Diff-only scopes PR failure to the author's actual change; the weekly cron catches background rot (stale vendor URLs, dangling internal links after deletions) on a reviewable rhythm. Pattern is standard in larger OSS repos (kubernetes, rust, etc.). No third-party action added for the diff — plain `git diff` in a bash step. (2026-04-21)
- GitHub Actions version bumps via Dependabot: `actions/checkout` 4→6, `actions/setup-python` 5→6, `actions/stale` 9→10, `peter-evans/create-issue-from-file` 5→6, `dessant/lock-threads` 5→6. All pure Node 16→20 runtime upgrades; input APIs unchanged for our usage. (2026-04-20, PRs #1-5)

---

## 2026-04-19 — Final hardening pass

### Added
- Path + size auto-labeller workflow (`actions/labeler` + `codelytv/pr-size-labeler`).
- Multi-link `contact_links` in issue-template chooser — deflects Claude Code bugs and usage questions off-repo.
- Prescriptive PR template with inline ✅/❌ examples for title format and "why" wording.
- Weekly `auto-cleanup` workflow — Prettier pass on `*.md`/`*.yml`; opens a PR only if changes exist.
- `CODEOWNERS` — auto-requests maintainer review; mirrors CONTRIBUTING's scope-boundaries table.
- Monthly `lock-closed` workflow (`dessant/lock-threads`, 90-day threshold).
- `SUPPORT.md` — traffic router for off-repo questions.
- `STYLE_GUIDE.md` — voice, placeholders, table markers, diagrams, formatting in one reviewable anchor.
- `.prettierrc` + `.prettierignore` — `proseWrap: preserve`, LF line endings, sample `.md.example` files excluded.
- 12 new labels: `area/*` (6), `size/*` (5), `chore`.

### Changed
- `CONTRIBUTING.md`: references to `STYLE_GUIDE.md` and `SUPPORT.md`.
- `README.md`: added `SUPPORT.md`, `STYLE_GUIDE.md` pointers in Reference section.

## 2026-04-19 — External-repo best practices

### Added
- `link-check` workflow (`lycheeverse/lychee-action`) — fails PRs on dead links; weekly Monday 06:00 UTC cron opens an Issue.
- `stale` workflow (`actions/stale`) — Issues 60d/14d, PRs 30d/14d, exempt labels `pinned`/`patterns-board`/`moderation`/`blocked`.
- `validate-samples` workflow + `scripts/validate_samples.py` — frontmatter completeness + shape-based leak detection (Windows/Unix home paths, concrete emails).
- `.github/dependabot.yml` — GitHub Actions ecosystem, weekly, `chore:` prefix.
- `.github/release.yml` — auto-categorised release notes.
- `CODE_OF_CONDUCT.md` (Contributor Covenant by reference) + `moderation_report.yml` issue template.
- `CONTRIBUTING.md` § "If you're a Claude Code instance reading this" — 7-step checklist for AI-authored PRs.
- 10 initial labels: `promoted`, `relegated`, `refined`, `skip-changelog`, `pinned`, `moderation`, `patterns-board`, `contribution-flow`, `component-proposal`, `improvement`.

## 2026-04-19 — fuel-project-inspired hardening

### Added
- `PATTERNS_BOARD.md` — promotion / relegation / refinement log for patterns surfacing across Discussions, Issues, and PRs. Signal-driven, human-reviewed.
- `CONTRIBUTING.md` § Scope boundaries — files needing a Discussion/Issue before PR.
- `CONTRIBUTING.md` § Commit conventions — Conventional Commits with type table and examples.
- `README.md` § "Who this is for" — four-tier reader taxonomy.
- `README.md` § "What a contribution looks like" — concrete anchors for prospective contributors.
- Freshness footers ("Last verified ... 2026-04-19") on core docs.
- PR template "Patterns board" link slot.

### Changed
- `CLAUDE.md` — flipped from gitignored-private to publicly-committed; contributor-focused guidance. Maintainer-specific grep patterns moved to private memory.

## 2026-04-19 — Pattern hub reframe

### Added
- `CONTRIBUTING.md` with types of contributions welcome, privacy rule, placeholder conventions, PR standards.
- Three issue templates: `component_proposal.yml`, `gap_or_correction.yml`, `workflow_improvement.yml`.
- `.github/ISSUE_TEMPLATE/config.yml` — disables blank issues, points open questions to Discussions.
- `.github/PULL_REQUEST_TEMPLATE.md` with inline privacy checklist.
- README "Contributing" section linking all three surfaces.

### Changed
- README framing shifted from "snapshot, take it or leave it" to "shared reference, pattern hub."
- Repo setting: `delete-branch-on-merge` enabled.

## 2026-04-19 — Repo creation

### Added
- Initial commit: redacted snapshot of the workspace meta-architecture.
- `README.md`, `META_ARCHITECTURE.md`, `LICENSE` (MIT), `.gitignore`.
- Table of contents + Conventions block in `META_ARCHITECTURE.md`.
- Mermaid diagrams (§1 layered architecture, §2 role composition, §9 heartbeat sequence).
- `[stock]` / `[plugin]` / `[local]` / `[custom]` table-row markers.
- Anthropic-docs links per feature section.
- `ADOPTION.md` — 5-step walkthrough.
- `samples/` scaffold: role template, filled example role, example project with binding, hook config, `orient` skill, task-layer explainer.
- `samples/CONTEXT.md.example` — generic project `CONTEXT.md` template.

---

*Last verified against the repo structure on **2026-04-21**.*
