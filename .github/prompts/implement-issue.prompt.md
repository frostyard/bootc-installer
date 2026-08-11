---
description: Implement a bootc-installer issue with the required verification
---

Implement the referenced issue in `bootc-installer`.

1. Read `AGENTS.md` and the complete issue before editing.
2. Inspect the current worktree, related implementation, tests, and open pull
   requests. Preserve unrelated changes.
3. Derive explicit acceptance criteria from the issue and identify evidence for
   each one.
4. Work on a branch based on `dev`. If fisherman changes are required, commit
   and push its repository separately before updating the parent pointer.
5. Add or update tests that exercise the changed behavior, including the
   synchronization rules in `AGENTS.md`.
6. Use `skills/qualify-installer-change/SKILL.md` to select verification gates.
7. For an install-path change, obtain full installation evidence; do not claim
   unit tests prove that an installed system boots.
8. Review the final diff for scope, secrets, generated files, and unrelated
   changes. Open the pull request against `dev` and link the issue.
