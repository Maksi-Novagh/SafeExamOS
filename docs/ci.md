# Continuous integration

Status: **active design / first implementation**

SafeExamOS uses GitHub Actions as a reproducible verification layer.

## Why CI matters here

This project is security-sensitive. A green check must describe a specific property rather than vaguely imply that the OS is secure.

The CI is therefore split into explicit levels.

## Level 1 — static checks

Workflow job: `Static checks`

Validates:

- shell script syntax;
- required documentation exists;
- mandatory build files exist;
- expected Debian packages are listed;
- Chromium is not launched with `--no-sandbox`;
- Cage is not launched with `-s` VT-switching enabled;
- UI contains the mandatory SEB-derived baseline tokens;
- obvious unrelated UI directions such as decorative gradients/glassmorphism are rejected.

This does **not** prove runtime security.

## Level 2 — ISO build

Workflow job: `Build amd64 live ISO`

Builds inside a privileged Debian 13 container on the GitHub-hosted Ubuntu runner.

Outputs:

- `SafeExamOS-amd64.iso`;
- SHA-256 file;
- GitHub Actions artifact retained for 14 days.

The job also checks that the resulting ISO contains a live filesystem, kernel and initrd.

## Level 3 — QEMU boot smoke

Workflow job: `QEMU boot smoke test`

The ISO is booted under QEMU with OVMF/UEFI.

A small systemd one-shot service in the guest emits:

```text
SAFEEXAMOS_CI_BOOT_OK
```

to the emulated serial port after the guest reaches the multi-user boot stage.

The workflow only passes if this marker appears.

### What this proves

- the produced artifact is bootable far enough to start systemd userspace;
- the embedded systemd unit can execute;
- the built filesystem is sufficiently coherent for the guest to reach that stage.

### What this does NOT prove

- Cage actually rendered a frame;
- Chromium successfully displayed the launcher;
- keyboard/mouse work in the graphical session;
- lockdown is escape-resistant;
- hardware drivers work on real computers;
- SEB compatibility;
- Secure Boot integrity.

Those require separate tests.

## Failure artifacts

When QEMU boot fails, the serial console log is uploaded as a GitHub Actions artifact.

This is intentional: boot failures should remain inspectable and reproducible.

## Security of workflow dependencies

Actions are initially referenced by major stable tags for development speed.

Before production releases, third-party actions should be pinned to audited commit SHAs and the release pipeline should use stronger provenance controls.

## Future CI levels

Planned:

- graphical VM test with screenshot comparison;
- Chromium launcher process health test;
- network pre-flight test;
- `.seb` fixture tests;
- URL-filter conformance tests;
- configuration fuzzing;
- hardware inventory fixture tests;
- arm64 emulation/build;
- reproducibility checks;
- SBOM and provenance generation.
