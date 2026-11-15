# Experimental native Linux SEB client — first executable milestone

Status: **native application source and image packaging implemented; GTK/WebKit runtime and full exam lockdown NOT validated**.

## Source basis and license decision

The preferred feature-by-feature reference is [SEB Windows 3.10.3](https://github.com/SafeExamBrowser/seb-win-refactoring/releases/tag/v3.10.3), published 2026-11-02. Its repository is under **Mozilla Public License 2.0**, with modules such as Configuration, Browser, Settings, Lockdown, Communication and Server. We also consult [the macOS/iOS repository](https://github.com/SafeExamBrowser/seb-mac) for interface and browser behavior.

The Windows sources depend on .NET/WPF/CefSharp and Win32 security APIs; the macOS sources depend on Cocoa/WebKit, Apple entitlements and proprietary binary security modules not included in the public repository. **Neither binary can simply be recompiled as a Linux client.** The macOS repository specifically warns that the source is primarily offered for education and that security modules are omitted.

This project is an **independent Linux rewrite** informed by public interfaces and behavior. The first source files below do not copy proprietary security modules, implement patented/certification claims, or reuse official SEB branding as if this were an official release. If future contributions copy MPL-covered source, preserve its notices, license and source-distribution obligations before publishing binaries.

## First architecture

```text
SafeExamOS live ISO
  |
  +-- existing Chromium / Smartschool portal (UNCHANGED DEFAULT)
  |
  +-- safeexamos-linux-seb (optional native application)
       +-- linux_seb_policy.py (pure Python, strict offline validation)
       +-- GTK 3 window, WebKit2GTK 4.1 ephemeral WebContext
       +-- one WebView / one start URL
       +-- exact HTTPS-origin navigation allowlist
       +-- no downloads, pop-ups, or Web permission grants
       +-- restricted application key handler (defense in depth only)
```

Debian 13 packages: `python3`, `python3-gi`, `gir1.2-gtk-3.0` and `gir1.2-webkit2-4.1`. The last package is the WebKitGTK 4.1 GObject introspection binding for the GTK 3 rendering API.

Image-installed paths:

- `/usr/local/bin/safeexamos-linux-seb`
- `/usr/local/bin/linux_seb_policy.py`

Source paths: `linux-seb/app.py`, `linux-seb/policy.py`.

## Lab-only configuration

Only the explicitly labeled `safeexamos-linux-seb-lab-v1` JSON schema is accepted. Example: `linux-seb/examples/fixture.json`.

```sh
safeexamos-linux-seb --check-config --config ./fixture.json
safeexamos-linux-seb --config ./fixture.json
```

The second command requires an existing graphical Linux session and does not automatically use a SEB Server or start a real exam.

Allowed URL scope is an exact set of canonical HTTPS origins; unknown settings, additional ports, credentials in URLs, local/IP hosts, unsupported upload/download privileges, and unknown security-sensitive keys fail closed. The configuration is **not signed/authenticated**. Loading a third-party JSON file must therefore not be treated as authorization to take a real examination.

## Current tests

`tests/linux-seb-smoke.py` validates policy behavior with no GUI and no network:

- valid HTTPS exam origin and exact-match navigation;
- prevention of arbitrary origins and special protocols;
- rejecting unsafe or unknown policy fields, uploads/downloads and unsupported SEB-specific claims;
- missing or oversized configuration;
- existence of the native runtime script and explicit Debian package requirements.

The existing `scripts/check-build-tree.sh` runs these tests. The new executable is installed but **not enabled as the default exam browser** until the first GUI integration smoke test demonstrates its behavior in QEMU/VMware.

## Explicitly NOT implemented

- Native Wayland keyboard interception or a security-reviewed kiosk session
- Encrypted `.seb` format, password/certificate handling, Browser Exam Key, Config Key
- SEB Server session and assessment-system interoperability
- Multiwindow/PDF/upload rules beyond this first conservative baseline
- Support for proctoring, audio/video capture or approved external tools
- Reliable permitted Ctrl+T/Alt+F4/VT behavior at compositor/OS level
- Identity, encrypted local logs, crash/restore, verified profile shredding
- Security certification or endorsement by the official SEB project

## Recommended next development

1. Install from the Debian 13 package repository and verify the native GTK/WebKit window in QEMU.
2. Use safe local navigation fixtures to verify allowed vs blocked navigation and permission dialogs.
3. Integrate a controlled handoff from the existing pre-exam supervisor to the native Linux client, with explicit cleanup and no overlap.
4. Implement audited `.seb` configuration import, settings mapping and cryptographic compatibility with published test vectors.
5. Add compositor-level keyboard/VT restrictions and regression tests, without relying on JavaScript shortcut interception.
6. Add SEB Server integration only after an authorized lab assessment system can validate the claimed interfaces.

Until these gates pass, **SafeExamOS is a prototype, not an official or compatible SEB client**.

## Native graphical test in QEMU

The native client now offers a **CI-only offline renderer** selected by the kernel parameter `safeexamos.native_ci=1`, in addition to the application option `--smoke-ui`. Normal live boot remains the existing Chromium/Smartschool portal.

When the explicit parameter is present, the unprivileged Wayland session launches `safeexamos-linux-seb` under Cage instead of the portal supervisor. It loads a fixed in-memory HTML page (no external network and no real exam). The WebKit load-finished callback emits `SAFEEXAMOS_NATIVE_SEB_UI_READY`; a root-owned CI observer passes `SAFEEXAMOS_CI_NATIVE_SEB_OK` to the QEMU serial port. The new `scripts/qemu-native-seb-smoke.sh` captures the framebuffer and rejects a black/blank screen.

The `QEMU native WebKitGTK smoke` Actions job is deliberately separate from the standard four jobs and consumes the already built ISO. **A first green native run is required before declaring the GTK/WebKit application functional in QEMU.** A visual image alone does not validate URL filtering, keyboard lockdown, renderer stability on VMware, SEB compatibility or security.

The laboratory fixture is installed at `/usr/share/safeexamos/linux-seb-fixture.json` and is never used to authenticate a real examination.

## Managed multiwindow experiment (2026-11-15)

A new pure-Python registry (`linux-seb/windows.py`) tracks the native browser's main WebView and explicitly approved secondary WebViews. The extended laboratory configuration accepts `max_browser_windows` (1–3) and `allow_secondary_windows` (boolean). By default **all secondary windows are denied**. Both settings must agree, URL origin policy applies to each child, and exceeding the count is blocked. Only the main SEB application may create managed WebKitGTK child views; the module never executes arbitrary applications.

For future scenarios requiring several simultaneously visible windows, the Debian image now includes **labwc**, an optional stacked-window Wayland compositor. The experimental QEMU boot flag `safeexamos.windows_ci=1` selects labwc with a controlled `rc.xml` that avoids default application-launching shortcuts, menu actions, and additional workspaces. This option is never selected by normal boot, which remains Cage and the Chromium portal supervisor. The dedicated `QEMU managed window compositor smoke` job starts the native offline fixture in labwc and checks the framebuffer. The existing Cage tests are preserved.

**Crucial boundary:** a stock labwc configuration is *not* a security-grade global surface/process allowlist, so it cannot prove that an unapproved local Wayland client could not connect to the display. The WebKit application registry only manages its own child views, not unrelated programs. At this stage arbitrary external applications are **not supported**; reliable native app control will need a compositor security policy or isolated Wayland socket/cgroup/permission boundary. Do not describe this as completed exam lockdown.

The next tests should exercise the actual WebKit `create` and `ready-to-show` signals with controlled fixture URLs, verify that a second approved window appears, and attempt an unapproved Wayland client to measure the compositor boundary. The current window policy has deterministic unit tests; graphical tests prove only that the native UI renders under labwc.
