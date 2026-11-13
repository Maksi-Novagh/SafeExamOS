# Pre-flight subsystem

Status: **first functional implementation**

## Purpose

The pre-flight stage detects whether the current machine is suitable to enter an exam before lockdown begins.

The first implementation is intentionally read-only: it **detects and reports** hardware/network state but does not yet change Wi-Fi networks, keyboard layouts, display scale or accessibility settings.

## Collector

Executable:

```text
/usr/local/sbin/safeexamos-preflight
```

The kiosk starts the bounded collector **asynchronously** and does not wait for it before launching Cage/Chromium.

The collector writes a small JavaScript data file into the private runtime launcher directory. The browser then reads that local data without exposing an HTTP service or privileged IPC endpoint.

## Current data

- CPU model;
- architecture;
- kernel;
- RAM;
- GPU/display controller;
- default route;
- NetworkManager state;
- network interfaces;
- Wi-Fi interfaces;
- configured keyboard layout;
- number of Linux input devices;
- connected DRM outputs;
- BIOS/UEFI mode;
- whether the root filesystem appears ephemeral.

## UI behavior

The launcher uses the current SEB-derived design language and shows:

- explicit status text;
- check/warning indicators;
- real device/system details;
- an overall readiness state.

The prototype currently displays local `Supported / Warning / Blocking` heuristics, but they are not hardware certification. A missing/degraded collector remains **Blocking**.

## Privacy

The pre-flight data stays local in the current prototype.

It does not collect:

- typed exam content;
- user files;
- browser history;
- webcam/microphone data;
- serial numbers intended to identify the student.

Future server reporting must define a data-minimized schema before any hardware report leaves the device.

## Next steps

- Wi-Fi scan and selection UI;
- keyboard layout selector (a typing field exists; real input validation remains pending);
- display scaling;
- accessibility controls;
- machine-readable hardware support classifications;
- PCI/USB identifiers for compatibility matching;
- validated policy beyond the current prototype `Supported / Warning / Blocking` heuristics;
- automated fixture tests for the collector.


## CI validation

The pre-flight integration is now covered by the graphical QEMU smoke path.

Run #18 on 2026-10-28 successfully booted the generated amd64 image, generated the runtime launcher data, started Cage and Chromium, reached the launcher and captured the framebuffer.

The session installs a conservative, image-provided fallback `preflight.js` and launches the graphical UI before the optional probes finish. A graphical smoke PASS does **not** imply all probes completed or that the readiness verdict is accurate.


## Startup resilience (2026-10-29)

The session installs a **degraded, blocking** snapshot before the collector runs; the collector atomically replaces it on successful completion. Individual potentially blocking commands have time limits; the kiosk wrapper enforces a maximum time for the full collection. A slow or unavailable NetworkManager must not leave the launcher on a blank screen. A degraded snapshot cannot be considered ready to start a real examination.

Diagnostics are sent to the systemd journal; the unprivileged kiosk does not write directly to `/dev/ttyS0`.

Run the standalone smoke test manually with `sh tests/preflight-smoke.sh`. This is not yet part of the Actions workflow.


## Non-blocking startup and fail-closed state

The kiosk session installs a read-only-image-provided `preflight.js` with `collectorStatus: "degraded"` before starting the browser. This default is intentionally **Blocking**, not a readiness pass. The collector starts asynchronously under a 14-second timeout; on success it atomically updates the runtime pre-flight file. The launcher refreshes the local file to display the new status. Incomplete or failed collection must remain blocking. This design allows the graphical UI to appear even when NetworkManager is unavailable or a hardware probe stalls.


## Latest CI verification — 2026-11-13

The four-job green [run #42](https://github.com/Maksi-Novagh/SafeExamOS/actions/runs/43408402740) covers the asynchronous pre-flight graphical startup path. The CI still checks Cage/Chromium presence and framebuffer capture, not actual typing, displayed verdict correctness, or a full test fixture for NetworkManager failures. Those require separate automation and physical checks.
