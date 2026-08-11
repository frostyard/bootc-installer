# Session summary

Use this template when handing unfinished work to another session. Replace the
prompt text rather than appending secrets or raw logs.

## Objective

State the user-requested outcome and link the issue or specification.

## Current state

- Branch and base commit:
- Working-tree status, including submodule state:
- Completed changes and commits:
- Open pull requests or external runs:

## Verification evidence

List each command or runtime check, its result, and what requirement it proves.
For install-path changes, include the disposable test environment, recipe class,
complete-install result, and post-reboot verification.

## Remaining work

List unmet acceptance criteria, failing checks, review findings, and the next
safe action. Distinguish confirmed blockers from untested assumptions.

## Decisions and corrections

Record durable technical decisions with evidence. Add reusable corrections to
`.memory/corrections.jsonl` and promote repository-wide invariants to
`AGENTS.md` or regression tests.

## Sensitive data check

Confirm the summary contains no passwords, passphrases, recovery keys, tokens,
private keys, personal data, recipes with secrets, or unredacted installer logs.
