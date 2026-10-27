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

The exact kernel and initrd are extracted from the built ISO and booted directly under QEMU while the same ISO remains attached as the live medium.

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

- graphical screenshot comparison against an approved reference;
- network pre-flight test;
- `.seb` fixture tests;
- URL-filter conformance tests;
- configuration fuzzing;
- hardware inventory fixture tests;
- arm64 emulation/build;
- reproducibility checks;
- SBOM and provenance generation.


## CI incident notes

### 2026-10-27 — ISO verifier false negatives

The first two amd64 build runs successfully produced an ISO, but the verification step failed for tooling reasons:

1. the first verifier used an invalid `xorriso -find ... -print` form for the runner's xorriso version;
2. the second verifier assumed exact path formatting from a generic ISO tree listing and produced another false negative.

The verifier now queries `/live` directly with `xorriso -ls /live` and checks for the live filesystem, kernel and initrd by filename class.

Lesson: CI checks must validate the intended property with the narrowest stable interface available, and build success must be distinguished from verifier failure.


### 2026-10-27 — checksum path false negative

The ISO structure check then passed and showed the expected live filesystem, kernel and initrd. The job still failed because the generated SHA-256 file contained the absolute build-container path (`/workspace/...`). The verification step runs from the artifact directory, where that absolute path does not exist.

The build now creates the checksum from inside the output directory so the checksum file contains only `SafeExamOS-amd64.iso`. This keeps the checksum portable between the build container, GitHub artifact storage and the verification job.


### 2026-10-27 — UEFI serial smoke test stalled before kernel handoff

Run #6 successfully completed the static checks, built the ISO, verified the ISO structure and uploaded the artifact. The QEMU smoke test then timed out.

The serial log showed OVMF loading and starting the SafeExamOS DVD boot entry, but no kernel output or SafeExamOS marker. This means the test was blocked in the graphical/bootloader path before the Linux kernel took over the serial console.

To avoid conflating two different properties, CI now separates them conceptually:

- the ISO verifier confirms that the image contains the expected bootable hybrid structure, live filesystem, kernel and initrd;
- the QEMU userspace smoke test extracts the exact kernel and initrd from that ISO and boots them directly with the ISO attached as the live medium.

This proves that the produced SafeExamOS live filesystem can reach systemd userspace and emit the CI marker. It does **not** by itself prove that the graphical UEFI boot menu automatically reaches the kernel. A dedicated UEFI/bootloader automation test remains a separate future milestone.


## Level 4 — graphical launcher smoke

Workflow job: `QEMU graphical launcher smoke test`

This test boots the exact kernel/initrd from the generated ISO with a virtual VGA device and the ISO attached as the live medium. Inside the guest, a CI-only observer waits for both:

- `cage`;
- `chromium`.

They must remain alive across consecutive checks. Only then does the guest emit:

```text
SAFEEXAMOS_CI_UI_OK
```

The host then asks QEMU through QMP to capture the current virtual framebuffer to:

```text
.ci/safeexamos-launcher.ppm
```

The serial log and framebuffer capture are uploaded as CI artifacts.

### What a PASS proves

A green graphical smoke test proves that, in the QEMU test environment:

- the live system reaches the normal exam-user session;
- Cage starts and remains alive;
- Chromium starts and remains alive;
- a graphical framebuffer exists and can be captured.

### What a PASS still does not prove

It does not yet prove:

- pixel-perfect visual conformity with the SEB design reference;
- keyboard and pointer interaction inside the launcher;
- automatic boot through the ISO's UEFI/bootloader menu;
- lockdown resistance;
- real-hardware GPU/input compatibility.

Pixel comparison and input automation are separate follow-up tests.

The UI marker is a CI observer only. It does not weaken the production session or provide a shell/remote-control interface.


### 2026-10-27 — graphical smoke test dependency failure

Run #8 did not reach the guest graphical session. The host-side graphical smoke script exited immediately because `socat`, used to communicate with QEMU's QMP socket, was not installed on the GitHub-hosted runner.

This was a CI dependency omission, not a SafeExamOS graphical runtime failure.

The graphical job now installs `socat` explicitly together with QEMU and xorriso before starting the VM.


### 2026-10-27 — graphical smoke test image-conversion dependency failure

Run #9 again stopped before starting QEMU because the host-side script required ImageMagick's `convert` and `identify` commands.

Those tools were unnecessary for the property being tested: QEMU's `screendump` command already writes a PPM framebuffer image directly. The graphical smoke test now validates the PPM header itself and uploads that raw capture, removing the ImageMagick dependency entirely.

This keeps the CI surface smaller and avoids another host-tooling false negative.
