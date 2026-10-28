# Release target — 2026-11-04

Status: **active development target**

Goal: produce a SafeExamOS prototype that is fully usable on the two reference targets and broadly usable on common amd64 PCs.

## Reference target A — QEMU amd64

Target state: **100% of the prototype acceptance checklist**

Required:

- ISO builds successfully;
- direct-kernel QEMU userspace smoke passes;
- graphical Cage + Chromium smoke passes;
- pre-flight data is generated;
- keyboard typing test works;
- network status is visible;
- local exam launcher renders;
- runtime state is ephemeral;
- browser restart does not expose a general desktop;
- clean shutdown path exists;
- image metrics are recorded.

## Reference target B — Lenovo V15 G2 ALC (82KD)

Target state: **100% of the prototype acceptance checklist**

Known baseline:

- amd64;
- AMD Ryzen 5 5500U;
- integrated Radeon/Vega graphics;
- 20 GiB RAM on the development machine.

Still to discover on physical hardware before certification:

- exact Wi-Fi PCI ID;
- exact Ethernet controller, if present;
- touchpad/input IDs;
- firmware/UEFI behavior;
- DRM connector behavior;
- battery/power reporting.

Required physical validation:

- UEFI boot;
- internal display;
- keyboard;
- touchpad;
- Wi-Fi;
- audio if exam policy requires it;
- suspend disabled/controlled during exams;
- AC/battery status readable;
- Chromium hardware acceleration or safe software fallback;
- no general desktop/shell exposed;
- session destruction on shutdown/reboot.

No component is marked certified until its actual PCI/USB IDs are collected from the machine.

## General amd64 compatibility target — 70%

The 70% target is **feature coverage for ordinary amd64 PCs**, not a claim that 70% of every PC model in existence is certified.

Expected baseline coverage:

- UEFI amd64 boot;
- standard USB keyboards and mice;
- common laptop touchpads exposed through Linux input;
- Intel/AMD integrated graphics with DRM/KMS;
- Ethernet through standard Linux drivers;
- common Intel/Realtek/Atheros/MediaTek Wi-Fi families covered by shipped firmware;
- DHCP networking;
- Chromium software-rendering fallback;
- common 1920x1080 and laptop display modes.

Allowed gaps at this stage:

- unusual discrete GPUs;
- proprietary vendor hotkeys;
- fingerprint readers;
- WWAN/LTE;
- niche USB devices;
- vendor-specific RGB/control software;
- exotic ARM devices;
- uncommon Wi-Fi chips without redistributable firmware.

## Release blockers

A reference-target release is blocked if any of these fail:

- cannot boot;
- no usable display;
- no usable keyboard/pointer;
- Chromium cannot launch with sandbox enabled;
- browser exit exposes an unrestricted shell or desktop;
- no network path where networking is required;
- pre-flight crashes the kiosk;
- session persistence leaks exam/browser state across reboot;
- critical regression is undocumented.

## Optimization gate

Image-size optimization is allowed only if both reference targets remain green.

For every optimization batch record:

- ISO size;
- squashfs size;
- package count;
- enabled systemd services;
- boot-to-launcher time;
- idle memory usage;
- QEMU result;
- Lenovo physical result.

If an optimization breaks the Lenovo target or the VM, revert it before continuing.
