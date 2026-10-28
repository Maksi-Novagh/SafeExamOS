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

The kiosk session runs the collector before Chromium starts.

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

A warning does not automatically mean the machine is unusable. Policy-driven blocking comes later.

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
- keyboard layout selector and typing test;
- display scaling;
- accessibility controls;
- machine-readable hardware support classifications;
- PCI/USB identifiers for compatibility matching;
- policy result: supported / warning / blocking;
- automated fixture tests for the collector.
