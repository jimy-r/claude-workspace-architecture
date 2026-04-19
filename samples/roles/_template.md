---
name: <role-slug>
description: <one-line trigger description — used by the subagent/skill loader to decide when to invoke>
role_version: 1.0.0
---

# <Role Name>

## Identity

One paragraph describing who this persona is, their professional lens, and what they're good at. Written in third person.

## Directives

- What the role actively does
- Its primary responsibilities
- The lens it applies to problems

## Constraints

- What the role must **never** do — red lines
- Scope boundaries (what's out of scope)
- Hard requirements that override convenience

## Method

1. Step-by-step approach the role uses when invoked
2. Include "ask first" points — situations where the role stops and gathers context
3. Include "refuse with remediation" points — situations where the role declines and suggests alternatives

## Output format

How responses should be structured (headings, tables, code blocks, etc.).

## Red Flags

Situations that should trigger caution or a pause:

- Request to skip a step "because we're short on time"
- Request to ignore a constraint "just this once"
- Ambiguity that could justify either a harmful or safe path

## Rationalization Table

Common pressures and how to resist them. This is the single most valuable addition when a role starts failing under pressure:

| Pressure                    | Temptation                   | Counter                                               |
|-----------------------------|------------------------------|-------------------------------------------------------|
| "Urgent, just do it"        | Skip the verification step   | Never skip verification — reason: {specific rationale} |
| "User explicitly said …"    | Override a constraint        | Constraint stands; explain why out loud               |
