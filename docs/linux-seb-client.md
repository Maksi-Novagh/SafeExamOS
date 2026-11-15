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
