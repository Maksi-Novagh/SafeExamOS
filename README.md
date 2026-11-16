# SafeExamOS

**A bootable, ephemeral examination operating system designed to interoperate with the Safe Exam Browser (SEB) ecosystem.**

> [!IMPORTANT]
> SafeExamOS is an independent community project. It is **not affiliated with, endorsed by, or maintained by** Safe Exam Browser, ETH Zürich, or the SEB Alliance.

SafeExamOS explores a complementary security model for digital examinations:

> Instead of trying to lock down an arbitrary student operating system, boot a small operating system whose only purpose is to run the exam.

## Project status

**Functional graphical amd64 prototype validated in QEMU. Not ready for real examinations.**

**Roadmap progress: 24%** — `█████░░░░░░░░░░░░░░░`

> Progress is the ratio of completed roadmap milestones, **not** a security/readiness score. SafeExamOS is not yet suitable for production examinations.

Current verified milestones (latest full CI pass: [run #42, 2026-11-13](https://github.com/Maksi-Novagh/SafeExamOS/actions/runs/43408402740), commit `28388848`):

- CI-built Debian 13 amd64 ISO;
- automated QEMU userspace boot;
- automated Cage + Chromium single-app graphical launcher boot using unprivileged `exam` and the seatd broker;
- dedicated unprivileged `exam` kiosk service;
- asynchronous hardware/network pre-flight with a fail-closed initial snapshot;
- framebuffer evidence captured by CI.

Pre-exam **school portal browser MVP** (2026-11-14, CI pending): choose Smartschool and enter a school platform name to open the institution's canonical HTTPS login page. The browser allows only administratively configured portal/SSO origins under Chromium managed policy. This is **not** an unrestricted browser, not a validated Smartschool examination integration, and not a secure exam session. [Portal integration details](docs/school-portals.md).

The November 14 security baseline adds a **read-only `.seb` format inspector** and stricter Chromium managed policies (DevTools and ordinary external navigation blocked by default). These are partial defensive controls, **not SEB compatibility or full shortcut lockdown**. `Ctrl+T` and other browser/native shortcuts remain an explicitly open release blocker until live tests confirm command interception. See [SEB inspection and browser policy](docs/seb-inspection-and-browser-policy.md).

The repository remains documentation-first: implementation, tests and documentation are updated together.

Autonomous regression work (2026-11-13): deterministic pre-flight/launcher fixtures passed in run #45, but the stronger QEMU visual assertion exposed a black frame and Cage EGL crash. A software-renderer correction is pending CI validation; no visible-UI success is claimed yet. These checks do not replace real-hardware certification or proof of exam security.

The image now includes a **DEMO** offline practice exam (four fictional questions and local-only submission), with automated state/UI fixtures; full graphical validation is pending. This is not a real exam or an SEB implementation.

Pre-flight UI includes a typing-test field and a local `Supported / Warning / Blocking` prototype verdict. The graphical CI does **not** exercise keyboard interaction, inspect the UI contents, or certify verdict correctness. Interactive Wi-Fi joining and system-level keyboard-layout switching remain pending.

The original **2026-11-04** reference-acceptance deadline has passed without full completion. Run #42 verifies QEMU graphical **smoke**, not UEFI bootloader handoff, live keyboard input, clean state destruction or Lenovo hardware. See the [historical release-target checklist](docs/release-target-2026-11-04.md) and the [next validation plan](docs/next-steps.md).

## Target workflow

```text
Power on
  |
Boot SafeExamOS from USB / disk / managed device
  |
Hardware + network pre-flight
  |
Load .seb file / exam URL / institution-issued exam code
  |
Validate configuration and compatibility
  |
Enter locked exam session
  |
Exam
  |
Submit / terminate
  |
Destroy ephemeral session state
  |
Shutdown
```

## Initial platform strategy

| Platform | Status | Notes |
|---|---|---|
| x86-64 / amd64 | Tier 1 target | Primary PC build |
| ARM64 / aarch64 | Tier 1 target | SBCs and UEFI ARM64 where hardware support exists |
| ARMv7 / armhf | Tier 2 target | Legacy/low-power ARM |
| x86 / i686 | Legacy research | Debian 13 no longer has a normal i386 kernel/installer |
| RISC-V 64 | Future research | Debian 13 supports riscv64, but not a near-term exam target |

The current base candidate is **Debian 13 (Trixie)** for amd64/arm64/armhf. The 32-bit x86 story is intentionally separate.

## Proposed architecture

```text
┌────────────────────────────────────────────┐
│               SafeExamOS UI                │
│ pre-flight · network · accessibility · exam│
├────────────────────────────────────────────┤
│             Exam Session Manager           │
├─────────────┬──────────────┬───────────────┤
│ SEB config  │ Browser      │ Audit /       │
│ compatibility│ policy      │ proctoring    │
├─────────────┴──────────────┴───────────────┤
│         Privileged Policy Daemon           │
│ input · devices · display · session · IPC  │
├────────────────────────────────────────────┤
│ systemd · Wayland kiosk · Linux kernel     │
├────────────────────────────────────────────┤
│ immutable root · ephemeral writable state  │
└────────────────────────────────────────────┘
```

A minimal Wayland kiosk compositor such as Cage is being evaluated as an implementation component, **not** as the security boundary. The security boundary must be enforced by the OS image, service configuration, privilege model, device policy, browser policy, and verified session lifecycle.

## Goals

- boot into a known and reproducible exam environment;
- avoid dependence on software installed in the student's normal OS;
- support Ethernet, Wi-Fi, common keyboards, mice, touchpads and accessibility settings;
- implement a documented subset of SEB configuration semantics before claiming broader compatibility;
- investigate SEB Server interoperability;
- implement URL filtering and browser restrictions;
- provide ephemeral sessions with minimal persistent state;
- provide a hardware compatibility checker and support database;
- support event-based auditing and privacy-conscious supervision;
- build reproducible images for multiple architectures;
- design around defensive security research and responsible disclosure.

## Non-goals

SafeExamOS is **not** intended to:

- bypass Safe Exam Browser;
- provide an exam-cheating environment;
- weaken SEB security controls;
- silently keylog students;
- claim compatibility with Browser Exam Key / Config Key until behavior has been independently validated;
- claim that Linux or kiosk mode is automatically secure;
- support every computer or every ARM board.

## Research baseline

The current research snapshot is in [docs/research/2026-10-27-seb-baseline.md](docs/research/2026-10-27-seb-baseline.md).

Key upstream observations:

- current SEB Windows uses Chromium/CefSharp and sends Config Key / Browser Exam Key-related request headers;
- SEB Server can supply exam configurations and session information;
- upstream SEB already contains production screen-proctoring functionality;
- current SEB Windows has active integrity, window-monitoring, application-monitoring and remote-session defenses;
- Browser Exam Key behavior is platform-specific, so compatibility cannot be assumed across architectures.

## Documentation

- [Architecture](docs/architecture.md)
- [Threat model](docs/threat-model.md)
- [Lockdown baseline](docs/lockdown-baseline.md)
- [Escape and cheating threat catalog](docs/escape-and-cheating-catalog.md)
- [SEB compatibility plan](docs/seb-compatibility.md)
- [Hardware support strategy](docs/hardware-support.md)
- [Pre-flight subsystem](docs/preflight.md)
- [Graphical session](docs/graphical-session.md)
- [CI verification](docs/ci.md)
- [Next validation plan](docs/next-steps.md)
- [Image optimization](docs/image-optimization.md)
- [Release target — 2026-11-04](docs/release-target-2026-11-04.md)
- [Proctoring and privacy](docs/proctoring-and-privacy.md)
- [Research baseline](docs/research/2026-10-27-seb-baseline.md)
- [Roadmap](ROADMAP.md)
- [Security policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)

## Upstream references

- Safe Exam Browser: https://safeexambrowser.org/
- SEB GitHub organization: https://github.com/SafeExamBrowser
- SEB Windows: https://github.com/SafeExamBrowser/seb-win-refactoring
- SEB Server: https://github.com/SafeExamBrowser/seb-server
- SEB screen proctoring server: https://github.com/SafeExamBrowser/seb-screen-proctoring-server

## License

No project-wide license has been selected yet. Do not assume that repository contents may be redistributed under a particular license until a LICENSE file is added.

Upstream SEB repositories have their own licenses (many use MPL-2.0). SafeExamOS must respect those licenses and avoid copying upstream code without preserving the required notices and obligations.


The November 15 mode-supervisor prototype separates the school portal browser and offline DEMO into sequential Chromium processes with different temporary profiles and token-authorized local transitions. **This is not yet a secure exam mode** because system browser policies are still shared and keyboard commands remain a release blocker. [Technical details](docs/browser-mode-supervisor.md).


**Native Linux SEB client (experimental):** a separately packaged GTK 3 / WebKit2GTK 4.1 browser with strict lab-only configuration validation, exact HTTPS-origin allowlisting and in-memory WebKit context has been added. This does **not** replace the existing Smartschool Chromium portal, nor does it claim encrypted `.seb`/SEB Server/BEK/CK or a fully locked examination session. See [Native Linux SEB architecture](docs/linux-seb-client.md).

Native Linux GUI regression (2026-11-15): a separate CI-only QEMU boot path now launches the experimental GTK/WebKitGTK client with a fixed offline page and checks its rendered framebuffer. This does not change the default Chromium Smartschool session or mean SEB interoperability is complete. See [native client](docs/linux-seb-client.md).

The native Linux port now contains an **experimental managed-window prototype**: configurable 1–3 WebKitGTK browser windows with strict URL policy and a separate QEMU-only labwc stacked-window session. Normal Cage/Chromium/Smartschool boot is unchanged. This is **not** a security-enforced allowlist for arbitrary Wayland clients. [Architecture and limits](docs/linux-seb-client.md).


A strengthened QEMU multiwindow regression (2026-11-15) now checks for **two real WebKitGTK surfaces** with distinct blue/orange fixture colors and a child-specific readiness marker. This is a pending CI improvement, not proof of complete compositor lockdown. See [native Linux client](docs/linux-seb-client.md).

A seventh opt-in QEMU test now targets native WebKitGTK JavaScript popup allow/deny behavior using offline content and two distinct framebuffer markers. Pending CI verification; not an official SEB-compatible client or secure compositor boundary.
