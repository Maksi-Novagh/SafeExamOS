# SafeExamOS roadmap

This roadmap is deliberately evidence-driven. A checkbox only means the item is implemented and validated in this repository.

## Phase 0 — Research and design

- [x] Establish current upstream SEB baseline (2026-10-27)
- [x] Draft system architecture
- [x] Draft threat model
- [x] Draft hardware support tiers
- [x] Draft SEB compatibility matrix
- [x] Select Debian 13 as the primary base candidate for amd64/arm64/armhf
- [ ] Decide project-wide license
- [ ] Validate SEB configuration serialization/encryption formats
- [ ] Map every supported SEB configuration key to SafeExamOS behavior
- [ ] Document unsupported and OS-specific keys
- [ ] Validate SEB Server protocol behavior in a lab
- [ ] Validate Browser Exam Key / Config Key behavior without claiming compatibility prematurely

## Phase 1 — Bootable proof of concept

- [ ] Reproducible amd64 image build
- [ ] Read-only base system
- [ ] Ephemeral writable state
- [ ] Automatic graphical boot
- [ ] Wayland kiosk session
- [ ] Chromium kiosk
- [ ] Ethernet setup
- [ ] Wi-Fi setup
- [ ] Keyboard layout selector
- [ ] Display scaling and accessibility controls
- [ ] Clean shutdown / session destruction
- [ ] Automated boot smoke test in QEMU

## Phase 2 — Exam launcher

- [ ] Local `.seb` file selection
- [ ] URL entry
- [ ] Institution exam-code flow
- [ ] Configuration validator
- [ ] Compatibility warnings
- [ ] Start URL
- [ ] URL filter
- [ ] certificate handling
- [ ] proxy handling
- [ ] controlled downloads/uploads
- [ ] controlled secondary windows
- [ ] browser cache/cookie lifecycle

## Phase 3 — Lockdown

- [ ] Dedicated unprivileged exam user
- [ ] Privileged policy daemon with narrow IPC
- [ ] Disable alternate TTY access
- [ ] Disable shell access from the exam session
- [ ] Device hotplug policy
- [ ] USB class policy
- [ ] Bluetooth profile policy
- [ ] display/output policy
- [ ] browser process containment
- [ ] system service minimization
- [ ] signed update strategy
- [ ] measured/verified boot design
- [ ] watchdog and fail-closed recovery
- [ ] security regression tests

## Phase 4 — Hardware

- [ ] Compatibility scanner
- [ ] PCI/USB hardware report format
- [ ] Hardware support database
- [ ] amd64 Tier 1 validation matrix
- [ ] arm64 generic UEFI research
- [ ] Raspberry Pi 4 validation
- [ ] Raspberry Pi 5 validation
- [ ] armhf legacy build research
- [ ] x86 32-bit legacy feasibility decision
- [ ] software-rendering fallback
- [ ] known-good USB Ethernet/Wi-Fi fallback devices

## Phase 5 — SEB ecosystem integration

- [ ] SEB Server connectivity prototype
- [ ] exam discovery / selection flow
- [ ] server-supplied configuration flow
- [ ] connectivity heartbeat
- [ ] event model interoperability research
- [ ] Browser Exam Key compatibility decision
- [ ] Config Key compatibility decision
- [ ] upstream discussion / RFC

## Phase 6 — Audit and proctoring

- [ ] event timeline
- [ ] security-event screenshots
- [ ] configurable screenshot retention
- [ ] explicit user-visible supervision indicator
- [ ] read-only live screen supervision research
- [ ] supervisor-access audit trail
- [ ] signed incident bundle
- [ ] privacy impact / data minimization guide
- [ ] no raw keylogging by default

## Phase 7 — Release engineering

- [x] Initial GitHub Actions CI definition
- [x] Static shell/build/UI-direction checks
- [x] ISO artifact upload pipeline
- [x] QEMU smoke-test harness with serial boot marker
- [ ] First successful CI-built amd64 ISO
- [ ] First successful automated QEMU boot
- [ ] SBOM
- [ ] reproducible build evidence
- [ ] signed artifacts
- [ ] release provenance
- [ ] CVE/dependency monitoring
- [ ] documented rollback process
- [ ] public beta hardware matrix
