# Quality status

This page is the human-readable quality dashboard for bootc-installer. GitHub
Actions is the live source for individual runs; this document defines the
required signals and where to inspect them.

## Required signals

| Signal | Gate | Source |
|---|---|---|
| Python compatibility | Unit suite passes on Python 3.11 and 3.12 | `CI Matrix` workflow |
| Python unit quality | Unit tests and 51% statement-coverage floor | `Python Tests` workflow |
| GTK integration | UI suite passes against compiled GResources under Xvfb | `Python Tests` workflow |
| Fisherman backend | Go vet, tests, 20% coverage floor, and race detector | `Go Tests` workflow |
| Flatpak packaging | Production and development manifests build | `Flatpak` workflow |
| Manifest structure | Installer manifests are valid JSON with expected app ID | `Validate Flatpak Manifests` workflow |
| Real installation | Scheduled Bootcrew install/boot qualification | `Nightly Tests` workflow and E2E evidence |

Inspect current runs at:

- <https://github.com/frostyard/bootc-installer/actions>
- <https://github.com/frostyard/bootc-installer/pulls>
- <https://github.com/frostyard/bootc-installer/issues>

## Release readiness

A candidate is not ready when a required check is failing or missing. Changes
to the install path additionally require evidence of a complete installation
and successful boot as described in `AGENTS.md`; green unit and UI tests do not
replace that qualification.

Review these trends monthly with `docs/metrics.md`:

- PR acceptance, rejection, rework, and revert rates.
- Median time to first human review and merge.
- Required-check failure causes and flaky-test frequency.
- Coverage floors and meaningful new regression coverage.
- E2E scenario pass rate, including encrypted and offline installs.
- Escaped defects discovered after merge or release.

Create an issue for degraded signals, name an owner, and link remediation PRs.
Do not hide regressions by lowering thresholds or reclassifying required checks
without a documented maintainer decision.
