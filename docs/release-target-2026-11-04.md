# Release target — 2026-11-04

Status: **historical deadline; full acceptance not achieved by 2026-11-04**

Original goal: produce a SafeExamOS prototype that is fully usable on the two reference targets and broadly usable on common amd64 PCs.

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

Hardware report helper:

```sh
./scripts/collect-hardware-report.sh
./scripts/report-runtime-metrics.sh
```

The first script captures PCI/USB IDs, drivers, DRM outputs, input handlers, network devices and power information. The second captures boot timing, memory/process usage and enabled/running services.

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


## Retrospective as of 2026-11-13

The original deadline is past. Full QEMU and Lenovo reference acceptance was **not demonstrated**, but [CI run #42](https://github.com/Maksi-Novagh/SafeExamOS/actions/runs/43408402740) passed four automated jobs on 2026-11-13 with commit `28388848`.

| Requirement | QEMU amd64 | Lenovo 82KD |
| --- | --- | --- |
| ISO construction and structure | PASS (#42) | ISO not physically booted |
| Direct-kernel userspace boot | PASS (#42) | Not tested |
| Cage/Chromium process startup and framebuffer | PASS (#42) | Not tested |
| Pre-flight and launcher interaction/typing | Not fully verified | Not tested |
| ISO bootloader/UEFI boot | Not tested by this run | Not tested |
| Clean shutdown, state destruction, restart safety | Not verified | Not verified |
| Security shortcut/escape regression | Not verified | Not verified |
| Image and runtime metrics acceptance package | Incomplete | Incomplete |

The 70% general amd64 target was an aspiration for **feature coverage**, never a measured proportion of compatible computer models. No certification is claimed. See [next steps](next-steps.md).
