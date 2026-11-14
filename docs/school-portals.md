# School portal browsing — pre-exam MVP (2026-11-14)

Status: **implementation awaiting full CI; real Smartschool login not yet independently tested**.

## Scope

SafeExamOS can show a school portal selector on its launcher. Smartschool is enabled by default. The user supplies only the school's platform code (for example `myschool`) or canonical `myschool.smartschool.be` hostname. The browser navigates to `https://myschool.smartschool.be/`, not an arbitrary user-supplied URL. Smartschool's official instructions confirm that schools have individual login subdomains: https://www.smartschool.be/fr/se-connecter/.

Chromium's managed `URLBlocklist` remains default-deny for HTTP/HTTPS with narrowly configured `URLAllowlist` exceptions. Per the documented Chrome filter format, a rule such as `https://smartschool.be` also matches its subdomains. Only an institution administrator should modify the catalog and rebuild an image; the student cannot add unrelated approved websites from the launcher.

Google and Microsoft identity-provider origins are allowed for common SSO flows. However **working login, MFA, redirects, cross-site cookies, CAPTCHAs, embedded exercises and third-party exam windows are NOT guaranteed or yet validated**. A real school may use additional domains and need a separately approved configuration.

## Institution-managed configuration

The source of truth is `config/portals.json` and its schema is strict:

- `kind: smartschool` exposes a constrained school-name field
- `kind: fixed` requires a canonical HTTPS `start_url`, such as an institution-owned platform URL
- `identity_origins` lists explicitly approved HTTPS SSO origins, without paths or queries

To add a fixed portal, an administrator edits `config/portals.json` and runs `python3 scripts/render-portals.py --write` before rebuilding. The generated files are `build/amd64/config/includes.chroot/usr/share/safeexamos/launcher/portals.js` and `build/amd64/config/includes.chroot/etc/chromium/policies/managed/safeexamos.json`. The CI executes `--check` to prevent policy/catalog mismatches. Changes must be reviewed and committed together.

The Chromium policy blocks general navigation, DevTools, printing, downloads and extensions. Only configured origins can show pop-ups; this is necessary for some SSO paths but introduces a **pre-exam** exception, not a secure exam lockdown. Configured-origin allowlisting does **not** prevent use of every unrelated feature within the provider's own website. Embedded assets and redirects hosted outside the configured origins may fail until explicitly reviewed.

## Separation from secured exam mode

This is a pre-exam portal browser with the same Chromium profile and process for the current prototype. It is **not** yet safe to use as a locked examination browser. Do not present a portal login as an exam launch or SEB certification.

Before production, the exam mode must be separate, with an authenticated exam configuration, its own narrow URL/device/browser policy, a protected profile/session transition, controlled uploads/secondary resources and proven browser-command/VT restrictions. `Ctrl+T` and similar shortcuts remain open security blockers.

## Testing and privacy

The tests use synthetic school names and platform URLs only; no real passwords are collected or logged. Network connectivity is a precondition. Full compatibility must be validated against a real school and each supported exam provider with authorization. Refer to `tests/portal-policy-smoke.py` and `tests/portal-browser-smoke.cjs` for current deterministic coverage.


## Data isolation between portal and demo (2026-11-15)

A new supervisor opens the local launcher through a loopback-only HTTP origin, then closes the portal browser and removes its temporary profile before launching the offline DEMO in a distinct profile. The return path similarly disposes of the demo profile. This is not a production exam: the global managed URL policy still allows Smartschool/SSO sites in both phases, and real exam launch integration is unverified. See [mode supervisor](browser-mode-supervisor.md).
