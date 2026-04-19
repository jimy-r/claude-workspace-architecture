# Example Project — CONTEXT

> Entity facts about this project. Loaded by role bindings under `.claude/agents/` to compose canonical roles with project-specific context. **Never** put credentials here — only pointers to the password-manager item.

## What this project is

One-paragraph description. Purely illustrative example:

> A small FastAPI service that fetches weather forecasts for a list of cities, caches each response for 60 minutes, and serves them as a JSON API with a simple key-based auth layer.

## Stack

- Language: Python 3.12
- Framework: FastAPI
- Cache: Redis
- Test runner: pytest
- Hosting: `<your PaaS of choice>`

## Key paths

- `app/` — main source
- `app/api/` — FastAPI routers
- `app/cache/` — Redis wrapper
- `tests/` — pytest suite
- `.env` — runtime configuration (hook-protected; not committed)

## Data flow

1. **Fetch** — upstream weather API → normalise payload
2. **Cache** — store in Redis with 60-minute TTL keyed by city
3. **Serve** — FastAPI endpoint returns cached-or-fetched JSON, with a key-based auth middleware

## Open strategic questions

- Rate-limit policy — upstream provider has a hard cap; when to back off vs return stale cache?
- Observability — currently logs only; metrics + tracing not yet wired.
- Redis failover — single-node deployment; multi-AZ not yet considered.

## Credential references

Credentials live in the password manager. This project references:

- `<weather-provider> — production API key`
- `<redis-provider> — connection string`

Agents needing a credential surface the item name; the user retrieves it manually.
