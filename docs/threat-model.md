# Threat model

Status: **initial draft**

SafeExamOS is a security-sensitive examination environment. This threat model defines what we are trying to protect before implementation begins.

## Assets

- exam questions and protected resources;
- integrity of student submissions;
- exam configuration and policy;
- session credentials/tokens;
- Browser Exam Key / Config Key-related material if supported;
- proctoring evidence;
- server credentials;
- integrity of the SafeExamOS image;
- privacy of the student.

## Adversaries

### A. Exam candidate with physical access

Assume the candidate can:

- press arbitrary key combinations;
- connect/disconnect USB and Bluetooth devices;
- connect external displays;
- attempt to switch TTY/session;
- reboot or power-cycle the computer;
- manipulate network connectivity;
- prepare local disks before boot;
- use unusual HID devices;
- inspect public SafeExamOS source code.

This is the primary adversary model.

### B. Malicious local peripheral

Examples:

- programmable HID;
- USB storage pretending to expose multiple interfaces;
- USB network adapter;
- Bluetooth composite device.

### C. Network attacker

May attempt:

- DNS spoofing;
- TLS interception;
- captive portal manipulation;
- denial of service;
- malicious local-network services.

### D. Malicious or compromised exam content

The browser may render attacker-controlled HTML/JS. Browser compromise must not automatically become root compromise.

### E. Supply-chain attacker

May target:

- build dependencies;
- GitHub Actions;
- package repositories;
- firmware packages;
- release artifacts.

## Security goals

- the exam user cannot reach a general-purpose desktop or shell through normal interfaces;
- arbitrary local applications cannot be launched;
- browser escape does not directly grant privileged OS control;
- unsupported devices are blocked or surfaced according to policy;
- writable session state is destroyed at the end of an exam;
- system files cannot be persistently modified from the exam session;
- network communication uses authenticated TLS where expected;
- security policy cannot be silently weakened by unknown config keys;
- audit logs are tamper-evident enough to support incident review;
- proctoring is visible and data-minimized.

## Explicit non-goals for the first releases

The project will **not** initially claim protection against:

- compromised firmware/UEFI;
- malicious hardware implants;
- a hostile hypervisor beneath SafeExamOS;
- CPU/platform management-engine compromise;
- destructive denial of service by physically powering off the machine;
- all side-channel attacks;
- sophisticated attacks requiring invasive hardware modification.

These can be revisited for managed institutional hardware.

## Major attack surfaces

### Boot chain

Risks:

- modified kernel/initramfs/rootfs;
- boot parameters weakening policy;
- alternate boot entry.

Mitigations planned:

- signed artifacts;
- immutable root;
- locked-down kernel command line for managed installs;
- Secure Boot / measured boot design.

### Browser

Risks:

- browser RCE;
- downloads;
- protocol handlers;
- external application launch;
- unrestricted devtools;
- sandbox weakening.

Mitigations planned:

- current security-supported browser;
- Chromium sandbox enabled;
- restricted protocols;
- minimal writable profile;
- no unnecessary integration with host services;
- fast browser security updates.

### Wayland/session

Risks:

- compositor exit exposing TTY;
- alternate session launch;
- desktop portal abuse;
- debug shortcuts;
- browser-native shortcuts opening new tabs/windows or closing the exam surface (`Ctrl+T`, `Ctrl+N`, `Ctrl+W`, `Ctrl+O`, `F6`, `Alt+F4`, and equivalents).

Mitigations planned:

- dedicated session;
- no general desktop;
- TTY policy;
- service restart/fail-closed behavior;
- no debug escape paths in production images;
- single-surface Chromium app mode as an interim reduction;
- compositor/policy-level interception of forbidden shortcuts;
- regression tests proving forbidden shortcuts cannot create, close, or escape the exam surface.

### Privileged daemon / IPC

Risks:

- confused deputy;
- command injection;
- untrusted data parsing;
- authorization mistakes.

Mitigations planned:

- small API;
- typed messages;
- unprivileged UI;
- strict state machine;
- no shell command concatenation;
- fuzzing and unit tests.

### Devices

Risks:

- new network path;
- storage exfiltration;
- composite HID;
- external display;
- programmable peripherals.

Mitigations planned:

- device-class policy;
- hotplug event handling;
- explicit Bluetooth profile policy;
- display topology enforcement;
- logging.

### Persistence

Risks:

- data left on disk;
- candidate plants files for later session;
- persistent browser cache.

Mitigations planned:

- tmpfs/ephemeral home;
- read-only base;
- explicit approved export paths only;
- session teardown verification.

## Privacy threats

Security controls can themselves become abusive.

SafeExamOS therefore treats these as threats too:

- hidden keylogging;
- unnecessary webcam/microphone collection;
- indefinite screenshot retention;
- supervisors viewing screens without audit;
- collecting credentials typed outside the exam context.

See [proctoring-and-privacy.md](proctoring-and-privacy.md).

## Escape and cheating catalog

The exhaustive defensive backlog lives in [escape-and-cheating-catalog.md](escape-and-cheating-catalog.md). It enumerates browser, session, device, network, storage, boot, virtualization, physical and audit attack classes without providing operational bypass instructions.

## Testing model

Security tests should be written as reproducible lab tests:

- expected policy;
- attack attempt;
- expected result;
- evidence;
- regression test.

Responsible-disclosure findings affecting upstream SEB should be reported privately before publication when appropriate.
