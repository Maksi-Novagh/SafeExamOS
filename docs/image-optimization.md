# Image optimization strategy

Status: **active, conservative optimization pass**

SafeExamOS should be as small as practical without trading away exam reliability, hardware compatibility, browser sandboxing or diagnosability.

## Rule: measure before aggressive removal

The project optimizes in layers.

### Layer 1 — safe build-time reductions

Implemented:

- disable APT recommended packages unless explicitly required;
- disable source-archive inclusion;
- omit installed man pages and info pages;
- omit most package documentation while preserving copyright/license files;
- remove APT package lists and downloaded package archives from the final live filesystem;
- remove temporary build/runtime files.

These changes should not alter the runtime feature set.

### Layer 2 — service minimization

Planned after the image remains stable:

- inventory enabled systemd units;
- disable services not required for boot, networking, input, graphics or exam runtime;
- verify that disabling each service does not break QEMU and physical hardware.

### Layer 3 — package and firmware pruning

Planned only with hardware evidence:

- remove packages not used by the kiosk, browser, network, pre-flight or boot path;
- split optional diagnostics from the production image;
- evaluate firmware by hardware-support tier instead of deleting broad firmware families blindly.

Wi-Fi firmware is intentionally not aggressively pruned yet. Missing firmware discovered at exam time is worse than a somewhat larger ISO.

### Layer 4 — browser/runtime optimization

Future work:

- evaluate Chromium language/resource payload;
- disable/remove features not used by SafeExamOS where packaging permits;
- measure cold-start time and resident memory;
- keep the Chromium sandbox fully enabled.

## Non-goals

Optimization must not:

- disable Chromium sandboxing;
- remove CA certificates;
- remove firmware before a support matrix exists;
- remove NetworkManager or Wi-Fi support;
- remove input/display diagnostics needed by pre-flight;
- make failures harder to diagnose during development.

## Measurements to record

For every optimization milestone, record:

- ISO size;
- squashfs size;
- boot-to-launcher time;
- launcher memory usage;
- installed package count;
- enabled systemd unit count;
- graphical smoke result;
- hardware regressions, if any.

The current project should prefer a slightly larger reliable image over an aggressively stripped image that only works in QEMU.


## Measurement tool

Use:

```sh
./scripts/report-image-metrics.sh build/amd64/out/SafeExamOS-amd64.iso
```

The report currently records:

- ISO bytes/MiB;
- SquashFS bytes/MiB;
- package-entry count from `/live/filesystem.packages`.

Boot timing, memory and enabled-service measurements will be added as runtime metrics once the optimized image has been validated.
