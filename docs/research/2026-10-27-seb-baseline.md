# SEB research baseline — 2026-10-27

This document freezes the initial upstream observations used to design SafeExamOS.

## Upstream activity

At the time of this snapshot:

- the SafeExamBrowser GitHub organization contains the Windows, macOS/iOS, server, verificator and screen-proctoring projects;
- the Windows repository was actively updated in October 2026;
- SEB Server and its GUI/setup repositories were also actively updated in October 2026.

Upstream organization:
https://github.com/SafeExamBrowser

## Windows client

Repository:
https://github.com/SafeExamBrowser/seb-win-refactoring

Current public release observed during research: **SEB 3.10.2**.

Important observations from the release notes and source:

- minimum Windows version is Windows 10 1803 for current 3.x releases;
- current Chromium engine is embedded through the Windows client stack;
- window monitoring and remote-session detection have received recent security work;
- runtime integrity verification exists;
- application monitoring includes prohibited remote-control software;
- Browser Exam Key is platform-specific.

### Request integrity headers

Current source in `SafeExamBrowser.Browser/Handlers/ResourceHandler.cs` conditionally adds:

- `X-SafeExamBrowser-ConfigKeyHash`;
- `X-SafeExamBrowser-RequestHash`.

The hashes are calculated using configuration/key material and the request URL.

Implication for SafeExamOS:

**We cannot claim BEK/CK interoperability merely by parsing a .seb file.**

A Linux build may require its own platform identity/test vectors and upstream cooperation.

## Configuration surface

Current Windows configuration keys include categories for:

- applications;
- browser;
- URL filtering;
- proxy;
- certificates;
- display;
- keyboard;
- mouse;
- proctoring;
- security;
- server/session behavior.

Source:
https://github.com/SafeExamBrowser/seb-win-refactoring/blob/master/SafeExamBrowser.Configuration/ConfigurationData/Keys.cs

SafeExamOS should build an explicit key-by-key compatibility table.

## SEB Server

Repository:
https://github.com/SafeExamBrowser/seb-server

The Windows runtime flow shows that server mode can:

- connect to a configured server;
- obtain available exams;
- obtain the configuration for an exam;
- load that configuration;
- notify the server about the selected exam;
- receive browser-exam-key-related session data;
- maintain connectivity during the exam.

This should be studied as a protocol/interoperability project, not reimplemented from guesses.

## Screen proctoring

Upstream already has:

- screen-proctoring code in the Windows client;
- a dedicated screen-proctoring server repository;
- a screen-proctoring GUI repository.

Relevant organization repositories:
https://github.com/SafeExamBrowser

Current Windows settings include:

- enabled flag;
- service URL;
- screenshot minimum/maximum interval;
- image format;
- image downscaling;
- quantization;
- cache size;
- optional metadata about active application/browser/window title.

SafeExamOS should first determine whether its supervision feature can interoperate with this ecosystem.

## Linux base research

### Debian 13

Debian 13 officially supports:

- amd64;
- arm64;
- armhf;
- riscv64;
- additional non-target architectures.

Debian 13 does **not** provide a normal i386 kernel/installer. i386 is now primarily a partial 32-bit userland on amd64.

Sources:

- https://www.debian.org/ports/i386/
- https://www.debian.org/releases/stable/release-notes/whats-new.en.html

### Chromium availability

Debian stable packages Chromium for at least:

- amd64;
- arm64;
- armhf.

Package versions may not be identical across architectures at the same moment, which matters for reproducibility and any browser-version-sensitive exam key behavior.

Source:
https://packages.debian.org/stable/chromium

### Kiosk compositor candidate

Cage is a small Wayland kiosk compositor intended to run a single maximized application.

Repository:
https://github.com/cage-kiosk/cage

It is a useful component candidate, but SafeExamOS must not treat compositor kiosk behavior as its only security boundary.

## Initial decisions resulting from this research

1. Use Debian 13 as the primary base candidate for amd64, arm64 and armhf.
2. Treat 32-bit x86 as a separate legacy feasibility track.
3. Start with documentation and compatibility tests before claiming SEB compatibility.
4. Keep the privileged policy core small and memory-safe.
5. Use an unprivileged browser/UI.
6. Build a hardware pre-flight environment before lockdown.
7. Research upstream screen-proctoring interoperability before inventing a new protocol.
8. Do not implement raw keylogging as a normal supervision feature.
9. Make Browser Exam Key / Config Key compatibility a gated milestone requiring test vectors.
