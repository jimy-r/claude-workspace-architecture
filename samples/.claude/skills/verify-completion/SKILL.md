---
name: verify-completion
description: Use when completing any implementation task, fixing a bug, or claiming tests, build, or lint pass.
---

## Iron Law

**NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE.**

If you have not run the verification command in this message, you cannot claim it passes. No exceptions.

## Gate Function

Before claiming any task is complete or any check passes:

1. **IDENTIFY** — What command proves this claim? (test runner, build, linter, original symptom reproduction)
2. **RUN** — Execute the full command now, in this message.
3. **READ** — Read the complete output. Check exit code. Count failures.
4. **VERIFY** — Does the output actually confirm the claim?
   - If NO: state the actual status with evidence.
   - If YES: state the claim with the evidence.
5. **CLAIM** — Only now may you say it passes.

Skipping any step means the claim is unverified.

## Common Failures

| Claim | Required Evidence | NOT Evidence |
|---|---|---|
| Tests pass | Test runner output showing 0 failures | "Should pass", previous run, "I'm confident" |
| Linter clean | Linter output with 0 warnings/errors | Extrapolation from reading the code |
| Build succeeds | Build command output with exit code 0 | "No obvious errors", linter passing |
| Bug fixed | Original symptom no longer reproduces | "The fix addresses the root cause" |
| Requirements met | Line-by-line checklist against spec | "All requirements handled" |

## Rationalization Table

| If you think... | Then... |
|---|---|
| "Should work now" | RUN the verification. |
| "I'm confident" | Confidence is not evidence. |
| "Partial check is enough" | Partial proves nothing about the rest. |
| "Agent said success" | Verify independently. |
| "I already checked earlier" | State changes. Re-verify now. |
| "There's no test suite" | Say so explicitly. Do not claim success. |

## Rules

- Never claim completion without pasting or citing the verification output.
- If a verification command fails, that failure is the new priority.
- If you cannot run verification (no test suite, no build command), state that explicitly rather than claiming success.
- "Done" means verified. "Code written" is not "done".
