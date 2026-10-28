# Hardware support strategy

SafeExamOS will not claim to run on "every computer". It will publish measurable support tiers and detect problems before the exam starts.

## Architecture tiers

### Tier 1

- amd64 / x86-64
- arm64 where the platform has a supported boot path and Linux hardware support

### Tier 2

- armhf / ARMv7
- specific certified SBCs

### Legacy research

- i686 / 32-bit x86

Debian 13 no longer ships a normal i386 kernel/installer, so a 32-bit x86 build would require a separate base/build strategy. Debian 12 LTS remains a possible temporary research base but is time-limited and should not dictate the main project architecture.

## Device support model

### Certified

A concrete model has been tested with a released SafeExamOS image.

### Supported

All critical devices have known in-kernel/firmware support and automated pre-flight passes.

### Compatible

Expected to work using standard Linux drivers, but not validated by the project.

### Limited

Boots, but one or more non-critical capabilities are unavailable.

### Unsupported

A critical component such as display, input, boot, or network is not functional.

## Pre-flight inventory

A first local collector is implemented in `/usr/local/sbin/safeexamos-preflight`. It currently detects a subset of the target inventory and displays it in the launcher. It is detection-only; configuration/repair actions come later.

Before lockdown, the target inventory is:

- CPU architecture/model;
- firmware/UEFI mode;
- RAM;
- GPU/DRM driver;
- display outputs;
- keyboard and input layout;
- pointer/touchpad/touchscreen;
- Ethernet;
- Wi-Fi chipset and driver/firmware;
- Bluetooth controller;
- audio if required;
- USB devices;
- battery/AC state where relevant.

The report should prefer hardware IDs over marketing names:

- PCI vendor/device IDs;
- USB VID/PID;
- modalias;
- loaded kernel module;
- firmware load failures.

## Wi-Fi

Wi-Fi is expected to be one of the most frequent compatibility problems.

Strategy:

1. ship a broad but legally redistributable firmware set;
2. identify chipset and loaded driver during pre-flight;
3. detect firmware failures from the kernel log;
4. provide a clear fallback path:
   - Ethernet;
   - known-good USB Ethernet;
   - known-good supported USB Wi-Fi;
   - spare institution device.

Never discover a missing Wi-Fi driver for the first time after exam lockdown.

## Keyboard layouts

Support should be independent from physical keyboard model whenever it is a standard HID keyboard.

Pre-flight UI should provide:

- layout selector;
- typing test;
- dead-key test;
- modifier-key test.

Changing layout is an accessibility/input function and should not expose a desktop.

## Bluetooth

Bluetooth support and Bluetooth permission are different concepts.

Suggested exam policy levels:

- disabled;
- input devices only;
- approved profiles/devices.

File-transfer, PAN/networking and other unnecessary profiles should be disabled for strict exam sessions.

## USB

Use device/interface class policy rather than "USB on/off".

Typical policy examples:

- HID keyboard: allow;
- HID mouse: allow;
- mass storage: block after configuration load unless explicitly required;
- USB network: institution policy;
- camera: only if an exam explicitly requires it;
- vendor-specific interfaces: review/block by default in strict mode.

Composite devices must be evaluated per interface.

## Graphics

The browser must have a software-rendering fallback.

An examination should not fail solely because GPU acceleration is unavailable. Hardware acceleration should remain optional unless a specific assessment requires it.

## ARM warning

"ARM64" is not a single hardware platform.

Raspberry Pi, generic UEFI ARM servers/laptops, Qualcomm laptops and Apple Silicon have different boot and driver realities. Support will therefore be certified by concrete platform family, not architecture string alone.

## Hardware database

Proposed record:

```json
{
  "hardware_id": "pci:8086:51f0",
  "class": "wifi",
  "status": "supported",
  "driver": "iwlwifi",
  "firmware": ["..."],
  "architectures": ["amd64"],
  "tested_images": ["..."],
  "notes": "..."
}
```

Community reports should never automatically become "certified" without reproducible validation.


## Implemented pre-flight subset

Current amd64 prototype:

- CPU model and architecture;
- kernel version;
- total RAM;
- first detected PCI graphics/display controller;
- default route and NetworkManager state;
- network interface names;
- Wi-Fi interface names;
- configured keyboard layout;
- Linux input-device count;
- connected DRM output count/names;
- UEFI vs legacy BIOS detection;
- basic ephemeral-root detection.

The collector deliberately does not yet classify a device as certified/supported/unsupported. That requires the hardware support database and policy layer.


## Reference profiles

Machine-specific validation data lives under `hardware/profiles/`.

Current reference profiles:

- `qemu-amd64.json`: automated virtual reference target;
- `lenovo-v15-g2-alc-82kd.json`: physical development target.

The Lenovo profile intentionally leaves Wi-Fi, Ethernet, input and DRM identifiers unknown until they are collected from SafeExamOS running on the actual laptop. Marketing-model assumptions are not accepted as certification evidence.
