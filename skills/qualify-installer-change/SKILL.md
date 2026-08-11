---
name: qualify-installer-change
description: Select and run verification for bootc-installer changes. Use when implementing, reviewing, or preparing a pull request that changes the Python GUI, fisherman backend, recipe generation, disk or encryption behavior, post-install steps, Flatpak packaging, or tests.
---

# Qualify Installer Change

Read `AGENTS.md` first. Treat its current commands and verification requirements
as authoritative when they differ from this workflow.

## Classify the change

- **Documentation or metadata only:** validate formatting and links; run focused
  checks if the metadata affects tooling.
- **Python logic or GUI:** run Ruff, relevant unit tests, and relevant UI tests.
- **Fisherman:** run Go formatting, vet, and relevant Go tests inside
  `fisherman/fisherman`; keep its commit separate from the parent pointer update.
- **Flatpak or build inputs:** validate manifests and perform the relevant build.
- **Install path:** apply all relevant checks above and obtain complete install
  evidence as described below.

Install-path changes include default filesystems, image or recipe defaults,
recipe generation, encryption, bootloaders, partitioning, and fisherman
post-install behavior. When uncertain, classify the change as install-path.

## Run focused checks while iterating

Choose the smallest test that directly exercises each behavior while editing.
Whenever a file named in the test-synchronization rules in `AGENTS.md` changes,
update and run the paired test module.

Use the repository commands, normally:

```bash
python3 -m ruff check bootc_installer/ tests/
pytest tests/unit/ -q
xvfb-run -a pytest tests/ui/ -q
```

For fisherman changes:

```bash
cd fisherman/fisherman
gofmt -w <changed-go-files>
go vet ./...
go test ./...
```

Do not use formatting commands on unrelated files.

## Require full-install evidence

For every install-path change, run the applicable dakota-iso E2E command from
`AGENTS.md`, or perform and document an equivalent real-hardware install, reboot,
and boot verification. State exactly which path was tested, including filesystem
and encryption mode.

If the environment cannot perform the install, report the missing evidence as a
release or merge blocker. Never substitute mocked unit tests, a successful GUI
walkthrough, or a Flatpak build for this requirement.

## Audit before handoff

1. Map every acceptance criterion to direct evidence.
2. Inspect the final diff and status; exclude unrelated and generated files.
3. Confirm new Python files appear in the relevant Meson source list.
4. Confirm fisherman and parent commits are separate when both changed.
5. Record commands and outcomes accurately, distinguishing local results from CI.
6. Target the pull request at `dev` and describe any full-install evidence or
   outstanding install-test blocker.
