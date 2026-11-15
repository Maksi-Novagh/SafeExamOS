# Continuous integration

Status: **four-job green QEMU smoke baseline — 2026-11-13 (run #42)**

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

The observer checks that both processes exist and that Chromium's command line contains the launcher path. Only then does the guest emit:

```text
SAFEEXAMOS_CI_UI_OK
```

The host then asks QEMU's monitor (HMP) to capture the current virtual framebuffer to:

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


### 2026-10-28 — graphical session stopped at tty1 login

Run #10 was the first graphical smoke run to reach the SafeExamOS guest itself. The serial log showed:

```text
SAFEEXAMOS_CI_BOOT_OK
Debian GNU/Linux 13 safeexamos ttyS0
safeexamos login:
```

The live system was healthy, but the kiosk session never started because the prototype only launches `safeexamos-session` from the `exam` user's login profile, and no automatic login was configured on `tty1`.

The image now installs a systemd getty override for `tty1` using `agetty --autologin exam`. This allows the prototype's login/PAM session to start and immediately hand off to Cage and Chromium.

This is a prototype bootstrap mechanism. The production design should replace profile-based autostart with a dedicated kiosk session unit that cannot fall back to an interactive shell.


### 2026-10-28 — replaced getty/profile bootstrap with dedicated kiosk service

Run #11 still reached userspace but never produced the graphical runtime marker. The autologin/profile-based startup path was therefore replaced by an explicit systemd kiosk service.

The new flow runs `safeexamos-session` as the unprivileged `exam` user, owns `tty1`, uses PAM/logind, has a dedicated runtime directory, conflicts with the normal tty1 getty, and writes minimal lifecycle markers to the serial console.

This makes the graphical session lifecycle observable and removes shell-profile startup as a dependency.


### 2026-10-28 — stale hook reference after session-bootstrap refactor

Run #12 failed during image construction before QEMU was reached.

The old shell-profile bootstrap file had correctly been removed, but `0100-safeexamos-permissions.hook.chroot` still attempted to chmod:

```text
/etc/profile.d/90-safeexamos-session.sh
```

Because the hook runs with `set -e`, the missing file aborted `live-build`.

The stale chmod was removed. This was a refactor cleanup bug, not a runtime failure of the new systemd kiosk service.


### 2026-10-28 — first successful graphical QEMU smoke test

Run #13 was the first fully successful graphical CI run.

Validated:

- static checks passed;
- amd64 ISO build passed;
- ISO structure and checksum validation passed;
- QEMU userspace boot passed;
- `safeexamos-kiosk.service` started the graphical session;
- Cage and Chromium stayed alive;
- the launcher URL was present in Chromium's command line;
- the guest emitted `SAFEEXAMOS_CI_UI_OK`;
- QEMU captured the framebuffer to `.ci/qemu-ui/safeexamos-ui.ppm`;
- serial log and framebuffer were uploaded as CI artifacts.

This is the first automated proof that the generated SafeExamOS image can reach the graphical launcher in the QEMU test environment.


### 2026-10-28 — graphical marker path changed by runtime pre-flight launcher

Run #16 built and booted successfully, but the graphical smoke test timed out after the pre-flight integration.

The reason was a CI observer mismatch: Chromium now loads the launcher from the kiosk runtime directory (for example `/run/.../launcher/index.html`) so that `preflight.js` can be generated beside it. The CI observer still required the old static path `/usr/share/safeexamos/launcher/index.html`.

The observer now accepts the runtime launcher path suffix `/launcher/index.html`.

The session also emits `SAFEEXAMOS_PREFLIGHT_OK` or `SAFEEXAMOS_PREFLIGHT_ERROR` before Cage starts, making future collector failures directly visible in the serial log.


### 2026-10-28 — graphical QEMU exited before guest serial initialization

Run #17 built the ISO and passed the userspace smoke test, but the graphical QEMU process exited after roughly 12 seconds. The uploaded `serial.log` was zero bytes, proving that this failure occurred before the guest produced any serial diagnostics.

The graphical smoke harness previously discarded QEMU stderr. It now:

- captures QEMU stderr to `.ci/qemu-ui/qemu-stderr.log`;
- records the QEMU exit code;
- prints both host-side QEMU stderr and guest serial output on early exit;
- uploads the stderr log with the graphical evidence artifact.

This change is diagnostic only; it does not alter SafeExamOS runtime behavior.


### 2026-10-28 — first successful pre-flight + graphical integration run

Run #18 (`6920e7a9`) completed successfully end-to-end.

Validated in the same generated amd64 ISO:

- static checks;
- ISO build and structure validation;
- userspace boot smoke test;
- runtime pre-flight generation before Chromium startup;
- Cage + Chromium graphical launcher;
- graphical runtime marker;
- framebuffer capture;
- graphical evidence artifact upload.

The guest serial log contained `SAFEEXAMOS_CI_BOOT_OK` and `SAFEEXAMOS_CI_UI_OK`. QEMU stderr only contained the expected termination message from the CI harness after the successful capture.

This is the first successful CI run after integrating the live pre-flight data path into the launcher.


### 2026-10-28 — apt-recommends optimization removed live-user setup

After `--apt-recommends false` was enabled, graphical runs intermittently reached the Debian login prompt without starting the SafeExamOS kiosk. The missing dependency was `user-setup`, which had previously arrived indirectly and is required by the Debian Live configuration path that creates the configured live user.

SafeExamOS now lists `user-setup` explicitly in the amd64 package list and the static build-tree check requires it.

This is an optimization regression: the runtime feature was valid before dependency pruning, but an implicit package dependency was removed by the image-size pass.


### 2026-10-28 — optimization regression removed live user creation

After the image-size pass switched live-build to `--apt-recommends false`, graphical runs reached the Debian login prompt instead of SafeExamOS. Build and userspace boot still passed, which made the failure look like a kiosk regression.

Root cause: `user-setup` had previously arrived indirectly. With recommended packages disabled, it disappeared, and the configured Debian Live user `exam` was no longer created by the expected live-config path.

Fix:

- add `user-setup` explicitly to the SafeExamOS package list;
- require it in `scripts/check-build-tree.sh`;
- treat implicit dependencies removed by optimization as release-blocking regressions.

Runs #25 and #27 are therefore not evidence that Cage or Chromium app mode failed; they never reached the intended live-user kiosk session.

### 2026-10-28 — build-tree validator corruption

A sequence of incremental text patches corrupted `scripts/check-build-tree.sh`, duplicating fragments and producing invalid POSIX shell syntax. Runs #30 and #31 failed in static checks before any ISO build/runtime validation.

The validator was rebuilt from scratch with a single canonical structure and now checks:

- required files;
- core runtime packages, including `user-setup`;
- Chromium sandbox remains enabled;
- app-mode launcher is present;
- legacy kiosk flag is absent;
- managed browser policy exists;
- logind automatic VTs are disabled.


### 2026-10-28 — kiosk service does not reach ExecStart

Run #37 still reached userspace but emitted no `SAFEEXAMOS_SESSION_START`, even after the `exam` user was pre-created during image construction.

The remaining failure is therefore before `safeexamos-session`: systemd service activation, unit conditions, PAM/session setup, or tty ownership.

Two changes were made:

- `getty@tty1.service` is now **masked**, not merely disabled, so it cannot race with the kiosk service which explicitly conflicts with it;
- the CI boot marker now prints the `exam` user state, kiosk enabled/active/failed state, full kiosk status, kiosk journal, and tty1 getty status to the serial log.

This turns the next graphical failure into a directly diagnosable systemd failure instead of a 150-second timeout.


### 2026-10-28 — kiosk blocked inside PAM session setup

Run #38 produced the first complete kiosk diagnostic.

Confirmed:

- user `exam` exists with expected video/input/render groups;
- `safeexamos-kiosk.service` is enabled;
- the service is active;
- `getty@tty1.service` is masked;
- `safeexamos-session` still never emits `SAFEEXAMOS_SESSION_START`.

The service main process remained as `(-session)`, and the journal ended after:

```text
pam_unix(login:session): session opened for user exam
```

This shows the unit was blocked in the `PAMName=login` session setup before reaching `ExecStart`.

The kiosk is a dedicated system service already configured with `User=exam`; it does not need to emulate an interactive login session. `PAMName=login` was therefore removed. tty ownership and the unprivileged user boundary remain enforced by systemd.


### 2026-10-29 — run #39: PAM resolved, pre-flight not completed

Run #39 built the ISO and booted userspace successfully. Its kiosk unit was enabled and active, with `safeexamos-session` and `safeexamos-preflight` running. Removing `PAMName=login` therefore resolved the earlier pre-`ExecStart` stall.

The graphical marker still timed out. The service journal showed permission errors when the unprivileged `exam` process wrote directly to `/dev/ttyS0`; the collector was still running at the diagnostic snapshot. This did **not** establish that Cage or Chromium had failed.

Changes for the next run:

- session lifecycle markers now use systemd's journal, not direct privileged serial writes;
- hardware and NetworkManager probes have bounded timeouts;
- the collector creates an explicit blocking fallback before attempting optional probes, then atomically publishes successful results;
- the session has an overall collector timeout and continues to the launcher only with an available pre-flight file;
- the root-owned UI observer prints kiosk journal diagnostics at timeout;
- a manually runnable regression test simulates a hung `nmcli`.

No GitHub Actions workflow definition was changed.


### 2026-10-29 — graphical startup no longer blocks on pre-flight

Run #40 built and booted the ISO, and reached the kiosk service. Its early diagnostic showed the pre-flight collector creating a fallback snapshot; it did not prove where the collector spent the remainder of the graphical smoke timeout.

The boot path now copies a blocking snapshot from the read-only image and starts the collector asynchronously with a 14-second timeout. Cage and Chromium launch without waiting. Once the collector succeeds, it atomically replaces the runtime data and the launcher polls for updates. A failed collection leaves a blocking verdict; it must not be interpreted as exam readiness.

The privileged CI observer emits early journal diagnostics, and the host smoke timeout has been enlarged for software-emulated QEMU. No GitHub Actions workflow YAML changes were made. A fresh green run is still required to validate the new path.


### 2026-11-13 — Run #41: Cage cannot acquire DRM seat

Run #41 successfully completed static checks, ISO build, userspace boot, and the asynchronous pre-flight inventory. The kiosk logs show `SAFEEXAMOS_CAGE_START` and `SAFEEXAMOS_PREFLIGHT_OK`, but wlroots/libseat reported `Could not get primary session for user`, `Could not open tty0 ... Permission denied`, `Timeout waiting session to become active`, and `Unable to create the wlroots backend`.

The exam user is unprivileged, and the project removed its old interactive `PAMName=login` session after the earlier PAM stall. Consequently, no working session/seat broker was available to grant Cage access to the DRM and input devices. This is **not** a pre-flight or Chromium failure.

Fix prepared for the next run:

- install Debian Trixie's `seatd` and `libseat1` explicitly with recommended packages disabled;
- run the system seatd daemon as root and expose its socket only to group `video`;
- keep `exam` in group `video` and force the `seatd` libseat backend;
- order the unprivileged kiosk service after `seatd.service`, with a bounded socket readiness check;
- add build-tree checks and capture both kiosk and seatd diagnostics on failure.

No browser sandbox, DRM permission broadening, or direct root execution of Cage is introduced. A successful CI run with a rendered framebuffer is still needed to verify the fix.


### 2026-11-13 — run #42: complete green optimized QEMU baseline

- Commit: `28388848bbf78baf7acb709d5807abf0c3c1df22`.
- Workflow: [run #42](https://github.com/Maksi-Novagh/SafeExamOS/actions/runs/43408402740), **SUCCESS**, completed 2026-11-13.
- Jobs: **Static checks PASS; Build amd64 live ISO PASS; QEMU boot smoke PASS; QEMU graphical launcher smoke PASS**.
- Graphical log: `Graphical runtime marker received`, `Captured graphical framebuffer: .ci/qemu-ui/safeexamos-ui.ppm`, `QEMU graphical smoke test: PASS`.
- Artifacts: ISO + SHA-256; serial log/QEMU stderr/framebuffer evidence. GitHub currently retains these artifacts for 14 days.

Run #41 had failed at the Cage DRM/VT seat boundary: `Could not get primary session for user` and `Could not open tty0`. Run #42 incorporates a dedicated `seatd` broker for the unprivileged `exam` user and passes the graphical smoke.

**Scope:** the CI boots kernel/initrd directly from the generated ISO, with that ISO attached as the live medium. A green run verifies process startup and a valid PPM capture. It does **not** prove pixel-accurate UI, real keyboard/pointer events, UEFI bootloader handoff, persistent-state erasure, shortcut security, full SEB interoperability, or Lenovo hardware compatibility.


### 2026-11-13 — autonomous UI and pre-flight regression checks

The developer requested no manual test steps. The existing static build-tree check now executes `tests/launcher-smoke.cjs` and `tests/preflight-smoke.sh`. The first runs the launcher controller in a minimal deterministic DOM fixture and asserts the `Supported`, `Warning`, and fail-closed `Blocking` states, keyboard feedback, simulated exam-code gating, and asynchronous pre-flight refresh. The second simulates a stalled NetworkManager command and checks that the collector completes within a bounded time, generates valid JavaScript, and retains an explicitly blocking static fallback until complete.

The existing graphical QEMU harness now validates the **actual image pixels** for the launcher white panel, dark text and DodgerBlue accent; it waits for a painted screen rather than merely trusting running processes. It then sends a single benign key via QEMU monitor, captures a second screenshot, and requires a visible change. A deterministic keyboard-feedback indicator has been added to the launcher, with focus placed on the typing field. The test is intentionally modest: visual differences could have other causes and do not prove input security, keyboard-layout correctness or exam lockdown.

New scripts: `scripts/verify-framebuffer.py`, `tests/launcher-smoke.cjs`, `tests/preflight-smoke.sh`. The existing GitHub Actions YAML remains unchanged. **These new checks are not marked validated until their first green CI run.**


### 2026-11-13 — run #45: framebuffer assertion reveals compositor crash

Run #45 (https://github.com/Maksi-Novagh/SafeExamOS/actions/runs/43428686952) passed static checks, ISO build, and the QEMU userspace smoke. The strengthened graphical check then rejected a near-black framebuffer (roughly one million dark pixels; no detected white/blue launcher pixels). The observer's earlier `SAFEEXAMOS_CI_UI_OK` only meant both named processes existed temporarily; it did not mean a visible page.

The guest journal shows repeated Cage crashes with `SIGSEGV`, preceded by `EGL_NOT_INITIALIZED`, DRI2 screen creation errors and a `kms_swrast` fallback. `seatd` itself was up and accepted the unprivileged user, and asynchronous pre-flight emitted `SAFEEXAMOS_PREFLIGHT_OK`. A separate warning indicated that an OpenGL shader cache could not be created under `/home/exam`, which the kiosk's `ProtectHome=true` deliberately protects.

Remediation submitted to the next CI run:

- make the currently unvalidated accelerated wlroots path deterministic and software-rendered with the documented `WLR_RENDERER=pixman` mode;
- use a software cursor for the reference image (`WLR_NO_HARDWARE_CURSORS=1`);
- move `HOME` and `XDG_CACHE_HOME` inside the private ephemeral runtime directory, retaining `ProtectHome=true`;
- retain the framebuffer color checks and keyboard screenshot comparison as **release-blocking** tests, rather than weakening them to obtain green CI.

This is a baseline software-renderer choice for the current prototype, **not** an assertion that it is optimal on the Lenovo or that GPU acceleration is supported. A new full CI pass remains required.


### 2026-11-13 — live network refresh and focus handling (implementation; CI pending)

A physical VMware screenshot shows the launcher rendering, with a detected `ens33` NIC but NetworkManager still `connecting` and no default route. Pre-flight was previously a one-time snapshot: the browser polling logic stopped after the first successful inventory, so a delayed DHCP route would not be reflected. The session now refreshes bounded inventory every 15 seconds, and the launcher polls the local snapshot every 8 seconds without stopping on success. Failed refreshes revert atomically to an explicit blocking baseline. The typing field uses `focus({preventScroll:true})` to avoid hiding the launcher header on smaller displays.

The launcher unit fixtures now assert a live transition from an online Supported state to an offline/connecting Warning state and check that a next poll remains scheduled. This does not guarantee VMware NAT/DHCP is configured correctly, and it does not grant network access in a locked exam.


### 2026-11-14 — offline demonstration exam (implementation, CI pending)

Added local-only `demo.html` and dependency-free `demo-exam.js`. The launcher accepts the single reserved demonstration code `DEMO` and navigates to a fixed local file only when the existing pre-flight has no blocking verdict. Arbitrary/institutional codes remain unsupported; none are used to construct URLs. The demo implements four fictional questions, navigation, answered-progress, review, confirmation and local submission with in-memory answer cleanup. It has no HTTP requests, analytics, exam grading, durable answer storage or SEB interoperability claims. Separate automated Node tests cover state transitions, invalid choices, result clearing, UI navigation and discard. The existing static checks execute the tests. No Actions workflow YAML change was made.


### 2026-11-14 — SEB inspection and Chromium policy baseline (awaiting CI)

`tests/inspect-seb-smoke.py` covers gzip/plnd/gzip plist, encrypted format rejection, malformed input, and maximum size. `scripts/check-chromium-policy.py` validates the expected managed Chromium policy keys, including disabled DevTools, printing, downloads, popups, extensions and a default HTTP/HTTPS navigation block. Existing Actions YAML is unchanged. A green static check does not demonstrate that Chromium actually blocks `Ctrl+T` or that the resulting client is SEB-compatible; this must be verified with live input tests.


### 2026-11-14 — managed school-portal catalog (implementation; CI pending)

The launcher now includes a restricted pre-exam portal selector. `config/portals.json` is the administrator-owned source for supported platforms. `scripts/render-portals.py` generates both the browser-facing portal catalog and Chromium managed URL/popup exceptions. The existing static job validates their exact consistency with `--check`, rejects unrecognized/unsafe portal URLs and runs `tests/portal-policy-smoke.py` plus `tests/portal-browser-smoke.cjs`. The test data contains no passwords or login tokens. The CI does not log in to Smartschool and cannot certify arbitrary exam-provider behavior. The existing workflow YAML is unchanged.


### 2026-11-15 — isolated portal/demo supervisor (implementation, CI pending)

The kiosk now invokes an unprivileged local browser-mode supervisor from Cage. It serves the launcher on loopback and uses an explicit local token-authenticated mode transition to switch between separate ephemeral portal/demo Chromium profiles. Static fixture tests check restricted file serving, token rotation, same-origin requests and separate command-line profile directories. The existing four-job workflow is unchanged. A passing static fixture alone cannot establish a secure lockdown, live Chromium transition, or differentiated browser policies.


### 2026-11-15 — native Linux SEB lab browser foundation (CI pending)

The build now contains a **separate, optional native GTK/WebKit2GTK 4.1 application** rather than altering the existing Smartschool Chromium portal. Pure Python policy tests reject unknown settings, unsafe/non-HTTPS origins, unsupported upload/download privileges and invalid files. `scripts/check-build-tree.sh` invokes `tests/linux-seb-smoke.py` and Python syntax checks; `python3-gi`, `gir1.2-gtk-3.0` and `gir1.2-webkit2-4.1` are explicit Debian packages. A green static check will validate the policy model, not the actual GUI, network behavior or exam security. The application is not autostarted or represented as official Safe Exam Browser.

### 2026-11-15 — native Linux GTK/WebKitGTK graphical regression gate

A new, separate QEMU graphical job boots the same Debian live ISO with the explicit **`safeexamos.native_ci=1`** kernel parameter. This selects the experimental native GTK/WebKitGTK offline page, leaving normal boot on the verified Chromium Smartschool portal. The test waits for a WebKit load-finished marker, captures a framebuffer and rejects black/blank renderings with the existing `verify-framebuffer.py` color signature.

The job is not a full exam-launch or security regression test. It must pass before claiming the native GUI is operational. The existing regular QEMU boot and graphical tests remain unchanged.
