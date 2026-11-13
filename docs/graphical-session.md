# Graphical session bootstrap

Status: **prototype implementation**

## Purpose

SafeExamOS must enter its launcher directly after boot without exposing a normal login prompt or depending on shell startup files.

## Current flow

```text
systemd
  -> safeexamos-kiosk.service
  -> system seatd daemon (root; restricted video-group socket)
  -> unprivileged exam kiosk session
  -> dedicated XDG runtime directory
  -> /usr/local/bin/safeexamos-session
  -> Cage
  -> Chromium kiosk
  -> SafeExamOS launcher
```

## Why the design changed

The first prototype used:

```text
getty -> autologin -> profile.d -> safeexamos-session
```

That proved fragile in automated graphical boots. The guest could reach userspace while the graphical session never started, and failures were difficult to distinguish from login/getty behavior.

The kiosk is now an explicit systemd service.

## Service properties

`safeexamos-kiosk.service`:

- runs as the unprivileged `exam` user;
- uses a dedicated seatd broker instead of an interactive PAM login;
- reserves `tty1` for the graphical surface;
- conflicts with the normal `getty@tty1` prompt;
- receives a private runtime directory;
- starts only the SafeExamOS session command;
- restarts on failure;
- does not intentionally fall back to an interactive shell.

## Runtime diagnostics

The session writes minimal CI/debug lifecycle markers to the serial console:

```text
SAFEEXAMOS_SESSION_START
SAFEEXAMOS_SESSION_USER=...
SAFEEXAMOS_SESSION_ERROR ...
```

These markers contain no exam content or user input. They exist to make boot/session failures diagnosable.

## Graphical CI success condition

The CI observer waits for:

- `cage`;
- `chromium`;
- Chromium command line containing the local SafeExamOS launcher URL.

Only then is `SAFEEXAMOS_CI_UI_OK` emitted.

## Security direction

The systemd kiosk service is closer to the intended production architecture than shell-profile autostart because the lifecycle and failure policy are explicit.

Further hardening is still required:

- dedicated seat/device policy;
- explicit capability and syscall restrictions;
- read-only service filesystem protections;
- watchdog/fail-closed screen;
- no fallback console;
- production removal of CI-only markers.


## Graphical-first startup

The session copies the launcher and a fail-closed default pre-flight snapshot into the private runtime directory, starts bounded hardware probes in the background, and immediately runs Cage with Chromium. No pre-flight operation may hold up the initial graphical window. A completed inventory can update the existing launcher; a failed inventory leaves the exam blocked.


## Seat/DRM access (2026-11-13)

The earlier graphical test reached Cage but failed with libseat errors because `exam` did not have a functional seat/session broker. Debian's `seatd` package now supplies a system daemon; a small systemd drop-in fixes socket ownership to group `video`. The kiosk unit requires `seatd.service` and sets `LIBSEAT_BACKEND=seatd`, while remaining `User=exam` with `NoNewPrivileges=true` and its existing service sandbox.

Before starting Cage, `safeexamos-seat-ready` checks that `/run/seatd.sock` is accessible to the unprivileged service account, failing closed with an explicit diagnostic otherwise. Do not make the socket world-writable or run the browser as root. Changes still require a green QEMU graphical smoke test and physical hardware validation.

Reference: Cage project's systemd boot documentation and Debian's seatd package/man page.
