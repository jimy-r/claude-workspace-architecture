# claude-workspace-architecture

A blueprint for a personal [Claude Code](https://claude.com/claude-code) workspace — personas, routines, hooks, skills, MCP servers, memory, and task coordination.

## Three ways in

- **[META_ARCHITECTURE.md](META_ARCHITECTURE.md)** — the full structural reference (~400 lines, with diagrams).
- **[ADOPTION.md](ADOPTION.md)** — a 5-step walkthrough for setting up a similar workspace, minimum-viable at each step.
- **[samples/](samples/)** — schematic scaffold files (CLAUDE.md and CONTEXT.md templates, a canonical role, a project binding, a custom skill, a hook config, a task list) you can fork and adapt.

## Who this is for

Four rough tiers — all welcome:

| Tier | What they get from this |
|---|---|
| **Browsers** | A worked example of how the full Claude Code toolkit fits together end-to-end. Read `META_ARCHITECTURE.md` and move on. |
| **Adopters** | A template to build their own workspace from. Follow `ADOPTION.md`, fork `samples/`, adapt. |
| **Contributors** | A shared reference they can improve. See [CONTRIBUTING.md](CONTRIBUTING.md). |
| **Maintainers** | Someone running their own derivative as a shared hub for their team or community. Fork and re-publish. |

## What a contribution looks like

- **Roles** — fixed schema (Identity / Directives / Constraints / Method / Output / Red Flags / Rationalization Table). See [`samples/roles/_template.md`](samples/roles/_template.md) for the skeleton and [`samples/roles/example-security-auditor.md`](samples/roles/example-security-auditor.md) filled in.
- **Skills** — single-file `SKILL.md` with a [CSO-style description](https://docs.claude.com/en/docs/claude-code/skills) (the trigger condition) + a procedure. See [`samples/.claude/skills/orient/SKILL.md`](samples/.claude/skills/orient/SKILL.md).
- **Hooks** — small JSON entries wiring a shell command to a tool event. See [`samples/.claude/settings.example.json`](samples/.claude/settings.example.json).
- **Project CONTEXT.md** — entity facts a role binding consumes. See [`samples/CONTEXT.md.example`](samples/CONTEXT.md.example).

If a pattern has worked in your own workspace, chances are it'll help someone else. Open an Issue or start a Discussion.

## What's in the doc

How a single working directory can host:

- **Roles library** — 16 canonical expert personas that compose with project-specific `CONTEXT.md` files via thin subagent bindings
- **Launcher scripts + scheduled routines** — the `.bat` layer that bootstraps sessions, plus the Claude Code app's Routines feature that is progressively replacing them
- **Hooks** — `PreToolUse` file-protection blocklist, `PostToolUse` auto-formatters, `SessionStart` context re-injection
- **Custom workspace skills** — `orient`, `wrap`, `tasks`, `verify-completion`, `systematic-debugging`, `role-pressure-test`
- **Heartbeat and audit subagents** — a 2-hourly project manager and a weekly auditor, both writing into a shared task list
- **MCP servers** — voice channel, browser automation, preview, Google Calendar + Workspace, remote chat, scheduled tasks
- **Memory system** — typed files (`user` / `feedback` / `project` / `reference`) indexed by `MEMORY.md`
- **Task coordination layer** — a question-then-action loop between the user and the heartbeat agent, backed by a small set of markdown files
- **Hardening** — a password-manager vault as the canonical credential store, `restic` backups to S3-compatible storage, and container sandboxing for external-facing agents

Tables in the doc use `[stock]` / `[plugin]` / `[local]` / `[custom]` markers so you can see what ships with Claude Code vs what someone had to write.

## Why it's shared

Nothing in here is proprietary or novel — it's just one working arrangement of the pieces Claude Code already provides. Published because a few people have asked how the whole thing fits together, and a single document is easier to hand over than a verbal tour.

The hope is that it becomes a **pattern hub** — a place where people bring their own roles, skills, hooks, scheduled tasks, and workflow ideas so everyone pulls from a richer palette than any one person can assemble solo.

## Contributing

Three surfaces, pick the right one:

- **[Discussions](https://github.com/jimy-r/claude-workspace-architecture/discussions)** — sketch an idea that's still forming, ask a usage question, or share what you've built in your own workspace.
- **[Issues](https://github.com/jimy-r/claude-workspace-architecture/issues/new/choose)** — propose a concrete component (role, skill, hook, routine, MCP pattern), flag a gap or typo, or suggest a workflow improvement. Templates guide the shape.
- **Pull requests** — fork, branch, PR. See [CONTRIBUTING.md](CONTRIBUTING.md) for standards.

**One hard rule:** no personal identifiers, no credentials, no business / health / financial specifics. Every commit must be safe for a public audience. Full guidance in [CONTRIBUTING.md](CONTRIBUTING.md).

## Caveats

- This started as one person's working setup; it's evolving into a shared reference with community contributions. The original author curates the core; contributors extend the library.
- Paths in the doc are generic (`<workspace>`, `<home>`) — any concrete setup will substitute its own.
- Nothing here executes on its own; the doc describes structure, not runnable tooling.

## Reference

- [Claude Code documentation](https://docs.claude.com/en/docs/claude-code/overview)
- Individual feature pages linked inline throughout `META_ARCHITECTURE.md`
- [SUPPORT.md](SUPPORT.md) — where to go for what (adaptation, bugs, Q&A)
- [STYLE_GUIDE.md](STYLE_GUIDE.md) — writing and formatting conventions
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — project norms, reporting path

## License

[MIT](LICENSE). Reuse freely.

---

*Last verified against the repo structure on **2026-04-19**.*
