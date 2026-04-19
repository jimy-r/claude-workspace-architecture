# Samples

Minimal scaffolding illustrating each major layer described in [META_ARCHITECTURE.md](../META_ARCHITECTURE.md). These are **schematic**, not intended to run verbatim — fork and adapt.

## Layout

```
samples/
├── CLAUDE.md.example              # workspace-level always-loaded context
├── CONTEXT.md.example             # generic project CONTEXT.md template
├── roles/
│   ├── _template.md               # canonical role skeleton
│   └── example-security-auditor.md
├── example-project/               # a project that consumes the role library
│   ├── CONTEXT.md                 # filled-in CONTEXT.md (counterpart to the template)
│   └── .claude/agents/
│       └── example-security.md    # thin binding: role + CONTEXT.md
├── .claude/
│   ├── settings.example.json      # hook configuration
│   └── skills/orient/SKILL.md     # a custom workspace skill
└── tasks/
    ├── README.md                  # task coordination layer explainer
    └── To-Do-Notes.example.md     # sample master task list
```

## How to read these

- **Start with** [`CLAUDE.md.example`](CLAUDE.md.example) — the root-level context your Claude sessions will always load.
- **Then** [`CONTEXT.md.example`](CONTEXT.md.example) — the blank template for project entity facts. The filled-in counterpart lives at [`example-project/CONTEXT.md`](example-project/CONTEXT.md).
- **Then** browse [`roles/`](roles/) to see the canonical-role → project-binding composition pattern.
- **Then** look at [`.claude/settings.example.json`](.claude/settings.example.json) for hooks and [`.claude/skills/orient/SKILL.md`](.claude/skills/orient/SKILL.md) for a skill.
- **Finally** [`tasks/README.md`](tasks/README.md) for the async question-then-action coordination layer.

## Adoption path

See the root [ADOPTION.md](../ADOPTION.md) — a 5-step walkthrough that maps these samples to concrete setup steps.
