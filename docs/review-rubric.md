# Pull-request review rubric

Reviewers evaluate correctness, safety, verification, maintainability, and
traceability. Findings come before summaries and must cite the affected file or
behavior.

## Finding severity

| Severity | Meaning | Merge effect |
|---|---|---|
| Critical | Can destroy the wrong disk, expose credentials, bypass secure-install guarantees, or make installed systems unbootable. | Block. Require a fix and complete install evidence. |
| High | Breaks a supported install path, recipe contract, sandbox boundary, or required CI/release behavior. | Block. Require regression coverage and proportional runtime evidence. |
| Medium | Incorrect edge behavior, missing validation, cleanup leak, compatibility regression, or materially weak test coverage. | Block unless a maintainer documents why follow-up is safe. |
| Low | Maintainability, diagnostics, or documentation defect with no current correctness impact. | May follow up if tracked and explicitly accepted. |

## Review checklist

### Contract and scope

- The PR links its issue and implements every acceptance criterion.
- The diff is focused; unrelated generated files and submodule changes are absent.
- Recipe/schema changes preserve backward compatibility or document migration.
- User-visible strings, assets, Meson sources, and translations stay in sync.

### Installer safety

- Target-disk selection is explicit and validated before destructive work.
- Errors preserve cleanup of mounts, mappers, scratch paths, and credentials.
- Flatpak/host boundaries use the established `flatpak-spawn --host` contracts.
- Secure-install changes remain fail-closed and do not log secret material.
- Bootloader, partition, filesystem, encryption, or post-install changes include
  a complete disposable-disk/VM install and successful reboot result.

### Verification

- New behavior and invalid inputs have regression tests at the correct layer.
- Python unit, GTK UI, Go, lint, coverage, and manifest gates relevant to the
  change pass.
- Tests do not rely on ambient host state without an explicit skip condition.
- Evidence is direct: a mocked GUI test does not prove the disk install path.

### Maintainability and operations

- Failure messages are actionable without exposing secrets.
- CI permissions are least-privilege and external actions are version-pinned.
- New operational behavior has diagnostics and rollback/recovery guidance.
- Documentation and quality metrics are updated when contracts change.

## Decision

Approve only when no blocking finding remains and the evidence matches the
risk. Use “request changes” for Critical, High, and unresolved Medium findings.
If verification cannot be performed, state the missing evidence and leave the
PR unapproved rather than inferring success.
