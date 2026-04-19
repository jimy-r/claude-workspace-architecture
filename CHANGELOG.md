# Changelog

Human-written record of notable changes. Complements GitHub's auto-generated release notes (configured in `.github/release.yml`) — this file captures the *why* and the *shape*, not every merged PR.

Format inspired by [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The project doesn't version releases on a schedule; entries are dated.

## [Unreleased]

### Added
- `SECURITY.md` — three-category security policy (privacy leaks / workflow vulns / docs weakening reader security) with public-vs-private reporting routes.
- `CHANGELOG.md` (this file).
- `ATTRIBUTION.md` — credit for patterns borrowed from other public repos.
- Diátaxis framing paragraph in `README.md` mapping the repo's docs across tutorial / how-to / reference / explanation quadrants.

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

*Last verified against the repo structure on **2026-04-19**.*
