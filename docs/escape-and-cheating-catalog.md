# Escape and cheating threat catalog

Status: **defensive research backlog**

Purpose: enumerate ways a candidate might try to leave, weaken, bypass, misuse, or work around the SafeExamOS exam session so each class can later receive a reproducible regression test and mitigation.

This document is intentionally **non-operational**. It names attack classes and expected security properties; it does not provide exploit recipes, payloads, bypass sequences, or instructions for defeating real examination systems.

## Perspectives used

The catalog is reviewed from three perspectives:

- **opportunistic candidate** — tries obvious shortcuts, UI tricks, peripherals and reboots;
- **advanced attacker** — understands browsers, Linux, hardware, networking and virtualization;
- **security engineer** — assumes every boundary can fail and asks what happens next.

## Severity model

- **Critical** — can expose a shell/general desktop, arbitrary applications, persistent privileged control, or protected exam material.
- **High** — can access unrestricted web/content, external communications, additional displays/devices, or bypass a major exam restriction.
- **Medium** — leaks useful information, weakens controls, or enables limited assistance.
- **Low** — nuisance, denial of service, confusing UX, or evidence-quality issue.

## A. Browser and launcher escape surface

- [ ] Browser-native new-tab shortcuts.
- [ ] Browser-native new-window shortcuts.
- [ ] Browser close-window/tab shortcuts.
- [ ] Open-file shortcuts and file pickers.
- [ ] Save-page / save-as flows.
- [ ] Print / print-preview surfaces.
- [ ] Find/address/location focus shortcuts.
- [ ] History/downloads/bookmarks/settings pages.
- [ ] Developer-tools entry points.
- [ ] View-source and internal browser pages.
- [ ] Chromium error pages exposing extra navigation.
- [ ] Context-menu actions.
- [ ] Middle-click / modifier-click opening secondary surfaces.
- [ ] Drag-and-drop URLs/files into the browser.
- [ ] Clipboard paste of arbitrary URLs.
- [ ] JavaScript-created windows, popups and dialogs.
- [ ] Links with `target=_blank`.
- [ ] Protocol-handler navigation.
- [ ] `file:`, `data:`, `blob:`, `about:`, `chrome:` and other special schemes.
- [ ] PDF viewer escape surfaces.
- [ ] Media viewer/download helper surfaces.
- [ ] Authentication popups and external identity-provider flows.
- [ ] Certificate-error interstitials.
- [ ] Captive-portal/browser-login flows.
- [ ] Browser crash pages.
- [ ] Browser restart/session-restore reopening unintended content.
- [ ] Browser extension/component surfaces if any are present.
- [ ] Spellcheck/translation/search integrations causing external requests.
- [ ] Password-manager/autofill UI.
- [ ] Web-share/open-in-external-app integrations.
- [ ] Accessibility browser UI exposing unintended commands.
- [ ] Fullscreen transitions that reveal compositor/background.
- [ ] Browser child-process crash causing fallback UI.
- [ ] Browser RCE escaping browser policy while remaining unprivileged.
- [ ] Chromium sandbox escape.
- [ ] Browser profile manipulation if writable state becomes attacker-controlled.

## B. Keyboard and input escape surface

- [ ] `Ctrl+W`, `Ctrl+T`, `Ctrl+N`, `Ctrl+O`, `F6`, `Alt+F4` and equivalents.
- [ ] OS/session shortcuts such as VT switching.
- [ ] SysRq combinations.
- [ ] Function-key firmware/vendor shortcuts.
- [ ] Alt/Super/Meta combinations handled below the browser.
- [ ] Compose/dead-key/IME behavior invoking extra UI.
- [ ] Sticky Keys / accessibility shortcut surfaces.
- [ ] On-screen keyboard invoking desktop components.
- [ ] Multimedia keys launching external handlers.
- [ ] Programmable keyboard/macropad sending unusual sequences.
- [ ] USB HID devices impersonating keyboard/mouse.
- [ ] Composite HID devices.
- [ ] Barcode scanners / presentation remotes acting as HID.
- [ ] Mouse extra buttons mapped to browser navigation.
- [ ] Touch gestures invoking system UI.
- [ ] Touchscreen edge gestures.
- [ ] Trackpad multi-finger gestures.
- [ ] Stylus buttons invoking helpers.
- [ ] Input-device hotplug changing policy after pre-flight.

## C. Wayland/compositor/session escape

- [ ] Cage exit exposing a TTY.
- [ ] Chromium exit exposing a TTY.
- [ ] Repeated Chromium crash causing service fallback.
- [ ] Kiosk-service crash/restart race.
- [ ] Alternate getty becoming available.
- [ ] Alternate TTY access.
- [ ] User-switching/session-switching.
- [ ] Unexpected desktop portal activation.
- [ ] XWayland availability enabling extra clients.
- [ ] Arbitrary Wayland client launch.
- [ ] Clipboard/primary-selection leakage between processes.
- [ ] Screenshot/screencopy protocol exposure.
- [ ] Remote-desktop Wayland protocol exposure.
- [ ] Virtual-keyboard protocol exposure.
- [ ] Layer-shell clients covering/spoofing the exam UI.
- [ ] Session bus services exposing launch/open APIs.
- [ ] D-Bus activation of unintended applications.
- [ ] PAM/login fallback behavior.
- [ ] systemd user services starting unexpected programs.
- [ ] Environment variables altering browser/compositor behavior.
- [ ] PATH or executable replacement in writable locations.

## D. Shell, process and local privilege escape

- [ ] Reachable shell binaries from any UI surface.
- [ ] Terminal emulator accidentally installed/reachable.
- [ ] File manager accidentally installed/reachable.
- [ ] Text editor with shell/plugin integration.
- [ ] Browser-opened external application.
- [ ] Helper application invocation.
- [ ] Script interpreters exposed to the exam user.
- [ ] Package-manager tools usable by the exam user.
- [ ] Sudo/polkit misconfiguration.
- [ ] Setuid/setgid binaries not required by SafeExamOS.
- [ ] Linux capabilities on unnecessary binaries.
- [ ] Writable systemd unit/drop-in locations.
- [ ] Writable executable directories.
- [ ] Unsafe temporary-file handling.
- [ ] Environment injection into privileged helpers.
- [ ] D-Bus authorization mistakes.
- [ ] Narrow policy daemon becoming a confused deputy.
- [ ] Command injection in local IPC.
- [ ] Path traversal in local IPC.
- [ ] TOCTOU issues between validation and privileged action.
- [ ] Kernel local privilege escalation.
- [ ] Driver vulnerabilities reachable from candidate-controlled devices.
- [ ] Browser-to-root exploit chain.
- [ ] Debug/profiling interfaces left enabled.
- [ ] `ptrace` access between exam-user processes.
- [ ] Core dumps leaking exam/session data.

## E. Networking and communications

- [ ] Unrestricted Internet access outside allowed exam destinations.
- [ ] Direct-IP navigation bypassing hostname policy.
- [ ] Alternate DNS resolvers.
- [ ] DNS-over-HTTPS / DNS-over-TLS bypass.
- [ ] IPv6 bypass when only IPv4 policy is enforced.
- [ ] Proxy configuration bypass.
- [ ] PAC/WPAD abuse.
- [ ] Captive portal escape.
- [ ] Local-network services reachable during exam.
- [ ] mDNS/LLMNR discovery.
- [ ] SSH/RDP/VNC clients accidentally present.
- [ ] Browser-based remote-desktop tools.
- [ ] WebRTC peer-to-peer communication.
- [ ] WebSocket tunnels.
- [ ] VPN/tunnel software accidentally present.
- [ ] USB Ethernet added after lockdown.
- [ ] Bluetooth PAN networking.
- [ ] Phone tethering.
- [ ] Wi-Fi hotspot switching.
- [ ] Multiple active interfaces defeating route policy.
- [ ] MAC randomization conflicting with institution controls.
- [ ] DNS rebinding against local services.
- [ ] Access to local router/admin interfaces.
- [ ] Exfiltration through allowed domains/services.
- [ ] Messaging/social tools embedded in allowed web applications.
- [ ] Cloud-storage access from allowed pages.
- [ ] Search-engine access from error/help pages.
- [ ] Time/NTP manipulation affecting policy or logs.
- [ ] TLS interception/certificate injection.
- [ ] Candidate-installed CA material.
- [ ] Network namespace escape/misconfiguration.

## F. Files, storage and persistence

- [ ] Internal disks mounted automatically.
- [ ] Existing host partitions readable.
- [ ] Existing host partitions writable.
- [ ] USB mass storage mounted.
- [ ] SD-card storage mounted.
- [ ] MTP/PTP phone storage.
- [ ] Browser upload dialogs accessing arbitrary files.
- [ ] Browser downloads written to persistent media.
- [ ] Crash dumps persisted.
- [ ] Browser cache/cookies persisted across reboot.
- [ ] LocalStorage/IndexedDB persisted across sessions.
- [ ] Service logs persisting exam content.
- [ ] Swap storing sensitive data.
- [ ] Hibernate image storing session state.
- [ ] EFI variables used as unintended persistence.
- [ ] Writable boot partition.
- [ ] Candidate-planted files loaded automatically next boot.
- [ ] Autorun-like behavior from removable media.
- [ ] Symlink/hardlink tricks into approved export paths.
- [ ] Archive extraction path traversal.
- [ ] Filename/protocol-handler abuse.
- [ ] Approved export path used as a covert data channel.

## G. Displays and visual exfiltration

- [ ] External HDMI/DisplayPort monitor.
- [ ] USB-C display/dock.
- [ ] DisplayLink/USB graphics.
- [ ] Wireless display/Miracast.
- [ ] Multiple DRM connectors becoming active after lockdown.
- [ ] Projector duplication/extension.
- [ ] EDID hotplug changes.
- [ ] Virtual display drivers.
- [ ] Screen capture APIs.
- [ ] Browser screen-share APIs.
- [ ] Screenshots saved locally.
- [ ] Screen recording.
- [ ] External camera photographing the screen.
- [ ] Privacy-screen assumptions failing on wide-angle displays.
- [ ] Brightness/display rotation tricks hiding supervision UI.

## H. USB and peripheral abuse

- [ ] Mass storage.
- [ ] HID injection.
- [ ] Composite HID + storage.
- [ ] USB network adapters.
- [ ] USB Wi-Fi adapters.
- [ ] Smartphones over USB.
- [ ] USB serial adapters.
- [ ] USB debug/JTAG-like devices.
- [ ] Vendor-specific USB interfaces.
- [ ] Audio devices carrying data.
- [ ] Cameras.
- [ ] Printers.
- [ ] Smartcard readers.
- [ ] Security tokens with browser integration.
- [ ] Thunderbolt/USB4 DMA-capable devices.
- [ ] Docks exposing multiple hidden device classes.
- [ ] Hotplug race during policy initialization.

## I. Bluetooth and wireless peripherals

- [ ] Bluetooth keyboard/mouse introduced after pre-flight.
- [ ] Bluetooth PAN/networking.
- [ ] Bluetooth file transfer.
- [ ] Bluetooth audio used for external assistance.
- [ ] Bluetooth serial profile.
- [ ] Nearby-device pairing dialogs.
- [ ] Previously paired trusted devices reconnecting automatically.
- [ ] Proprietary wireless dongles appearing as HID/network devices.
- [ ] Wireless presentation remotes.
- [ ] Headsets with microphones where audio is prohibited.

## J. Audio, camera and sensor abuse

- [ ] Microphone used for external communication.
- [ ] Speakers/headphones used to receive assistance.
- [ ] Webcam access outside exam policy.
- [ ] Camera QR-code scanning to transfer information.
- [ ] Ambient-light/proximity sensors triggering system UI.
- [ ] Accelerometer/orientation changes.
- [ ] Fingerprint/biometric helper launching external UI.
- [ ] Voice assistants.
- [ ] Bluetooth headset voice assistant buttons.

## K. Boot, firmware and recovery

- [ ] Booting a different OS instead of SafeExamOS.
- [ ] Changing boot order.
- [ ] Editing kernel command line.
- [ ] Recovery/rescue boot entries.
- [ ] Single-user/emergency targets.
- [ ] Initramfs emergency shell.
- [ ] Bootloader console.
- [ ] Secure Boot disabled where institution policy expects it.
- [ ] Unsigned modified image.
- [ ] Modified initramfs/rootfs.
- [ ] Writable USB boot media altered by candidate.
- [ ] Firmware setup hotkeys.
- [ ] OEM recovery environment.
- [ ] PXE/network boot.
- [ ] External disk boot.
- [ ] Firmware-provided shell.
- [ ] Malicious or compromised firmware.
- [ ] TPM/measured-boot policy mismatch.

## L. Power, suspend and reset behavior

- [ ] Suspend/resume escaping session assumptions.
- [ ] Hibernate persistence.
- [ ] Lid-close behavior.
- [ ] Power-button menu.
- [ ] Magic SysRq/reboot.
- [ ] Forced power cycle.
- [ ] Battery removal/critical-battery shutdown.
- [ ] AC disconnect causing power-policy UI.
- [ ] Resume with changed devices/display/network.
- [ ] RTC/time reset.
- [ ] Watchdog failure exposing recovery UI.

## M. Virtualization and emulation

- [ ] SafeExamOS running inside QEMU/KVM.
- [ ] VMware.
- [ ] VirtualBox.
- [ ] Hyper-V.
- [ ] Xen.
- [ ] Nested virtualization.
- [ ] Candidate-controlled hypervisor beneath SafeExamOS.
- [ ] Virtual USB/device injection.
- [ ] Virtual serial/clipboard channels.
- [ ] Shared folders.
- [ ] Host-to-guest clipboard.
- [ ] Host screen capture.
- [ ] Host automation injecting input.
- [ ] VM snapshots restoring exam state.
- [ ] VM clock manipulation.
- [ ] Hypervisor network adapters bypassing intended hardware assumptions.
- [ ] Hypervisor hiding virtualization indicators.
- [ ] False-positive virtualization detection on real hardware.

Future policy should classify the environment as `bare-metal`, `virtualized`, `container`, or `unknown` with confidence/evidence rather than relying on one boolean signal.

## N. Exam configuration and policy parsing

- [ ] Unknown security-sensitive setting silently ignored.
- [ ] Malformed configuration causing fail-open behavior.
- [ ] Type confusion/default-value mistakes.
- [ ] Duplicate/conflicting keys.
- [ ] Unsupported OS-specific option misinterpreted.
- [ ] URL-filter precedence bugs.
- [ ] Wildcard/regex mistakes.
- [ ] IDN/punycode hostname confusion.
- [ ] URL canonicalization differences.
- [ ] Redirect chains escaping allowlists.
- [ ] Mixed HTTP/HTTPS policy mistakes.
- [ ] Certificate pinning/config mistakes.
- [ ] Proxy-policy mismatch.
- [ ] Start-URL parsing ambiguity.
- [ ] Configuration downgrade.
- [ ] Old cached configuration reused.
- [ ] Unsigned/untrusted configuration accepted.
- [ ] Browser Exam Key / Config Key compatibility assumptions creating fail-open behavior.

## O. Web application and content-layer cheating

- [ ] Exam page itself exposes unrestricted links.
- [ ] Search boxes embedded in allowed content.
- [ ] External images/content revealing information.
- [ ] Embedded chat/help widgets.
- [ ] AI assistants embedded in permitted sites.
- [ ] Copy/paste between exam questions and external allowed tools.
- [ ] Browser translation or dictionary services.
- [ ] Spellcheck sending content externally.
- [ ] Accessibility tools exposing content to external services.
- [ ] Web developer APIs exposing local/system information unexpectedly.
- [ ] Cross-origin iframe escape through allowed third-party domains.
- [ ] OAuth/SSO flows leading to unrestricted provider pages.
- [ ] Error/help/documentation links reaching general web content.

## P. Human and out-of-band cheating

These are outside a purely technical lockdown boundary but must exist in the threat model.

- [ ] Second phone/tablet/laptop.
- [ ] Smartwatch.
- [ ] Earbuds/headset receiving assistance.
- [ ] Printed notes.
- [ ] Another person in the room.
- [ ] Camera pointed at the exam screen.
- [ ] Off-screen displays or mirrored output.
- [ ] Remote human assistance before/after session.
- [ ] Memorized/encoded information on permitted physical objects.
- [ ] Social-engineering the supervisor.
- [ ] Sharing exam credentials/session links.
- [ ] Shoulder surfing another candidate.
- [ ] Coordinated timing/signaling between candidates.

SafeExamOS cannot solve all of these alone. Institution policy, supervision and exam design remain necessary.

## Q. Audit, evidence and monitoring weaknesses

- [ ] Candidate can delete or alter local logs.
- [ ] Clock manipulation makes event ordering unreliable.
- [ ] Logs omit failed policy actions.
- [ ] Logs contain sensitive typed content unnecessarily.
- [ ] Screenshot evidence misses the relevant moment.
- [ ] Evidence queue can be exhausted.
- [ ] Disk/RAM pressure disables audit.
- [ ] Network loss silently drops evidence.
- [ ] Supervisor access is not itself audited.
- [ ] Supervision indicator can be hidden/spoofed.
- [ ] Evidence exported without integrity metadata.
- [ ] Duplicate/replayed events confuse incident review.
- [ ] Privacy controls accidentally weaken security-critical auditing.

## R. Denial of service and fail-open behavior

- [ ] Repeatedly crash Chromium.
- [ ] Repeatedly crash Cage.
- [ ] Exhaust memory.
- [ ] Exhaust file descriptors.
- [ ] Fill tmpfs.
- [ ] Trigger GPU reset.
- [ ] Trigger NetworkManager restart.
- [ ] Remove/reinsert critical input device.
- [ ] Disconnect display.
- [ ] Network flap.
- [ ] DNS failure.
- [ ] Certificate failure.
- [ ] Corrupt local runtime state.
- [ ] Trigger watchdog/recovery.
- [ ] Cause a helper to time out.
- [ ] Abuse any recovery path that exposes unrestricted controls.

Security requirement: failures should be **fail-closed and recoverable**, not fail-open into a shell/desktop.

## S. Supply-chain and update attacks

- [ ] Compromised Debian package.
- [ ] Compromised firmware package.
- [ ] Malicious dependency.
- [ ] Compromised GitHub Action.
- [ ] Compromised build runner.
- [ ] Replaced release artifact.
- [ ] Unsigned update.
- [ ] Rollback to vulnerable image.
- [ ] Dependency confusion.
- [ ] Typosquatted package/tool.
- [ ] Compromised upstream browser build.
- [ ] Stale Chromium with known vulnerabilities.
- [ ] Institution distributing an unverified USB image.

## T. Privacy-driven security conflicts

- [ ] Overly invasive monitoring encourages users/institutions to disable security features.
- [ ] Raw keylogging captures passwords or unrelated content.
- [ ] Excessive screenshot retention creates a high-value data target.
- [ ] Webcam/microphone collection exceeds exam need.
- [ ] Privacy prompts interrupt or weaken lockdown.
- [ ] Data retention differs from documented policy.
- [ ] Remote-control capability is hidden inside supervision tooling.

## Regression-test rule

Every item that receives a mitigation should eventually gain:

1. a test identifier;
2. an expected policy result;
3. a reproducible lab attempt;
4. expected evidence;
5. a PASS/FAIL result;
6. the SafeExamOS version/image tested.

Items remain unchecked until both implementation **and validation** exist.

## Priority order

Recommended implementation order:

1. browser/session escape shortcuts and fail-closed kiosk lifecycle;
2. TTY/shell/process escape;
3. browser navigation/protocol restrictions;
4. networking and file/storage boundaries;
5. device/display hotplug;
6. ephemeral-state verification;
7. boot-chain integrity;
8. virtualization/environment policy;
9. audit integrity;
10. broader hardware and physical/out-of-band controls.
