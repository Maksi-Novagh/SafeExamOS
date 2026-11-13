# Next validation plan — 2026-11-13

Status: **prioritized engineering plan, not a release certification**

## Baseline

The latest fully successful four-job CI baseline is [run #42](https://github.com/Maksi-Novagh/SafeExamOS/actions/runs/43408402740), commit `28388848`: static checks, Debian 13 amd64 ISO build, QEMU direct-kernel userspace boot, and a graphical Cage/Chromium smoke with captured framebuffer.

The GUI and browser are running in QEMU. That is not evidence of safe interactive input, reliable real-hardware operation, complete exam lockdown, or actual interoperability with SEB.

## Priority 0 — Record a stable regression baseline

- Preserve the run #42 artifact, SHA-256, serial diagnostics and framebuffer as the known-good reference.
- Measure ISO/SquashFS size, installed package count, enabled services, boot-to-launcher time and memory use.
- Make the QEMU graphical test assert visible launcher content, rather than just detecting processes and a valid PPM header (implementation added 2026-11-13; CI validation pending).
- Add deterministic collector/UI fixture tests, especially failure of NetworkManager and the fail-closed pre-flight state (implementation added 2026-11-13; CI validation pending).
- Avoid further aggressive dependency pruning until both reference environments are checked.

**Done when:** evidence is reproducible, and boot/UI tests detect a blank or broken launcher.

## Priority 1 — Validate Lenovo V15 G2 ALC (82KD) in a lab

- Boot the verified ISO from removable media without overwriting Windows or the internal disk.
- Test actual firmware boot, built-in display, keyboard, typing field, touchpad, Wi-Fi and wired network if available.
- Capture real PCI/USB identifiers, driver/firmware status, DRM outputs and power information; do not infer chipset IDs from product marketing names.
- Verify clean shutdown, reboot and hardware compatibility, then update the Lenovo hardware profile using observed results only.
- Test a safe graphics fallback where hardware acceleration fails.

**Done when:** a completed hardware checklist with reproducible evidence exists; critical unknowns remain clearly unvalidated.

## Priority 2 — Session lifecycle and reliability

- Specify a minimal state machine: PRE_FLIGHT → CONFIG_VALIDATED → EXAM_RUNNING → TERMINATING → DESTROYED.
- Implement authorized exit/shutdown without revealing a general desktop or terminal.
- Verify browser/compositor crash behavior, recovery/restarts, loss of display/network/input and safe failure handling.
- Confirm no sensitive browser/session state survives reboot unexpectedly.
- Test the ISO's UEFI/bootloader handoff separately from direct-kernel QEMU.

**Done when:** tests document PASS/FAIL for shutdown, fresh boot, recovery, and state cleanup.

## Priority 3 — Defensive lockdown test suite

- Turn the [escape and cheating threat catalog](escape-and-cheating-catalog.md) into safe, lab-only test identifiers with expected blocked/allowed outcomes.
- Test browser shortcuts, alternate windows, file dialogs, console/VT switching, device hotplug and input policy at the OS/compositor boundary.
- Keep Cage/Chromium unprivileged and their sandbox enabled; verify seatd permissions remain minimal.
- Do not claim a secure exam environment until high-risk bypass classes have reproducible mitigation and regression evidence.

**Done when:** defined, scoped regression results are recorded and critical failures are addressed.

## Priority 4 — First controlled exam integration

- Support one explicitly documented exam configuration or URL workflow.
- Validate supported and unsupported .seb settings without silently ignoring security-sensitive keys.
- Apply navigation, popup, download/upload and lifecycle restrictions.
- Run a complete mock exam from pre-flight through submission and state cleanup.
- Treat SEB Server, Browser Exam Key and Config Key compatibility as research until independently proven.

**Done when:** a lab-only end-to-end mock exam passes without claiming broad SEB compatibility.

## Deferred work and evidence discipline

Virtualization detection remains deferred, as previously requested; QEMU is a valid laboratory reference. ARM images, production proctoring, commercial deployment and certification remain outside this immediate validation cycle.

**Recommendation:** start with Priority 0's framebuffer/UI assertions and input validation, then proceed to the physical Lenovo test. These provide far more useful confidence than implementing the full threat catalog before confirming the basic user interactions.
