# SafeExamOS

**A bootable, ephemeral examination operating system designed to interoperate with the Safe Exam Browser (SEB) ecosystem.**

> [!IMPORTANT]
> SafeExamOS is an independent community project. It is **not affiliated with, endorsed by, or maintained by** Safe Exam Browser, ETH Zürich, or the SEB Alliance.

SafeExamOS explores a complementary security model for digital examinations:

> Instead of trying to lock down an arbitrary student operating system, boot a small operating system whose only purpose is to run the exam.

## Project status

**Research / architecture / functional boot prototype. Not ready for real examinations.**

**Roadmap progress: 21%** — `████░░░░░░░░░░░░░░░░`

> Progress is the ratio of completed roadmap milestones, **not** a security/readiness score. SafeExamOS is not yet suitable for production examinations.

Current verified milestones:

- CI-built Debian 13 amd64 ISO;
- automated QEMU userspace boot;
- automated Cage + Chromium graphical launcher boot;
- dedicated unprivileged `exam` kiosk service;
- local hardware/network pre-flight inventory integrated into the verified graphical boot path;
- framebuffer evidence captured by CI.

The repository remains documentation-first: implementation, tests and documentation are updated together.

Latest pre-flight work (validation pending): keyboard typing test and a local `Supported / Warning / Blocking` compatibility verdict. Interactive Wi-Fi joining and system-level keyboard-layout switching are still pending.

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
│               SafeExamOS UI               │
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
- [SEB compatibility plan](docs/seb-compatibility.md)
- [Hardware support strategy](docs/hardware-support.md)
- [Pre-flight subsystem](docs/preflight.md)
- [Graphical session](docs/graphical-session.md)
- [CI verification](docs/ci.md)
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
