# Cross-session reflections

This directory carries durable, non-sensitive lessons between agent sessions.
Add a short Markdown entry when a review correction, incident, or surprising
repository behavior would help a future contributor avoid repeating work.

Each entry should include the date, context, evidence, lesson, and affected
paths. State what was observed rather than inventing intent. Link an issue or
pull request when public, and remove credentials, personal data, machine
addresses, and installation recipes containing secrets.

Suggested filename: `YYYY-MM-DD-short-topic.md`.

```markdown
# Short topic

- Date: YYYY-MM-DD
- Context: issue or task
- Evidence: test, log, review, or source path
- Lesson: durable guidance
- Applies to: relevant paths or workflows
```

`AGENTS.md`, tests, and current source remain authoritative. When a reflection
conflicts with them, update or retire the reflection instead of silently
following stale guidance.
