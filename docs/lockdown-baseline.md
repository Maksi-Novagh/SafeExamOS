# Lockdown baseline

Status: **implemented baseline, validation in progress**

This document records security controls already present in the prototype. It is not a claim that SafeExamOS is escape-proof.

## Browser surface

SafeExamOS launches Chromium as a single application surface rather than a normal tabbed browser window.

Managed Chromium policies currently disable:

- guest profiles;
- adding browser profiles;
- password saving;
- background browser processes;
- bookmark editing;
- browser file-selection dialogs;
- persistent "always allow" external-protocol choices;
- profile picker on startup.

These policies are machine-managed JSON under:

```text
/etc/chromium/policies/managed/
```

The policy directory is part of the read-only image and is not writable by the exam user.

## Session and console surface

The image currently:

- does not auto-spawn virtual terminals;
- reserves no alternate VT through logind;
- masks gettys on tty2 through tty6;
- masks the serial getty;
- masks `debug-shell.service`;
- masks `ctrl-alt-del.target`;
- runs the graphical session as the unprivileged `exam` user;
- uses a seatd broker with a socket restricted to the `video` group instead of launching Cage as root;
- restarts the kiosk service on failure;
- applies `NoNewPrivileges`;
- uses a private `/tmp`;
- protects the user's home from the service;
- prevents writes to kernel tunables/modules/cgroups through the kiosk service;
- forbids acquiring SUID/SGID privilege;
- locks process personality changes;
- forbids realtime scheduling;
- applies a restrictive `077` umask.

## Remaining critical work

The following are still not considered solved:

- compositor/policy-level blocking of forbidden keyboard shortcuts;
- proof that browser exit cannot expose any usable console on physical hardware;
- restricted URL/navigation policy;
- controlled upload/download flows;
- device hotplug enforcement;
- explicit session teardown;
- local privileged policy daemon;
- security regression automation for shortcut attempts.

The defensive threat catalog in `docs/escape-and-cheating-catalog.md` remains the authoritative backlog.


## 2026-11-13 QEMU evidence

[Run #42](https://github.com/Maksi-Novagh/SafeExamOS/actions/runs/43408402740) passed the graphical smoke and captured a framebuffer after the seatd correction. It **does not** validate the shortcut restrictions, TTY escape resistance, storage erasure, device hotplug or physical hardware.

## 2026-11-16 — Wayland cross-UID confinement regression

The kiosk service already owns a private systemd `RuntimeDirectory=safeexamos-exam` with mode `0700`, running as the unprivileged `exam` UID. A dedicated opt-in QEMU regression with `safeexamos.wayland_acl_ci=1` now tests the *actual* Wayland Unix-domain socket: the authorized `exam` UID must connect, while an unrelated `nobody` UID must fail. The probe also rejects a runtime directory with the wrong owner or permissions. The CI check requires both the socket marker and a visible graphical framebuffer, rather than trusting a static configuration check.

**Threat-model scope:** cross-UID filesystem/DAC isolation only. A same-UID process can still open that socket; neither Cage nor labwc is an authenticated per-client broker. Root, malicious exam-UID processes, compromised browser processes, kernel attacks and compositor shortcuts remain outside this test. This must not be described as complete Wayland confinement. Rollback: remove the opt-in test hook and CI job without changing the normal kiosk service.

## 2026-11-16 — read-only filesystem sandbox for kiosk process tree

The `safeexamos-kiosk.service` now sets `ProtectSystem=strict` in addition to its existing `NoNewPrivileges`, `PrivateTmp` and `ProtectHome` settings. The operating system's root filesystem is mounted read-only inside the service's mount namespace; browser state stays in the explicitly private runtime directory under `/run/safeexamos-exam`, while systemd's private temporary directory remains writable. The change applies to Cage, the mode supervisor and child browsers and is subject to all existing graphical/QEMU regression jobs. It is a defense in depth against accidental or compromised-process writes to system files, *not* a per-process Wayland socket policy.

**Known limitations:** the compositor and browser still execute as the `exam` UID and can reach sockets available to that UID. Root, kernel and firmware compromise are not covered; read-only mounts alone do not mean a verified immutable boot chain. If CI reveals a legitimate filesystem write dependency, add a narrowly scoped writable path rather than turning off the sandbox globally. Reverting `ProtectSystem=strict` restores the previous behavior.
