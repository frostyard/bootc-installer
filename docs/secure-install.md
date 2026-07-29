# Snosi Secure Install

Snosi schema-1 secure installation is selected only by explicit image catalog
metadata. It is never inferred from an image name or registry reference.

## Product configuration

Dakota's host-visible `images.json` must set `secure_install: true` on the
`cayo`, `snow`, and `snowfield` image nodes (or their common parent). The
installer inherits that setting for nested leaves and emits Fisherman's API
object:

```json
{
  "secureInstall": {
    "recoveryKeyFile": "/host-visible/ephemeral-recovery-file",
    "mokPasswordFile": "/host-visible/ephemeral-mok-password-file"
  },
  "cosignPubKey": "/usr/lib/snosi/cosign.pub"
}
```

The installer creates both parent-managed files beside each other with mode
`0600` and one link. The recovery file contains the selected recovery
passphrase as UTF-8 bytes without stripping a trailing newline. The MOK file
contains a cryptographically random, one-time, 16-character ASCII-alphanumeric
MokManager password. The recipe contains only their paths, never either secret.
Both parent-created files are removed after Fisherman exits, on cancellation,
and if recipe generation fails. The secrets are not written into Fisherman
recipes, logs, progress events, or provenance.
On startup it may remove a crash-leftover only when it is a regular, unlinked,
mode-0600 generated file older than 24 hours; active files, symlinks, and
caller-owned paths are retained.

Secure metadata forces the automatic layout, Btrfs, composefs, systemd-boot,
and `luks-passphrase` recipe mode. It disables a separate `/var` disk and blocks
progress unless UEFI Secure Boot and TPM 2.0 are available. Fisherman validates
the remaining contract before it writes the disk. Secure installs always use the
selected remote registry image for both `image` and `targetImgref`; they never
substitute an NVIDIA or `containers-storage:` local ISO source.
The destructive confirmation explicitly warns that MokManager approval is
required on the next boot.

## Post-install and recovery

After a successful secure install the GUI separately acknowledges any displayed
LUKS recovery key and the required next-boot MokManager enrollment. Before it
deletes its generated MOK file, the parent retains its generated password only
in process memory for this post-success page. The password is selectable and
the operator must acknowledge recording it before continuing; acknowledgement
clears the displayed and retained value. Enter it when MokManager requests the
MOK enrollment password on the next boot.

For an external autoinstall recipe, `secureInstall.mokPasswordFile` remains
caller-owned. The parent neither reads, displays, nor deletes it. The MOK page
instead tells the operator to use the password supplied by the autoinstall
operator.

There is no established operations UI. Use Fisherman's narrowly-scoped CLI
operations with a raw, byte-exact recovery credential file:

```sh
fisherman secure-restage-mok <target-root> <recovery-key-file>
fisherman secure-repair-esp <target-root> <recovery-key-file>
```

The restage operation only repeats MOK staging. ESP repair authenticates the
existing encrypted root and replaces only the validated secure second stage.
