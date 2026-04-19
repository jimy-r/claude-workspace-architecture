# claude-workspace-architecture

A blueprint for a personal [Claude Code](https://claude.com/claude-code) workspace — personas, routines, hooks, skills, MCP servers, memory, and task coordination.

## Three ways in

- **[META_ARCHITECTURE.md](META_ARCHITECTURE.md)** — the full structural reference (~400 lines, with diagrams).
- **[ADOPTION.md](ADOPTION.md)** — a 5-step walkthrough for setting up a similar workspace, minimum-viable at each step.
- **[samples/](samples/)** — schematic scaffold files (CLAUDE.md and CONTEXT.md templates, a canonical role, a project binding, a custom skill, a hook config, a task list) you can fork and adapt.

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

## Caveats

- This is a **snapshot**, not a maintained product. The source workspace evolves; this copy may drift.
- Paths in the doc are generic (`<workspace>`, `<home>`) — any concrete setup will substitute its own.
- Nothing here executes on its own; the doc describes structure, not runnable tooling.

## Reference

- [Claude Code documentation](https://docs.claude.com/en/docs/claude-code/overview)
- Individual feature pages linked inline throughout `META_ARCHITECTURE.md`

## License

[MIT](LICENSE). Reuse freely.
