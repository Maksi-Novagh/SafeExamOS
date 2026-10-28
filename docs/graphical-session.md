# Graphical session bootstrap

Status: **prototype implementation**

## Purpose

SafeExamOS must enter the exam launcher automatically after boot without exposing a normal login workflow.

The current prototype uses a dedicated live user named `exam` and an automatic local login on `tty1`.

## Flow

```text
systemd
  -> getty@tty1
  -> agetty --autologin exam
  -> PAM/login session
  -> /etc/profile.d/90-safeexamos-session.sh
  -> /usr/local/bin/safeexamos-session
  -> Cage
  -> Chromium kiosk
  -> SafeExamOS launcher
```

## Why this is required

The initial graphical CI run reached userspace successfully but stopped at the login prompt. The kiosk launcher was only started from the `exam` user's login profile, so without an automatic `tty1` login neither Cage nor Chromium could ever start.

## Security note

This autologin is not equivalent to granting a shell in the final design.

In the current prototype, the user session still begins through a normal login/PAM path and immediately replaces the shell with the SafeExamOS graphical session on `tty1`.

Before production use, the prototype profile-based bootstrap should be replaced with a dedicated systemd/logind-managed kiosk session whose failure behavior is explicit and does not fall back to an interactive shell.

## Current CI expectation

The graphical smoke test waits until:

- `cage` is running;
- `chromium` is running;
- both remain alive for consecutive checks.

Only then does the guest emit `SAFEEXAMOS_CI_UI_OK`.
