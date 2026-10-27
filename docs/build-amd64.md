# amd64 live-image prototype

Status: **implementation draft**

## Goal

Boot directly into a SafeExamOS-styled launcher without installing or depending on the host operating system.

## Technology choices

- **Debian 13 / live-build** for the first declarative live image.
- **Cage** as the initial single-application Wayland compositor. SafeExamOS does not pass Cage's `-s` option, which is the option that enables VT switching.
- **Chromium** as the first browser target. Sharing a Chromium family with SEB Windows does not imply SEB compatibility.
- **NetworkManager** for Ethernet/Wi-Fi pre-flight support.

## Boot flow

```text
UEFI/BIOS
  -> Debian live boot
  -> live-config exam user
  -> tty1 session
  -> profile.d SafeExamOS autostart
  -> safeexamos-session
  -> Cage
  -> Chromium kiosk
  -> local launcher
```

## Persistence model

The first prototype relies on Debian Live's ephemeral overlay and explicitly puts the Chromium profile below `/run/user/<uid>/safeexamos-chromium`.

This must later be hardened and tested for downloads, crash dumps, swap, caches and approved exports.

## Current hardening

- Chromium runs unprivileged;
- no full desktop is installed;
- SysRq is disabled;
- kernel pointer visibility and dmesg access are restricted;
- Cage is launched without VT-switch permission.

This is **not** a complete lockdown.

## UI

The launcher follows `docs/design-system.md`: #F0F0F0 utility background, white panels, DodgerBlue accent/focus, LightBlue hover, black primary text, DimGray secondary text and a Segoe UI-compatible font stack. No SEB logo asset is embedded.

## Reproducibility caveat

The source configuration is reproducible, but package repositories are not yet snapshot-pinned, so builds at different dates are not expected to be bit-for-bit identical.

## First smoke-test checklist

- [ ] build succeeds on Debian 13 amd64
- [ ] ISO boots under UEFI QEMU
- [ ] tty1 reaches SafeExamOS session
- [ ] Cage starts
- [ ] Chromium starts
- [ ] launcher renders
- [ ] keyboard and pointer work
- [ ] NetworkManager sees virtual Ethernet
- [ ] browser crash does not expose a general desktop
- [ ] reboot destroys browser runtime state

Any failure must be documented before these boxes are checked.
