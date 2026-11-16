# Isolated browser-mode supervisor — prototype (2026-11-15)

Status: **implementation pending CI**. The scope is portal/demo data separation, NOT a certified examination browser.

## Motivation

The initial SafeExamOS launcher opened Smartschool and the local DEMO exam in one Chromium process/profile. That allowed cookies, storage, cache and session history from pre-exam portal use to remain accessible to the demonstration. JavaScript navigation cannot prevent this.

## Design

- Cage runs an unprivileged Python supervisor rather than one permanent Chromium process.
- The supervisor creates a loopback-only HTTP origin on `127.0.0.1:38652` and serves only files explicitly allowed in its current mode.
- `portal` serves the launcher and portal configuration; `demo` serves only the local demonstration.
- A transition request requires same-origin POST, application/json, an unpredictable token embedded in the currently served page, and a valid state transition.
- Browser instances have distinct profiles in `/run/safeexamos-exam/profiles/portal` and `/run/safeexamos-exam/profiles/demo`.
- The supervisor terminates the prior process group and deletes its profile before starting a new browser. Token rotates at transition.
- Unexpected Chromium exit causes a fail-closed supervisor exit and existing systemd restart, rather than silently opening a general desktop.
- Chromium sandbox, unprivileged `exam` account, seatd, Cage and the Pixman reference renderer stay enabled.
- Pre-flight snapshots remain within the temporary run directory; neither account secrets nor exam responses are intentionally logged.

## Crucial limitations

**Shared managed policies:** portal and demo still use the same system-level Chromium policies, including the Smartschool/SSO URL exceptions. Isolating browser profiles does **not** make the demo a restricted exam mode or prevent all external navigation. A separate exam policy and enforcement mechanism must be built and tested before any production use.

**Browser shortcuts:** Ctrl+T/Ctrl+N/Ctrl+W/Alt+F4 and OS-level keyboard escape protections are still not fully validated. Browser DevTools policy is present, but shortcut/command interception remains a blocker.

**Portal-to-exam flow:** Smartschool login is still a general pre-exam portal experience. A real portal's exam launch link and SSO redirect chain have not been tested and do not automatically enter our demo mode. `DEMO` from the local launcher is the only implemented controlled transition.

**Authentication:** the local transition token prevents ordinary external web pages from requesting mode switches. It is not an institutional identity check, signed exam configuration, or a defense against malicious local processes with the same user's privileges.

**Network:** the loopback address is explicitly allowed in the managed Chromium URL policy. The external Smartschool/SSO origin list remains a pre-exam allowance. Demo mode does not yet have its own network namespace or dedicated browser enterprise policy.

## Test coverage

`tests/session-supervisor-smoke.py` exercises portal/demo allowlisted files, localhost host checks, same-origin and token requirements, token rotation, invalid transition rejection, and distinct Chromium profile arguments. The existing launcher and demo model fixtures use transition requests rather than direct navigation. Static checks also ensure `python3` is explicitly installed and that Cage invokes the supervisor.

Next acceptance work: QEMU graphical transition with browser process termination and profile absence assertions, separate network/policy enforcement for exam mode, controlled session lifecycle on reboot, and actual Smartschool authentication with institutional authorization.

## Optional native WebKitGTK supervised laboratory handoff — 2026-11-16

An explicit kernel argument `safeexamos.native_supervisor_lab=1` enables an experimental **NATIVE** code in the existing launcher. With the flag absent, the native transition is rejected and the ordinary Smartschool/DEMO modes are unchanged. The loopback supervisor rotates its transition token, terminates Chromium and deletes its temporary profile, then starts the separately packaged native WebKitGTK executable with its lab fixture. The native process supplies a trusted GTK button to end the lab; only a clean exit (code 0) returns to the portal with a fresh profile. A non-zero exit fails closed rather than silently continuing. WebKit uses its ephemeral context and is not granted a Chromium profile. Native mode serves no launcher files over the loopback HTTP server.

**This remains a developer-only integration test, not a secure assessment flow:** the bundled JSON is an unsigned fixture, keyboard/compositor escape controls are incomplete, and the mode does not authenticate an exam or support SEB Server. The static/HTTP tests cover authorization and state transitions; a QEMU interactive transition and real WebKit shutdown must still be tested before calling the full graphical handoff verified. Rollback: boot without the flag or revert these changes.

The supervised native lab page is loaded from in-memory offline HTML rather than navigating to the fixture's fictitious HTTPS start URL; this prevents an unintended network request during the integration demonstration. It does not constitute an exam delivery path.

## QEMU native handoff and cleanup regression (2026-11-16)

A dedicated opt-in QEMU kernel flag, `safeexamos.native_handoff_ci=1`, runs a deterministic portal-to-native transition without real credentials. The unprivileged supervisor terminates Chromium, checks that the removed profile path no longer exists, launches the offline GTK/WebKit lab, then observes its controlled exit. The integration fixture records named transition and cleanup markers; a dedicated GitHub Actions job checks them, plus the captured display framebuffer. The supervisor no longer dereferences a cleared process handle when testing the native exit status.

This test verifies supervisor-controlled termination and profile-directory deletion, **not** provable erasure of bytes on storage, compositor-wide client isolation, or secure examination delivery. A successful test cannot certify the resistance of the Wayland compositor to another same-UID process. Without the explicit boot flag, the default Smartschool/DEMO boot path remains unchanged.
