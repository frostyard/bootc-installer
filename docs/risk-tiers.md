# Change risk tiers

Every pull request declares the highest applicable tier. Reviewers may raise a
tier; lowering one requires a written rationale. A small diff can still be
high-risk when it touches destructive installation behavior.

| Tier | Typical changes | Required evidence |
|---|---|---|
| 1 — Low | Documentation, comments, translations, non-executable assets | Focused review; documentation or structural checks |
| 2 — Moderate | UI behavior, refactors, packaging metadata, non-destructive automation | Relevant unit/UI tests and lint; manual behavior check where useful |
| 3 — High | Recipe generation, privileges, networking, CI permissions, authentication, data migration | Security-focused review, regression tests, failure-path evidence, and all affected CI gates |
| 4 — Critical | Partitioning, filesystems, encryption, bootloader, image installation, or post-install mutation | Tier 3 evidence plus a complete disposable-disk or hardware install and successful reboot |

## Classification rules

- Use the highest tier touched by the change, including generated or submodule
  changes.
- Treat secrets, new write permissions, and third-party workflow execution as
  at least Tier 3.
- Treat any path that can erase a disk or prevent boot as Tier 4.
- Split unrelated risk domains into separate pull requests when possible.
- Record mitigations and residual risk in the pull-request description.

Tier classification does not replace the review rubric in
[`docs/review-rubric.md`](review-rubric.md) or the install verification rules in
`AGENTS.md`.
