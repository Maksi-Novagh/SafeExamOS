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


## User-visible VMware feedback (2026-11-13)

An actual VMware Workstation boot shows the pre-flight launcher, VMware SVGA II display, six input devices, and an ephemeral live session. The NIC `ens33` exists, but no default route is established at the timestamp shown; a later DHCP result was not automatically refreshed by the previous UI. Refresh support and non-scrolling input focus have been implemented for subsequent CI verification. The next engineering gate remains reliable network setup and a local, explicitly non-production demonstration exam. Hardware model certification and virtualization detection remain deferred.


## Offline demonstration examination (2026-11-14)

The first *local-only* exam path is implemented as a separate `demo.html` and `demo-exam.js`, accessed by entering **DEMO** in the existing launcher after its current pre-flight is not Blocking. It contains four fictional multiple-choice questions, previous/next navigation, an answered count, review including unanswered questions, explicit local submission and a confirmation screen. The demo does not fetch an exam, use a server, grade a student or persist a result. Responses are kept in volatile JS memory and cleared on submission. Leaving the demo discards the page's ephemeral state. The standard exam-code flow remains intentionally unsupported. The demo is a UI and state-transition exercise, **not** an exam-security guarantee.

The existing build-tree check now runs `tests/demo-exam-smoke.cjs` alongside the launcher/pre-flight fixtures. Further evidence required: real Chromium/QEMU interaction with the demo screen, session crash/recovery/teardown and UEFI/physical boot. The original SEB integration and shortcut lockdown remain separate milestones. No new GitHub workflow is added.


## Security finding (2026-11-14)

The user observed browser shortcuts (`Ctrl+T`, `Ctrl+Shift+I`) still functioning in SafeExamOS. Blocking them is a **release-critical defect**, not a cosmetic limitation. The first mitigation adds managed Chromium policies and an L0 `.seb` inspector with fail-closed handling, but real command interception and runtime verification are not complete. See [SEB inspection and browser policy](seb-inspection-and-browser-policy.md). Do not attempt real examinations yet.


## Pre-exam school portal browser — 2026-11-14 (CI pending)

A new administrator-generated portal catalog can offer Smartschool and explicitly approved fixed-URL exam platforms. The launcher accepts a canonical Smartschool school slug or hostname and opens its HTTPS login page. Chromium keeps its default HTTP/HTTPS blocklist with only configured portal and known identity-provider exceptions. This is a **pre-exam browsing mode**, NOT a secure examination session: pop-ups and authentication redirects may be needed, and browser shortcuts such as Ctrl+T are still unresolved. External providers may need additional allowed hosts, cookies, OAuth/SSO behavior, popup handling or uploads; these have not been validated against real Smartschool accounts. See [school portal integration](school-portals.md).

Next acceptance steps: QEMU/VMware live login tests with institution consent; exact redirect/domain mapping and third-party-cookie evaluation; properly scoped exam mode with a separate browser policy/profile and verified shortcut containment. Never enter real exam credentials into CI fixtures.


## 2026-11-15 — mode-separated browser prototype

The launcher-to-DEMO transition now replaces the browser process and its temporary profile rather than navigating within the same Chromium profile. A loopback-only supervisor authorizes the transition and serves different local page sets by phase. This is a **data isolation milestone only**: the system-wide Chromium URL exceptions are still shared, and the compositor/shortcut controls remain unverified. See [browser mode supervisor](browser-mode-supervisor.md).


## Native Linux SEB application — 2026-11-15

A separate GTK/WebKit2GTK Linux client is now staged in `linux-seb/` and in the Debian live image, without replacing the verified Chromium/Smartschool UI. It offers lab configuration validation, a one-window native browser and conservative navigation restrictions. Its GUI has not yet been exercised by QEMU; the policy model is unit-tested. The next development priority is a GUI smoke plus a controlled application handoff, then official `.seb` cryptographic and SEB Server interoperability research. See [native client](linux-seb-client.md). Do not confuse this proof-of-concept with a complete Windows/macOS SEB port.
