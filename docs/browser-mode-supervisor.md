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
