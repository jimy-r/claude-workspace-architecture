# Contributing

This started as one person's working setup; the goal from here is a **pattern hub** — a place where people share roles, skills, hooks, scheduled tasks, and workflow ideas so everyone pulls from a richer palette. Contributions of all shapes are welcome.

## Pick the right surface

| If you… | Go to |
|---|---|
| Have an idea that's still forming | [Discussions → Ideas](https://github.com/jimy-r/claude-workspace-architecture/discussions) |
| Want to share what you've built | [Discussions → Show and tell](https://github.com/jimy-r/claude-workspace-architecture/discussions) |
| Have a usage question | [Discussions → Q&A](https://github.com/jimy-r/claude-workspace-architecture/discussions) |
| Want to propose a concrete component | [Open an Issue → Component proposal](https://github.com/jimy-r/claude-workspace-architecture/issues/new/choose) |
| Spotted a gap or typo | [Open an Issue → Gap or correction](https://github.com/jimy-r/claude-workspace-architecture/issues/new/choose) |
| Want to suggest a workflow improvement | [Open an Issue → Workflow improvement](https://github.com/jimy-r/claude-workspace-architecture/issues/new/choose) |
| Are ready to submit a change | Fork → branch → PR |

## What's welcome

**Very welcome:**
- A **new canonical role** you've found useful — use [`samples/roles/_template.md`](samples/roles/_template.md) as the schema.
- A **custom skill** you've built — CSO-style description, reference [`samples/.claude/skills/orient/SKILL.md`](samples/.claude/skills/orient/SKILL.md) for shape.
- A **hook pattern** that's saved you from a mistake (file protection, formatting, session-start re-injection, etc.).
- A **scheduled task / routine** that produces value unattended — heartbeat variants, audit variants, daily briefs, etc.
- An **MCP wiring pattern** — how you cleanly integrated an external system.
- **Workflow improvements** to something already in the doc — a cleaner way to do an existing thing.
- **Corrections, clarifications, broken-link fixes, rendering issues** (especially Mermaid).

**Also welcome:**
- "I tried this and it didn't work because X" — a lesson worth capturing.
- Migration notes as Claude Code's stock features evolve.
- Diagrams, examples, or walkthroughs that make an existing section clearer.

**Not in scope:**
- Secrets, credentials, private content — see [Privacy](#privacy) below.
- Product pitches or unrelated self-promotion.
- Bulk refactors that don't preserve the doc's opinionated simplicity.

## Privacy — the one hard rule

Every commit must be safe for a public audience. That means **no**:

- **Personal identifiers** — real names, email addresses, usernames tied to identity, home or workplace locations.
- **Business / product specifics** — company names, product names, customer-specific details, infrastructure providers tied to a specific customer.
- **Credentials, tokens, API keys, or anything adjacent** — ever. Not even expired ones. Not even in example placeholders.
- **Health, financial, or legal data** — ever.
- **Paths that reveal a user's machine layout** — absolute paths like `/home/alice/...` or `C:/Users/alice/...`. Use the generic placeholders below.

**Use these placeholders:**

| Use | Instead of |
|---|---|
| `<workspace>` | an actual working-directory path |
| `<home>` | an actual home-directory path |
| `<project>` | a named project folder |
| `<workspace-id>` | a hashed / real identifier |
| "the user" / "the author" | a real first name |
| "a commercial password manager" | a specific vendor brand |
| "`<cloud-provider>`" / "`<PaaS>`" | a real service name |

When in doubt, generalise. Reviewers will bounce PRs that contain identifiers — not as punishment, just to keep the repo safe for everyone who reads it.

## Proposing a new component

1. **Start in [Discussions](https://github.com/jimy-r/claude-workspace-architecture/discussions)** — sketch the idea, get feedback on shape and fit before you build.
2. **Follow the templates** — [`samples/roles/_template.md`](samples/roles/_template.md) for roles, [`samples/CONTEXT.md.example`](samples/CONTEXT.md.example) for project context files, existing SKILL.md format for skills.
3. **Keep entity facts out** — roles are pure (no entity facts). Infrastructure-specific details go in a `CONTEXT.md` companion, never in the role itself.
4. **One component per PR** — small and reviewable beats big and sprawling.

## Pull-request standards

- **One focused change per PR.** Refactors and content additions go in separate PRs.
- **Run the redaction check before pushing.** A quick `grep` for personal identifiers, paths, business specifics. Any hit, fix it before `git add`.
- **Preview rendering on GitHub** if you've touched a Mermaid diagram or heavy markdown — Mermaid especially can render differently between editors and GitHub.
- **PR description should answer:** what changed, why, and did you run the redaction check?
- Keep existing tone: terse, structural, opinionated.

## Branching

- Main branch is `main`. Fork → branch → PR.
- Branch names: short, descriptive — `add-role-X`, `fix-mermaid-section-9`, `improve-heartbeat-loop`.
- Delete merged branches; the repo has auto-delete enabled.

## Conduct

Be honest, be terse, credit sources, critique ideas not people. No performative politeness, no passive-aggression. Disagreement is expected and welcome; keep it focused on the work.
