"""
Shared primitives for the heartbeat-as-PR-agent architecture.

Modules:
    classify_task   — classify a task bullet into has-default / needs-intent / out-of-scope
    check_rejections — grep HEARTBEAT_REJECTIONS.md for prior attempts on a task
    create_staging  — create a git worktree (for git-scope tasks) or staging folder (otherwise)

Design reference: <workspace>/tasks/todo.md § "Heartbeat-as-PR-agent — architectural plan"
"""
