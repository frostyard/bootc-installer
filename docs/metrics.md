# Pull-request acceptance metrics

The repository tracks whether proposed changes are accepted and how quickly
they move through review. Metrics are reviewed monthly and cover pull requests
targeting `dev`, the integration branch.

## Definitions

| Metric | Definition |
|---|---|
| Accepted PR | A non-draft PR merged into `dev` during the reporting window. |
| Rejected PR | A non-draft PR closed without merge during the reporting window. |
| Acceptance rate | `accepted / (accepted + rejected) * 100`. |
| Time to first review | Median time from PR creation to the first approving review or change request. Bot-only reviews do not count. |
| Time to merge | Median time from PR creation to merge. |
| Rework rate | Percentage of merged PRs receiving commits after the first human review. |
| Revert rate | Percentage of merged PRs reverted within 30 days. |

Draft PRs, automated dependency PRs, and PRs closed because they were replaced
by an explicitly linked successor are reported separately and excluded from the
acceptance-rate denominator. Record exclusions with their PR numbers so the
metric remains auditable.

## Monthly collection

Use GitHub's pull-request search as the source of truth. Replace the dates with
the reporting window:

```sh
gh pr list --repo frostyard/bootc-installer --base dev --state merged \
  --search 'merged:2026-08-01..2026-08-31' \
  --json number,title,author,createdAt,mergedAt,url

gh pr list --repo frostyard/bootc-installer --base dev --state closed \
  --search 'closed:2026-08-01..2026-08-31' \
  --json number,title,author,isDraft,createdAt,closedAt,mergedAt,url
```

Publish the totals, exclusions, rates, median durations, and links to the query
results in the monthly quality report or a tracking issue. Never optimize for a
higher acceptance rate by merging weak changes: the review rubric and required
CI remain the quality gates.

## Interpretation

Compare trends over multiple months rather than treating one small sample as a
target. Investigate sharp changes alongside review findings, CI failures,
reverts, and issue severity. A high acceptance rate with rising revert or
failure rates indicates weak review, not improved performance.
