# Architecture

Status: **design draft**

## Design principles

1. **The kiosk UI is not the security boundary.**
2. **The exam user is unprivileged.**
3. **Writable state is ephemeral by default.**
4. **Privileged operations are small, explicit and auditable.**
5. **Configuration compatibility is versioned and testable.**
6. **Hardware failures are handled before lockdown.**
7. **Fail closed for security-critical policy, fail clearly for hardware compatibility.**
8. **Do not silently collect more proctoring data than required.**

## High-level components

### 1. Boot and image layer

Responsibilities:

- bootloader and kernel;
- read-only / immutable root filesystem;
- initramfs;
- firmware required for supported hardware;
- signed artifact metadata;
- eventual Secure Boot / measured boot support.

The first prototype may use a conventional Debian live image. Production security must not rely on the live-image defaults alone.

### 2. Pre-flight environment

A first read-only pre-flight collector is now implemented on amd64. It runs inside the unprivileged kiosk session before Chromium starts and writes local runtime data consumed by the launcher.

Current implementation reports CPU, RAM, GPU, network/default route, NetworkManager state, interfaces, keyboard layout, input count, connected DRM outputs, boot mode and ephemeral-root status.

Available **before** exam lockdown:

- network selection;
- keyboard layout;
- mouse/touchpad validation;
- display scaling;
- audio/accessibility settings when required;
- hardware compatibility scan;
- exam configuration loading.

This environment must be separate from the exam session so hardware troubleshooting does not require exposing a general desktop during an exam.

### 3. Session manager

Owns the lifecycle:

```text
PRE_FLIGHT
  -> CONFIG_VALIDATED
  -> LOCKDOWN_PREPARED
  -> EXAM_RUNNING
  -> SUBMITTING / TERMINATING
  -> SESSION_DESTROYED
  -> SHUTDOWN
```

Unexpected transitions are security events.

### 4. SEB compatibility layer

Responsibilities:

- parse supported `.seb` configuration data;
- normalize settings into SafeExamOS policy;
- reject or warn for unsupported OS-specific behavior;
- generate a machine-readable compatibility report;
- eventually interoperate with SEB Server where protocol behavior is understood.

It must never silently interpret an unknown security-sensitive key as "allowed".

### 5. Browser policy layer

Initial candidate: Debian Chromium.

Responsibilities:

- start URL;
- navigation policy;
- URL/content filtering;
- popup/secondary-window policy;
- download/upload restrictions;
- certificate handling;
- cache/cookie lifecycle;
- custom request headers only where compatibility is validated.

Browser command-line kiosk flags are convenience controls, not a complete lockdown mechanism.

### 6. Wayland kiosk layer

The amd64 prototype now uses **Cage** and launches it through `safeexamos-kiosk.service` as the unprivileged `exam` user. This path is covered by an automated QEMU graphical smoke test.

Cage is intentionally used to run a single maximized application.

SafeExamOS must additionally remove or block:

- alternate shells;
- unrestricted TTY switching;
- unexpected desktop portals;
- arbitrary process launch;
- unnecessary XWayland exposure;
- debug escape paths.

### 7. Privileged policy daemon

Proposed implementation language: **Rust**.

Reason: the daemon will process untrusted device/session events while holding privileges. Memory safety and a small dependency surface are valuable.

Potential responsibilities:

- input policy;
- device hotplug policy;
- Bluetooth profile policy;
- display/output policy;
- shutdown;
- selected network operations;
- security-event emission.

The daemon should expose a narrow authenticated local IPC API. The UI must not run as root.

### 8. Audit subsystem

Events, not raw surveillance, are the primary primitive.

Example events:

- forbidden shortcut attempted;
- device inserted/removed;
- display topology changed;
- network disconnected/reconnected;
- browser navigation blocked;
- policy daemon restarted;
- session state transition;
- integrity check failed.

Each event should have:

- monotonic timestamp;
- event type;
- severity;
- non-sensitive structured metadata;
- optional evidence reference;
- chained/signable integrity metadata for incident export.

### 9. Supervision subsystem

Optional and policy-controlled.

Potential capabilities:

- event-triggered screenshot;
- interval screenshot compatible with an upstream service where legally and technically appropriate;
- read-only live screen view.

Not planned by default:

- raw keylogging;
- hidden microphone/camera capture;
- invisible remote control.

## Base distribution decision

Primary candidate: **Debian 13 (Trixie)**.

Reasons:

- stable lifecycle;
- amd64, arm64 and armhf are supported release architectures;
- Chromium is packaged for those targets;
- large firmware/driver ecosystem;
- systemd and standard Linux security primitives;
- strong reproducibility/build tooling ecosystem.

### 32-bit x86

Debian 13 no longer provides a normal i386 kernel/installer. SafeExamOS therefore treats 32-bit x86 as a separate legacy feasibility track instead of compromising the main architecture around it.

## Open architecture questions

- live-build vs custom image pipeline;
- dm-verity / UKI / systemd-boot strategy;
- Secure Boot key ownership for community vs institution builds;
- NetworkManager vs iwd/systemd-networkd;
- Cage vs a purpose-built minimal compositor;
- Chromium sandbox constraints inside the immutable image;
- exact SEB config encryption/decryption compatibility;
- SEB Server protocol compatibility and versioning;
- compatibility-key calculation and whether upstream cooperation is required;
- update channel and rollback design.
