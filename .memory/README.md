# Correction memory

`corrections.jsonl` stores durable, repository-specific corrections learned
from reviews, CI failures, and implementation work. Each line is an independent
JSON object with these fields:

- `date`: discovery date in `YYYY-MM-DD` format.
- `scope`: short affected area.
- `incorrect`: the disproven assumption or action.
- `correct`: the behavior future contributors should follow.
- `evidence`: repository path, issue, PR, test, or workflow proving the lesson.

Add only reusable technical corrections. Do not store chat transcripts,
personal data, recipes, passwords, recovery keys, tokens, certificates, or
unredacted installer logs. Promote corrections that establish project-wide
invariants into `AGENTS.md` or the relevant test as well.
